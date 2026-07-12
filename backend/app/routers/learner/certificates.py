import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate, ContentItem, User
from app.security import require_learner
from app.services.linkedin_service import linkedin_add_to_profile_url

router = APIRouter(prefix="/api/learner/certificates", tags=["learner:certificates"])


def _cert_out(cert: Certificate, course: ContentItem) -> dict:
    return {
        "id": str(cert.id),
        "type": cert.type.value,
        "serial_number": cert.serial_number,
        "qr_code_url": cert.qr_code_url,
        "issued_at": cert.issued_at.isoformat(),
        "course": {
            "id": str(course.id),
            "title_ar": course.title_ar,
            "title_fr": course.title_fr,
        },
        "linkedin_url": linkedin_add_to_profile_url(
            cert, f"{course.title_ar} / {course.title_fr}"
        ),
    }


@router.get("")
def my_certificates(db: Session = Depends(get_db), learner: User = Depends(require_learner)):
    certs = db.query(Certificate).filter(Certificate.learner_id == learner.id).all()
    return [_cert_out(c, db.get(ContentItem, c.course_id)) for c in certs]


@router.get("/{cert_id}/download")
def download_certificate(
    cert_id: uuid.UUID, db: Session = Depends(get_db), learner: User = Depends(require_learner)
):
    cert = db.get(Certificate, cert_id)
    if cert is None or cert.learner_id != learner.id:
        raise HTTPException(status_code=404, detail="شهادة غير موجودة / Certificat introuvable")
    return FileResponse(
        cert.pdf_path, media_type="application/pdf", filename=f"{cert.serial_number}.pdf"
    )
