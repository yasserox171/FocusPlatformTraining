"""خدمة الشهادات — توليد PDF + QR + الرقم التسلسلي

⚠️ قالب الشهادة الرسمي سيوفره ياسر لاحقاً — انظر app/utils/pdf_generator.py
"""
import secrets
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Certificate, CertificateType, ContentItem, User
from app.utils.pdf_generator import render_certificate_pdf
from app.utils.qr_generator import generate_qr_data_uri

CERT_TYPE_LABELS = {
    CertificateType.attendance: ("شهادة حضور", "Certificat de présence"),
    CertificateType.competency: ("شهادة كفاءة", "Certificat de compétence"),
}


def _generate_serial() -> str:
    year = datetime.now(timezone.utc).year
    return f"FPT-{year}-{secrets.token_hex(4).upper()}"


def issue_certificate(
    db: Session, learner: User, course: ContentItem, cert_type: CertificateType
) -> Certificate:
    """يُصدر الشهادة إن لم تكن موجودة (idempotent per learner+course+type)"""
    existing = db.query(Certificate).filter(
        Certificate.learner_id == learner.id,
        Certificate.course_id == course.id,
        Certificate.type == cert_type,
    ).first()
    if existing is not None:
        return existing

    # 1. رقم تسلسلي فريد
    serial = _generate_serial()
    while db.query(Certificate).filter(Certificate.serial_number == serial).first():
        serial = _generate_serial()

    # 2+3. QR يشير لصفحة التحقق العامة
    verify_url = f"{settings.APP_URL}/verify/{serial}"
    qr_data_uri = generate_qr_data_uri(verify_url)

    # 4. توليد PDF بالقالب (placeholder حتى يصل قالب ياسر)
    type_ar, type_fr = CERT_TYPE_LABELS[cert_type]
    issued = datetime.now(timezone.utc)
    pdf_path = str(Path(settings.CERTIFICATES_DIR) / f"{serial}.pdf")
    render_certificate_pdf(
        pdf_path,
        learner_name_ar=learner.full_name_ar,
        learner_name_fr=learner.full_name_fr,
        course_title_ar=course.title_ar,
        course_title_fr=course.title_fr,
        cert_type_ar=type_ar,
        cert_type_fr=type_fr,
        serial_number=serial,
        issued_date=issued.strftime("%Y-%m-%d"),
        qr_data_uri=qr_data_uri,
    )

    # 5. حفظ في قاعدة البيانات
    cert = Certificate(
        learner_id=learner.id,
        course_id=course.id,
        type=cert_type,
        serial_number=serial,
        qr_code_url=verify_url,
        pdf_path=pdf_path,
        issued_at=issued,
        template_data={
            "learner_name_ar": learner.full_name_ar,
            "learner_name_fr": learner.full_name_fr,
            "course_title_ar": course.title_ar,
            "course_title_fr": course.title_fr,
        },
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert
