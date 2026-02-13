import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PARSER_PROMPT = """
Extract structured data from resume.

Return JSON only:
{
  "identity": {
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": "",
    "github": ""
  },
  "skills": [],
  "education": [],
  "employment": []
}
"""


def parse_resume(file_path):
    with open(file_path, "r", errors="ignore") as f:
        text = f.read()

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0,
        messages=[
            {"role": "system", "content": PARSER_PROMPT},
            {"role": "user", "content": text},
        ],
    )

    try:
        parsed = json.loads(response.choices[0].message.content)
    except:
        parsed = {}

    parsed["raw_text"] = text
    return parsed
