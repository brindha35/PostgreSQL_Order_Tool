
from fastapi import FastAPI, HTTPException

app = FastAPI()

customers = {
    1: {
        "name": "Arun",
        "plan": "Premium",
        "email": "arun@gmail.com",
        "city": "Chennai"
    },
    2: {
        "name": "Priya",
        "plan": "Basic",
        "email": "priya@gmail.com",
        "city": "Bangalore"
    },
    3: {
        "name": "Rahul",
        "plan": "Standard",
        "email": "rahul@gmail.com",
        "city": "Mumbai"
    },
    4: {
        "name": "Karthik",
        "plan": "Premium",
        "email": "karthik@gmail.com",
        "city": "Coimbatore"
    },
    5: {
        "name": "Divya",
        "plan": "Basic",
        "email": "divya@gmail.com",
        "city": "Trichy"
    }
}


@app.get("/customers/search")
def get_customer_by_email(email: str):

    for customer in customers.values():

        if customer["email"].lower() == email.lower():
            return customer

    raise HTTPException(
        status_code=404,
        detail="Customer not found"
    )


@app.get("/customers/{id}")
def get_customer(id: int):

    if id not in customers:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customers[id]
