from typing import List, Optional
from pydantic import BaseModel
from .customer import CustomerProfile

class ScoreBreakdown(BaseModel):
    product_fit_score: float
    regional_opportunity_score: float
    urgency_budget_score: float
    final_score: float

class CustomerRecommendation(BaseModel):
    customer: CustomerProfile
    match_score: float
    score_breakdown: ScoreBreakdown
    regional_context: str
    commercial_recommendation: str
    risk_and_competitor_analysis: str
    suggested_approach: str

class RecommendationResponse(BaseModel):
    product_name: str
    total_analyzed: int
    recommended_count: int
    top_recommendations: List[CustomerRecommendation]
    regional_summary: dict
