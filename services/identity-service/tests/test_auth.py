def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "plain_password": "password123", "name": "Test User", "role": "PASAJERO"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert data["role"] == "PASAJERO"
    assert "password_hash" not in data

def test_register_user_duplicate_email(client):
    client.post(
        "/api/auth/register",
        json={"email": "duplicate@example.com", "plain_password": "password123", "name": "Test User", "role": "CONDUCTOR"}
    )
    response = client.post(
        "/api/auth/register",
        json={"email": "duplicate@example.com", "plain_password": "newpassword", "name": "Another User", "role": "PASAJERO"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "plain_password": "password123", "name": "Login User", "role": "CONDUCTOR"}
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "plain_password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "plain_password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_get_me_success(client):
    client.post(
        "/api/auth/register",
        json={"email": "me@example.com", "plain_password": "password123", "name": "Me User", "role": "PASAJERO"}
    )
    login_response = client.post(
        "/api/auth/login",
        json={"email": "me@example.com", "plain_password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["role"] == "PASAJERO"

def test_get_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
