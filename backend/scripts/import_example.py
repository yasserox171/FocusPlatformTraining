"""مثال Python Script — الإدراج التلقائي عبر API Key

الاستخدام:
    export FPT_API_URL=http://localhost:8000
    export FPT_API_KEY=fpt_xxxxxxxx
    python scripts/import_example.py
"""
import os

import httpx

API_URL = os.environ.get("FPT_API_URL", "http://localhost:8000")
API_KEY = os.environ["FPT_API_KEY"]

content = {
    "type": "lesson",
    "title_ar": "مقدمة في السلامة المهنية",
    "title_fr": "Introduction à la sécurité au travail",
    "lessons": [
        {
            "title_ar": "مقدمة في السلامة المهنية",
            "title_fr": "Introduction à la sécurité au travail",
            "order": 0,
            "paragraphs": [
                {
                    "type": "text",
                    "order": 0,
                    "lang_hint": "ar",
                    "content_html": "<h2>ما هي السلامة المهنية؟</h2><p>مجموعة الإجراءات...</p>",
                },
                {
                    "type": "quiz",
                    "order": 1,
                    "quiz_questions": [
                        {
                            "question_text": "La sécurité au travail est-elle obligatoire ?",
                            "question_type": "yes_no",
                            "options": [
                                {"id": "yes", "text": "Oui", "is_correct": True},
                                {"id": "no", "text": "Non", "is_correct": False},
                            ],
                            "hint": "Pensez au code du travail.",
                        }
                    ],
                },
            ],
        }
    ],
}

response = httpx.post(
    f"{API_URL}/api/v1/content/import",
    json=content,
    headers={"X-API-Key": API_KEY},
    timeout=30,
)
response.raise_for_status()
print("تم الإنشاء كـ Draft:", response.json())
