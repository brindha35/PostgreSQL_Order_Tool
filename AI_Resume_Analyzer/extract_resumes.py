
from pathlib import Path
import json
import urllib.request
import urllib.error
import pymupdf



BASE_DIR = Path(__file__).resolve().parent
RESUME_DIR = BASE_DIR / "resumes"
PROMPT_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "outputs"


MODEL = "llama3.2:1b"
OLLAMA_URL = "http://localhost:11434/api/chat"


def read_resume(file_path):

    if file_path.suffix.lower() == ".pdf":

        doc = pymupdf.open(file_path)

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text

    elif file_path.suffix.lower() == ".txt":

        return file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

    return ""


def clean_text(text):

    return " ".join(text.split())


def load_schema():

    schema_path = PROMPT_DIR / "schema.json"

    with open(schema_path, "r", encoding="utf-8") as file:

        return json.load(file)


def load_system_prompt():

    prompt_path = PROMPT_DIR / "system_prompt.txt"

    with open(prompt_path, "r", encoding="utf-8") as file:

        return file.read()


def extract_resume_information(resume_text, schema, system_prompt):

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": "Extract information from this resume:\n\n"
                           + resume_text
            }
        ],
        "format": schema,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=180) as response:

        result = json.loads(response.read().decode("utf-8"))

    content = result["message"]["content"]

    return json.loads(content)


def main():

    OUTPUT_DIR.mkdir(exist_ok=True)

    schema = load_schema()

    system_prompt = load_system_prompt()

    resume_files = sorted(
        file for file in RESUME_DIR.glob("resume_*")
        if file.suffix.lower() in [".txt", ".pdf"]
    )

    if not resume_files:

        print("No resume files found!")

        return

    print("Total resumes found:", len(resume_files))

    successful = 0
    failed = 0

    for resume_file in resume_files:

        print("\nProcessing:", resume_file.name)

        try:

            resume_text = read_resume(resume_file)

            resume_text = clean_text(resume_text)

            if not resume_text:

                print("No readable text found!")

                failed += 1

                continue

            extracted_data = extract_resume_information(
                resume_text,
                schema,
                system_prompt
            )

            output_file = OUTPUT_DIR / (
                resume_file.stem + ".json"
            )

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    extracted_data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            print("Extraction successful!")
            print("Saved:", output_file.name)

            successful += 1

        except Exception as error:

            print("Extraction failed:", error)

            failed += 1

    print("\n========== EXTRACTION SUMMARY ==========")

    print("Total resumes:", len(resume_files))
    print("Successful:", successful)
    print("Failed:", failed)


if __name__ == "__main__":

    main()
