import hashlib, hmac, json

KEY = {"X-API-Key": "test-api-key"}

def payload(name="Arun", email="arun@example.com"):
    return {"name": name, "email": email}

def test_create_customer(client):
    r = client.post("/customers", json=payload(), headers=KEY)
    assert r.status_code == 201
    assert r.json()["name"] == "Arun"

def test_list_customers_pagination(client):
    for i in range(6):
        client.post("/customers", json=payload(f"User{i}", f"u{i}@example.com"), headers=KEY)
    r = client.get("/customers?page=1&per_page=5", headers=KEY)
    assert r.status_code == 200
    assert len(r.json()) == 5

def test_get_customer(client):
    created = client.post("/customers", json=payload(), headers=KEY).json()
    assert client.get(f"/customers/{created['id']}", headers=KEY).status_code == 200

def test_update_customer(client):
    created = client.post("/customers", json=payload(), headers=KEY).json()
    r = client.put(f"/customers/{created['id']}", json=payload("Arun Updated", "new@example.com"), headers=KEY)
    assert r.status_code == 200 and r.json()["name"] == "Arun Updated"

def test_delete_customer(client):
    created = client.post("/customers", json=payload(), headers=KEY).json()
    assert client.delete(f"/customers/{created['id']}", headers=KEY).status_code == 204

def test_missing_api_key_is_401(client):
    assert client.get("/customers").status_code == 401

def test_wrong_api_key_is_403(client):
    assert client.get("/customers", headers={"X-API-Key": "wrong"}).status_code == 403

def test_unknown_customer_is_404(client):
    assert client.get("/customers/999", headers=KEY).status_code == 404

def test_duplicate_email_is_409(client):
    client.post("/customers", json=payload(), headers=KEY)
    assert client.post("/customers", json=payload("Other"), headers=KEY).status_code == 409

def test_invalid_payload_is_422(client):
    assert client.post("/customers", json={"name": ""}, headers=KEY).status_code == 422

def test_webhook_valid(client):
    body = json.dumps({"order_id": 123}).encode()
    sig = hmac.new(b"test-webhook-secret", body, hashlib.sha256).hexdigest()
    r = client.post("/webhooks/order-events", content=body, headers={"X-Signature": sig, "Content-Type": "application/json"})
    assert r.status_code == 200

def test_webhook_tampered(client):
    body = b'{"order_id":123}'
    r = client.post("/webhooks/order-events", content=body, headers={"X-Signature": "bad"})
    assert r.status_code == 401
