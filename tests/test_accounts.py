def test_create_account_success(client, auth_headers):
    response = client.post("/accounts", json={
        "name": "Checking",
        "account_type": "checking",
        "balance": "1000.00",
        "currency": "USD"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Checking"
    assert data["balance"] == "1000.00"

def test_get_accounts_empty(client, auth_headers):
    response = client.get("/accounts", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_accounts_returns_only_own(client, auth_headers):
    client.post("/accounts", json={
        "name": "My Account", "account_type": "checking", "balance": "500.00", "currency": "USD"
    }, headers=auth_headers)

    response = client.get("/accounts", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_account_by_id(client, auth_headers):
    created = client.post("/accounts", json={
        "name": "Savings", "account_type": "savings", "balance": "2000.00", "currency": "USD"
    }, headers=auth_headers).json()

    response = client.get(f"/accounts/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_account_not_found(client, auth_headers):
    response = client.get("/accounts/99999", headers=auth_headers)
    assert response.status_code == 404

def test_get_account_wrong_user(client, auth_headers):
    # Create a second user and their account
    client.post("/auth/register", json={
        "email": "other@example.com", "password": "password123", "full_name": "Other"
    })
    other_token = client.post("/auth/login", data={
        "username": "other@example.com", "password": "password123"
    }).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    other_account = client.post("/accounts", json={
        "name": "Other Account", "account_type": "checking", "balance": "100.00", "currency": "USD"
    }, headers=other_headers).json()

    response = client.get(f"/accounts/{other_account['id']}", headers=auth_headers)
    assert response.status_code == 403


def test_patch_account_success(client, auth_headers):
    created = client.post("/accounts", json={
        "name": "Checking", "account_type": "checking", "balance": "1000.00", "currency": "USD"
    }, headers=auth_headers).json()

    response = client.patch(f"/accounts/{created['id']}", json={
        "name": "Renamed", "balance": "1500.00"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Renamed"
    assert data["balance"] == "1500.00"
    assert data["account_type"] == "checking"


def test_patch_account_invalid_type(client, auth_headers):
    created = client.post("/accounts", json={
        "name": "Checking", "account_type": "checking", "balance": "1000.00", "currency": "USD"
    }, headers=auth_headers).json()

    response = client.patch(f"/accounts/{created['id']}", json={
        "account_type": "piggybank"
    }, headers=auth_headers)
    assert response.status_code == 422


def test_patch_account_not_found(client, auth_headers):
    response = client.patch("/accounts/99999", json={"name": "Nope"}, headers=auth_headers)
    assert response.status_code == 404


def test_patch_account_wrong_user(client, auth_headers):
    client.post("/auth/register", json={
        "email": "other3@example.com", "password": "password123", "full_name": "Other3"
    })
    other_token = client.post("/auth/login", data={
        "username": "other3@example.com", "password": "password123"
    }).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    other_account = client.post("/accounts", json={
        "name": "Other Account", "account_type": "checking", "balance": "100.00", "currency": "USD"
    }, headers=other_headers).json()

    response = client.patch(f"/accounts/{other_account['id']}", json={"name": "Hacked"}, headers=auth_headers)
    assert response.status_code == 403


def test_delete_account_success(client, auth_headers):
    account = client.post("/accounts", json={
        "name": "To Delete", "account_type": "checking", "balance": "0.00", "currency": "USD"
    }, headers=auth_headers).json()

    response = client.delete(f"/accounts/{account['id']}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/accounts/{account['id']}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_account_blocked_by_transactions(client, auth_headers):
    account = client.post("/accounts", json={
        "name": "Has Transactions", "account_type": "checking", "balance": "500.00", "currency": "USD"
    }, headers=auth_headers).json()

    client.post("/transactions", json={
        "account_id": account["id"],
        "amount": "50.00",
        "description": "Test transaction",
        "transaction_date": "2025-01-15",
        "is_income": False
    }, headers=auth_headers)

    response = client.delete(f"/accounts/{account['id']}", headers=auth_headers)
    assert response.status_code == 400


def test_delete_account_not_found(client, auth_headers):
    response = client.delete("/accounts/99999", headers=auth_headers)
    assert response.status_code == 404

def test_delete_account_wrong_user(client, auth_headers):
    client.post("/auth/register", json={
        "email": "other2@example.com", "password": "password123", "full_name": "Other2"
    })
    other_token = client.post("/auth/login", data={
        "username": "other2@example.com", "password": "password123"
    }).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    other_account = client.post("/accounts", json={
        "name": "Other Account", "account_type": "checking", "balance": "100.00", "currency": "USD"
    }, headers=other_headers).json()

    response = client.delete(f"/accounts/{other_account['id']}", headers=auth_headers)
    assert response.status_code == 403

def test_create_account_invalid_type(client, auth_headers):
    response = client.post("/accounts", json={
        "name": "Bad Account", "account_type": "piggybank", "balance": "0.00", "currency": "USD"
    }, headers=auth_headers)
    assert response.status_code == 422