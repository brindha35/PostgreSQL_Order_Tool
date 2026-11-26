
import requests
import time
import csv
import json

BASE_URL = "http://127.0.0.1:8000"

scenarios = [
    {
        "id": "TC01",
        "question": "What are the working days mentioned in the document?",
        "expected": "monday",
        "session_id": "report01"
    },
    {
        "id": "TC02",
        "question": "Who should I contact for a password reset?",
        "expected": "it support",
        "session_id": "report02"
    },
    {
        "id": "TC03",
        "question": "When is the salary credited every month?",
        "expected": "last working day",
        "session_id": "report03"
    },
    {
        "id": "TC04",
        "question": "What is my passport number?",
        "expected": "passport",
        "session_id": "report04"
    },
    {
        "id": "TC05",
        "question": "Who won the cricket match yesterday?",
        "expected": "not aware",
        "session_id": "report05"
    },
    {
        "id": "TC06",
        "question": "Get customer details for customer ID 1.",
        "expected": "arun",
        "session_id": "report06"
    },
    {
        "id": "TC07",
        "question": "Find the customer with email priya@gmail.com.",
        "expected": "priya",
        "session_id": "report07"
    },
    {
        "id": "TC08",
        "question": "Get order details for order ID 1.",
        "expected": "shipped",
        "session_id": "report08"
    },
    {
        "id": "TC09",
        "question": "What is the status of order ID 1?",
        "expected": "shipped",
        "session_id": "report09"
    }
]

results = []

for scenario in scenarios:

    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": scenario["question"],
                "session_id": scenario["session_id"]
            },
            timeout=120
        )

        elapsed = round((time.time() - start_time) * 1000, 2)

        data = response.json()

        answer = data.get("response", "").lower()

        if scenario["id"] == "TC05":
            print("TC05 ANSWER:", answer)

        expected = scenario["expected"]

        if response.status_code == 200 and expected in answer:
            status = "PASS"
        else:
            status = "FAIL"

        tools_used = [
            item["tool"]
            for item in data.get("tool_calls", [])
        ]

        results.append({
            "Test ID": scenario["id"],
            "Status": status,
            "Response Time (ms)": elapsed,
            "Tools Used": ", ".join(tools_used) or "None"
        })

    except Exception as error:

        elapsed = round((time.time() - start_time) * 1000, 2)

        results.append({
            "Test ID": scenario["id"],
            "Status": "ERROR",
            "Response Time (ms)": elapsed,
            "Tools Used": str(error)
        })




try:

    requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": "A customer placed order 1. Please thank them for their order.",
            "session_id": "report10"
        },
        timeout=120
    ).raise_for_status()

    start_time = time.time()

    response = requests.post(
        f"{BASE_URL}/draft-email",
        json={
            "session_id": "report10",
            "tone": "formal"
        },
        timeout=120
    )

    elapsed = round((time.time() - start_time) * 1000, 2)

    data = response.json()

    if (
        response.status_code == 200
        and data.get("subject")
        and data.get("body")
    ):
        status = "PASS"
    else:
        status = "FAIL"

    results.append({
        "Test ID": "TC10",
        "Status": status,
        "Response Time (ms)": elapsed,
        "Tools Used": "Email Draft"
    })

except Exception as error:

    results.append({
        "Test ID": "TC10",
        "Status": "ERROR",
        "Response Time (ms)": 0,
        "Tools Used": str(error)
    })




with open(
    "tests/test_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Test ID",
            "Status",
            "Response Time (ms)",
            "Tools Used"
        ]
    )

    writer.writeheader()
    writer.writerows(results)


print("\nEND-TO-END TEST REPORT\n")

for result in results:
    print(result)

print("\nReport saved to tests/test_results.csv")
