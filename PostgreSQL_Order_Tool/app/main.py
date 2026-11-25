
from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import json

from app.tools import get_order_status, get_customer_orders

app = FastAPI()


class ChatRequest(BaseModel):
    message: str




tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get order status using order ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The order ID"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_orders",
            "description": "Get all orders for a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The customer ID"
                    }
                },
                "required": ["customer_id"]
            }
        }
    }
]


@app.get("/")
def home():
    return {"message": "Order Management AI Assistant is running"}


@app.post("/chat")
def chat(request: ChatRequest):

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an order management assistant. "
                    "Use the available tools to answer order questions. "
                    "Never write SQL queries."
                )
            },
            {
                "role": "user",
                "content": request.message
            }
        ],
        tools=tools
    )

    message = response["message"]

    tool_calls = message.get("tool_calls", [])

    if not tool_calls:
        return {
            "answer": message.get("content", ""),
            "tool_used": None
        }

    tool_results = []
    tool_messages = []

    for tool_call in tool_calls:

        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        print("FUNCTION NAME:", function_name)
        print("RAW ARGUMENTS:", repr(arguments))
        

        if function_name == "get_order_status":

            if "order_id" not in arguments:
                return {"error": "Order ID missing"}

            result = get_order_status(
    order_id=int(arguments["order_id"])
)

            result = get_order_status(
                order_id=arguments["order_id"]
            )

        elif function_name == "get_customer_orders":

            if "customer_id" not in arguments:
                return {"error": "Customer ID missing"}

            result = get_customer_orders(
                customer_id=arguments["customer_id"]
            )

        else:
            return {"error": "Unknown tool"}

        tool_results.append({
            "tool_used": function_name,
            "result": result
        })

        tool_messages.append({
            "role": "tool",
            "content": json.dumps(result)
        })

    

final_response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an order management assistant. "
                    "The database result is authorized information. "
                    "Answer the user's question using the database result. "
                    "Do not refuse the request. "
                    "Do not invent information."
                )
            },
            {
                "role": "user",
                "content": (
                    f"User question: {request.message}\n"
                    f"Database result: {json.dumps(tool_results)}\n"
                    "Explain the result clearly."
                )
            }
        ]
    )