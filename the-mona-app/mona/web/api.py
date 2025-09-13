from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(title="The Mona API")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
