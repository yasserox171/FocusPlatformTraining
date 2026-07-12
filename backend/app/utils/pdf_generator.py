"""توليد PDF الشهادة بـ WeasyPrint — القالب الرسمي لمركز Focus

القالب: صورة app/assets/certificate_template.png (A4 landscape) كخلفية كاملة،
تُركَّب فوقها الحقول الديناميكية في مواضعها الدقيقة:
  - اسم المتعلم، عنوان الدورة، مدة التكوين، فترة التكوين،
    تاريخ الإصدار، وQR code التحقق.
النصوص المؤقتة في الصورة (Nom et Prénom, XX heures...) تُغطى بلون الخلفية
الكريمي (#FCF9F4) قبل الكتابة فوقها.

الإحداثيات بالملم على صفحة 297×210 (مشتقة من بكسلات الصورة 1491×1055
بمعامل 0.1992 mm/px).
"""
import base64
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
TEMPLATE_IMAGE = ASSETS_DIR / "certificate_template.png"
# خط كتابي لاسم المتعلم — Great Vibes (ترخيص OFL)
SCRIPT_FONT = ASSETS_DIR / "fonts" / "GreatVibes-Regular.ttf"

CREAM = "#FCF9F4"
NAVY = "#293757"
GOLD = "#B58733"

CERTIFICATE_TEMPLATE_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{ size: A4 landscape; margin: 0; }}
  @font-face {{
    font-family: 'Great Vibes';
    src: url("{script_font_uri}");
  }}
  body {{ margin: 0; font-family: 'DejaVu Serif', serif; }}
  .page {{
    position: relative;
    width: 297mm; height: 210mm;
    background-image: url("{background_data_uri}");
    background-size: 297mm 210mm;
    background-repeat: no-repeat;
  }}
  .cover {{ position: absolute; background: {cream}; }}
  .field {{ position: absolute; text-align: center; }}

  /* اسم المتعلم — مكان "Nom et Prénom" */
  .name-cover {{ left: 84mm; top: 96mm; width: 135mm; height: 17mm; }}
  .name {{
    left: 48mm; top: 95.5mm; width: 201mm; height: 18mm;
    line-height: 18mm;
    font-family: 'Great Vibes', 'DejaVu Serif', serif;
    font-size: 38pt;
    word-spacing: 0.25em;
    color: {navy};
  }}

  /* عنوان الدورة — مكان "Intitulé de la formation" */
  .title-cover {{ left: 93mm; top: 127mm; width: 112mm; height: 9.5mm; }}
  .course-title {{
    left: 48mm; top: 127.5mm; width: 201mm; height: 9mm;
    line-height: 9mm;
    font-size: 15pt; font-weight: bold; letter-spacing: 1px;
    color: {gold};
    text-transform: uppercase;
  }}

  /* مدة التكوين — مكان "XX heures" */
  .duration-cover {{ left: 76mm; top: 149mm; width: 36mm; height: 7mm; }}
  .duration {{
    left: 76mm; top: 149.4mm; width: 36mm; height: 6mm;
    line-height: 6mm; text-align: left;
    font-size: 10.5pt; color: {navy};
  }}

  /* فترة التكوين — مكان "Du XX/XX/XXXX au XX/XX/XXXX" */
  .period-cover {{ left: 125mm; top: 149mm; width: 58mm; height: 7mm; }}
  .period {{
    left: 118mm; top: 149.4mm; width: 72mm; height: 6mm;
    line-height: 6mm;
    font-size: 10.5pt; color: {navy};
  }}

  /* تاريخ الإصدار — مكان "XX/XX/XXXX" تحت DÉLIVRÉ LE */
  .issued-cover {{ left: 137mm; top: 184mm; width: 25mm; height: 6mm; }}
  .issued {{
    left: 129mm; top: 184.2mm; width: 41mm; height: 5.5mm;
    line-height: 5.5mm;
    font-size: 9.5pt; font-weight: bold; color: {navy};
  }}

  /* QR التحقق — فوق مربع الـ QR في القالب */
  .qr-cover {{ left: 33.5mm; top: 168mm; width: 20.5mm; height: 20.5mm; }}
  .qr {{ position: absolute; left: 34mm; top: 168.5mm; width: 19.5mm; height: 19.5mm; }}
</style>
</head>
<body>
  <div class="page">
    <div class="cover name-cover"></div>
    <div class="field name">{learner_name}</div>

    <div class="cover title-cover"></div>
    <div class="field course-title">&#10022;&nbsp; {course_title} &nbsp;&#10022;</div>

    <div class="cover duration-cover"></div>
    <div class="field duration">{duration_text}</div>

    <div class="cover period-cover"></div>
    <div class="field period">Du {period_start} au {period_end}</div>

    <div class="cover issued-cover"></div>
    <div class="field issued">{issued_date}</div>

    <div class="cover qr-cover"></div>
    <img class="qr" src="{qr_data_uri}" alt="QR">
  </div>
</body>
</html>
"""


def _data_uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def render_certificate_pdf(
    output_path: str,
    *,
    learner_name: str,
    course_title: str,
    duration_hours: int | None,
    period_start: str,
    period_end: str,
    issued_date: str,
    qr_data_uri: str,
) -> str:
    # استيراد كسول — WeasyPrint يتطلب مكتبات نظام (pango/cairo) لا تلزم إلا هنا
    from weasyprint import HTML

    html = CERTIFICATE_TEMPLATE_HTML.format(
        background_data_uri=_data_uri(TEMPLATE_IMAGE, "image/png"),
        script_font_uri=_data_uri(SCRIPT_FONT, "font/ttf"),
        cream=CREAM,
        navy=NAVY,
        gold=GOLD,
        learner_name=learner_name,
        course_title=course_title,
        duration_text=f"{duration_hours} heures" if duration_hours else "&nbsp;",
        period_start=period_start,
        period_end=period_end,
        issued_date=issued_date,
        qr_data_uri=qr_data_uri,
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(output_path)
    return output_path
