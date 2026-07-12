"""صفحة التحقق من الشهادة — عامة (بدون login) — لا تعرض بيانات حساسة"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate, ContentItem, User

router = APIRouter(tags=["public"])


@router.get("/api/verify/{serial_number}")
def verify_certificate(serial_number: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.serial_number == serial_number).first()
    if cert is None:
        raise HTTPException(status_code=404, detail="شهادة غير موجودة / Certificat introuvable")
    learner = db.get(User, cert.learner_id)
    course = db.get(ContentItem, cert.course_id)
    # بيانات العرض فقط — لا email ولا معلومات حساسة
    return {
        "valid": True,
        "serial_number": cert.serial_number,
        "type": cert.type.value,
        "issued_at": cert.issued_at.date().isoformat(),
        "learner_name_ar": learner.full_name_ar,
        "learner_name_fr": learner.full_name_fr,
        "course_title_ar": course.title_ar,
        "course_title_fr": course.title_fr,
    }
