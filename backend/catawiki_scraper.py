import asyncio
import re
from typing import List, Dict
from playwright.async_api import async_playwright

class CatawikiScraper:
    def __init__(self):
        self.base_url = "https://www.catawiki.com"
    
    async def search_closed_auctions(self, keywords: List[str], max_results: int = 20) -> List[Dict]:
        search_query = " ".join(keywords)
        search_url = f"{self.base_url}/es/s?q={search_query.replace(' ', '+')}&status=closed"
        
        print(f"🔍 Buscando subastas cerradas en Catawiki: {search_query}")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
                page = await browser.new_page()
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(3)
                
                products = []
                selectors = ['[data-testid="search-result"]', '.c-lot-card', 'article[class*="lot"]']
                
                items = []
                for selector in selectors:
                    items = await page.query_selector_all(selector)
                    if len(items) > 0:
                        break
                
                for item in items[:max_results]:
                    try:
                        title_elem = await item.query_selector('[data-testid="lot-title"], h3, .c-lot-card__title')
                        title = await title_elem.inner_text() if title_elem else ""
                        
                        price_elem = await item.query_selector('[data-testid="lot-price"], span[class*="price"]')
                        price_text = await price_elem.inner_text() if price_elem else "0"
                        price = float(re.sub(r'[^\d,.]', '', price_text).replace(',', '.'))
                        
                        link_elem = await item.query_selector('a')
                        href = await link_elem.get_attribute('href') if link_elem else ""
                        url = f"{self.base_url}{href}" if href and not href.startswith('http') else href
                        
                        if title and price > 0:
                            products.append({
                                'title': title.strip(),
                                'price': price,
                                'url': url,
                                'platform': 'catawiki',
                                'image_url': '',
                                'location': 'Internacional'
                            })
                    except:
                        continue
                
                await browser.close()
                print(f"✅ Encontradas {len(products)} subastas en Catawiki")
                return products
        except Exception as e:
            print(f"❌ Error scraping Catawiki: {str(e)}")
            return []

async def search_catawiki_closed(keywords: List[str], max_results: int = 20) -> List[Dict]:
    scraper = CatawikiScraper()
    return await scraper.search_closed_auctions(keywords, max_results)
