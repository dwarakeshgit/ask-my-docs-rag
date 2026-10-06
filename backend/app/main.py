from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.ask import router as ask_router
from backend.app.api.upload import router as upload_router
from backend.app.api.documents import router as documents_router
from backend.app.services.rag_service import RAGService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create the shared RAG service when FastAPI starts.
    """

    print("Initializing Ask My Docs RAG service...")

    app.state.rag_service = RAGService()

    print("Ask My Docs RAG service initialized successfully.")

    yield

    print("Ask My Docs RAG service shutting down...")


app = FastAPI(
    lifespan=lifespan
)


# Allow the local frontend to communicate with the FastAPI backend.
# This is suitable for local development.
# When deploying to Render, replace "*" with the actual frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(documents_router)


@app.get("/")
def read_root():
    return {
        "message": "Ask My Docs API is running!"
    }