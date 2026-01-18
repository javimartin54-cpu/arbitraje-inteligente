import asyncio
import re
from typing import List, Dict
from playwright.async_api import async_playwright

class VintedScraper:
    def __init__(self):
        self.base_url = "https://www.vinted.es"
    
    async def search_items(self, keywords: List[str], max_results: int = 20) -> List[Dict]:
        search_query = " ".join(keywords)
        search_url = f"{self.base_url}/catalog?search_text={search_query.replace(' ', '+')}"
        
        print(f"🔍 Buscando en Vinted: {search_query}")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
                page = await browser.new_page()
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(3)
                
                products = []
                selectors = ['[data-testid="feed-grid"] > div', '.feed-grid__item', 'article[class*="item"]']
                
                items = []
                for selector in selectors:
                    items = await page.query_selector_all(selector)
                    if len(items) > 0:
                        break
                
                for item in items[:max_results]:
                    try:
                        title_elem = await item.query_selector('[data-testid="item-title"], h3, div[class*="title"]')
                        title = await title_elem.inner_text() if title_elem else ""
                        
                        price_elem = await item.query_selector('[data-testid="item-price"], div[class*="price"]')
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
                                'platform': 'vinted',
                                'image_url': '',
                                'location': 'España'
                            })
                    except:
                        continue
                
                await browser.close()
                print(f"✅ Encontrados {len(products)} productos en Vinted")
                return products
        except Exception as e:
            print(f"❌ Error scraping Vinted: {str(e)}")
            return []

async def search_vinted(keywords: List[str], max_results: int = 20) -> List[Dict]:
    scraper = VintedScraper()
    return await scraper.search_items(keywords, max_results)
