"""I2 — محرك البحث عن مصادر تعليمية وفق الـ Prompt (Celery Task يستدعيه)

يستخدم Claude مع أداة البحث في الويب إن توفرت، وإلا يولّد قائمة مصادر
معرفية من النموذج نفسه. يلتزم باللغة المطلوبة في الـ Prompt.
"""
import anthropic

from app.config import settings
from app.services.ai_pipeline.claude_client import ask_claude_json

SYSTEM = """أنت باحث عن مصادر تعليمية لمنصة تكوينية.
ابحث عن مصادر موثوقة حول الموضوع المطلوب، بنفس اللغة المطلوبة في الطلب.
أجب بـ JSON: {"sources": [{"title": "...", "url": "...", "summary": "...", "language": "ar"|"fr"}]}
أدرج 5 إلى 10 مصادر."""


def search_sources(prompt: str, language: str, topic: str) -> dict:
    """يُعيد {"sources": [...]} — يحاول أولاً بأداة web_search ثم يتراجع للنموذج"""
    query = f"الطلب: {prompt}\nالموضوع: {topic}\nاللغة المطلوبة: {language}"
    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4096,
            system=SYSTEM,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
            messages=[{"role": "user", "content": query}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        import json

        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception:
        # fallback: بدون أداة البحث
        return ask_claude_json(SYSTEM, query)
