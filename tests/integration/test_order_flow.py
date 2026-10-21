import os

import httpx

ORDER_URL = os.getenv(
    "ORDER_URL",
    "http://127.0.0.1:8004" ,
)

def test_create_order_end_to_end():
    payload = {
        "customer_id": "integration-test-user" ,
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "unit_price": "2499.00",
            }
        ],
    }
    
    response = httpx.post(
        f"{ORDER_URL}/orders",
        json=payload,
        timeout=5,
    )
    
    print(response.status_code)
    print(response.text)
    assert response.status_code == 201
    body =  response.json()
    assert body["status"] == "CONFIRMED"
    assert body["customer_id"] == "integration-test-user"