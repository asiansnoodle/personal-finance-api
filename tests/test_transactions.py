import pytest


@pytest.fixture()
def account(client, auth_headers):
    return client.post("/accounts", json={
        "name": "Checking", "account_type": "checking", "balance": "1000.00", "currency": "USD"
    }, headers=auth_headers).json()


@pytest.fixture()
def other_user_account(client):
    client.post("/auth/register", json={
        "email": "other@example.com", "password": "password123", "full_name": "Other"
    })
    other_token = client.post("/auth/login", data={
        "username": "other@example.com", "password": "password123"
    }).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    account = client.post("/accounts", json={
        "name": "Other Account", "account_type": "checking", "balance": "500.00", "currency": "USD"
    }, headers=other_headers).json()

    return account, other_headers


def test_create_transaction_success(client, auth_headers, account):
    response = client.post("/transactions", json={
        "account_id": account["id"],
        "amount": "50.00",
        "description": "Groceries",
        "category": "groceries",
        "transaction_date": "2025-01-15",
        "is_income": False
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["account_id"] == account["id"]
    assert data["amount"] == "50.00"
    assert data["category"] == "groceries"


def test_create_transaction_account_not_found(client, auth_headers):
    response = client.post("/transactions", json={
        "account_id": 99999,
        "amount": "50.00",
        "description": "Groceries",
        "transaction_date": "2025-01-15",
        "is_income": False
    }, headers=auth_headers)
    assert response.status_code == 404


def test_create_transaction_wrong_user_account(client, auth_headers, other_user_account):
    other_account, _ = other_user_account
    response = client.post("/transactions", json={
        "account_id": other_account["id"],
        "amount": "50.00",
        "description": "Groceries",
        "transaction_date": "2025-01-15",
        "is_income": False
    }, headers=auth_headers)
    assert response.status_code == 403


def test_get_transactions_empty(client, auth_headers):
    response = client.get("/transactions", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_transactions_returns_only_own(client, auth_headers, account, other_user_account):
    other_account, other_headers = other_user_account

    client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Mine",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers)
    client.post("/transactions", json={
        "account_id": other_account["id"], "amount": "50.00", "description": "Theirs",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=other_headers)

    response = client.get("/transactions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Mine"


def test_get_transaction_by_id(client, auth_headers, account):
    created = client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Groceries",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers).json()

    response = client.get(f"/transactions/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_transaction_not_found(client, auth_headers):
    response = client.get("/transactions/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_transaction_wrong_user(client, auth_headers, other_user_account):
    other_account, other_headers = other_user_account
    other_transaction = client.post("/transactions", json={
        "account_id": other_account["id"], "amount": "50.00", "description": "Theirs",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=other_headers).json()

    response = client.get(f"/transactions/{other_transaction['id']}", headers=auth_headers)
    assert response.status_code == 403


def test_get_transactions_filter_by_category(client, auth_headers, account):
    client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Groceries", "category": "groceries",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers)
    client.post("/transactions", json={
        "account_id": account["id"], "amount": "20.00", "description": "Coffee", "category": "dining",
        "transaction_date": "2025-01-16", "is_income": False
    }, headers=auth_headers)

    response = client.get("/transactions?category=groceries", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "groceries"


def test_get_transactions_filter_by_date_range(client, auth_headers, account):
    client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Early",
        "transaction_date": "2025-01-05", "is_income": False
    }, headers=auth_headers)
    client.post("/transactions", json={
        "account_id": account["id"], "amount": "20.00", "description": "Late",
        "transaction_date": "2025-01-25", "is_income": False
    }, headers=auth_headers)

    response = client.get("/transactions?start_date=2025-01-10&end_date=2025-01-31", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Late"


def test_get_transactions_filter_by_account_id(client, auth_headers, account):
    second_account = client.post("/accounts", json={
        "name": "Savings", "account_type": "savings", "balance": "0.00", "currency": "USD"
    }, headers=auth_headers).json()

    client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Checking txn",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers)
    client.post("/transactions", json={
        "account_id": second_account["id"], "amount": "20.00", "description": "Savings txn",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers)

    response = client.get(f"/transactions?account_id={second_account['id']}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Savings txn"


def test_patch_transaction_success(client, auth_headers, account):
    created = client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Groceries",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers).json()

    response = client.patch(f"/transactions/{created['id']}", json={
        "amount": "75.00", "description": "Groceries (updated)"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == "75.00"
    assert data["description"] == "Groceries (updated)"


def test_patch_transaction_move_to_owned_account(client, auth_headers, account):
    second_account = client.post("/accounts", json={
        "name": "Savings", "account_type": "savings", "balance": "0.00", "currency": "USD"
    }, headers=auth_headers).json()

    created = client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Groceries",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers).json()

    response = client.patch(f"/transactions/{created['id']}", json={
        "account_id": second_account["id"]
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["account_id"] == second_account["id"]


def test_patch_transaction_move_to_unowned_account(client, auth_headers, account, other_user_account):
    other_account, _ = other_user_account
    created = client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Groceries",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers).json()

    response = client.patch(f"/transactions/{created['id']}", json={
        "account_id": other_account["id"]
    }, headers=auth_headers)
    assert response.status_code == 403


def test_patch_transaction_not_found(client, auth_headers):
    response = client.patch("/transactions/99999", json={"amount": "10.00"}, headers=auth_headers)
    assert response.status_code == 404


def test_patch_transaction_wrong_user(client, auth_headers, other_user_account):
    other_account, other_headers = other_user_account
    other_transaction = client.post("/transactions", json={
        "account_id": other_account["id"], "amount": "50.00", "description": "Theirs",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=other_headers).json()

    response = client.patch(f"/transactions/{other_transaction['id']}", json={"amount": "1.00"}, headers=auth_headers)
    assert response.status_code == 403


def test_delete_transaction_success(client, auth_headers, account):
    created = client.post("/transactions", json={
        "account_id": account["id"], "amount": "50.00", "description": "Groceries",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=auth_headers).json()

    response = client.delete(f"/transactions/{created['id']}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/transactions/{created['id']}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_transaction_not_found(client, auth_headers):
    response = client.delete("/transactions/99999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_transaction_wrong_user(client, auth_headers, other_user_account):
    other_account, other_headers = other_user_account
    other_transaction = client.post("/transactions", json={
        "account_id": other_account["id"], "amount": "50.00", "description": "Theirs",
        "transaction_date": "2025-01-15", "is_income": False
    }, headers=other_headers).json()

    response = client.delete(f"/transactions/{other_transaction['id']}", headers=auth_headers)
    assert response.status_code == 403
