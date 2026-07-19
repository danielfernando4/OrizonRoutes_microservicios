# Plan de Migración: Booking Service (Reservas y Pagos)

> **Propósito**: Documentar la migración del módulo de Reservas y Pagos desde el monolito Django (app `trips`) hacia un microservicio independiente en FastAPI, preservando la misma funcionalidad de negocio pero con acoplamiento débil y comunicación HTTP entre servicios.

---

## 1. Estado Actual en el Monolito

### 1.1 Ubicación del Código Fuente

| Archivo | Rol | Líneas |
|---------|-----|--------|
| `trips/models.py` | Modelos `Reservation` y `Trip` (juntos) | 139 |
| `trips/views.py` | Vistas de reserva: `CreateReservationView`, `CaptureOrderView`, `ReservationSuccessView`, `PassengerReservationListView`, `CancelTripView` | 364 (total) |
| `trips/urls.py` | Rutas de reserva bajo prefijo `/trips/` | 19 |
| `trips/paypal_client.py` | Cliente PayPal (`PayPalClient`) | 137 |
| `trips/forms.py` | Formularios de viaje (no aplica a Booking) | 137 |
| `trips/templates/trips/reservation_success.html` | Template de éxito de reserva | 72 |
| `trips/templates/trips/passenger_reservations.html` | Template de historial de reservas | 110 |
| `trips/templates/trips/trip_cancel.html` | Template de cancelación de viaje | 37 |
| `trips/templates/trips/trip_detail.html` | Template con widget de reserva (sidebar) | 328 |
| `config/settings.py` | Config PayPal (`PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`) | 131 |
| `.env.example` | Variables de entorno de PayPal | 7 |

### 1.2 Modelos Actuales (Acoplados)

**`Trip`** (permanece en Catalog Service):
```python
# trips/models.py (monolito)
class Trip(models.Model):
    driver = FK(User)           # → driver_id (UUID referencial)
    vehicle = FK(Vehicle)       # → vehicle_id (UUID referencial)
    origin, destination         # se queda en Catalog
    departure_datetime          # se queda en Catalog
    price_per_seat              # se queda en Catalog
    distance_km                 # se queda en Catalog
    duration_minutes            # se queda en Catalog
    status                      # active/cancelled/finished
    
    @property
    def available_seats(self):  # se queda en Catalog
        return self.vehicle.capacity - self.reserved_seats
    
    @property
    def reserved_seats(self):   # se queda en Catalog (suma de reservations)
        # AGREGAR: endpoint PATCH /api/catalog/trips/{id}/seats
        # para que Booking Service notifique cambios
```

**`Reservation`** (migra a Booking Service):
```python
# trips/models.py (monolito) → booking_service/app/models/reservation.py
class Reservation(models.Model):
    passenger = FK(User)           # → passenger_id (UUID, sin FK)
    trip = FK(Trip)                # → trip_id (UUID, sin FK)
    paypal_order_id                # → migra a Payment model
    paypal_capture_id              # → migra a Payment model
    payment_status                 # → pasa a Reservation.status
    quantity                       # → pasa a seats_reserved
    reservation_code               # se queda en Reservation
    created_at                     # se queda
```

### 1.3 Flujo de Reserva Actual (Modo Desarrollo)

En `trips/views.py:CreateReservationView.post()` (líneas 257-318):

```
1. POST /trips/{pk}/reserve/  (Form submit con quantity)
2. Verifica trip.status == 'active'
3. Validación: usuario != driver
4. transaction.atomic() + select_for_update()
5. Verifica available_seats >= quantity
6. Crea Reservation(payment_status='pending')
   ┌─ Código PayPal COMENTADO ──────────────────────────┐
   │ 7. paypal.create_order(total) → approval_link       │
   │ 8. Redirige a PayPal                                │
   │ 9. PayPal redirige a /trips/capture/?token=XXX      │
   │ 10. CaptureOrderView captura orden                  │
   └─────────────────────────────────────────────────────┘
   # MODO DESARROLLO (activo):
   7. reservation.payment_status = 'paid'
   8. Redirige a /reservation/{pk}/success/
```

