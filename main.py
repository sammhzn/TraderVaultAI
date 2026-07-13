from fastapi import FastAPI

app = FastAPI(
    title="Trader Vault AI",
    description="AI-powered XAUUSD Trading Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "project": "Trader Vault AI",
        "version": "0.1.0",
        "status": "Running Successfully"
    }