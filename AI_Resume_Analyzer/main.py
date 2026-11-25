
from pathlib import Path
import pymupdf
import tiktoken
import re
import json


def clean_text(text):
    text = re.sub(r"Page \d+ of \d+", "", text)
    text = re.sub(r"Page \d+", "", text)
    text = " ".join(text.split())
    return text


def extract_name(text):
    for line in text.splitlines():
        if line.startswith("Name:"):
            return line.replace("Name:", "").strip()

    return "Not found"


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

Extract these details:
1. Name
2. Skills
3. Experience
4. Education

Return only JSON.
If information is missing, return null.
Do not invent information.

Resume:
{resume_text}
"""
    return prompt


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
                text = file.read()

            return text

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
        print("Error - no text found")
        continue

    cleaned_text = clean_text(resume_text)

    
    details = extract_details(resume_text)

    print("Extracted Details:", details)

    
    json_output = json.dumps(details, indent=4)

    print("JSON Output:")
    print(json_output)

    
    prompt = create_prompt(resume_text)

    print("Generated Prompt:")
    print(prompt)

    
    characters = len(cleaned_text)
    tokens = encoding.encode(cleaned_text)

    print(
        resume_path.name,
        ":",
        characters,
        "characters,",
        len(tokens),
        "tokens"
    )
