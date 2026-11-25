
from pathlib import Path
import pymupdf
import tiktoken
import re
import json
import requests



def clean_text(text):
    text = re.sub(r"Page \d+ of \d+", "", text)
    text = re.sub(r"Page \d+", "", text)
    text = " ".join(text.split())
    return text



def extract_details(text):
    details = {}

    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            details[key.strip().lower()] = value.strip()

    return details


def create_prompt(resume_text):
    prompt = f"""
You are an AI Resume Analyzer.

Extract the following four fields from the resume:
1. name
2. skills
3. experience
4. education

Rules:
- Use exactly these four lowercase JSON keys.
- Extract all available information.
- Do not invent information.
- If information is missing, return null.
- Keep every value as a string.
- Return only valid JSON.

Example output:
{{
    "name": "Arun",
    "skills": "Python, SQL",
    "experience": "3 years",
    "education": "B.Tech"
}}

Resume:
{resume_text}
"""
    return prompt



def analyze_resume_with_ai(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0
                }
            },
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        return result["response"]

    except requests.RequestException as error:
        return f"AI Error: {error}"



def read_resume(path):
    try:
        if path.endswith(".pdf"):
            doc = pymupdf.open(path)
            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

            if not text.strip():
                return "NO_TEXT_FOUND"

            return text

        elif path.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as file:
                return file.read()

        else:
            print("Unsupported file format")
            return ""

    except FileNotFoundError:
        print("Error: Resume file not found")
        return ""



resume_folder = Path("resumes")
resume_files = list(resume_folder.glob("*"))

encoding = tiktoken.get_encoding("cl100k_base")


for resume_path in resume_files:

    print("\nChecking:", resume_path.name)

    resume_text = read_resume(str(resume_path))

    if resume_text == "NO_TEXT_FOUND":
        print("Error - no text found (scanned or empty PDF)")
        continue

    if not resume_text.strip():
        print("Error - empty resume")
        continue

    cleaned_text = clean_text(resume_text)

    
    details = extract_details(resume_text)

    print("\nPython Extracted Details:")
    print(json.dumps(details, indent=4))

    
    prompt = create_prompt(cleaned_text)

    
    ai_result = analyze_resume_with_ai(prompt)

    print("\nAI Extracted Result:")
    print(ai_result)

    
    characters = len(cleaned_text)
    tokens = encoding.encode(cleaned_text)

    print(
        "\n",
        resume_path.name,
        ":",
        characters,
        "characters,",
        len(tokens),
        "tokens"
    )
