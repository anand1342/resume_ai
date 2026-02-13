import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PARSER_PROMPT = """
Extract factual resume data.

Return JSON only:
{
  "education": [{"degree":"","field":"","start_year":"","end_year":""}],
  "employment": [{"company":"","role":"","start_date":"","end_date":""}]
}
"""

def parse_resume(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            temperature=0,
            messages=[
                {"role": "system", "content": PARSER_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"education": [], "employment": []}
