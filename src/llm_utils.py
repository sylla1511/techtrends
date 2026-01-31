import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

# Initialize OpenAI client
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)
# Function to summarize text using OpenAI
def summarize_text(text: str, max_words: int = 120) -> str:
    if not API_KEY:
        return "Clé API OpenAI manquante. Veuillez configurer OPENAI_API_KEY."
    if not text:
        return "Aucun contenu à résumer."

    prompt = (
        "Tu es un assistant qui résume des articles tech en français.\n"
        f"Résume le texte suivant en environ {max_words} mots, "
        "en listant les idées principales de façon claire et concise :\n\n"
        f"{text}"
    )

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.5,
    )
    return resp.choices[0].message.content.strip()
