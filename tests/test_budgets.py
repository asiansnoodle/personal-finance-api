import pytest


@pytest.fixture()
def budget_payload():
    return {
        "category": "food",
        "monthly_limit": "500.00",
        "month": 1,
        "year": 2025
    }


def test_create_budget_success(client, auth_headers, budget_payload):
    response = client.post("/budgets/", json=budget_payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "food"
    assert data["monthly_limit"] == "500.00"
    assert data["month"] == 1
    assert data["year"] == 2025


def test_create_budget_duplicate_period(client, auth_headers, budget_payload):
    client.post("/budgets/", json=budget_payload, headers=auth_headers)
    response = client.post("/budgets/", json=budget_payload, headers=auth_headers)
    assert response.status_code == 400


def test_get_budgets_empty(client, auth_headers):
    response = client.get("/budgets/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_budgets(client, auth_headers, budget_payload):
    client.post("/budgets/", json=budget_payload, headers=auth_headers)
    response = client.get("/budgets/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_budgets_filter_by_month(client, auth_headers):
    client.post("/budgets/", json={
        "category": "food", "monthly_limit": "400.00", "month": 1, "year": 2025
    }, headers=auth_headers)
    client.post("/budgets/", json={
        "category": "food", "monthly_limit": "400.00", "month": 2, "year": 2025
    }, headers=auth_headers)

    response = client.get("/budgets/?month=1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["month"] == 1


def test_get_budgets_filter_by_year(client, auth_headers):
    client.post("/budgets/", json={
        "category": "food", "monthly_limit": "400.00", "month": 1, "year": 2025
    }, headers=auth_headers)
    client.post("/budgets/", json={
        "category": "food", "monthly_limit": "400.00", "month": 1, "year": 2026
    }, headers=auth_headers)

    response = client.get("/budgets/?year=2025", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["year"] == 2025


def test_get_budget_by_id(client, auth_headers, budget_payload):
    created = client.post("/budgets/", json=budget_payload, headers=auth_headers).json()
    response = client.get(f"/budgets/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_budget_not_found(client, auth_headers):
    response = client.get("/budgets/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_budget_wrong_user(client, auth_headers, budget_payload):
    client.post("/auth/register", json={
        "email": "other@example.com", "password": "password123", "full_name": "Other"
    })
    other_token = client.post("/auth/login", data={
        "username": "other@example.com", "password": "password123"
    }).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    other_budget = client.post("/budgets/", json=budget_payload, headers=other_headers).json()

    response = client.get(f"/budgets/{other_budget['id']}", headers=auth_headers)
    assert response.status_code == 403


def test_patch_budget_success(client, auth_headers, budget_payload):
    created = client.post("/budgets/", json=budget_payload, headers=auth_headers).json()

    response = client.patch(f"/budgets/{created['id']}", json={
        "monthly_limit": "750.00"
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["monthly_limit"] == "750.00"


def test_patch_budget_duplicate_conflict(client, auth_headers):
    client.post("/budgets/", json={
        "category": "food", "monthly_limit": "400.00", "month": 1, "year": 2025
    }, headers=auth_headers)
    second = client.post("/budgets/", json={
        "category": "transport", "monthly_limit": "200.00", "month": 1, "year": 2025
    }, headers=auth_headers).json()

    response = client.patch(f"/budgets/{second['id']}", json={"category": "food"}, headers=auth_headers)
    assert response.status_code == 400


def test_delete_budget_success(client, auth_headers, budget_payload):
    created = client.post("/budgets/", json=budget_payload, headers=auth_headers).json()

    response = client.delete(f"/budgets/{created['id']}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/budgets/{created['id']}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_budget_not_found(client, auth_headers):
    response = client.delete("/budgets/99999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_budget_wrong_user(client, auth_headers, budget_payload):
    client.post("/auth/register", json={
        "email": "other2@example.com", "password": "password123", "full_name": "Other2"
    })
    other_token = client.post("/auth/login", data={
        "username": "other2@example.com", "password": "password123"
    }).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    other_budget = client.post("/budgets/", json=budget_payload, headers=other_headers).json()

    response = client.delete(f"/budgets/{other_budget['id']}", headers=auth_headers)
    assert response.status_code == 403
