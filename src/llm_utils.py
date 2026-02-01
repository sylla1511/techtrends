import os
from dotenv import load_dotenv

# Charge .env si présent
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
HAS_OPENAI = bool(API_KEY) and API_KEY.startswith("sk-")

client = None
if HAS_OPENAI:
    try:
        from openai import OpenAI  # openai>=1.x
        client = OpenAI(api_key=API_KEY)
    except Exception:
        # Si la lib openai n'est pas installée ou autre souci,
        # on désactive simplement la fonctionnalité LLM.
        client = None
        HAS_OPENAI = False


def summarize_text(text: str, max_words: int = 120) -> str:
    """
    Résumé optionnel via OpenAI.
    - Si OPENAI_API_KEY n'est pas définie => fallback (pas de crash)
    - Si erreur réseau/quota => message, app continue
    """
    text = (text or "").strip()

    # Mode dégradé sans clé / sans client
    if not HAS_OPENAI or client is None:
        preview = (text[:150] + "...") if len(text) > 150 else text
        return (
            "🔒 Résumé indisponible (OpenAI non configuré).\n\n"
            f"Aperçu: {preview}\n\n"
            "Pour activer: ajoute OPENAI_API_KEY dans le fichier .env"
        )

    if not text:
        return "Aucun contenu à résumer."

    # Prompt
    prompt = (
        "Tu es un assistant qui résume des articles tech en français.\n"
        f"Résume le texte suivant en environ {max_words} mots, "
        "en listant les idées principales de façon claire et concise :\n\n"
        f"{text}"
    )

    try:
        # API OpenAI v1.x
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        msg = str(e).replace("\n", " ")
        return (
            "⚠️ Erreur OpenAI temporaire.\n\n"
            f"Détail: {msg[:120]}...\n\n"
            "(Le scraping, la base et les graphiques fonctionnent normalement.)"
        )