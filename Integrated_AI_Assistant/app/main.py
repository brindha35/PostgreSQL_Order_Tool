
from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import json

from app.tools import get_customer_details

app = FastAPI()

sessions = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class EmailDraft(BaseModel):
    subject: str
    body: str


class EmailDraftRequest(BaseModel):
    session_id: str
    tone: str = "formal"


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_customer_details",
            "description": "Retrieve customer details from the mock CRM database using customer ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID"
                    }
                },
                "required": ["customer_id"]
            }
        }
    }
]


@app.post("/chat")
def chat(request: ChatRequest):

    session_id = request.session_id

    if session_id not in sessions:
        sessions[session_id] = []

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful CRM assistant. "
                "Answer general questions politely. "
                "When the user mentions a customer ID or asks about a customer, "
                "use the get_customer_details tool. "
                "If the customer ID is available in previous conversation messages, "
                "use that ID. "
                "Never invent customer IDs or customer information. "
                "Use previous conversation messages to understand context."
            )
        }
    ]

    messages.extend(sessions[session_id])

    messages.append({
        "role": "user",
        "content": request.message
    })

    # Check whether the message is related to a customer
    customer_keywords = ["customer", "customer id", "customer details"]

    is_customer_query = any(
        keyword in request.message.lower()
        for keyword in customer_keywords
    )

    if not is_customer_query:

        response = ollama.chat(
            model="llama3.2:1b",
            messages=messages
        )

        answer = response.message.content

    else:

        response = ollama.chat(
            model="llama3.2:1b",
            messages=messages,
            tools=tools
        )

        if response.message.tool_calls:

            for tool_call in response.message.tool_calls:

                if tool_call.function.name == "get_customer_details":

                    customer_id = tool_call.function.arguments["customer_id"]

                    result = get_customer_details(customer_id)

                    messages.append(response.message)

                    messages.append({
                        "role": "tool",
                        "name": "get_customer_details",
                        "content": json.dumps(result)
                    })

                    final_response = ollama.chat(
                        model="llama3.2:1b",
                        messages=messages
                    )

                    answer = final_response.message.content
                    break

            else:
                answer = response.message.content

        else:
            answer = response.message.content

    # Save conversation history
    sessions[session_id].append({
        "role": "user",
        "content": request.message
    })

    sessions[session_id].append({
        "role": "assistant",
        "content": answer
    })

    return {"response": answer}


@app.post("/draft-email", response_model=EmailDraft)
def draft_email(request: EmailDraftRequest):

    if request.session_id not in sessions or not sessions[request.session_id]:
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
