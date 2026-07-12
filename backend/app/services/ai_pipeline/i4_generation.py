"""I4 — توليد المحتوى (claude-fable-5)

⚠️ لا تُولَّد فيديوهات هنا أبداً — نصوص وكويزات وتمارين فقط.
كل محتوى يُنشأ كـ Draft بـ is_ai_generated=True.
"""
import uuid

from sqlalchemy.orm import Session

from app.models import ContentType, User
from app.schemas.content import ContentItemCreate, LessonIn, ParagraphIn
from app.services.ai_pipeline.claude_client import ask_claude_json
from app.services.content_service import create_content_item

SYSTEM = """أنت مولّد محتوى تعليمي لمنصة تكوينية ثنائية اللغة (عربي/فرنسي).
ولّد المحتوى المطلوب بناءً على المصادر. ممنوع توليد فيديوهات.
أجب بـ JSON:
{
  "items": [
    {
      "type": "lesson"|"quiz"|"exercise",
      "title_ar": "...", "title_fr": "...",
      "paragraphs": [
        {"type": "text", "lang_hint": "ar"|"fr"|"auto", "content_html": "<p>...</p>"},
        {"type": "quiz", "questions": [
          {"question_text": "...", "question_type": "mcq"|"yes_no",
           "options": [{"id": "a", "text": "...", "is_correct": true}], "hint": "..."}
        ]},
        {"type": "exercise", "description": "...", "solution": "...", "hint": "..."}
      ]
    }
  ]
}
- المحتوى بلغة المصادر المطلوبة.
- content_html: HTML نظيف (p, h2, h3, ul, ol, li, strong, em)."""


def generate_contents(
    db: Session,
    admin: User,
    search_results: dict,
    analysis_results: dict,
    user_answer: dict,
    category_id: str | None,
) -> list[str]:
    """يولّد المحتويات المختارة ويُنشئها كـ Drafts — يُعيد قائمة IDs"""
    user_msg = (
        f"المصادر:\n{search_results}\n\n"
        f"التحليل:\n{analysis_results}\n\n"
        f"المحتويات المطلوب توليدها (اختيار المستخدم):\n{user_answer}"
    )
    generated = ask_claude_json(SYSTEM, user_msg, max_tokens=16384)

    created_ids: list[str] = []
    for item in generated.get("items", []):
        paragraphs: list[ParagraphIn] = []
        for i, p in enumerate(item.get("paragraphs", [])):
            ptype = p.get("type")
            if ptype == "text":
                paragraphs.append(
                    ParagraphIn(
                        type="text",
                        order=i,
                        lang_hint=p.get("lang_hint", "auto"),
                        content_html=p.get("content_html", ""),
                    )
                )
            elif ptype == "quiz":
                paragraphs.append(
                    ParagraphIn(
                        type="quiz",
                        order=i,
                        quiz_questions=[
                            {
                                "question_text": q["question_text"],
                                "question_type": q.get("question_type", "mcq"),
                                "options": q.get("options", []),
                                "hint": q.get("hint"),
                                "is_final_quiz": False,
                            }
                            for q in p.get("questions", [])
                        ],
                    )
                )
            elif ptype == "exercise":
                paragraphs.append(
                    ParagraphIn(
                        type="exercise",
                        order=i,
                        exercises=[
                            {
                                "description": p.get("description", ""),
                                "solution": p.get("solution", ""),
                                "hint": p.get("hint"),
                            }
                        ],
                    )
                )
            # ⚠️ أي نوع "video" يُتجاهل عمداً

        payload = ContentItemCreate(
            type=ContentType(item.get("type", "lesson")),
            title_ar=item.get("title_ar", ""),
            title_fr=item.get("title_fr", ""),
            category_id=uuid.UUID(category_id) if category_id else None,
            lessons=[
                LessonIn(
                    title_ar=item.get("title_ar", ""),
                    title_fr=item.get("title_fr", ""),
                    order=0,
                    paragraphs=paragraphs,
                )
            ],
        )
        content = create_content_item(db, payload, admin, is_ai_generated=True)
        created_ids.append(str(content.id))

    return created_ids
