import os
import json
from typing import List, Dict, Any, Optional
import httpx
from ..schemas.product import ProductDefinition
from ..schemas.customer import CustomerProfile
from ..schemas.recommendation import CustomerRecommendation, RecommendationResponse
from .scoring import CommercialScoringEngine
from ..data.regional_market import RegionalMarketService
from ..data.customers_repo import CustomersRepository

SYSTEM_PROMPT = """Você é o Agente Comercial Consultivo de Inteligência de Mercado no Brasil.
Sua missão é identificar e recomendar com máxima precisão quais são os melhores clientes potenciais para um determinado produto, fundamentando suas escolhas na análise estratégica de oferta e demanda em todas as regiões e estados do Brasil.

Suas diretrizes obrigatórias de atuação:
1. Postura e Tom: Seja sempre extremamente educado, polido, respeitoso e executivo. Trate o interlocutor com cordialidade (ex: "Prezado(a)", "É uma satisfação auxiliá-lo(a) nesta estratégia comercial").
2. Rigor aos Requisitos do Produto: Nunca recomende um cliente que viole as exigências técnicas, de porte ou de nicho do produto. Se houver restrições de infraestrutura ou modelo de entrega, deixe isso explícito.
3. Inteligência de Oferta e Demanda Regional: Explique detalhadamente por que determinada região é favorável (exemplo: alta demanda com oferta reprimida/pouca concorrência vs regiões saturadas onde haverá disputa de preços).
4. Próximos Passos Consultivos: Para cada recomendação principal, sugira uma abordagem comercial cortês, personalizada para a dor específica do decisor do cliente.
5. Sempre responda em Português do Brasil com excelente redação e formatação clara.
"""

