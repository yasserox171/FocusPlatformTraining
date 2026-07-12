"""كشف المحتوى المكرر — قبل توليد المحتوى (I4)

يقارن الموضوعات المستخرجة من التحليل مع عناوين ContentItem الموجودة.
تشابه > 80% → تحذير للمستخدم (إنشاء جديد أم تحديث الموجود؟)
"""
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models import ContentItem

SIMILARITY_THRESHOLD = 0.8


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


def check_duplicates(db: Session, topics: list[str]) -> list[dict]:
    """يُعيد قائمة تحذيرات: [{"topic", "existing_id", "existing_title", "similarity"}]"""
    items = db.query(ContentItem).all()
    warnings: list[dict] = []
    for topic in topics:
        for item in items:
            score = max(_similarity(topic, item.title_ar), _similarity(topic, item.title_fr))
            if score > SIMILARITY_THRESHOLD:
                warnings.append(
                    {
                        "topic": topic,
                        "existing_id": str(item.id),
                        "existing_title": f"{item.title_ar} / {item.title_fr}",
                        "similarity": round(score * 100, 1),
                    }
                )
    return warnings
