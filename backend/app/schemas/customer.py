from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RequirementsProfile(BaseModel):
    requires_local_support: bool = False
    cloud_or_onprem: str = "Cloud"
    integration_with_erp: Optional[str] = None
    min_ticket_accepted: float = 0.0
    max_ticket_accepted: float = 999999999.0

class CustomerProfile(BaseModel):
    id: str
    name: str
    cnpj: Optional[str] = None
    sector: str
    subsector: Optional[str] = None
    size: str
    annual_revenue_bracket: Optional[str] = None
    state: str
    city: str
    region: str
    contact_name: Optional[str] = None
    contact_role: Optional[str] = None
    current_pain_points: str
    demand_level: str = "Média"
    urgency: str = "Média"
    budget_capacity: str = "Médio"
    decision_cycle: Optional[str] = None
    requirements_profile: Optional[RequirementsProfile] = None
    current_competitor_vendor: Optional[str] = None
    strategic_fit_summary: Optional[str] = None
