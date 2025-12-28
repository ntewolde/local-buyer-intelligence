def test_requires_auth(client):
    res = client.get("/api/v1/geography")
    assert res.status_code == 401

def test_client_access_with_token(client, client_token):
    res = client.get(
        "/api/v1/geography",
        headers={"Authorization": f"Bearer {client_token}"}
    )
    assert res.status_code in (200, 404)


