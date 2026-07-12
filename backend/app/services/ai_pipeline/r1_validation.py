"""R1 — تقييم وضوح الـ Prompt عبر Claude API (claude-fable-5)"""
from app.services.ai_pipeline.claude_client import ask_claude_json

SYSTEM = """أنت مدقق طلبات لمنصة تكوينية ثنائية اللغة (عربي/فرنسي).
قيّم وضوح طلب البحث عن مواد تعليمية.
أجب بـ JSON: {"clear": true/false, "reason": "...", "language": "ar"|"fr"|"both", "topic": "..."}
- clear=false إذا كان الطلب غامضاً أو لا يحدد موضوعاً تعليمياً.
- language: اللغة المطلوبة للمصادر حسب الطلب."""


def validate_prompt(prompt: str) -> dict:
    """يُعيد {"clear": bool, "reason": str, "language": str, "topic": str}
    يرفع الاستثناء عند فشل الاتصال — يعالجه الـ task بـ error="connection_error"
    """
    result = ask_claude_json(SYSTEM, prompt)
    if not isinstance(result, dict) or "clear" not in result:
        return {"clear": False, "reason": "prompt_unclear", "language": "both", "topic": ""}
    return result
