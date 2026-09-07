from typing import List, Optional
from pydantic import BaseModel, Field

class ProductDefinition(BaseModel):
    name: str = Field(..., description="Nome do produto ou serviço")
    description: str = Field(..., description="Descrição detalhada do produto e proposta de valor")
    target_sectors: List[str] = Field(default_factory=list, description="Setores-alvo (ex: Agronegócio, Saúde, Tecnologia, Indústria, etc.)")
    target_company_sizes: List[str] = Field(
        default=["Médio Porte", "Grande Porte", "Corporativo / Muito Grande"],
        description="Portes de empresa ideais"
    )
    ticket_price: float = Field(default=10000.0, description="Preço ou valor anual/mensal médio estimado do produto em R$")
    target_regions: List[str] = Field(
        default=["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"],
        description="Regiões geográficas de atendimento"
    )
    mandatory_requirements: List[str] = Field(
        default_factory=list,
        description="Exigências obrigatórias para o cliente (ex: faturamento mínimo, ERP prévio, suporte local ou nuvem)"
    )
    delivery_model: str = Field(default="Cloud / Remoto", description="Modelo de entrega (ex: Cloud / Remoto, Presencial / On-premise, Híbrido)")
    differentiators: Optional[str] = Field(None, description="Diferenciais competitivos do produto frente à concorrência")
