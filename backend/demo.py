from datetime import date, timedelta
from supabase import Client

def load_demo(sb: Client, user_id: str, force: bool) -> dict:
    real = sb.table("listings").select("id").eq("user_id", user_id).eq("is_demo", False).limit(1).execute().data
    if real and not force:
        return {"ok": False, "status": 409, "message": "Ya tienes datos reales. No se mezcla demo con real. Usa force=true si quieres."}

    src = sb.table("sources").upsert({
        "user_id": user_id, "type": "manual_url", "name": "Demo", "notes": "Datos de ejemplo"
    }, on_conflict="user_id,name").execute().data[0]

    def upsert_product(name, category, liquidity):
        ex = sb.table("products").select("id").eq("user_id", user_id).eq("canonical_name", name).limit(1).execute().data
        if ex:
            return ex[0]["id"]
        return sb.table("products").insert({
            "user_id": user_id, "canonical_name": name, "category": category,
            "aliases": [], "liquidity_class": liquidity, "is_demo": True
        }).execute().data[0]["id"]

    p1 = upsert_product("Sony WH-1000XM4", "headphones", "medium")
    p2 = upsert_product("Apple AirPods Pro 2", "headphones", "medium")
    p3 = upsert_product("LEGO 75257 Millennium Falcon", "collectibles", "low")

    def insert_listing(platform, url, title, price, ship, category, cond, product_id):
        lst = sb.table("listings").upsert({
            "user_id": user_id, "source_id": src["id"], "platform": platform,
            "url": url, "title": title, "price": price, "currency": "EUR",
            "shipping_price": ship, "category": category, "item_condition": cond,
            "is_demo": True
        }, on_conflict="user_id,platform,url").execute().data[0]
        sb.table("listing_product_match").upsert({
            "listing_id": lst["id"], "product_id": product_id, "user_id": user_id,
            "confidence": 1.0, "method": "demo"
        }).execute()

    insert_listing("wallapop", "https://example.com/wallapop-xm4", "Sony WH-1000XM4 como nuevos", 120, 6, "headphones", "like_new", p1)
    insert_listing("vinted", "https://example.com/vinted-airpods", "AirPods Pro 2", 140, 5, "headphones", "good", p2)
    insert_listing("wallapop", "https://example.com/wallapop-lego", "LEGO 75257 Millennium Falcon", 85, 7, "collectibles", "good", p3)

    def add_sales(product_id, prices):
        today = date.today()
        for i, pr in enumerate(prices):
            sb.table("observed_sales").insert({
                "user_id": user_id, "platform": "ebay", "product_id": product_id,
                "sold_price": float(pr), "sold_at": (today - timedelta(days=2*i)).isoformat(),
                "item_condition": "good", "is_demo": True
            }).execute()

    add_sales(p1, [179,185,189,199,205])
    add_sales(p2, [185,195,199,210,215])
    add_sales(p3, [135,140,145,150,160])

    return {"ok": True, "status": 200, "inserted": {"products": 3, "listings": 3, "observed_sales": 15}}
