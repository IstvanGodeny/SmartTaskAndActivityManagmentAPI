from tests.utils import create_user_helper, login_helper, TEST_PASSWORD

# Test for DB is on or down
def test_ping(client):
    response = client.get("/db/ping")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_login_returns_token(client):
    user = create_user_helper(client)
    token_data = login_helper(client, user["email"], TEST_PASSWORD)
    assert isinstance(token_data["access_token"], str)
    assert token_data["access_token"]
    assert token_data["token_type"] == "bearer"


def test_me_without_token(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_me_with_token(client):
    user = create_user_helper(client)
    token_data = login_helper(client, user["email"], TEST_PASSWORD)
    response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer " + token_data["access_token"]})
    assert response.status_code == 200
    assert response.json()["email"] == user["email"]
    assert response.json()["id"] == user["id"]
