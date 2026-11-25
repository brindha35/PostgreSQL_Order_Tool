
from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import json

from app.tools import get_customer_details

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


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

    messages = [
        {
            "role": "system",
            "content": (
                "You are a CRM assistant. "
                "You have access to an authorized mock CRM database. "
                "When the user asks for customer details or information "
                "about a customer, you MUST call the "
                "get_customer_details tool using the customer ID. "
                "Do not refuse requests for the mock CRM data. "
                "Use the tool result to answer the user. "
                "Never invent customer information."
            )
        },
        {
            "role": "user",
            "content": request.message
        }
    ]

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

                return {
                    "response": final_response.message.content
                }

    return {
        "response": response.message.content
    }
