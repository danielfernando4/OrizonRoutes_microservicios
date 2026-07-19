import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.catalog_client import CatalogClient, CatalogServiceUnavailableError


class TestCatalogClient:
    @pytest.fixture
    def client(self):
        return CatalogClient()

    @pytest.mark.asyncio
    async def test_get_trip_success(self, client: CatalogClient, mock_trip_data: dict):
        response = MagicMock()
        response.json = MagicMock(return_value=mock_trip_data)
        response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", AsyncMock(return_value=response)):
            result = await client.get_trip(str(uuid.uuid4()))
            assert result["id"] == mock_trip_data["id"]
            assert result["price_per_seat"] == 25.0

    @pytest.mark.asyncio
    async def test_get_trip_not_found(self, client):
        response = MagicMock()
        response.status_code = 404
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=response
        )

        with patch("httpx.AsyncClient.get", AsyncMock(side_effect=httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=response
        ))):
            result = await client.get_trip(str(uuid.uuid4()))
            assert result is None

    @pytest.mark.asyncio
    async def test_get_trip_service_unavailable(self, client):
        with (
            patch("httpx.AsyncClient.get", AsyncMock(side_effect=httpx.RequestError("Connection error"))),
            pytest.raises(CatalogServiceUnavailableError),
        ):
            await client.get_trip(str(uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_validate_and_hold_seats_success(self, client):
        response = MagicMock()
        response.status_code = 200

        with patch("httpx.AsyncClient.post", AsyncMock(return_value=response)):
            result = await client.validate_and_hold_seats(str(uuid.uuid4()), 2)
            assert result is True

    @pytest.mark.asyncio
    async def test_validate_and_hold_seats_failure(self, client):
        response = MagicMock()
        response.status_code = 409

        with patch("httpx.AsyncClient.post", AsyncMock(return_value=response)):
            result = await client.validate_and_hold_seats(str(uuid.uuid4()), 2)
            assert result is False

    @pytest.mark.asyncio
    async def test_confirm_seats_deducted(self, client):
        response = MagicMock()
        response.status_code = 200

        with patch("httpx.AsyncClient.patch", AsyncMock(return_value=response)):
            result = await client.confirm_seats_deducted(str(uuid.uuid4()), 2)
            assert result is True

    @pytest.mark.asyncio
    async def test_release_held_seats(self, client):
        response = MagicMock()
        response.status_code = 200

        with patch("httpx.AsyncClient.patch", AsyncMock(return_value=response)):
            result = await client.release_held_seats(str(uuid.uuid4()), 2)
            assert result is True

    @pytest.mark.asyncio
    async def test_cancel_trip_notify(self, client):
        response = MagicMock()
        response.status_code = 200

        with patch("httpx.AsyncClient.patch", AsyncMock(return_value=response)):
            result = await client.cancel_trip_notify(str(uuid.uuid4()))
            assert result is True


class TestPayPalClient:
    @pytest.fixture
    def client(self):
        from app.services.paypal import PayPalClient
        return PayPalClient()

    @pytest.mark.asyncio
    async def test_get_access_token_caches(self, client):
        token_response = MagicMock()
        token_response.json = MagicMock(return_value={"access_token": "TOKEN123"})
        token_response.raise_for_status = MagicMock()

        with (
            patch("httpx.AsyncClient.post", AsyncMock(return_value=token_response)),
        ):
            token1 = await client._get_access_token()
            token2 = await client._get_access_token()
            assert token1 == "TOKEN123"
            assert token2 == "TOKEN123"

    @pytest.mark.asyncio
    async def test_create_order(self, client):
        token_response = MagicMock()
        token_response.json = MagicMock(return_value={"access_token": "TOKEN"})
        token_response.raise_for_status = MagicMock()

        order_response = MagicMock()
        order_response.is_success = True
        order_response.json = MagicMock(
            return_value={
                "id": "ORDER123",
                "links": [{"rel": "approve", "href": "https://paypal.com/approve/123"}],
            }
        )
        order_response.raise_for_status = MagicMock()

        with (
            patch.object(client, "_get_access_token", AsyncMock(return_value="TOKEN")),
            patch("httpx.AsyncClient.post", AsyncMock(return_value=order_response)),
        ):
            order_id, link = await client.create_order(50.0)
            assert order_id == "ORDER123"
            assert "paypal.com" in link

    @pytest.mark.asyncio
    async def test_capture_order(self, client):
        with (
            patch.object(client, "_get_access_token", AsyncMock(return_value="TOKEN")),
        ):
            capture_response = MagicMock()
            capture_response.raise_for_status = MagicMock()
            capture_response.json = MagicMock(
                return_value={
                    "status": "COMPLETED",
                    "purchase_units": [
                        {
                            "payments": {
                                "captures": [{"id": "CAPTURE123", "status": "COMPLETED"}]
                            }
                        }
                    ],
                }
            )

            with patch("httpx.AsyncClient.post", AsyncMock(return_value=capture_response)):
                capture_id, status = await client.capture_order("ORDER123")
                assert capture_id == "CAPTURE123"
                assert status == "COMPLETED"

    @pytest.mark.asyncio
    async def test_refund_capture(self, client):
        with (
            patch.object(client, "_get_access_token", AsyncMock(return_value="TOKEN")),
        ):
            refund_response = MagicMock()
            refund_response.raise_for_status = MagicMock()
            refund_response.json = MagicMock(
                return_value={"id": "REFUND123", "status": "COMPLETED"}
            )

            with patch("httpx.AsyncClient.post", AsyncMock(return_value=refund_response)):
                refund_id, status = await client.refund_capture("CAPTURE123")
                assert refund_id == "REFUND123"
                assert status == "COMPLETED"
