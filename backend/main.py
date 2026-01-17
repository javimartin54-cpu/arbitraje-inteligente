import os
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from supabase_client import get_supabase
from auth import get_current_user
from models import ListingIn, BrowserSearchIn, ObservedSaleIn, RefreshIn, DemoLoadIn
from opportunities import refresh, sell_search_url
from demo import load_demo

load_dotenv()

app = FastAPI(title="Arbitraje Inteligente API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def current_user_id(authorization: str = Header(None)):
    return get_current_user(authorization=authorization, jwks_url=os.environ["SUPABASE_JWKS_URL"])

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/v1/demo/load")
def demo_load(body: DemoLoadIn, user_id: str = Depends(current_user_id)):
    sb = get_supabase()
    res = load_demo(sb, user_id, body.force)
    if not res["ok"]:
        raise HTTPException(status_code=res["status"], detail=res["message"])
    return {"demo_loaded": True, **res["inserted"]}

@app.post("/v1/listings/import/url")
def import_url(item: ListingIn, user_id: str = Depends(current_user_id)):
    sb = get_supabase()
    ins = {
        "user_id": user_id,
        "platform": item.platform,
        "url": item.url,
        "title": item.title,
        "price": item.price,
        "currency": item.currency,
        "shipping_price": item.shipping_price,
        "category": item.category,
        "item_condition": item.condition,
        "location": item.location,
        "images": item.images,
        "is_demo": bool(item.is_demo),
    }
    res = sb.table("listings").upsert(ins, on_conflict="user_id,platform,url").execute().data[0]
    return {"id": res["id"]}

@app.post("/v1/ingest/browser/listing")
def ingest_browser_listing(item: ListingIn, user_id: str = Depends(current_user_id)):
    return import_url(item, user_id)

@app.post("/v1/ingest/browser/search_results")
def ingest_search(payload: BrowserSearchIn, user_id: str = Depends(current_user_id)):
    sb = get_supabase()
    src = sb.table("sources").upsert({
        "user_id": user_id, "type": "browser_extension", "name": "Extension", "notes": "Capturas de navegador"
    }, on_conflict="user_id,name").execute().data[0]
    inserted = 0
    for r in payload.results:
        ins = {
            "user_id": user_id,
            "source_id": src["id"],
            "platform": payload.platform,
            "url": r.url,
            "title": r.title,
            "price": r.price,
            "currency": "EUR",
            "location": r.location,
            "item_condition": "unknown",
            "is_demo": bool(payload.is_demo),
        }
        sb.table("listings").upsert(ins, on_conflict="user_id,platform,url").execute()
        inserted += 1
    return {"inserted": inserted}

@app.post("/v1/observed-sales")
def add_observed_sale(item: ObservedSaleIn, user_id: str = Depends(current_user_id)):
    sb = get_supabase()
    ins = {
        "user_id": user_id,
        "platform": item.platform,
        "product_id": item.product_id,
        "keyword": item.keyword,
        "sold_price": item.sold_price,
        "sold_at": item.sold_at.isoformat(),
        "item_condition": item.condition,
        "url": item.url,
        "notes": item.notes,
        "is_demo": bool(item.is_demo),
    }
    res = sb.table("observed_sales").insert(ins).execute().data[0]
    return {"id": res["id"]}

@app.post("/v1/opportunities/refresh")
def refresh_opps(body: RefreshIn, user_id: str = Depends(current_user_id)):
    sb = get_supabase()
    out = refresh(sb, user_id, body.model_dump())
    return {"refreshed": True, **out}

@app.get("/v1/opportunities")
def list_opps(min_score: float = 0, include_demo: bool = False, user_id: str = Depends(current_user_id)):
    sb = get_supabase()
    q = sb.table("opportunities").select("*").eq("user_id", user_id).gte("total_score", min_score).order("total_score", desc=True)
    if not include_demo:
        q = q.eq("is_demo", False)
    return {"items": q.execute().data}

@app.get("/v1/opportunities/{opp_id}")
def get_opp(opp_id: str, user_id: str = Depends(current_user_id)):
    sb = get_supabase()
    opp = sb.table("opportunities").select("*").eq("user_id", user_id).eq("id", opp_id).single().execute().data
    lst = sb.table("listings").select("*").eq("user_id", user_id).eq("id", opp["buy_listing_id"]).single().execute().data
    prod = None
    if opp.get("product_id"):
        prod = sb.table("products").select("*").eq("user_id", user_id).eq("id", opp["product_id"]).single().execute().data

    keyword = (prod["canonical_name"] if prod else lst["title"])
    sell_url = sell_search_url(opp["sell_platform"], keyword)

    sales = []
    if opp.get("product_id"):
        sales = sb.table("observed_sales").select("sold_price,sold_at,item_condition,url").eq("user_id", user_id).eq("platform", opp["sell_platform"]).eq("product_id", opp["product_id"]).order("sold_at", desc=True).limit(20).execute().data

    return {
        "id": opp["id"],
        "buy_listing": {"platform": lst["platform"], "price": lst["price"], "shipping_price": lst["shipping_price"], "title": lst["title"], "url": lst["url"]},
        "product": {"id": prod["id"], "canonical_name": prod["canonical_name"]} if prod else None,
        "sell_platform": opp["sell_platform"],
        "pricing": {
            "est_sell_price": opp["est_sell_price"],
            "net_margin": opp["net_margin"],
            "roi": opp["roi"],
            "breakeven_sell_price": opp["breakeven_sell_price"],
            "est_days_to_sell": opp["est_days_to_sell"]
        },
        "recent_sales": {"items": sales},
        "actions": {"buy_url": lst["url"], "sell_url": sell_url}
    }
