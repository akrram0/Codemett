import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
You are CodeMett AI.

Rules:
- Be concise, exact, and practical.
- If the user says hi/hello or asks a normal question, answer naturally and briefly.
- If the user asks to analyze code, return ONLY:
Root Cause:
- ...
Fix:
- ...
Files Affected:
- ...
- Keep it short.
- No essay.
- No extra explanations.

Rewrite mode rules:
- If the user asks to improve, rewrite, refactor, or rewrite code:
  - return ONLY the final full rewritten code
  - no markdown
  - no explanation
  - no code fences
  - no comments unless useful in code
  - keep functionality unless the user asked to change it
"""

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing. Check your .env file")

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
                "temperature": 0.2
            },
            timeout=90
        )

        if r.status_code != 200:
            return f"HTTP ERROR {r.status_code}: {r.text}"

        data = r.json()
        if "choices" not in data:
            return f"API ERROR: {data}"

        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        return "AI TIMEOUT"
    except Exception as e:
        return f"AI ERROR: {e}"
