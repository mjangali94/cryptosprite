from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.routes.price import router as price_router
from api.routes.history import router as history_router
from api.routes.signals import router as signals_router

app = FastAPI(title="Crypto Sprite")

app.include_router(price_router)
app.include_router(history_router)
app.include_router(signals_router)


# ===== CORS SETTINGS =====
origins = [
    "http://localhost:3000",  # frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)