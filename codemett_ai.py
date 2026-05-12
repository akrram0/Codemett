import requests
import os
from dotenv import load_dotenv

# 🔥 load .env file
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
You are CodeMett AI, a debugging engine.
Return:
- root cause
- fix
- short explanation
"""

# =========================
# SAFETY CHECK
# =========================

if not API_KEY:
    raise Exception("❌ GROQ_API_KEY is missing. Check your .env file")


# =========================
# AI CALL
# =========================

def ask_ai(prompt):

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            },
            timeout=60
        )

        # 🔥 HTTP error check
        if r.status_code != 200:
            return f"❌ HTTP ERROR {r.status_code}: {r.text}"

        data = r.json()

        if "choices" not in data:
            return f"❌ API ERROR: {data}"

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "❌ AI TIMEOUT"

    except Exception as e:
        return f"❌ AI ERROR: {e}"
