import json
import os
from typing import Dict, Any, Optional

class RegionalMarketService:
    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            data_path = os.path.join(base_dir, "data", "regional_indicators.json")
        self.data_path = data_path
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"regions": {}, "state_modifiers": {}}

    def get_all_regions_summary(self) -> Dict[str, Any]:
        return self.data.get("regions", {})

    def get_state_info(self, state_uf: str) -> Optional[Dict[str, Any]]:
        state_uf = state_uf.upper().strip()
        modifiers = self.data.get("state_modifiers", {})
        return modifiers.get(state_uf)

    def calculate_regional_opportunity_score(self, region_name: str, state_uf: str, sector: str) -> Dict[str, Any]:
        """
        Calcula o índice de oportunidade com base na demanda e oferta (concorrência).
        Regiões com ALTA DEMANDA e BAIXA A MÉDIA OFERTA recebem as maiores pontuações.
        """
        regions = self.data.get("regions", {})
        region_info = regions.get(region_name)
        
        # Valores padrão caso não encontre
        base_demand = 70.0
        base_supply = 60.0
        opportunity_label = "Média"
        notes = "Mercado regional em equilíbrio."

        if region_info:
            dynamics = region_info.get("sector_dynamics", {})
            sector_data = dynamics.get(sector)
            if not sector_data:
                # Tenta match parcial por palavra-chave
                for s_key, s_val in dynamics.items():
                    if s_key.lower() in sector.lower() or sector.lower() in s_key.lower():
                        sector_data = s_val
                        break
            
            if sector_data:
                base_demand = float(sector_data.get("demand_index", 70))
                base_supply = float(sector_data.get("supply_competition_index", 60))
                opportunity_label = sector_data.get("market_opportunity", "Média")
            
            notes = region_info.get("strategic_notes", "")

        # Aplicar multiplicadores de UF
        state_info = self.get_state_info(state_uf)
        demand_boost = state_info.get("demand_boost", 1.0) if state_info else 1.0
        competition_boost = state_info.get("competition_boost", 1.0) if state_info else 1.0
        logistics_score = state_info.get("logistics_score", 80) if state_info else 80

        adjusted_demand = min(100.0, base_demand * demand_boost)
        adjusted_supply = min(100.0, base_supply * competition_boost)

        # Cálculo do Score de Oportunidade:
        # Alta Demanda pontua positivamente.
        # Alta Concorrência (Oferta instalada) gera pressão de preço e dificuldade de entrada.
        # Oportunidade Líquida = (Demanda Ajustada * 0.65) + ((100 - Oferta Ajustada) * 0.35)
        raw_opportunity = (adjusted_demand * 0.65) + ((100.0 - adjusted_supply) * 0.35)
        
        # Ponderação com viabilidade logística (10% de peso)
        final_regional_score = (raw_opportunity * 0.90) + (logistics_score * 0.10)
        final_regional_score = round(max(0.0, min(100.0, final_regional_score)), 1)

        return {
            "region": region_name,
            "state": state_uf.upper(),
            "sector": sector,
            "demand_index": round(adjusted_demand, 1),
            "supply_competition_index": round(adjusted_supply, 1),
            "logistics_score": logistics_score,
            "regional_score": final_regional_score,
            "opportunity_label": opportunity_label,
            "strategic_notes": notes
        }
