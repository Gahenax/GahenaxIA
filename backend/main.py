from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gahenax_app.api.gahenax_api import router, bridge_router
import uvicorn

app = FastAPI(title="Gahenax Core API (v1.1.1)")

# Allow the Gahenax Claude Bridge userscript (claude.ai origin) to POST telemetry
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(router)
app.include_router(bridge_router)

@app.get("/")
async def root():
    return {"status": "ONLINE", "system": "Gahenax Core v1.1.1", "paradigm": "P over NP Governed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
