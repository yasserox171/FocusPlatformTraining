"""عميل Claude API — مشترك بين مراحل الـ Pipeline (R1, I3, I4)"""
import json

import anthropic

from app.config import settings


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def ask_claude(system: str, user: str, max_tokens: int = 4096) -> str:
    client = get_client()
    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def ask_claude_json(system: str, user: str, max_tokens: int = 4096) -> dict | list:
    """يطلب من Claude إخراج JSON فقط ويفكّه — يتسامح مع أسوار الكود"""
    text = ask_claude(system + "\n\nأخرج JSON صالحاً فقط، بدون أي نص آخر.", user, max_tokens)
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