**Problemas identificados:**
- PayPal está desactivado (código comentado)
- No hay separación entre datos de pago y reserva
- La lógica de disponibilidad de asientos depende de FK directa a Trip
- No hay comunicación con Catalog Service vía HTTP
- Autenticación por sesión Django (no JWT)

---

## 2. Arquitectura Objetivo: Booking Service (FastAPI)

### 2.1 Estructura del Proyecto

```
booking-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS, routers
│   ├── database.py              # SQLAlchemy async engine + session
│   ├── config.py                # Pydantic BaseSettings (variables de entorno)
│   ├── dependencies.py          # Dependencias: get_db, get_current_user
│   ├── models/
│   │   ├── __init__.py
│   │   ├── reservation.py       # Modelo Reservation
│   │   └── payment.py           # Modelo Payment
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── reservation.py       # Pydantic schemas de entrada/salida
│   │   └── payment.py           # Pydantic schemas de pago
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── reservations.py      # Endpoints de reservas
│   │   └── payments.py          # Endpoints de pagos
│   └── services/
│       ├── __init__.py
│       ├── paypal.py            # PayPalClient (adaptado de trips/paypal_client.py)
│       └── catalog_client.py    # Cliente HTTP para Catalog Service
├── requirements.txt
├── Dockerfile
└── .env.example
```

### 2.2 Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Framework | **FastAPI** | >=0.110.0 |
| ASGI Server | **Uvicorn** | >=0.27.0 |
| ORM | **SQLAlchemy** (async) | >=2.0.0 |
| DB Driver | **asyncpg** | >=0.29.0 |
| HTTP Client | **httpx** (async) | >=0.27.0 |
| Validation | **Pydantic v2** | >=2.5.0 |
| Auth | **PyJWT** | >=2.8.0 |
| Env | **python-dotenv** | >=1.0.0 |
| DB | **PostgreSQL** (db_booking) | 16 |

### 2.3 Variables de Entorno (`.env.example`)

```env
# FastAPI
APP_NAME=Booking Service
DEBUG=true

# Base de datos (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@db_booking:5432/db_booking

# JWT (debe coincidir con Identity Service)
JWT_SECRET_KEY=clave-secreta-compartida-con-identity-service
JWT_ALGORITHM=HS256

# PayPal Sandbox
PAYPAL_CLIENT_ID=sandbox-client-id
PAYPAL_CLIENT_SECRET=sandbox-client-secret
PAYPAL_SANDBOX=true
PAYPAL_RETURN_URL=http://localhost/api/booking/capture
PAYPAL_CANCEL_URL=http://localhost:5173

# Catalog Service (URL interna en Docker)
CATALOG_SERVICE_URL=http://catalog-service:8002

# Server
HOST=0.0.0.0
PORT=8003
```

### 2.4 Modelos de Base de Datos (`db_booking`)

**`reservations`**:
| Campo | Tipo | Notas |
|-------|------|-------|
| `id` | UUID | PK, default=uuid4 |
| `trip_id` | UUID | **Sin FK** — referencial a Catalog Service |
| `passenger_id` | UUID | **Sin FK** — referencial a Identity Service |
| `seats_reserved` | Integer | cantidad de asientos |
| `total_price` | Decimal(10,2) | price_per_seat × seats_reserved |
| `status` | Enum | `PENDING` \| `PAID` \| `CANCELLED` \| `REFUNDED` |
| `reservation_code` | String(16) | único, auto-generado (UUID8 hex upper) |
| `created_at` | DateTime | auto_now_add |
| `updated_at` | DateTime | auto_now |

