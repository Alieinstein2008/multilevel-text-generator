from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.classifier_api import router as classifier_router

app = FastAPI(
    title="Multilevel Text Generator API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classifier_router)