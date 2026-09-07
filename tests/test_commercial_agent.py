import pytest
from backend.app.data.regional_market import RegionalMarketService
from backend.app.data.customers_repo import CustomersRepository
from backend.app.agent.scoring import CommercialScoringEngine
from backend.app.agent.commercial_agent import CommercialAgent
from backend.app.schemas.product import ProductDefinition

def test_regional_market_service():
    market = RegionalMarketService()
    regions = market.get_all_regions_summary()
    assert "Centro-Oeste" in regions
    assert "Sudeste" in regions
    assert "Nordeste" in regions

    # Teste de pontuação de oportunidade
    co_agro = market.calculate_regional_opportunity_score("Centro-Oeste", "MT", "Agronegócio")
    assert co_agro["regional_score"] > 60
    assert co_agro["demand_index"] > 80

def test_customers_repo_loading():
    repo = CustomersRepository()
    customers = repo.get_all()
    assert len(customers) >= 10
    cli_1 = repo.get_by_id("CLI-001")
    assert cli_1 is not None
    assert cli_1.state == "MT"
    assert cli_1.sector == "Agronegócio"

def test_scoring_agro_product():
    market = RegionalMarketService()
    repo = CustomersRepository()
    engine = CommercialScoringEngine(market)

    agro_product = ProductDefinition(
        name="Plataforma de Telemetria e Monitoramento de Silos",
        description="Monitoramento inteligente de grãos, umidade e prevenção de perdas com IoT para grandes produtores rurais.",
        target_sectors=["Agronegócio"],
        target_company_sizes=["Grande Porte", "Corporativo / Muito Grande"],
        ticket_price=25000.0,
        target_regions=["Centro-Oeste", "Sul"]
    )

    cust_mt = repo.get_by_id("CLI-001") # AgroCerrado no MT
    cust_sp_ind = repo.get_by_id("CLI-003") # Metalúrgica em SP

    rec_mt = engine.score_customer(agro_product, cust_mt)
    rec_sp = engine.score_customer(agro_product, cust_sp_ind)

    # O cliente do agro no MT deve ter pontuação consideravelmente superior à metalúrgica paulista
    assert rec_mt.match_score > rec_sp.match_score
    assert rec_mt.match_score >= 80.0
    assert rec_mt.score_breakdown.product_fit_score > rec_sp.score_breakdown.product_fit_score

def test_commercial_agent_polite_consultative_response():
    import asyncio
    market = RegionalMarketService()
    repo = CustomersRepository()
    agent = CommercialAgent(market, repo)

    product = ProductDefinition(
        name="IA de Triagem Hospitalar",
        description="Triagem rápida e auditoria de prontuários médicos para hospitais de grande porte.",
        target_sectors=["Saúde"],
        target_company_sizes=["Grande Porte"],
        ticket_price=15000.0,
        target_regions=["Nordeste", "Sudeste"]
    )

    reply = asyncio.run(agent.answer_consultative_query(
        user_query="Qual é o melhor cliente no Nordeste e por que a oferta e demanda da região favorece esse fechamento?",
        product=product
    ))

    # Verifica cordialidade e polidez
    assert ("satisfação" in reply.lower() or "olá" in reply.lower() or "prezado" in reply.lower())
    # Deve citar o hospital em Recife ou o contexto do Nordeste
    assert "nordeste" in reply.lower()
    assert "score" in reply.lower() or "demanda" in reply.lower()

