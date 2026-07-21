import uuid

from fastapi import status


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Chat Service"


class TestHistoryEndpoint:
    PASSENGER_ID = "test-passenger"

    def test_get_history_requires_auth(self, client, trip_id):
        response = client.get(f"/api/chat/history/{trip_id}/{self.PASSENGER_ID}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_history_rejects_invalid_token(self, client, trip_id):
        client.headers.update({"Authorization": "Bearer not-a-real-token"})
        response = client.get(f"/api/chat/history/{trip_id}/{self.PASSENGER_ID}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_history_success(self, auth_client, trip_id, mock_messages):
        response = auth_client.get(f"/api/chat/history/{trip_id}/{self.PASSENGER_ID}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["trip_id"] == trip_id
        assert data["total"] == len(mock_messages)
        assert len(data["items"]) == len(mock_messages)
        assert data["items"][0]["content"] == mock_messages[0]["content"]

    def test_get_history_pagination_params(self, auth_client, trip_id):
        response = auth_client.get(
            f"/api/chat/history/{trip_id}/{self.PASSENGER_ID}",
            params={"page": 2, "page_size": 10},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10

    def test_get_history_invalid_page_size_rejected(self, auth_client, trip_id):
        response = auth_client.get(
            f"/api/chat/history/{trip_id}/{self.PASSENGER_ID}",
            params={"page_size": 999},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListRoomsEndpoint:
    def test_list_rooms_requires_auth(self, client, trip_id):
        response = client.get("/api/chat/rooms")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_rooms_as_passenger_returns_rooms(self, auth_client, trip_id, mock_rooms):
        response = auth_client.get("/api/chat/rooms")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(mock_rooms)
        assert data[0]["trip_id"] == trip_id
        assert "passenger_id" in data[0]

    def test_list_rooms_filtered_by_trip_ids(self, auth_client, trip_id, mock_rooms):
        response = auth_client.get(
            "/api/chat/rooms",
            params={"trip_ids": f"{trip_id},other-trip-id"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(mock_rooms)

    def test_list_rooms_empty_trip_ids_uses_passenger_filter(self, auth_client):
        response = auth_client.get(
            "/api/chat/rooms",
            params={"trip_ids": ""},
        )
        assert response.status_code == status.HTTP_200_OK
