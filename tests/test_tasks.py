from urllib import response

import pytest

from tests.utils import create_task_helper


# User isolation test
def test_user_isolation(client, user_a, user_b):
    task_a = create_task_helper(client, headers=user_a["headers"], payload_override={"title":"A task"})
    task_b = create_task_helper(client, headers=user_b["headers"], payload_override={"title":"B task"})

    # Test - User B cannot see User A's tasks
    response_a = client.get("/api/v1/tasks/",
                            headers=user_a["headers"])

    response_b = client.get("/api/v1/tasks/",
                            headers=user_b["headers"])
    assert response_a.status_code == response_b.status_code == 200  # Check for success request for both users
    assert len(response_a.json()) == len(response_b.json()) == 1    # Check for tasks for both users

    ids = {t["id"] for t in response_a.json()}
    assert task_a["id"] in ids
    assert task_b["id"] not in ids


# Ownership test with parameters
@pytest.mark.parametrize("method,json_body",
                         [
                             pytest.param("get", None, id="user-B-see-user-A-task"),
                             pytest.param("patch", {"is_done":True}, id="user-B-update-user-A-task"),
                             pytest.param("delete", None, id="user-B-delete-user-A-task"),

                         ])
def test_ownership(client, user_a, user_b, method, json_body):
    task = create_task_helper(client, headers=user_a["headers"], payload_override={"title":"A task"})
    path = f"/api/v1/tasks/{task['id']}"
    request = getattr(client, method)
    if json_body is None:
        response = request(path, headers=user_b["headers"])
    else:
        response = request(path, headers=user_b["headers"], json=json_body)

    assert response.status_code == 404
    assert response.json().get("detail") == "Task not found"


# Auth test with parameters
@pytest.mark.parametrize("method, path, json_body",
                         [
                             pytest.param("get", "/api/v1/tasks/", None, id="get-all-tasks"),
                             pytest.param("get", "/api/v1/tasks/1", None, id="get-one-task"),
                             pytest.param("post", "/api/v1/tasks/", {"title":"A task"}, id="create-task"),
                             pytest.param("patch", "/api/v1/tasks/1", {"is_done":True}, id="update-task"),
                             pytest.param("delete", "/api/v1/tasks/1", None, id="delete-task"),
                         ])
def test_auth_requires_with_parameters(client, method, path, json_body):
    request = getattr(client, method)

    if json_body is None:
        response = request(path, headers={})
    else:
        response = request(path, headers={}, json=json_body)

    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


def test_positive(client, user_a):
    task = create_task_helper(client, headers=user_a["headers"], payload_override={"title":"A task"})

    # User A can get their tasks (list)
    response_get_tasks = client.get("/api/v1/tasks/",
                              headers=user_a["headers"])
    assert response_get_tasks.status_code == 200
    assert type(response_get_tasks.json()) == list

    # User A can get own task by ID (dictionary)
    response_get_a_task = client.get(f"/api/v1/tasks/{task['id']}",
                              headers=user_a["headers"])
    assert response_get_a_task.status_code == 200
    assert type(response_get_a_task.json()) == dict

    # User A can update own task by ID (dictionary)
    response_patch = client.patch(f"/api/v1/tasks/{task['id']}",
                                  headers=user_a["headers"],
                                  json={"is_done": True})
    assert response_patch.status_code == 200
    assert type(response_patch.json()) == dict
    assert response_patch.json()["is_done"] == True

    # User A can delete own task by ID (dictionary)
    response_delete = client.delete(f"/api/v1/tasks/{task['id']}",
                                  headers=user_a["headers"])
    assert response_delete.status_code == 204

# Filtering
def test_task_filtering(client, user_a):
    task1 = create_task_helper(
        client,
        headers=user_a["headers"],
        payload_override={
            "title":"Task1",
            "is_done":False,
            "due_at":"2026-03-01T10:00:00",
        }
    )

    task2 = create_task_helper(
        client,
        headers=user_a["headers"],
        payload_override={
            "title": "Task2",
            "is_done": True,
            "due_at": "2026-03-02T10:00:00",
        }
    )

    task3 = create_task_helper(
        client,
        headers=user_a["headers"],
        payload_override={
            "title": "Task3",
            "is_done": False,
            "due_at": None,
        }
    )

    cases = [
        ({"is_done": False}, 200, {"Task1", "Task3"}),
        ({"is_done": True}, 200, {"Task2"}),
        ({"due_before": "2026-03-01T23:59:59"}, 200, {"Task1"}),
        ({"due_after": "2026-03-02T00:00:00"}, 200, {"Task2"}),
        ({"is_done": False, "due_before": "2026-03-01T23:59:59"}, 200, {"Task1"}),
        ({"due_after": "2026-03-02T00:00:00", "due_before": "2026-03-01T00:00:00"}, 422, "Date contradiction"),
        ({"is_done": False, "due_after": "2026-03-02T00:00:00", "due_before": "2026-03-01T00:00:00"}, 422, "Date contradiction"),
        ({"is_done": True, "due_after": "2026-03-02T00:00:00", "due_before": "2026-03-01T00:00:00"}, 422, "Date contradiction"),
        ({"due_after": "2026-03-01T00:00:00", "due_before": "2026-03-02T00:00:00"}, 200, {"Task1"}),
        ({"is_done": False, "due_after": "2026-03-01T00:00:00", "due_before": "2026-03-02T00:00:00"}, 200, {"Task1"}),
        ({"is_done": True, "due_after": "2026-03-01T00:00:00", "due_before": "2026-03-02T00:00:00"}, 200, set()),
    ]

    for params, expected_status, expected_result in cases:
        response = client.get(
            "/api/v1/tasks/",
            headers=user_a["headers"],
            params=params
        )
        assert response.status_code == expected_status
        if response.status_code == 200:
            titles = {t["title"] for t in response.json()}
            assert titles == expected_result
        elif response.status_code == 422:
            assert response.json()["detail"] == expected_result
