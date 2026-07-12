"""مشاركة الشهادة على LinkedIn — رابط "Add to Profile" الرسمي"""
from urllib.parse import urlencode

from app.models import Certificate, CertificateType

ORGANIZATION_NAME = "Focus Platform Training"


def linkedin_add_to_profile_url(cert: Certificate, course_title: str) -> str:
    params = {
        "startTask": "CERTIFICATION_NAME",
        "name": course_title,
        "organizationName": ORGANIZATION_NAME,
        "issueYear": cert.issued_at.year,
        "issueMonth": cert.issued_at.month,
        "certUrl": cert.qr_code_url,
        "certId": cert.serial_number,
    }
    return "https://www.linkedin.com/profile/add?" + urlencode(params)
