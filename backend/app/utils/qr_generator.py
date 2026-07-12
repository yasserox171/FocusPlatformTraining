"""توليد QR code يشير لصفحة التحقق العامة /verify/{serial_number}"""
import base64
import io

import qrcode


def generate_qr_png_bytes(url: str) -> bytes:
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_qr_data_uri(url: str) -> str:
    """Data URI لتضمين الـ QR مباشرة في HTML القالب (WeasyPrint)"""
    png = generate_qr_png_bytes(url)
    return "data:image/png;base64," + base64.b64encode(png).decode()
