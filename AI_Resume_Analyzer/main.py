
from pathlib import Path
import pymupdf
import tiktoken
import re


def clean_text(text):

    text = re.sub(r"Page \d+ of \d+", "", text)

    text = re.sub(r"Page \d+", "", text)

    text = " ".join(text.split())

    return text


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
            with open(path, "r") as file:
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


    print("Checking:", resume_path.name)

    resume_text = read_resume(str(resume_path))

    cleaned_text = clean_text(resume_text)

    if cleaned_text == "NO_TEXT_FOUND":
        print(resume_path.name, ": Error - no text found (scanned or empty PDF)")
        continue

    if not cleaned_text:
        print(resume_path.name, ": Error - no text found")
        continue

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