**`payments`**:
| Campo | Tipo | Notas |
|-------|------|-------|
| `id` | UUID | PK, default=uuid4 |
| `reservation_id` | UUID | FK → reservations.id |
| `paypal_order_id` | String(255) | ID de orden PayPal |
| `paypal_capture_id` | String(255) | nullable, ID de captura |
| `amount` | Decimal(10,2) | monto pagado |
| `currency` | String(3) | default='USD' |
| `status` | Enum | `CREATED` \| `APPROVED` \| `COMPLETED` \| `FAILED` \| `REFUNDED` |
| `created_at` | DateTime | auto_now_add |

---

## 3. API Endpoints (Booking Service)

### 3.1 Mapeo de Funcionalidad Actual a Microservicio

| Funcionalidad Monolito (Django) | Endpoint Booking Service | Método |
|-------------------------------|--------------------------|--------|
| `POST /trips/{pk}/reserve/` (crear reserva) | `POST /api/booking/reserve` | Crear intención + PayPal Order |
| `GET /trips/capture/` (capturar PayPal) | `POST /api/booking/capture` | Capturar + confirmar |
| `GET /trips/reservation/{pk}/success/` | `GET /api/booking/reservations/{id}` | Obtener detalle reserva |
| `GET /trips/my-reservations/` | `GET /api/booking/my-reservations` | Listar historial |
| `POST /trips/{pk}/cancel/` (reembolso) | `POST /api/booking/cancel` | Cancelar + reembolsar |
| (nuevo) Webhook PayPal | `POST /api/booking/paypal-webhook` | Notificaciones asíncronas |

### 3.2 Endpoints Detallados

#### `POST /api/booking/reserve`
**Request:**
```json
{
  "trip_id": "uuid-del-viaje",
  "seats_requested": 2
}
```
**Headers:** `Authorization: Bearer <jwt>`
**Response (201):**
```json
{
  "reservation_id": "uuid",
  "status": "PENDING",
  "paypal_approval_link": "https://www.sandbox.paypal.com/..."
}
```
**Lógica:**
1. Extraer `passenger_id` y `role` del JWT validado
2. `httpx.get("catalog-service:8002/api/catalog/trips/{trip_id}")` para validar:
   - El viaje existe y está activo
   - `available_seats >= seats_requested`
   - Obtener `price_per_seat`
3. Calcular `total_price = price_per_seat * seats_requested`
4. `httpx.post("catalog-service:8002/api/catalog/trips/{trip_id}/validate-seats", json={"seats": seats_requested})` para **apartar temporalmente** los asientos (evitar race condition)
5. `paypal.create_order(total_price, ...)` → obtener `paypal_order_id` y `approval_link`
6. Crear `Reservation(status=PENDING)` en `db_booking`
7. Crear `Payment(status=CREATED, paypal_order_id=...)` en `db_booking`
8. Retornar `{ reservation_id, paypal_approval_link }`

#### `POST /api/booking/capture`
**Request:**
```json
{
  "paypal_order_id": "order-id-de-paypal",
  "reservation_id": "uuid-de-la-reserva"
}
```
**Headers:** `Authorization: Bearer <jwt>`
**Response (200):**
```json
{
  "reservation_id": "uuid",
  "status": "PAID",
  "reservation_code": "A1B2C3D4",
  "total_price": 50.00,
  "seats_reserved": 2,
  "trip_id": "uuid"
}
```
**Lógica:**
1. Obtener `Reservation` por `reservation_id` (validar que pertenece al `passenger_id` del JWT)
2. Obtener `Payment` asociado
3. `paypal.capture_order(paypal_order_id)` → obtener `capture_id`
4. Actualizar `Payment(status=COMPLETED, paypal_capture_id=capture_id)`
5. Actualizar `Reservation(status=PAID, reservation_code=generado)`
6. **Notificar a Catalog Service:**
   `httpx.patch("catalog-service:8002/api/catalog/trips/{trip_id}/seats", json={"seats_reserved": seats_reserved})`
   → Catalog Service decrementa `available_seats`
7. Retornar detalle de reserva

