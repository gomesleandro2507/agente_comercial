import json
import csv
import io
import os
from typing import List, Optional, Dict, Any
from ..schemas.customer import CustomerProfile, RequirementsProfile

class CustomersRepository:
    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            data_path = os.path.join(base_dir, "data", "sample_customers.json")
        self.data_path = data_path
        self._customers: List[CustomerProfile] = []
        self.reload()

    def reload(self) -> None:
        self._customers = []
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
                for item in raw_items:
                    req_prof = None
                    if item.get("requirements_profile"):
                        req_prof = RequirementsProfile(**item["requirements_profile"])
                    item["requirements_profile"] = req_prof
                    self._customers.append(CustomerProfile(**item))

    def get_all(self) -> List[CustomerProfile]:
        return list(self._customers)

    def get_by_id(self, customer_id: str) -> Optional[CustomerProfile]:
        for c in self._customers:
            if c.id.lower() == customer_id.lower():
                return c
        return None

    def add_customer(self, customer: CustomerProfile) -> None:
        # Substitui se já existir, senão adiciona
        self._customers = [c for c in self._customers if c.id != customer.id]
        self._customers.append(customer)

    def import_from_csv(self, csv_content: str) -> int:
        f = io.StringIO(csv_content)
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            cid = row.get("id") or f"CLI-{len(self._customers)+1:03d}"
            cust = CustomerProfile(
                id=cid,
                name=row.get("name", "Cliente Sem Nome"),
                cnpj=row.get("cnpj"),
                sector=row.get("sector", "Geral"),
                subsector=row.get("subsector"),
                size=row.get("size", "Médio Porte"),
                annual_revenue_bracket=row.get("annual_revenue_bracket"),
                state=row.get("state", "SP").upper(),
                city=row.get("city", "São Paulo"),
                region=row.get("region", "Sudeste"),
                contact_name=row.get("contact_name"),
                contact_role=row.get("contact_role"),
                current_pain_points=row.get("current_pain_points", "Necessidade de modernização operacional"),
                demand_level=row.get("demand_level", "Média"),
                urgency=row.get("urgency", "Média"),
                budget_capacity=row.get("budget_capacity", "Médio"),
                decision_cycle=row.get("decision_cycle", "Médio")
            )
            self.add_customer(cust)
            count += 1
        return count
