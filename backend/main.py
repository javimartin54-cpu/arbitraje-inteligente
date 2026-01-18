from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from wallapop_scraper import search_wallapop
from ebay_scraper import search_ebay_sold
from vinted_scraper import search_vinted
from catawiki_scraper import search_catawiki_closed

app = FastAPI(title="Arbitraje Inteligente API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    keywords: List[str]
    max_results: int = 20

PLATFORM_FEES = {
    'wallapop': {'buy': 0.05, 'sell': 0.05},
    'ebay': {'buy': 0.0, 'sell': 0.125},
    'vinted': {'buy': 0.0, 'sell': 0.05},
    'catawiki': {'buy': 0.09, 'sell': 0.09}
}

SHIPPING_COSTS = {
    'wallapop': 5.0,
    'ebay': 7.0,
    'vinted': 6.0,
    'catawiki': 8.0
}

def calculate_arbitrage_opportunity(buy_product: dict, sell_product: dict) -> dict:
    buy_platform = buy_product['platform']
    sell_platform = sell_product['platform']
    
    buy_price = buy_product['price']
    buy_commission = buy_price * PLATFORM_FEES[buy_platform]['buy']
    buy_shipping = SHIPPING_COSTS[buy_platform]
    
    sell_price = sell_product['price']
    sell_commission = sell_price * PLATFORM_FEES[sell_platform]['sell']
    sell_shipping = SHIPPING_COSTS[sell_platform]
    payment_fee = sell_price * 0.03
    
    packaging = 2.0
    taxes = (sell_price - buy_price) * 0.19 if sell_price > buy_price else 0
    
    total_investment = buy_price + buy_commission + buy_shipping + packaging
    total_costs = total_investment + sell_commission + sell_shipping + payment_fee + taxes
    net_profit = sell_price - total_costs
    
    roi_percent = (net_profit / total_investment * 100) if total_investment > 0 else 0
    score = min(100, max(0, roi_percent))
    
    return {
        'buy_title': buy_product['title'],
        'buy_price': round(buy_price, 2),
        'buy_platform': buy_platform,
        'buy_url': buy_product.get('url', ''),
        'sell_title': sell_product['title'],
        'sell_price': round(sell_price, 2),
        'sell_platform': sell_platform,
        'sell_url': sell_product.get('url', ''),
        'net_profit': round(net_profit, 2),
        'roi_percent': round(roi_percent, 2),
        'score': round(score, 2),
        'total_investment': round(total_investment, 2),
        'costs_breakdown': {
            'buy_price': round(buy_price, 2),
            'buy_commission': round(buy_commission, 2),
            'buy_shipping': round(buy_shipping, 2),
            'sell_commission': round(sell_commission, 2),
            'sell_shipping': round(sell_shipping, 2),
            'payment_fee': round(payment_fee, 2),
            'packaging': round(packaging, 2),
            'taxes': round(taxes, 2)
        }
    }

@app.get("/")
async def root():
    return {"message": "Arbitraje Inteligente API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/search-arbitrage")
async def search_arbitrage(request: SearchRequest):
    try:
        keywords = request.keywords
        max_results = request.max_results
        
        print(f"🔍 Buscando en todas las plataformas: {keywords}")
        
        results = await asyncio.gather(
            search_wallapop(keywords, max_results),
            search_ebay_sold(keywords, max_results),
            search_vinted(keywords, max_results),
            search_catawiki_closed(keywords, max_results),
            return_exceptions=True
        )
        
        wallapop_products = results[0] if not isinstance(results[0], Exception) else []
        ebay_products = results[1] if not isinstance(results[1], Exception) else []
        vinted_products = results[2] if not isinstance(results[2], Exception) else []
        catawiki_products = results[3] if not isinstance(results[3], Exception) else []
        
        all_products = {
            'wallapop': wallapop_products,
            'ebay': ebay_products,
            'vinted': vinted_products,
            'catawiki': catawiki_products
        }
        
        print(f"📊 Resultados: Wallapop={len(wallapop_products)}, eBay={len(ebay_products)}, Vinted={len(vinted_products)}, Catawiki={len(catawiki_products)}")
        
        opportunities = []
        
        for buy_platform, buy_products in all_products.items():
            for sell_platform, sell_products in all_products.items():
                if buy_platform == sell_platform:
                    continue
                
                for buy_product in buy_products:
                    for sell_product in sell_products:
                        if sell_product['price'] > buy_product['price'] * 1.2:
                            opportunity = calculate_arbitrage_opportunity(buy_product, sell_product)
                            
                            if opportunity['roi_percent'] > 0:
                                opportunities.append(opportunity)
        
        opportunities.sort(key=lambda x: x['roi_percent'], reverse=True)
        opportunities = opportunities[:50]
        
        print(f"✅ Encontradas {len(opportunities)} oportunidades de arbitraje")
        
        return {
            'success': True,
            'total_opportunities': len(opportunities),
            'opportunities': opportunities,
            'platforms_searched': {
                'wallapop': len(wallapop_products),
                'ebay': len(ebay_products),
                'vinted': len(vinted_products),
                'catawiki': len(catawiki_products)
            }
        }
        
    except Exception as e:
        print(f"❌ Error en búsqueda: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