#### `GET /api/booking/my-reservations`
**Headers:** `Authorization: Bearer <jwt>`
**Query Params:** `?page=1&page_size=10`
**Response (200):**
```json
{
  "items": [
    {
      "reservation_id": "uuid",
      "trip_id": "uuid",
      "origin": "Quito",
      "destination": "Guayaquil",
      "departure_datetime": "2026-08-15T08:00:00Z",
      "seats_reserved": 2,
      "total_price": 50.00,
      "status": "PAID",
      "reservation_code": "A1B2C3D4",
      "driver_name": "Juan Pérez",
      "driver_id": "uuid",
      "created_at": "2026-07-18T20:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 10
}
```
**Lógica:**
1. Extraer `passenger_id` del JWT
2. Query `Reservation` por `passenger_id`
3. **Por cada reserva**, hacer `httpx.get("catalog-service:8002/api/catalog/trips/{trip_id}")` para obtener:
   - `origin`, `destination`, `departure_datetime`
   - `driver_id`
4. **Opcional**: hacer `httpx.get("identity-service:8001/api/auth/users/{driver_id}")` para obtener nombre del conductor
5. Retornar colección enriquecida

#### `GET /api/booking/reservations/{reservation_id}`
**Headers:** `Authorization: Bearer <jwt>`
**Response (200):** Detalle completo de la reserva (igual schema que item de my-reservations pero individual)

#### `POST /api/booking/cancel`
**Request:**
```json
{
  "trip_id": "uuid-del-viaje"
}
```
**Headers:** `Authorization: Bearer <jwt>`
**Response (200):**
```json
{
  "message": "Viaje cancelado. 3 reembolso(s) procesado(s).",
  "refunded_count": 3
}
```
**Lógica:**
1. Extraer `user_id` y `role` del JWT (solo conductores pueden cancelar)
2. Obtener todas las `Reservation` con `trip_id` y `status=PAID`
3. Para cada una:
   - Obtener `Payment` asociado con `paypal_capture_id`
   - `paypal.refund_capture(capture_id)`
   - Actualizar `Payment(status=REFUNDED)`
   - Actualizar `Reservation(status=REFUNDED)`
4. **Notificar a Catalog Service:**
   `httpx.patch("catalog-service:8002/api/catalog/trips/{trip_id}/cancel")`
   → Catalog Service marca trip como `cancelled` y libera asientos

#### `POST /api/booking/paypal-webhook`
**Request:** Payload estándar de PayPal Webhook
**Lógica:**
1. Verificar firma del webhook (validar con PayPal)
2. Manejar eventos:
   - `CHECKOUT.ORDER.APPROVED`: Actualizar `Payment(status=APPROVED)`
   - `PAYMENT.CAPTURE.COMPLETED`: Actualizar `Payment(status=COMPLETED)`, `Reservation(status=PAID)`
   - `PAYMENT.CAPTURE.REFUNDED`: Actualizar `Payment(status=REFUNDED)`, `Reservation(status=REFUNDED)`

---

## 4. Cliente HTTP para Catalog Service

```python
# app/services/catalog_client.py
"""
Cliente asíncrono para comunicación con Catalog Service.
Reemplaza la FK directa a Trip del monolito.
"""

import httpx
from app.config import settings

class CatalogClient:
    def __init__(self):
        self.base_url = settings.CATALOG_SERVICE_URL
        self.timeout = 5.0  # 5 segundos máximo

    async def get_trip(self, trip_id: str) -> dict | None:
        """Obtiene detalle del viaje para validar disponibilidad y precio."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/catalog/trips/{trip_id}"
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            # Catalog Service caído — no se puede procesar reserva
            raise CatalogServiceUnavailableError(
                "El servicio de catálogo no está disponible. Intente más tarde."
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None  # Viaje no encontrado
            raise

    async def validate_and_hold_seats(self, trip_id: str, seats: int) -> bool:
        """Valida y aparta asientos temporalmente (evita race conditions)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/catalog/trips/{trip_id}/validate-seats",
                    json={"seats": seats}
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False

    async def confirm_seats_deducted(self, trip_id: str, seats: int) -> bool:
        """Confirma la reserva descontando asientos definitivamente."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/api/catalog/trips/{trip_id}/seats",
                    json={"seats_reserved": seats}
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False

    async def release_held_seats(self, trip_id: str, seats: int) -> bool:
        """Libera asientos apartados si la reserva falla (compensación)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/api/catalog/trips/{trip_id}/seats",
                    json={"seats_released": seats}
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False

    async def cancel_trip_notify(self, trip_id: str) -> bool:
        """Notifica al Catalog que un viaje fue cancelado (con reembolsos)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/api/catalog/trips/{trip_id}/cancel"
                )
                return response.status_code == 200
        except httpx.RequestError:
            return False


catalog_client = CatalogClient()
```

