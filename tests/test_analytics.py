import pytest


@pytest.fixture()
def seeded(client, auth_headers):
    """Creates an account with known transactions and budgets for January 2025."""
    account = client.post("/accounts", json={
        "name": "Main", "account_type": "checking", "balance": "5000.00", "currency": "USD"
    }, headers=auth_headers).json()

    transactions = [
        {"account_id": account["id"], "amount": "100.00", "description": "Groceries",
         "category": "food", "transaction_date": "2025-01-05", "is_income": False},
        {"account_id": account["id"], "amount": "50.00", "description": "More food",
         "category": "food", "transaction_date": "2025-01-10", "is_income": False},
        {"account_id": account["id"], "amount": "200.00", "description": "Gas + metro",
         "category": "transport", "transaction_date": "2025-01-12", "is_income": False},
        {"account_id": account["id"], "amount": "3000.00", "description": "Paycheck",
         "category": "salary", "transaction_date": "2025-01-15", "is_income": True},
    ]
    for t in transactions:
        client.post("/transactions", json=t, headers=auth_headers)

    budgets = [
        {"category": "food", "monthly_limit": "200.00", "month": 1, "year": 2025},
        {"category": "transport", "monthly_limit": "150.00", "month": 1, "year": 2025},
    ]
    for b in budgets:
        client.post("/budgets/", json=b, headers=auth_headers)

    return account


def test_summary_empty_month(client, auth_headers):
    response = client.get("/analytics/summary?month=6&year=2025", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_spend"] == "0"
    assert data["total_income"] == "0"
    assert data["net"] == "0"
    assert data["by_category"] == []


def test_summary_totals(client, auth_headers, seeded):
    response = client.get("/analytics/summary?month=1&year=2025", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_spend"]) == 350.00
    assert float(data["total_income"]) == 3000.00
    assert float(data["net"]) == 2650.00


def test_summary_by_category(client, auth_headers, seeded):
    response = client.get("/analytics/summary?month=1&year=2025", headers=auth_headers)
    by_category = {c["category"]: c for c in response.json()["by_category"]}

    assert "food" in by_category
    assert float(by_category["food"]["total"]) == 150.00
    assert by_category["food"]["transaction_count"] == 2

    assert "transport" in by_category
    assert float(by_category["transport"]["total"]) == 200.00
    assert by_category["transport"]["transaction_count"] == 1


def test_summary_category_percentages(client, auth_headers, seeded):
    response = client.get("/analytics/summary?month=1&year=2025", headers=auth_headers)
    by_category = {c["category"]: c for c in response.json()["by_category"]}

    # food is 150/350 = ~42.86%, transport is 200/350 = ~57.14%
    assert abs(by_category["food"]["percentage"] - 42.86) < 0.1
    assert abs(by_category["transport"]["percentage"] - 57.14) < 0.1


def test_variance_no_budgets(client, auth_headers):
    response = client.get("/analytics/variance?month=3&year=2025", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_variance_under_budget(client, auth_headers, seeded):
    response = client.get("/analytics/variance?month=1&year=2025", headers=auth_headers)
    assert response.status_code == 200
    by_category = {v["category"]: v for v in response.json()}

    # food: budgeted 200, spent 150 → variance +50 (under)
    food = by_category["food"]
    assert float(food["budgeted"]) == 200.00
    assert float(food["actual"]) == 150.00
    assert float(food["variance"]) == 50.00
    assert food["percentage_used"] == pytest.approx(75.0, abs=0.1)


def test_variance_over_budget(client, auth_headers, seeded):
    response = client.get("/analytics/variance?month=1&year=2025", headers=auth_headers)
    by_category = {v["category"]: v for v in response.json()}

    # transport: budgeted 150, spent 200 → variance -50 (over)
    transport = by_category["transport"]
    assert float(transport["variance"]) == -50.00
    assert transport["percentage_used"] == pytest.approx(133.33, abs=0.1)


def test_variance_category_with_no_spending(client, auth_headers):
    # Budget exists but no transactions in that category
    client.post("/budgets/", json={
        "category": "entertainment", "monthly_limit": "100.00", "month": 2, "year": 2025
    }, headers=auth_headers)

    response = client.get("/analytics/variance?month=2&year=2025", headers=auth_headers)
    data = response.json()
    assert len(data) == 1
    assert float(data[0]["actual"]) == 0.00
    assert float(data[0]["variance"]) == 100.00
    assert data[0]["percentage_used"] == 0.0
