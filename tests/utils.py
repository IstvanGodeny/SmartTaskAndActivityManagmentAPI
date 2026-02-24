import uuid

TEST_PASSWORD="TestPassword"


# Helpers
def make_email() -> str:
    return f"user_{uuid.uuid4().hex}@example.com"


def create_user_helper(client) -> dict:
    response = client.post("/api/v1/users/", json={"email": make_email(), "password": TEST_PASSWORD})
    assert response.status_code == 201
    return response.json()


def login_helper(client, user_email: str, password: str) -> dict:
    response = client.post("/api/v1/auth/login/", json={"email": user_email, "password": password})
    assert response.status_code == 200
    return response.json()

def create_task_helper(client, headers, payload_override=None) -> dict:
    response = client.post("/api/v1/tasks/", json=payload_override, headers=headers)
    assert response.status_code == 201
    return response.json()
