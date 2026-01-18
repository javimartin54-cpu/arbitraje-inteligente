import asyncio
import re
from typing import List, Dict
from playwright.async_api import async_playwright
import random

class EbayScraper:
    def __init__(self):
        self.base_url = "https://www.ebay.es"
    
    async def search_sold_items(self, keywords: List[str], max_results: int = 20) -> List[Dict]:
        search_query = " ".join(keywords)
        search_url = f"{self.base_url}/sch/i.html?_from=R40&_nkw={search_query.replace(' ', '+')}&_sacat=0&LH_Sold=1&LH_Complete=1&rt=nc"
        
        print(f"🔍 Buscando ventas completadas en eBay: {search_query}")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
                page = await browser.new_page()
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(3)
                
                products = []
                items = await page.query_selector_all('.s-item')
                
                for item in items[:max_results]:
                    try:
                        title_elem = await item.query_selector('.s-item__title')
                        title = await title_elem.inner_text() if title_elem else ""
                        
                        price_elem = await item.query_selector('.s-item__price')
                        price_text = await price_elem.inner_text() if price_elem else "0"
                        price = float(re.sub(r'[^\d,.]', '', price_text).replace(',', '.'))
                        
                        link_elem = await item.query_selector('.s-item__link')
                        url = await link_elem.get_attribute('href') if link_elem else ""
                        
                        if title and price > 0 and "Shop on eBay" not in title:
                            products.append({
                                'title': title.strip(),
                                'price': price,
                                'url': url,
                                'platform': 'ebay',
                                'image_url': '',
                                'location': 'España'
                            })
                    except:
                        continue
                
                await browser.close()
                print(f"✅ Encontrados {len(products)} productos vendidos en eBay")
                return products
        except Exception as e:
            print(f"❌ Error scraping eBay: {str(e)}")
            return []

async def search_ebay_sold(keywords: List[str], max_results: int = 20) -> List[Dict]:
    scraper = EbayScraper()
    return await scraper.search_sold_items(keywords, max_results)
