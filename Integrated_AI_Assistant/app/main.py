
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import ollama
import json
import re
from pathlib import Path

from app.tools import get_customer_details, get_customer_by_email
from orders.tools import get_order_status

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

sessions = {}


# Read uploaded text documents
def read_document():

    document_folder = Path("uploads")
    content = ""

    for file_path in document_folder.glob("*.txt"):
        content += file_path.read_text(encoding="utf-8") + "\n"

    return content


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class EmailDraft(BaseModel):
    subject: str
    body: str


class EmailDraftRequest(BaseModel):
    session_id: str
    tone: str = "formal"


# Chat Endpoint
@app.post("/chat")
def chat(request: ChatRequest):

    session_id = request.session_id
    used_tools = []

    if session_id not in sessions:
        sessions[session_id] = []

    messages = [
        {
            "role": "system",
            "content": (
                "You are an internal CRM assistant. "
                "Answer general questions politely."
            )
        }
    ]

    messages.extend(sessions[session_id])

    messages.append({
        "role": "user",
        "content": request.message
    })

    message_lower = request.message.lower()

    # Document query detection
    is_document_query = any(
        keyword in message_lower
        for keyword in [
            "document",
            "working days",
            "password reset",
            "salary",
            "credited"
        ]
    )

    # Customer query detection
    customer_keywords = [
        "customer",
        "customer id",
        "customer details"
    ]

    is_customer_query = any(
        keyword in message_lower
        for keyword in customer_keywords
    )

    # Order query detection
    order_match = re.search(
        r"\border\s*(?:id)?\s*(\d+)\b",
        message_lower
    )

    is_order_query = (
        "order" in message_lower
        and order_match is not None
    )

    # Email detection
    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        request.message
    )

    is_email_query = (
        is_customer_query
        and email_match is not None
    )

    try:

        # Document question answering
        if is_document_query:

            document_content = read_document()

            if not document_content:
                answer = "No document content found."

            else:

                response = ollama.chat(
                    model="llama3.2:1b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Answer only using the provided document. "
                                "If the answer is not available in the "
                                "document, say so. Never guess."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Document:\n{document_content}\n\n"
                                f"Question: {request.message}"
                            )
                        }
                    ]
                )

                answer = response.message.content

        # Order details
        elif is_order_query:

            order_id = int(order_match.group(1))

            result = get_order_status(order_id)

            used_tools.append({
                "tool": "get_order_status",
                "arguments": {
                    "order_id": order_id
                }
            })

            answer = json.dumps(result, indent=2)

        # Customer email lookup
        elif is_email_query:

            email = email_match.group(0)

            result = get_customer_by_email(email)

            used_tools.append({
                "tool": "get_customer_by_email",
                "arguments": {
                    "email": email
                }
            })

            answer = json.dumps(result, indent=2)

        # Customer ID lookup
        elif is_customer_query:

            match = re.search(
                r"\b(\d+)\b",
                request.message
            )

            if match:

                customer_id = int(match.group(1))

                result = get_customer_details(customer_id)

                used_tools.append({
                    "tool": "get_customer_details",
                    "arguments": {
                        "customer_id": customer_id
                    }
                })

                answer = json.dumps(result, indent=2)

            else:

                answer = "Please provide a customer ID or email address."

        # General questions
        else:

            response = ollama.chat(
                model="llama3.2:1b",
                messages=messages
            )

            answer = response.message.content

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    sessions[session_id].append({
        "role": "user",
        "content": request.message
    })

    sessions[session_id].append({
        "role": "assistant",
        "content": answer
    })

    # Response sources
    if is_document_query:
        sources = ["Document: uploads"]

    elif is_order_query:
        sources = ["Orders: get_order_status"]

    elif is_email_query:
        sources = ["CRM: get_customer_by_email"]

    elif used_tools:
        sources = ["CRM: get_customer_details"]

    else:
        sources = []

    return {
        "response": answer,
        "sources": sources,
        "tool_calls": used_tools
    }


# Draft Email Endpoint
@app.post("/draft-email", response_model=EmailDraft)
def draft_email(request: EmailDraftRequest):

    if (
        request.session_id not in sessions
        or not sessions[request.session_id]
    ):

        return {
            "subject": "No conversation found",
            "body": "No conversation history is available for this session."
        }

    conversation = sessions[request.session_id]

    tone = request.tone.lower()

    if tone not in ["formal", "friendly"]:
        tone = "formal"

    prompt = f"""
    Based on the following conversation, create a polite summary email.

    Tone: {tone}

    Include:
    - Suitable email subject
    - Recipient greeting if recipient is known
    - Important conversation points
    - Next steps

    Return only valid JSON with exactly two keys:
    subject and body.

    Do not send the email. Only create a draft.

    Conversation:
    {json.dumps(conversation)}
    """

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format=EmailDraft.model_json_schema()
    )

    email_data = json.loads(response.message.content)

    return EmailDraft(**email_data)


# Document Upload Endpoint
@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join(
        "uploads",
        os.path.basename(file.filename)
    )

    try:

        with open(file_path, "wb") as f:
            f.write(await file.read())

        return {
            "message": "Document uploaded successfully",
            "filename": file.filename
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Document upload failed"
        )
