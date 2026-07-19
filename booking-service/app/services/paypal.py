import logging
from decimal import Decimal

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class PayPalClient:
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.base_url = (
            "https://api-m.sandbox.paypal.com"
            if settings.PAYPAL_SANDBOX
            else "https://api-m.paypal.com"
        )
        self._access_token = None

    async def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            self._access_token = data["access_token"]
            return self._access_token

    async def create_order(
        self,
        value: Decimal,
        currency: str = "USD",
        return_url: str = "",
        cancel_url: str = "",
    ) -> tuple[str, str]:
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": str(value),
                    },
                }
            ],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders",
                json=payload,
                headers=headers,
            )
            if not response.is_success:
                logger.error(
                    "PayPal create_order failed: %s %s",
                    response.status_code,
                    response.text,
                )
            response.raise_for_status()
            data = response.json()

            order_id = data["id"]
            approval_link = None
            for link in data.get("links", []):
                if link.get("rel") in ("approve", "payer-action"):
                    approval_link = link["href"]
                    break

            if not approval_link:
                approval_link = (
                    f"https://www.sandbox.paypal.com/checkoutnow?token={order_id}"
                )

            return order_id, approval_link

    async def capture_order(self, order_id: str) -> tuple[str | None, str]:
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            capture_id = None
            status = data.get("status", "UNKNOWN")

            for pu in data.get("purchase_units", []):
                captures = pu.get("payments", {}).get("captures", [])
                if captures:
                    capture_id = captures[0]["id"]
                    status = captures[0].get("status", status)
                    break

            return capture_id, status

    async def refund_capture(self, capture_id: str) -> tuple[str | None, str]:
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v2/payments/captures/{capture_id}/refund",
                json={},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("id"), data.get("status", "COMPLETED")


paypal_client = PayPalClient()
