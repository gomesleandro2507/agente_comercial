import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from .schemas.product import ProductDefinition
from .schemas.customer import CustomerProfile
from .schemas.recommendation import RecommendationResponse
from .data.regional_market import RegionalMarketService
from .data.customers_repo import CustomersRepository
from .agent.commercial_agent import CommercialAgent

app = FastAPI(
    title="Agente Comercial de Prospecção & Inteligência de Mercado",
    description="Identificação dos melhores clientes com base nos requisitos do produto e oferta/demanda no Brasil.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização dos serviços
market_service = RegionalMarketService()
customers_repo = CustomersRepository()
commercial_agent = CommercialAgent(market_service, customers_repo)

class ChatRequest(BaseModel):
    query: str
    product: Optional[ProductDefinition] = None

class ChatResponse(BaseModel):
    reply: str
    product_name: Optional[str] = None

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "Agente Comercial Inteligente",
        "customers_count": len(customers_repo.get_all())
    }

@app.get("/api/market/regions")
def get_market_regions():
    return market_service.get_all_regions_summary()

@app.get("/api/customers", response_model=List[CustomerProfile])
def get_customers():
    return customers_repo.get_all()

@app.post("/api/products/analyze", response_model=RecommendationResponse)
def analyze_product(product: ProductDefinition):
    try:
        return commercial_agent.analyze_product_and_recommend(product, top_n=6)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/chat", response_model=ChatResponse)
async def chat_with_agent(req: ChatRequest):
    try:
        reply = await commercial_agent.answer_consultative_query(
            user_query=req.query,
            product=req.product
        )
        return ChatResponse(
            reply=reply,
            product_name=req.product.name if req.product else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers/upload")
async def upload_customers_csv(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        text = contents.decode("latin-1")
    
    count = customers_repo.import_from_csv(text)
    return {
        "message": f"Sucesso! {count} clientes foram importados com sucesso.",
        "total_customers": len(customers_repo.get_all())
    }

# Servir arquivos estáticos do Frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
