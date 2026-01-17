from statistics import median
from urllib.parse import quote_plus
from supabase import Client

def sell_search_url(platform: str, keyword: str) -> str:
    q = quote_plus(keyword)
    if platform == "ebay":
        return f"https://www.ebay.es/sch/i.html?_nkw={q}"
    if platform == "wallapop":
        return f"https://es.wallapop.com/app/search?keywords={q}"
    if platform == "vinted":
        return f"https://www.vinted.es/catalog?search_text={q}"
    if platform == "catawiki":
        return f"https://www.catawiki.com/es/s?q={q}"
    if platform == "miravia":
        return f"https://www.miravia.es/search?q={q}"
    return ""

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def breakeven(invested: float, fee_sell_percent: float, fee_sell_fixed: float,
              ship_sell: float, packaging: float, tax_rate: float, tax_enabled: bool,
              risk_buffer: float) -> float:
    pct = fee_sell_percent + (tax_rate if tax_enabled else 0.0) + risk_buffer
    denom = 1.0 - pct
    if denom <= 0.05:
        return 999999.0
    return (invested + fee_sell_fixed + ship_sell + packaging) / denom

def refresh(sb: Client, user_id: str, body: dict) -> dict:
    settings = sb.table("user_settings").select("*").eq("user_id", user_id).single().execute().data
    fees = sb.table("platform_fees").select("*").eq("user_id", user_id).execute().data
    fee = {f["platform"]: f for f in fees}

    q = sb.table("listings").select("*").eq("user_id", user_id).in_("platform", body["platforms_buy"]).order("imported_at", desc=True).limit(body["limit"])
    if not body.get("include_demo", False):
        q = q.eq("is_demo", False)
    listings = q.execute().data

    updated = 0
    for lst in listings:
        # product match or create simple product by title
        m = sb.table("listing_product_match").select("product_id").eq("user_id", user_id).eq("listing_id", lst["id"]).limit(1).execute().data
        product_id = m[0]["product_id"] if m else None
        if not product_id:
            canonical = (lst["title"] or "")[:120]
            ex = sb.table("products").select("id").eq("user_id", user_id).eq("canonical_name", canonical).limit(1).execute().data
            if ex:
                product_id = ex[0]["id"]
            else:
                product_id = sb.table("products").insert({
                    "user_id": user_id, "canonical_name": canonical, "category": lst.get("category"),
                    "aliases": [], "liquidity_class": "medium", "is_demo": bool(lst.get("is_demo", False))
                }).execute().data[0]["id"]
            sb.table("listing_product_match").upsert({
                "listing_id": lst["id"], "product_id": product_id, "user_id": user_id,
                "confidence": 0.7, "method": "auto_title"
            }).execute()

        prod = sb.table("products").select("*").eq("user_id", user_id).eq("id", product_id).single().execute().data
        keyword = prod["canonical_name"]

        liquidity = prod.get("liquidity_class","medium")
        est_days = int(settings["liquidity_days_medium"])
        if liquidity == "high":
            est_days = int(settings["liquidity_days_high"])
        elif liquidity == "low":
            est_days = int(settings["liquidity_days_low"])

        p_buy = float(lst["price"])
        ship_buy = float(lst["shipping_price"] or 0.0)

        fb = fee.get(lst["platform"], {"fee_percent":0.0,"fee_fixed":0.0})
        fee_buy = p_buy * float(fb["fee_percent"]) + float(fb["fee_fixed"])
        invested = p_buy + fee_buy + ship_buy

        for sell_plat in body["platforms_sell"]:
            obsq = sb.table("observed_sales").select("sold_price").eq("user_id", user_id).eq("platform", sell_plat).eq("product_id", product_id).order("sold_at", desc=True).limit(50)
            if not body.get("include_demo", False):
                obsq = obsq.eq("is_demo", False)
            obs = obsq.execute().data
            if len(obs) >= 5:
                p_sell = float(median([float(x["sold_price"]) for x in obs]))
            else:
                p_sell = p_buy * 1.35

            fs = fee.get(sell_plat, {"fee_percent":0.0,"fee_fixed":0.0})
            fee_sell = p_sell * float(fs["fee_percent"]) + float(fs["fee_fixed"])

            ship_sell = 0.0
            packaging = float(settings["packaging_cost"])
            tax_enabled = bool(settings["tax_enabled"])
            tax_rate = float(settings["tax_rate"])
            risk_buffer = float(settings["risk_buffer"])
            tax = p_sell * tax_rate if tax_enabled else 0.0
            risk = p_sell * risk_buffer

            net_margin = (p_sell - fee_sell - ship_sell - packaging - tax - risk) - invested
            roi = (net_margin / invested) if invested > 0 else 0.0
            be = breakeven(invested, float(fs["fee_percent"]), float(fs["fee_fixed"]), ship_sell, packaging, tax_rate, tax_enabled, risk_buffer)

            score_nm = clamp(net_margin/100.0, 0.0, 1.0) * 30.0
            score_roi = clamp(roi/0.40, 0.0, 1.0) * 20.0
            profit_score = score_nm + score_roi
            liquidity_score = clamp(1.0 - (est_days/60.0), 0.0, 1.0) * 25.0
            demand_score = 12.5
            total_score = profit_score + liquidity_score + demand_score

            if net_margin < body["min_net_margin"] or roi < body["min_roi"]:
                continue

            sb.table("opportunities").upsert({
                "user_id": user_id,
                "buy_listing_id": lst["id"],
                "sell_platform": sell_plat,
                "product_id": product_id,
                "est_sell_price": round(p_sell,2),
                "net_margin": round(net_margin,2),
                "roi": round(roi,4),
                "breakeven_sell_price": round(be,2),
                "est_days_to_sell": est_days,
                "demand_score": round(demand_score,2),
                "liquidity_score": round(liquidity_score,2),
                "total_score": round(total_score,2),
                "is_demo": bool(lst.get("is_demo", False)),
            }, on_conflict="user_id,buy_listing_id,sell_platform").execute()
            updated += 1

    return {"updated": updated}
