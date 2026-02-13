import json
import os
from openai import OpenAI

# Ensure API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=api_key)

PARSER_PROMPT = """
You are a resume parsing engine.

Extract ONLY factual information.
Return STRICT JSON:

{
  "education": [
    {
      "degree": "",
      "field": "",
      "start_year": "",
      "end_year": ""
    }
  ],
  "employment": [
    {
      "company": "",
      "role": "",
      "start_date": "",
      "end_date": ""
    }
  ]
}

Rules:
- No guessing
- No commentary
- JSON only
"""


def parse_resume(resume_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            temperature=0,
            messages=[
                {"role": "system", "content": PARSER_PROMPT},
                {"role": "user", "content": resume_text},
            ],
        )

        content = response.choices[0].message.content or ""

        return json.loads(content)

    except json.JSONDecodeError:
        print("❌ JSON parsing failed — invalid format returned by model")
    except Exception as e:
        print(f"❌ Resume parsing error: {e}")

    # Safe fallback
    return {"education": [], "employment": []}
