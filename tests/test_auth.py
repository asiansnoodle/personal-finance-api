
def test_register_success(client):
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "password" not in data


def test_register_duplicate_email(client, registered_user):
    response = client.post("/auth/register", json={
        "email": registered_user["email"],
        "password": "anotherpassword",
        "full_name": "Duplicate"
    })
    assert response.status_code == 400


def test_login_success(client, registered_user):
    response = client.post("/auth/login", data={
        "username": registered_user["email"],
        "password": registered_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", data={
        "username": registered_user["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={
        "username": "ghost@example.com",
        "password": "password123"
    })
    assert response.status_code == 401


    assert response.status_code == 401


def test_protected_route_no_token(client):
    response = client.get("/accounts")
    assert response.status_code == 401


def test_protected_route_invalid_token(client):
    response = client.get("/accounts", headers={"Authorization": "Bearer faketoken"})
    assert response.status_code == 401