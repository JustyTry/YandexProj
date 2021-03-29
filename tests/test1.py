from requests import patch, post

data = post("http://127.0.0.1:8080/orders", json={"data": [{
    "order_id": 1,
    "weight": 0.23,
    "region": 12,
    "delivery_hours": ["09:00-18:00"]}]})
print(data)
