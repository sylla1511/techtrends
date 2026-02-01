import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Vérif clé OpenAI → Mode dégradé automatique
API_KEY = os.getenv("OPENAI_API_KEY")
HAS_OPENAI = bool(API_KEY and API_KEY.startswith("sk-"))

# Initialise client UNIQUEMENT si clé valide
client = None
if HAS_OPENAI:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY)

def summarize_text(text: str, max_words: int = 120) -> str:
    """Résume texte avec OpenAI (fallback automatique sans clé)."""
    
    # Fallback si pas de clé
    if not HAS_OPENAI:
        return f"🔒 Résumé indisponible (OpenAI non configuré)\n\n" \
               f"Titre/Clés: {text[:150]}...\n" \
               f"Ajoute OPENAI_API_KEY dans .env pour activer."
    
    if not text:
        return "Aucun contenu à résumer."
    
    try:
        prompt = (
            "Tu es un assistant qui résume des articles tech en français.\n"
            f"Résume le texte suivant en environ {max_words} mots, "
            "en listant les idées principales de façon claire et concise :\n\n"
            f"{text}"
        )
        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # Corrigé (gpt-4.1-mini n'existe pas)
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
        
    except Exception as e:
        return f"⚠️ Erreur OpenAI temporaire: {str(e)[:50]}...\n" \
               f"(Scraping + graphs fonctionnent normalement)"
