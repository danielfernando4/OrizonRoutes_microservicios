from fastapi import FastAPI
from app.routers import auth
from app.database import Base, engine

# Create tables for standard run (not used in tests because conftest overrides it)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Identity Service", description="Orizon Routes Identity API")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Identity Service is running"}
