"""I3 — محرك التحليل (claude-fable-5)

يحلل المصادر، يصنّفها حسب Category الموجودة (أو ينشئ جديدة created_by_ai=True)،
ويحدد أنواع المحتوى الممكن إنشاؤها (R3 request).
"""
from sqlalchemy.orm import Session

from app.models import Category
from app.services.ai_pipeline.claude_client import ask_claude_json

SYSTEM = """أنت محلل محتوى تعليمي لمنصة تكوينية ثنائية اللغة (عربي/فرنسي).
حلّل المصادر المعطاة وأجب بـ JSON:
{
  "topics": ["..."],
  "category": {"existing_id": "uuid أو null", "name_ar": "...", "name_fr": "..."},
  "possible_contents": [
    {"type": "lesson"|"quiz"|"exercise"|"course", "title_ar": "...", "title_fr": "...", "description": "..."}
  ]
}
- إذا وُجدت فئة مناسبة في القائمة المعطاة استخدم existing_id، وإلا اقترح فئة جديدة (existing_id=null).
- possible_contents: 3 إلى 8 اقتراحات واقعية مبنية على المصادر."""


def analyze_sources(db: Session, prompt: str, search_results: dict) -> dict:
    categories = db.query(Category).all()
    cat_list = "\n".join(f"- {c.id}: {c.name_ar} / {c.name_fr}" for c in categories) or "(لا فئات بعد)"
    user_msg = (
        f"الطلب الأصلي: {prompt}\n\n"
        f"الفئات الموجودة:\n{cat_list}\n\n"
        f"المصادر:\n{search_results}"
    )
    analysis = ask_claude_json(SYSTEM, user_msg, max_tokens=8192)

    # إنشاء Category جديدة إذا لم توجد فئة مناسبة
    cat = analysis.get("category") or {}
    if not cat.get("existing_id") and cat.get("name_ar"):
        new_cat = Category(
            name_ar=cat["name_ar"], name_fr=cat.get("name_fr", cat["name_ar"]), created_by_ai=True
        )
        db.add(new_cat)
        db.commit()
        db.refresh(new_cat)
        analysis["category"]["existing_id"] = str(new_cat.id)

    return analysis
