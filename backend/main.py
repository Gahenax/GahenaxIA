from fastapi import FastAPI
from gahenax_app.api.gahenax_api import router as gahenax_router
from gahenax_app.api.ruflo_api import router as ruflo_router
import uvicorn

app = FastAPI(
    title="Gahenax Core API (v1.1.1)",
    description=(
        "Sovereign Inference Engine — LLL + UA physics + CMR ledger. "
        "Ruflo multi-agent orchestration layer integrated (Enlace 1-6)."
    ),
)

app.include_router(gahenax_router)
app.include_router(ruflo_router)

@app.get("/")
async def root():
    return {"status": "ONLINE", "system": "Gahenax Core v1.1.1", "paradigm": "P over NP Governed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
