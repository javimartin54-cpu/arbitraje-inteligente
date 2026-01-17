from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import date

Platform = Literal["wallapop","vinted","ebay","catawiki","miravia"]
Condition = Literal["new","like_new","good","fair","unknown"]

class ListingIn(BaseModel):
    platform: Platform
    url: str
    title: str
    price: float
    currency: str = "EUR"
    shipping_price: Optional[float] = None
    category: Optional[str] = None
    condition: Condition = "unknown"
    location: Optional[str] = None
    images: List[str] = []
    is_demo: bool = False

class BrowserSearchResult(BaseModel):
    title: str
    price: float
    url: str
    location: Optional[str] = None

class BrowserSearchIn(BaseModel):
    platform: Platform
    query: str = ""
    url: str
    results: List[BrowserSearchResult]
    is_demo: bool = False

class ObservedSaleIn(BaseModel):
    platform: Platform
    product_id: Optional[str] = None
    keyword: Optional[str] = None
    sold_price: float
    sold_at: date
    condition: Condition = "unknown"
    url: Optional[str] = None
    notes: Optional[str] = None
    is_demo: bool = False

class RefreshIn(BaseModel):
    platforms_buy: List[Platform] = ["wallapop","vinted"]
    platforms_sell: List[Platform] = ["ebay"]
    min_roi: float = 0.10
    min_net_margin: float = 10.0
    limit: int = 200
    include_demo: bool = False

class DemoLoadIn(BaseModel):
    force: bool = False
