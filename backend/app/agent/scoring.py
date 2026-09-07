from typing import Dict, Any, List, Tuple
from ..schemas.product import ProductDefinition
from ..schemas.customer import CustomerProfile
from ..schemas.recommendation import ScoreBreakdown, CustomerRecommendation
from ..data.regional_market import RegionalMarketService

class CommercialScoringEngine:
    def __init__(self, market_service: RegionalMarketService):
        self.market_service = market_service

    def score_customer(self, product: ProductDefinition, customer: CustomerProfile) -> CustomerRecommendation:
        # 1. Avaliação de Aderência aos Requisitos do Produto (0 a 100)
        fit_score, fit_notes = self._calculate_product_fit(product, customer)

        # 2. Avaliação de Oportunidade Regional de Mercado (0 a 100)
        regional_info = self.market_service.calculate_regional_opportunity_score(
            region_name=customer.region,
            state_uf=customer.state,
            sector=customer.sector
        )
        regional_score = regional_info["regional_score"]

        # Se a região do cliente não estiver no escopo do produto:
        if product.target_regions and customer.region not in product.target_regions:
            regional_score = regional_score * 0.3  # Penalidade severa por estar fora da área atendida

        # 3. Avaliação de Prontidão e Urgência do Cliente (0 a 100)
        urgency_budget_score = self._calculate_urgency_and_budget(product, customer)

        # 4. Score Final Ponderado:
        # 40% Fit do Produto | 35% Oportunidade Regional (Oferta x Demanda) | 25% Urgência/Orçamento
        final_score = (fit_score * 0.40) + (regional_score * 0.35) + (urgency_budget_score * 0.25)
        final_score = round(max(0.0, min(100.0, final_score)), 1)

        breakdown = ScoreBreakdown(
            product_fit_score=round(fit_score, 1),
            regional_opportunity_score=round(regional_score, 1),
            urgency_budget_score=round(urgency_budget_score, 1),
            final_score=final_score
        )

        # Contextualização e Diagnóstico Comercial
        regional_context = (
            f"Região {customer.region} ({customer.state}): Índice de Demanda em {regional_info['demand_index']}/100 "
            f"com Concorrência/Oferta local em {regional_info['supply_competition_index']}/100. "
            f"Status de Oportunidade: {regional_info['opportunity_label']}."
        )

        commercial_rec = self._generate_commercial_recommendation(customer, final_score, fit_notes)
        risk_analysis = self._generate_risk_analysis(customer, regional_info)
        suggested_approach = self._generate_approach(customer, product)

        return CustomerRecommendation(
            customer=customer,
            match_score=final_score,
            score_breakdown=breakdown,
            regional_context=regional_context,
            commercial_recommendation=commercial_rec,
            risk_and_competitor_analysis=risk_analysis,
            suggested_approach=suggested_approach
        )

    def _calculate_product_fit(self, product: ProductDefinition, customer: CustomerProfile) -> Tuple[float, List[str]]:
        notes = []
        score = 70.0

        # Verificação de Setor
        if product.target_sectors:
            sector_matches = any(
                s.lower() in customer.sector.lower() or customer.sector.lower() in s.lower()
                for s in product.target_sectors
            )
            if sector_matches:
                score += 20.0
                notes.append(f"Setor {customer.sector} é prioritário para o produto.")
            else:
                score -= 35.0
                notes.append(f"Setor {customer.sector} está fora do foco primário ({', '.join(product.target_sectors)}).")
        else:
            score += 10.0
            notes.append("Produto com aderência multissetorial.")

        # Verificação de Porte de Empresa
        if product.target_company_sizes:
            if customer.size in product.target_company_sizes:
                score += 10.0
                notes.append(f"Porte ({customer.size}) perfeitamente alinhado ao ICP.")
            else:
                score -= 20.0
                notes.append(f"Porte ({customer.size}) diverge do perfil ideal desejado.")

        # Verificação de Modelo de Entrega vs Requisitos
        if customer.requirements_profile:
            rp = customer.requirements_profile
            # Se cliente exige suporte presencial e produto é puramente remoto/cloud
            if rp.requires_local_support and "remoto" in product.delivery_model.lower():
                score -= 15.0
                notes.append("Atenção: Cliente exige suporte local/presencial, enquanto o produto opera em modelo remoto.")

            # Ticket range
            if product.ticket_price < rp.min_ticket_accepted:
                score -= 10.0
                notes.append("Ticket do produto pode ser percebido como abaixo do padrão corporativo do cliente.")
            elif product.ticket_price > rp.max_ticket_accepted:
                score -= 25.0
                notes.append("Ticket do produto ultrapassa o limite orçamentário aceito pelo cliente.")

        return max(10.0, min(100.0, score)), notes

    def _calculate_urgency_and_budget(self, product: ProductDefinition, customer: CustomerProfile) -> float:
        demand_weights = {"Muito Alta": 100.0, "Alta": 85.0, "Média": 65.0, "Baixa": 40.0}
        urgency_weights = {"Muito Alta": 100.0, "Alta": 85.0, "Média": 60.0, "Baixa": 35.0}
        budget_weights = {"Muito Alto": 100.0, "Alto": 90.0, "Médio-Alto": 80.0, "Médio": 65.0, "Baixo": 40.0}

        d_val = demand_weights.get(customer.demand_level, 65.0)
        u_val = urgency_weights.get(customer.urgency, 60.0)
        b_val = budget_weights.get(customer.budget_capacity, 65.0)

        return (d_val * 0.40) + (u_val * 0.35) + (b_val * 0.25)

    def _generate_commercial_recommendation(self, customer: CustomerProfile, score: float, fit_notes: List[str]) -> str:
        if score >= 85:
            qualif = "Cliente Altamente Recomendado (Lead Quente A+)"
        elif score >= 70:
            qualif = "Cliente Recomendado com Forte Potencial (Lead Qualificado A)"
        elif score >= 55:
            qualif = "Cliente em Potencial com Necessidade de Nutrição Comercial (Lead B)"
        else:
            qualif = "Cliente com Baixa Prioridade Comercial (Fora do Perfil Imediato)"

        details = " ".join(fit_notes)
        return f"{qualif}. {details}"

    def _generate_risk_analysis(self, customer: CustomerProfile, regional_info: Dict[str, Any]) -> str:
        vendor = customer.current_competitor_vendor or "Nenhum concorrente formal mapeado"
        supply_idx = regional_info.get("supply_competition_index", 50)
        
        if supply_idx >= 75:
            comp_threat = "Alta saturação de concorrentes na UF. Risco de disputa acirrada por preço."
        elif supply_idx <= 45:
            comp_threat = "Baixa presença de concorrentes diretos locais. Excelente janela para posicionamento de pioneirismo."
        else:
            comp_threat = "Concorrência regional moderada. Decisão será pautada por diferenciais técnicos e relacionamento."

        return f"Cenário Concorrencial: Fornecedor atual reportado: '{vendor}'. {comp_threat}"

    def _generate_approach(self, customer: CustomerProfile, product: ProductDefinition) -> str:
        contact = f"{customer.contact_name} ({customer.contact_role})" if customer.contact_name else "Diretoria de Compras"
        return (
            f"Abordar cortês e consultivamente {contact}. Apresentar caso prático focado na dor: "
            f"'{customer.current_pain_points}', destacando como o produto resolve essa deficiência com alto retorno sobre investimento."
        )
