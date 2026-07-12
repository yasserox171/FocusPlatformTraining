"""توليد PDF الشهادة بـ WeasyPrint

⚠️ PLACEHOLDER — قالب الشهادة الرسمي سيوفره ياسر لاحقاً.
عند استلام القالب: استبدل CERTIFICATE_TEMPLATE_HTML أدناه (أو حمّله من ملف)
مع الإبقاء على نفس placeholders: {learner_name_ar}, {learner_name_fr},
{course_title_ar}, {course_title_fr}, {cert_type_ar}, {cert_type_fr},
{serial_number}, {issued_date}, {qr_data_uri}
"""
from pathlib import Path

# ============================================================
# PLACEHOLDER TEMPLATE — سيُستبدل بقالب ياسر الرسمي
# ============================================================
CERTIFICATE_TEMPLATE_HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="utf-8">
<style>
  @page {{ size: A4 landscape; margin: 0; }}
  body {{
    font-family: 'Cairo', 'DejaVu Sans', sans-serif;
    margin: 0; padding: 60px;
    background: #F1F5F9;
    color: #0F172A;
  }}
  .frame {{
    border: 6px double #1B4FD8;
    border-radius: 12px;
    padding: 48px;
    text-align: center;
    background: white;
    height: 100%;
  }}
  h1 {{ color: #1B4FD8; font-size: 34px; margin: 0 0 8px; }}
  .subtitle {{ color: #475569; font-size: 16px; margin-bottom: 32px; }}
  .name {{ font-size: 28px; font-weight: bold; margin: 16px 0; }}
  .course {{ font-size: 20px; color: #1B4FD8; margin: 8px 0 24px; }}
  .type {{ display: inline-block; background: #059669; color: white;
          padding: 6px 20px; border-radius: 999px; font-size: 14px; }}
  .footer {{ margin-top: 40px; display: flex; justify-content: space-between;
            align-items: flex-end; }}
  .serial {{ font-size: 12px; color: #475569; }}
  img.qr {{ width: 110px; height: 110px; }}
</style>
</head>
<body>
  <div class="frame">
    <h1>Focus Platform Training</h1>
    <div class="subtitle">شهادة / Certificat — مركز Focus، سافي، المغرب</div>
    <div class="type">{cert_type_ar} / {cert_type_fr}</div>
    <div class="name" dir="auto">{learner_name_ar}</div>
    <div class="name" dir="auto">{learner_name_fr}</div>
    <div class="course" dir="auto">{course_title_ar} / {course_title_fr}</div>
    <div class="footer">
      <div class="serial">
        الرقم التسلسلي / N° de série: {serial_number}<br>
        تاريخ الإصدار / Date: {issued_date}
      </div>
      <img class="qr" src="{qr_data_uri}" alt="QR">
    </div>
  </div>
</body>
</html>
"""


def render_certificate_pdf(output_path: str, **fields) -> str:
    # استيراد كسول — WeasyPrint يتطلب مكتبات نظام (pango/cairo) لا تلزم إلا هنا
    from weasyprint import HTML

    html = CERTIFICATE_TEMPLATE_HTML.format(**fields)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(output_path)
    return output_path