class CommercialAgent:
    def __init__(self, market_service: RegionalMarketService, customers_repo: CustomersRepository):
        self.market_service = market_service
        self.customers_repo = customers_repo
        self.scoring_engine = CommercialScoringEngine(market_service)
        self.api_key = os.getenv("GEMINI_API_KEY")

    def analyze_product_and_recommend(self, product: ProductDefinition, top_n: int = 5) -> RecommendationResponse:
        all_customers = self.customers_repo.get_all()
        scored_recommendations: List[CustomerRecommendation] = []

        for cust in all_customers:
            rec = self.scoring_engine.score_customer(product, cust)
            scored_recommendations.append(rec)

        # Ordenar pelo Score final descrescente
        scored_recommendations.sort(key=lambda x: x.match_score, reverse=True)
        top_recs = scored_recommendations[:top_n]

        # Resumo regional
        regional_summary = {}
        for rec in top_recs:
            reg = rec.customer.region
            regional_summary[reg] = regional_summary.get(reg, 0) + 1

        return RecommendationResponse(
            product_name=product.name,
            total_analyzed=len(all_customers),
            recommended_count=len(top_recs),
            top_recommendations=top_recs,
            regional_summary=regional_summary
        )

    async def answer_consultative_query(
        self,
        user_query: str,
        product: Optional[ProductDefinition] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Responde a questionamentos comerciais de forma educada, precisa e consultiva,
        utilizando a API do Gemini ou o motor heurístico especializado.
        """
        all_customers = self.customers_repo.get_all()
        current_product = product or ProductDefinition(
            name="Solução Corporativa de Produtividade & Inteligência",
            description="Solução escalável para otimização de processos e eficiência operacional",
            target_sectors=["Agronegócio", "Saúde", "Tecnologia & Software", "Indústria", "Logística & Transporte"],
            ticket_price=12000.0
        )

        recommendations = self.analyze_product_and_recommend(current_product, top_n=5)

        # Se houver API KEY do Gemini configurada, utiliza o modelo LLM
        if self.api_key:
            try:
                return await self._call_gemini_api(user_query, current_product, recommendations, chat_history)
            except Exception as e:
                # Caso ocorra falha na API remota, fallback elegante para motor heurístico
                return self._generate_consultative_response_local(user_query, current_product, recommendations)

        return self._generate_consultative_response_local(user_query, current_product, recommendations)

    async def _call_gemini_api(
        self,
        user_query: str,
        product: ProductDefinition,
        recommendations: RecommendationResponse,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        
        # Montar contexto com dados dos clientes analisados
        recs_context = []
        for r in recommendations.top_recommendations:
            recs_context.append({
                "cliente": r.customer.name,
                "estado_regiao": f"{r.customer.state} ({r.customer.region})",
                "setor": r.customer.sector,
                "porte": r.customer.size,
                "score": r.match_score,
                "detalhe_regional": r.regional_context,
                "dor_principal": r.customer.current_pain_points,
                "contato": f"{r.customer.contact_name} ({r.customer.contact_role})"
            })

        prompt_payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{
                        "text": (
                            f"Produto sob análise:\n"
                            f"- Nome: {product.name}\n"
                            f"- Proposta: {product.description}\n"
                            f"- Setores-alvo: {', '.join(product.target_sectors)}\n"
                            f"- Ticket Médio: R$ {product.ticket_price:,.2f}\n"
                            f"- Exigências: {', '.join(product.mandatory_requirements) if product.mandatory_requirements else 'Padrão'}\n\n"
                            f"Top Clientes Qualificados pelo Algoritmo de Oferta x Demanda:\n"
                            f"{json.dumps(recs_context, ensure_ascii=False, indent=2)}\n\n"
                            f"Pergunta do Usuário: {user_query}\n\n"
                            f"Instrução: Responda com extrema polidez e cortesia executiva, detalhando os motivos de oferta/demanda e a adequação aos requisitos do produto."
                        )
                    }]
                }
            ]
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=prompt_payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
        
        return self._generate_consultative_response_local(user_query, product, recommendations)

    def _generate_consultative_response_local(
        self,
        user_query: str,
        product: ProductDefinition,
        recommendations: RecommendationResponse
    ) -> str:
        """
        Motor de geração consultiva heurística, elegante, educado e estruturado.
        Garante respostas de alto nível mesmo sem conexão externa ou API Key.
        """
        top = recommendations.top_recommendations
        query_lower = user_query.lower()

        # Saudação e introdução cortês
        greeting = (
            "Olá! É uma satisfação atendê-lo(a). Com base nas diretrizes e exigências do produto "
            f"**{product.name}**, realizei uma varredura completa considerando as dinâmicas de oferta e demanda "
            "em todas as regiões do Brasil.\n\n"
        )

        if not top:
            return (
                greeting +
                "Lamento informar que, no momento, nenhum dos clientes cadastrados atende com segurança às exigências mínimas "
                "especificadas para este produto. Recomendo revisarmos os filtros de setor ou flexibilizarmos os critérios de atendimento regional."
            )

        # Resposta caso pergunte especificamente sobre regiões (ex: Nordeste, Centro-Oeste, Sudeste, Sul, Norte)
        for reg in ["norte", "nordeste", "centro-oeste", "sudeste", "sul"]:
            if reg in query_lower:
                reg_recs = [r for r in top if r.customer.region.lower() == reg]
                if reg_recs:
                    best = reg_recs[0]
                    return (
                        greeting +
                        f"Permita-me destacar a análise para a **Região {best.customer.region}**:\n\n"
                        f"O cliente mais recomendado nesta região é **{best.customer.name}** ({best.customer.city}/{best.customer.state}), "
                        f"atingindo um **Match Score de {best.match_score}%**.\n\n"
                        f"📊 **Contexto de Oferta e Demanda Local**:\n"
                        f"{best.regional_context}\n\n"
                        f"🎯 **Aderência aos Requisitos do Produto**:\n"
                        f"- Porte: {best.customer.size} ({best.customer.annual_revenue_bracket or 'Consolidado'})\n"
                        f"- Dor Imediata: {best.customer.current_pain_points}\n"
                        f"- Nível de Demanda: {best.customer.demand_level} | Urgência: {best.customer.urgency}\n\n"
                        f"🤝 **Recomendação de Abordagem Comercial**:\n"
                        f"{best.suggested_approach}\n\n"
                        "Estou à inteira disposição para aprofundarmos em outros aspectos desta praça ou de outras regiões brasileiras."
                    )

        # Resposta padrão detalhada apresentando os melhores clientes com justificativa cortês
        best_client = top[0]
        second_client = top[1] if len(top) > 1 else None

        body = (
            f"Tendo em vista a proposta de valor do produto e as exigências estabelecidas, identifiquei que o cliente **mais indicado** é:\n\n"
            f"### 🏆 1º Lugar: {best_client.customer.name} (Score: {best_client.match_score}%)\n"
            f"- **Localização**: {best_client.customer.city} - {best_client.customer.state} ({best_client.customer.region})\n"
            f"- **Setor / Porte**: {best_client.customer.sector} | {best_client.customer.size}\n"
            f"- **Por que é o mais indicado?**: {best_client.commercial_recommendation}\n"
            f"- **Fator Regional de Oferta x Demanda**: {best_client.regional_context}\n"
            f"- **Cenário de Concorrência**: {best_client.risk_and_competitor_analysis}\n"
            f"- **Estratégia de Contato**: {best_client.suggested_approach}\n\n"
        )

        if second_client:
            body += (
                f"### 🥈 2º Lugar: {second_client.customer.name} (Score: {second_client.match_score}%)\n"
                f"- **Localização**: {second_client.customer.city} - {second_client.customer.state} ({second_client.customer.region})\n"
                f"- **Setor / Porte**: {second_client.customer.sector} | {second_client.customer.size}\n"
                f"- **Destaque de Oportunidade**: Apresenta alta receptividade ({second_client.customer.demand_level}), "
                f"com dor latente em '{second_client.customer.current_pain_points}'.\n\n"
            )

        closing = (
            "📌 **Resumo Estratégico**:\n"
            "Observamos que as regiões com maior disparidade positiva entre demanda aquecida e menor pressão competitiva "
            "oferecem o ciclo de fechamento mais rápido e menor erosão de margem de preço.\n\n"
            "Gostaria que eu elaborasse uma minuta personalizada de abordagem comercial ou comparemos com outra praça específica?"
        )

        return greeting + body + closing
