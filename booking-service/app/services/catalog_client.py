import httpx

from app.config import settings


class CatalogServiceUnavailableError(Exception):
    pass


class CatalogClient:
    def __init__(self):
        self.base_url = settings.CATALOG_SERVICE_URL
        self.timeout = 5.0

    async def get_trip(self, trip_id: str) -> dict | None:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/catalog/trips/{trip_id}"
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise CatalogServiceUnavailableError(
                "El servicio de catálogo no está disponible. Intente más tarde."
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def validate_and_hold_seats(self, trip_id: str, seats: int) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/catalog/trips/{trip_id}/validate-seats",
                    json={"seats": seats},
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False

    async def confirm_seats_deducted(self, trip_id: str, seats: int) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/api/catalog/trips/{trip_id}/seats",
                    json={"seats_reserved": seats},
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False

    async def release_held_seats(self, trip_id: str, seats: int) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/api/catalog/trips/{trip_id}/seats",
                    json={"seats_released": seats},
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False

    async def cancel_trip_notify(self, trip_id: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/api/catalog/trips/{trip_id}/cancel"
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False


catalog_client = CatalogClient()
