# app/services/llm.py
import logging
from typing import List
import openai
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# Models confirmed available in your account
AVAILABLE_CHAT_MODELS: List[str] = [
    getattr(settings, "GROQ_MODEL", "openai/gpt-oss-20b"),
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
]

def get_groq_client() -> OpenAI:
    api_key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else ""
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

def generate_rag_answer(question: str, context: str) -> str:
    """
    Generates a concise, context-grounded response using Groq.
    Tries the configured model first, falling back to other active models if needed.
    """
    if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.strip():
        return "Configuration Error: GROQ_API_KEY is missing. Please set it in your .env file."

    client = get_groq_client()

    system_prompt = (
        "You are IntelliDocs, a study tutor who explains concepts FAST and SIMPLE.\n"
        "STRICT RULES:\n"
        "- Maximum 4-5 sentences OR 3-4 short bullet points. Never more.\n"
        "- No headers, markdown titles, or multi-section breakdowns.\n"
        "- Explain like you are texting a friend before an exam — quick and clear.\n"
        "- Use your own words. Never copy verbatim sentences from the notes.\n"
        "- If the answer is not in the notes, say: \"Not in your notes, but here's a quick explanation:\" then answer briefly.\n"
        "- Never refuse to answer."
    )

    if context and context.strip():
        user_prompt = f"NOTES CONTEXT:\n{context.strip()}\n\nQUESTION: {question}"
    else:
        user_prompt = f"QUESTION: {question}"

    # Deduplicate candidate models
    models_to_try = []
    for model in AVAILABLE_CHAT_MODELS:
        if model and model not in models_to_try:
            models_to_try.append(model)

    last_error = ""

    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=250,
                temperature=0.3
            )
            return response.choices[0].message.content

        except openai.NotFoundError as e:
            last_error = f"Model '{model_name}' not accessible"
            logger.warning(f"{last_error}. Trying next fallback...")
            continue

        except openai.AuthenticationError:
            return "Authentication Error: Invalid GROQ_API_KEY. Please check your credentials in .env."

        except openai.RateLimitError:
            return "Rate Limit: Groq API limit reached. Please wait a moment and try again."

        except Exception as e:
            return f"Service Error: Unable to generate reply ({str(e)})."

    return f"LLM Error: Could not generate reply ({last_error})."