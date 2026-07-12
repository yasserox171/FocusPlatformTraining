from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Category,
    Certificate,
    CertificateType,
    ContentItem,
    ContentStatus,
    ContentType,
    LearnerProgress,
    ProgressStatus,
    User,
    UserRole,
)
from app.security import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin:analytics"])


@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    learners_count = db.query(func.count(User.id)).filter(User.role == UserRole.learner).scalar()
    content_count = db.query(func.count(ContentItem.id)).scalar()
    certificates_count = db.query(func.count(Certificate.id)).scalar()
    drafts = (
        db.query(ContentItem)
        .filter(ContentItem.status == ContentStatus.draft)
        .order_by(ContentItem.created_at.desc())
        .limit(10)
        .all()
    )
    recent = (
        db.query(ContentItem).order_by(ContentItem.created_at.desc()).limit(10).all()
    )
    return {
        "learners_count": learners_count,
        "content_count": content_count,
        "certificates_count": certificates_count,
        "pending_drafts": [
            {
                "id": str(d.id),
                "type": d.type.value,
                "title_ar": d.title_ar,
                "title_fr": d.title_fr,
                "is_ai_generated": d.is_ai_generated,
                "created_at": d.created_at.isoformat(),
            }
            for d in drafts
        ],
        "recent_activity": [
            {
                "id": str(c.id),
                "type": c.type.value,
                "title_ar": c.title_ar,
                "title_fr": c.title_fr,
                "status": c.status.value,
                "created_at": c.created_at.isoformat(),
            }
            for c in recent
        ],
    }


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    # أكثر المحتويات مشاهدةً (حسب عدد سجلات التقدم)
    most_viewed = (
        db.query(
            ContentItem.id,
            ContentItem.title_ar,
            ContentItem.title_fr,
            func.count(LearnerProgress.id).label("views"),
        )
        .join(LearnerProgress, LearnerProgress.content_item_id == ContentItem.id)
        .group_by(ContentItem.id)
        .order_by(func.count(LearnerProgress.id).desc())
        .limit(10)
        .all()
    )

    # نسب إكمال الدورات
    courses = db.query(ContentItem).filter(
        ContentItem.type == ContentType.course,
        ContentItem.status == ContentStatus.published,
    ).all()
    completion_rates = []
    for course in courses:
        started = (
            db.query(func.count(func.distinct(LearnerProgress.learner_id)))
            .filter(LearnerProgress.content_item_id == course.id)
            .scalar()
        )
        completed = (
            db.query(func.count(func.distinct(LearnerProgress.learner_id)))
            .filter(
                LearnerProgress.content_item_id == course.id,
                LearnerProgress.paragraph_id.is_(None),
                LearnerProgress.unit_id.is_(None),
                LearnerProgress.lesson_id.is_(None),
                LearnerProgress.status == ProgressStatus.completed,
            )
            .scalar()
        )
        completion_rates.append(
            {
                "course_id": str(course.id),
                "title_ar": course.title_ar,
                "title_fr": course.title_fr,
                "started": started,
                "completed": completed,
                "rate": round(completed / started * 100, 1) if started else 0.0,
            }
        )

    # الشهادات: حضور vs كفاءة
    attendance = (
        db.query(func.count(Certificate.id))
        .filter(Certificate.type == CertificateType.attendance)
        .scalar()
    )
    competency = (
        db.query(func.count(Certificate.id))
        .filter(Certificate.type == CertificateType.competency)
        .scalar()
    )

    # توزيع المحتوى بالفئة
    by_category = (
        db.query(
            Category.id,
            Category.name_ar,
            Category.name_fr,
            func.count(ContentItem.id).label("count"),
        )
        .outerjoin(ContentItem, ContentItem.category_id == Category.id)
        .group_by(Category.id)
        .all()
    )

    return {
        "most_viewed": [
            {"id": str(r.id), "title_ar": r.title_ar, "title_fr": r.title_fr, "views": r.views}
            for r in most_viewed
        ],
        "completion_rates": completion_rates,
        "certificates": {"attendance": attendance, "competency": competency},
        "by_category": [
            {"id": str(r.id), "name_ar": r.name_ar, "name_fr": r.name_fr, "count": r.count}
            for r in by_category
        ],
    }