---

## 5. Cliente PayPal (Migrado de `trips/paypal_client.py`)

```python
# app/services/paypal.py
"""
Cliente PayPal adaptado del monolito (trips/paypal_client.py).
Cambios clave:
  - httpx asíncrono en lugar de requests síncrono
  - Configuración vía Pydantic Settings
  - Manejo de errores con try/except y timeout
"""

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
        """Obtiene token de acceso OAuth2 de PayPal (con caché en memoria)."""
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
        self, value: Decimal, currency: str = "USD",
        return_url: str = "", cancel_url: str = ""
    ) -> tuple[str, str]:
        """Crea una orden PayPal y retorna (order_id, approval_link)."""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": currency,
                    "value": str(value),
                },
            }],
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
                    f"PayPal create_order failed: {response.status_code} {response.text}"
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
        """Captura una orden PayPal aprobada. Retorna (capture_id, status)."""
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
        """Reembolsa una captura. Retorna (refund_id, status)."""
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
```

---

## 6. Flujo Completo de Reserva (Post-Migración)

```
FRONTEND (React)                    BOOKING SERVICE              CATALOG SERVICE         PAYPAL API
       │                                  │                          │                      │
       │ 1. POST /api/booking/reserve     │                          │                      │
       │    { trip_id, seats_requested }  │                          │                      │
       │ ───────────────────────────────► │                          │                      │
       │                                  │ 2. Valida JWT            │                      │
       │                                  │    (passenger_id, role)  │                      │
       │                                  │                          │                      │
       │                                  │ 3. GET /api/catalog/     │                      │
       │                                  │    trips/{trip_id}       │                      │
       │                                  │ ───────────────────────► │                      │
       │                                  │ ◄─────────────────────── │                      │
       │                                  │    { price_per_seat,     │                      │
       │                                  │      available_seats }   │                      │
       │                                  │                          │                      │
       │                                  │ 4. POST /api/catalog/    │                      │
       │                                  │    trips/{id}/           │                      │
       │                                  │    validate-seats        │                      │
       │                                  │ ───────────────────────► │                      │
       │                                  │ ◄─────────────────────── │                      │
       │                                  │    200 OK (seats held)   │                      │
       │                                  │                          │                      │
       │                                  │ 5. POST /v2/checkout/    │                      │
       │                                  │    orders                │                      │
       │                                  │ ───────────────────────────────────────────────► │
       │                                  │ ◄─────────────────────────────────────────────── │
       │                                  │    { order_id,           │                      │
       │                                  │      approval_link }     │                      │
       │                                  │                          │                      │
       │                                  │ 6. Crea Reservation      │                      │
       │                                  │    (status=PENDING)      │                      │
       │                                  │ 7. Crea Payment          │                      │
       │                                  │    (status=CREATED)      │                      │
       │                                  │                          │                      │
       │ ◄─────────────────────────────── │                          │                      │
       │ { reservation_id,                │                          │                      │
       │   paypal_approval_link }         │                          │                      │
       │                                  │                          │                      │
       │ 8. Redirige a PayPal             │                          │                      │
       │ ───────────────────────────────────────────────────────────────────────────────► │
       │                                  │                          │                      │
       │ 9. Usuario aprueba pago          │                          │                      │
       │ ◄─────────────────────────────────────────────────────────────────────────────── │
       │                                  │                          │                      │
       │ 10. POST /api/booking/capture    │                          │                      │
       │     { paypal_order_id,           │                          │                      │
       │       reservation_id }           │                          │                      │
       │ ───────────────────────────────► │                          │                      │
       │                                  │ 11. POST /v2/checkout/   │                      │
       │                                  │     orders/{id}/capture  │                      │
       │                                  │ ───────────────────────────────────────────────► │
       │                                  │ ◄─────────────────────────────────────────────── │
       │                                  │     { capture_id, status}│                      │
       │                                  │                          │                      │
       │                                  │ 12. Payment → COMPLETED  │                      │
       │                                  │     Reservation → PAID   │                      │
       │                                  │     reservation_code gen │                      │
       │                                  │                          │                      │
       │                                  │ 13. PATCH /api/catalog/  │                      │
       │                                  │     trips/{id}/seats     │                      │
       │                                  │     { seats_reserved }   │                      │
       │                                  │ ───────────────────────► │                      │
       │                                  │                          │ (decrementa          │
       │                                  │                          │  available_seats)    │
       │                                  │ ◄─────────────────────── │                      │
       │                                  │    200 OK                │                      │
       │                                  │                          │                      │
       │ ◄─────────────────────────────── │                          │                      │
       │ { reservation_code, status,      │                          │                      │
       │   total_price, seats_reserved }  │                          │                      │
```

