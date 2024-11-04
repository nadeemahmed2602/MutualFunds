from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str

class FundFamilyRequest(BaseModel):
    family:str


class WatchlistItem(BaseModel):
    fund_family_id: str
    scheme_code: int