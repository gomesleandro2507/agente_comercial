from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["customers_count"] >= 10

def test_market_regions_endpoint():
    res = client.get("/api/market/regions")
    assert res.status_code == 200
    regions = res.json()
    assert "Sudeste" in regions
    assert "Centro-Oeste" in regions

def test_product_analyze_endpoint():
    payload = {
        "name": "Software de Gestão Hospitalar",
        "description": "Prontuário eletrônico e triagem com IA para redes de saúde.",
        "target_sectors": ["Saúde"],
        "ticket_price": 20000.0,
        "target_regions": ["Nordeste", "Sudeste"]
    }
    res = client.post("/api/products/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["product_name"] == "Software de Gestão Hospitalar"
    assert len(data["top_recommendations"]) > 0
    top1 = data["top_recommendations"][0]
    assert top1["customer"]["sector"] == "Saúde"
    assert top1["match_score"] > 70

def test_agent_chat_endpoint():
    payload = {
        "query": "Quem é o cliente mais promissor para este produto e por quê?",
        "product": {
            "name": "Software Agrícola",
            "description": "Automação de grãos",
            "target_sectors": ["Agronegócio"],
            "ticket_price": 30000.0
        }
    }
    res = client.post("/api/agent/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    # Verifica tom educado
    assert any(w in data["reply"].lower() for w in ["satisfação", "olá", "prezado", "honra"])

def test_frontend_index_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "Agente Comercial" in res.text
