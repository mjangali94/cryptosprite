from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.routes import router as api_router

app = FastAPI(title="Crypto Sprite")
app.include_router(api_router)


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