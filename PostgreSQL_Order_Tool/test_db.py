from app.tools import get_order_status, get_customer_orders

print("Testing Order Status")

result = get_order_status(1042)
print(result)

print("\nTesting Customer Orders")

result = get_customer_orders(202)
print(result)