---

## 7. Esquema de Compensación (Patrón Saga)

Para manejar fallos en comunicación entre servicios, se implementa un patrón Saga coreografiado:

```
Reserva Exitosa:
  Reserve → PayPal Order OK → Capture → PayPal Capture OK → 
  Catalog deduct seats ✅

Fallo en Captura PayPal:
  Reserve → PayPal Order OK → Capture → PayPal Capture FALLÓ ❌
  → Liberar asientos en Catalog (release_held_seats)
  → Marcar Reservation(status=CANCELLED)
  → Marcar Payment(status=FAILED)

Fallo en Catalog (post-captura):
  Reserve → PayPal Order OK → Capture → PayPal Capture OK ✅
  → Catalog deduct seats FALLÓ ❌
  → Hacer refund en PayPal (compensación)
  → Marcar Reservation(status=REFUNDED)
  → Marcar Payment(status=REFUNDED)
```

**Implementación en el Router de Reservas:**

```python
# app/routers/reservations.py
@router.post("/reserve", status_code=201)
async def create_reservation(
    payload: ReserveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # 1. Validar viaje en Catalog Service
    trip = await catalog_client.get_trip(payload.trip_id)
    if not trip:
        raise HTTPException(404, "Viaje no encontrado")
    if trip["status"] != "active":
        raise HTTPException(400, "El viaje no está activo")
    if trip["available_seats"] < payload.seats_requested:
        raise HTTPException(400, f"Solo hay {trip['available_seats']} asientos disponibles")

    # 2. Calcular total
    total_price = Decimal(str(trip["price_per_seat"])) * payload.seats_requested

    # 3. Apartar asientos en Catalog (hold temporal)
    held = await catalog_client.validate_and_hold_seats(
        payload.trip_id, payload.seats_requested
    )
    if not held:
        raise HTTPException(503, "Error al validar disponibilidad")

    # 4. Crear orden PayPal
    try:
        order_id, approval_link = await paypal_client.create_order(
            value=total_price,
            return_url=settings.PAYPAL_RETURN_URL,
            cancel_url=settings.PAYPAL_CANCEL_URL,
        )
    except Exception as e:
        # Compensación: liberar asientos
        await catalog_client.release_held_seats(
            payload.trip_id, payload.seats_requested
        )
        raise HTTPException(502, f"Error al conectar con PayPal: {e}")

    # 5. Persistir en DB
    reservation = Reservation(
        trip_id=payload.trip_id,
        passenger_id=current_user["id"],
        seats_reserved=payload.seats_requested,
        total_price=total_price,
        status="PENDING",
    )
    db.add(reservation)
    await db.flush()

    payment = Payment(
        reservation_id=reservation.id,
        paypal_order_id=order_id,
        amount=total_price,
        status="CREATED",
    )
    db.add(payment)
    await db.commit()

    return {
        "reservation_id": str(reservation.id),
        "status": "PENDING",
        "paypal_approval_link": approval_link,
    }
```

