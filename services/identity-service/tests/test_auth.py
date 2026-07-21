STRONG_PASSWORD = "Valid123!"


def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "plain_password": STRONG_PASSWORD,
            "name": "Test User",
            "role": "pasajero",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert data["role"] == "pasajero"
    assert "password_hash" not in data


def test_register_user_duplicate_email(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "plain_password": STRONG_PASSWORD,
            "name": "Test User",
            "role": "conductor",
        },
    )
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "plain_password": "OtherPass1!",
            "name": "Another User",
            "role": "pasajero",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_user_weak_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "weak@example.com",
            "plain_password": "short",
            "name": "Weak User",
            "role": "pasajero",
        },
    )
    assert response.status_code == 422


def test_register_user_password_missing_uppercase(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "noupper@example.com",
            "plain_password": "alllowercase1!",
            "name": "No Upper",
            "role": "pasajero",
        },
    )
    assert response.status_code == 422


def test_register_user_password_missing_digit(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "nodigit@example.com",
            "plain_password": "NoDigit!a",
            "name": "No Digit",
            "role": "pasajero",
        },
    )
    assert response.status_code == 422


def test_register_user_password_missing_special(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "nospecial@example.com",
            "plain_password": "NoSpecial1",
            "name": "No Special",
            "role": "pasajero",
        },
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "plain_password": STRONG_PASSWORD,
            "name": "Login User",
            "role": "conductor",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "plain_password": STRONG_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "plain_password": STRONG_PASSWORD},
    )
    assert response.status_code == 401


def test_get_me_success(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "me@example.com",
            "plain_password": STRONG_PASSWORD,
            "name": "Me User",
            "role": "pasajero",
        },
    )
    login_response = client.post(
        "/api/auth/login",
        json={"email": "me@example.com", "plain_password": STRONG_PASSWORD},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["role"] == "pasajero"


def test_get_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
