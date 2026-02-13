import json

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0,
        messages=[
            {"role": "system", "content": PARSER_PROMPT},
            {"role": "user", "content": resume_text}
        ]
    )

    try:
        return json.loads(response.choices[0].message.content)
    except:
        print("❌ Parsing failed")
        return {"education": [], "employment": []}
