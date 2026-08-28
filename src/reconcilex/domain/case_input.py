from datetime import datetime
from pydantic import BaseModel

class CaseInput(BaseModel):
    case_id: str
    reported_issue: str
    primary_invoice_id: str | None = None
    known_payment_id: str | None = None
    observed_at: datetime