---

## 8. Autenticación y Seguridad

### 8.1 Validación JWT (Middleware/Dependencia)

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Valida JWT y extrae payload del usuario autenticado."""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return {
            "id": payload.get("user_id"),
            "role": payload.get("role"),
            "email": payload.get("email"),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
```

### 8.2 Roles y Permisos (Manteniendo la lógica del monolito)

| Endpoint | Rol Requerido | Equivalente Monolito |
|----------|--------------|---------------------|
| `POST /api/booking/reserve` | `pasajero` | `PasajeroRequiredMixin` |
| `POST /api/booking/confirm-payment` | `pasajero` | `LoginRequiredMixin` |
| `GET /api/booking/my-reservations` | `pasajero` | `PasajeroRequiredMixin` |
| `POST /api/booking/cancel` | `conductor` | `ConductorRequiredMixin` |
| `POST /api/booking/paypal-webhook` | Público (validar firma) | No existía |

```python
# app/dependencies.py
from fastapi import HTTPException, status


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return current_user


pasajero_required = RoleChecker(["pasajero"])
conductor_required = RoleChecker(["conductor"])
authenticated = RoleChecker(["pasajero", "conductor"])
```

---

## 9. Catalog Service — Endpoints Requeridos para Booking

El Catalog Service debe exponer los siguientes endpoints para que Booking Service pueda comunicarse:

### Existentes (ya en especificación del Catalog):
- `GET /api/catalog/trips/{trip_id}` → Detalle del viaje (incluye `price_per_seat`, `available_seats`, `status`, `driver_id`, `origin`, `destination`, `departure_datetime`)

### Nuevos (necesarios para Booking):
- `POST /api/catalog/trips/{trip_id}/validate-seats` → Aparta asientos temporalmente (hold), retorna 200 si hay suficientes, 409 si no
- `PATCH /api/catalog/trips/{trip_id}/seats` → Descuenta asientos definitivamente (`{"seats_reserved": N}`) o libera asientos (`{"seats_released": N}`)
- `PATCH /api/catalog/trips/{trip_id}/cancel` → Marca viaje como `cancelled`

---

## 10. Configuración Docker

### `Dockerfile`
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

### `requirements.txt`
```
fastapi>=0.110.0,<1.0.0
uvicorn[standard]>=0.27.0,<1.0.0
sqlalchemy[asyncio]>=2.0.0,<3.0.0
asyncpg>=0.29.0,<1.0.0
pydantic>=2.5.0,<3.0.0
pydantic-settings>=2.1.0,<3.0.0
httpx>=0.27.0,<1.0.0
pyjwt>=2.8.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0
psycopg2-binary>=2.9.0,<3.0.0
alembic>=1.13.0,<2.0.0
```

---

## 11. Línea Base para Migración (Checklist)

### Fase 1: Preparación (Contexto)
- [ ] Crear nuevo repositorio `booking-service`
- [ ] Copiar este documento al repo como `docs/migration-plan.md`
- [ ] Configurar variables de entorno en `.env`

### Fase 2: Infraestructura
- [ ] Crear estructura de carpetas (`app/`, `app/models/`, `app/schemas/`, `app/routers/`, `app/services/`)
- [ ] Implementar `app/config.py` (Pydantic Settings)
- [ ] Implementar `app/database.py` (SQLAlchemy async)
- [ ] Implementar `app/main.py` (FastAPI app + CORS + routers)
- [ ] Migrar `PayPalClient` a `app/services/paypal.py` (versión async con httpx)
- [ ] Implementar `app/services/catalog_client.py`

### Fase 3: Modelos y Base de Datos
- [ ] Definir modelo `Reservation` en `app/models/reservation.py`
- [ ] Definir modelo `Payment` en `app/models/payment.py`
- [ ] Definir schemas Pydantic en `app/schemas/reservation.py`
- [ ] Definir schemas Pydantic en `app/schemas/payment.py`
- [ ] Configurar Alembic para migraciones
- [ ] Crear migración inicial
- [ ] Probar conexión a PostgreSQL

### Fase 4: Endpoints
- [ ] Implementar `POST /api/booking/reserve`
- [ ] Implementar `POST /api/booking/capture`
- [ ] Implementar `GET /api/booking/my-reservations`
- [ ] Implementar `GET /api/booking/reservations/{id}`
- [ ] Implementar `POST /api/booking/cancel`
- [ ] Implementar `POST /api/booking/paypal-webhook` (opcional)

### Fase 5: Seguridad
- [ ] Implementar dependencia `get_current_user` (JWT validation)
- [ ] Implementar `RoleChecker` para roles `pasajero`/`conductor`
- [ ] Probar autenticación con tokens del Identity Service

### Fase 6: Pruebas
- [ ] Test unitarios con `pytest` + `TestClient` (FastAPI)
- [ ] Mock de `CatalogClient` y `PayPalClient` en tests
- [ ] Probar flujo completo: reserve → capture → my-reservations
- [ ] Probar escenarios de error: asientos insuficientes, PayPal fallido, Catalog caído

### Fase 7: Dockerización
- [ ] Crear `Dockerfile`
- [ ] Agregar al `docker-compose.yml` maestro del proyecto
- [ ] Configurar Nginx en API Gateway para ruta `/api/booking/*`

---

## 12. Convenciones y Buenas Prácticas

1. **Manejo de errores estandarizado**: Todos los errores retornan `HTTPException` con el mismo formato que FastAPI. El frontend captura con Axios interceptor y muestra Toast.

2. **Timeouts en comunicación HTTP**: CatalogClient usa timeout de 5 segundos. PayPalClient usa timeout de 30 segundos.

3. **IDs como UUIDs**: Todos los IDs expuestos son UUIDs. Las FK internas también son UUIDs pero sin constraint de base de datos (referenciales).

4. **No exponer IDs internos**: El `reservation_code` (código alfanumérico legible) es lo que se muestra al usuario, no el UUID.

5. **Logging estructurado**: Usar `logging` con niveles INFO para flujo normal, ERROR para fallos, DEBUG para desarrollo. Cada log debe incluir `reservation_id` y `trip_id` para trazabilidad.

6. **Sin sesiones ni cookies**: Booking Service es completamente stateless. Toda la autenticación es vía JWT en header `Authorization: Bearer <token>`.

7. **Compatibilidad con el Frontend existente**: Los nombres de campos en las responses (reservation_code, trip_id, etc.) deben coincidir con lo que espera el frontend React para minimizar cambios.

---

## 13. Diferencias Clave con el Monolito

| Aspecto | Monolito (Django) | Microservicio (FastAPI) |
|---------|-------------------|------------------------|
| Framework | Django 6.0 + CBV | FastAPI + async |
| Base de datos | SQLite | PostgreSQL (db_booking) |
| ORM | Django ORM | SQLAlchemy 2.0 async |
| HTTP Client | requests (síncrono) | httpx (asíncrono) |
| Auth | Session + CSRF | JWT (Bearer token) |
| PayPal | Código comentado | Activo con PayPal Sandbox |
| Disponibilidad | FK directa a Trip | HTTP call a Catalog Service |
| Transacciones | transaction.atomic() | Saga Pattern (compensación) |
| Server | Daphne/runserver | Uvicorn |
| Tests | unittest | pytest + TestClient |
| Validación | Django Forms | Pydantic v2 |
| Config | settings.py + .env | Pydantic BaseSettings |
