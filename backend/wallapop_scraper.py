import asyncio
import re
from typing import List, Dict
from playwright.async_api import async_playwright

class WallapopScraper:
    def __init__(self):
        self.base_url = "https://es.wallapop.com"
    
    async def search_items(self, keywords: List[str], max_results: int = 20) -> List[Dict]:
        search_query = " ".join(keywords)
        search_url = f"{self.base_url}/app/search?keywords={search_query.replace(' ', '%20')}"
        
        print(f"🔍 Buscando en Wallapop: {search_query}")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
                page = await browser.new_page()
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(3)
                
                products = []
                items = await page.query_selector_all('[data-testid="product-card"]')
                
                for item in items[:max_results]:
                    try:
                        title_elem = await item.query_selector('p[class*="title"]')
                        title = await title_elem.inner_text() if title_elem else ""
                        
                        price_elem = await item.query_selector('span[class*="price"]')
                        price_text = await price_elem.inner_text() if price_elem else "0"
                        price = float(re.sub(r'[^\d,.]', '', price_text).replace(',', '.'))
                        
                        link_elem = await item.query_selector('a')
                        url = await link_elem.get_attribute('href') if link_elem else ""
                        url = f"{self.base_url}{url}" if url and not url.startswith('http') else url
                        
                        if title and price > 0:
                            products.append({
                                'title': title.strip(),
                                'price': price,
                                'url': url,
                                'platform': 'wallapop',
                                'image_url': '',
                                'location': 'España'
                            })
                    except:
                        continue
                
                await browser.close()
                print(f"✅ Encontrados {len(products)} productos en Wallapop")
                return products
        except Exception as e:
            print(f"❌ Error scraping Wallapop: {str(e)}")
            return []

async def search_wallapop(keywords: List[str], max_results: int = 20) -> List[Dict]:
    scraper = WallapopScraper()
    return await scraper.search_items(keywords, max_results)
