# 🚗 Orizon Routes

Orizon Routes es una plataforma web moderna de viajes compartidos (carpooling) diseñada para conectar conductores y pasajeros de forma segura y eficiente. 

Este proyecto ha sido desarrollado con un enfoque estricto en la **Arquitectura de Microservicios**[cite: 2], garantizando alta escalabilidad, resiliencia y un despliegue ágil mediante prácticas de **DevSecOps** y monitoreo avanzado[cite: 6].

## 🏗️ Arquitectura del Sistema

El ecosistema de Orizon Routes está compuesto por un Frontend moderno (SPA) y cuatro microservicios independientes en el Backend. La arquitectura se fundamenta en los siguientes patrones de diseño:
* **API Gateway:** Nginx actúa como proxy inverso centralizando y enrutando todo el tráfico externo hacia los microservicios correspondientes (`/api/auth`, `/api/catalog`, `/api/booking`, `/ws/chat`)[cite: 2].
* **Database per Microservice:** Cada microservicio es dueño exclusivo de sus datos, garantizando un desacoplamiento estricto[cite: 2]. La comunicación inter-servicios se realiza únicamente mediante peticiones HTTP asíncronas[cite: 2].

## 🧩 Módulos (Microservicios)

1. **🔐 Identity Service:** Gestiona la autenticación, autorización (JWT), roles y el ciclo de vida de los usuarios[cite: 2]. Base de datos: PostgreSQL (`db_identity`)[cite: 2].
2. **🚙 Catalog Service:** Administra el inventario de vehículos y la publicación/búsqueda de viajes, integrando la API de OSRM para cálculos de distancia[cite: 2]. Base de datos: PostgreSQL (`db_catalog`)[cite: 2].
3. **💳 Booking Service:** Maneja las transacciones financieras y la confirmación de asientos, integrando la API de PayPal (Sandbox)[cite: 2]. Base de datos: PostgreSQL (`db_booking`)[cite: 2].
4. **💬 Chat Service:** Provee comunicación bidireccional en tiempo real entre pasajeros y conductores usando WebSockets[cite: 2]. Base de datos: MongoDB (`db_chat`)[cite: 2].

## 🚀 Tecnologías Utilizadas

**Frontend (Interfaz de Usuario):**
* React, TypeScript, Vite[cite: 4]
* Tailwind CSS, Axios, React Router DOM[cite: 4, 6]

**Backend (Lógica y Servicios):**
* Python 3, FastAPI, Uvicorn[cite: 2, 5]
* SQLAlchemy (ORM relacional), Motor/PyMongo/Beanie (Driver NoSQL)[cite: 2]
* PyJWT, Passlib (Seguridad y Hashing)[cite: 2]
* Pytest (Pruebas unitarias)[cite: 2]

**Infraestructura, DevOps y Observabilidad:**
* Docker & Docker Compose (Contenerización y Orquestación)[cite: 2]
* Nginx (API Gateway)[cite: 2]
* GitHub Actions (CI/CD Pipeline)[cite: 6]
* Prometheus & Grafana (Recolección de métricas y Dashboards de salud)[cite: 6]
* Loki & Promtail (Agregación y visualización centralizada de logs)[cite: 6]

## 🛠️ Instalación y Despliegue Local

Para ejecutar este proyecto en tu entorno local, asegúrate de tener instalado el motor de **Docker** y **Docker Compose**.

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/OrizonRoutes_microservicios.git](https://github.com/tu-usuario/OrizonRoutes_microservicios.git)
   cd OrizonRoutes_microservicios
