import os
import uvicorn
from fastapi import FastAPI
from backend.app import router  # ajuste conforme sua estrutura real

app = FastAPI()

# Rota raiz para evitar erro 405 no Render
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "API funcionando!",
        "autor": "Leandro Gomes"
    }

# Inclui suas rotas reais
app.include_router(router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
