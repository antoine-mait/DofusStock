from playwright.sync_api import sync_playwright
import json

def scrape_dofus_build_items(url):
    try:
        # Define excluded items
        exclude_items = [
            'Personnage', 'Capital vitalité', 'Capital', 'Parchemin', 
            'Parchemin vitalité', 'Bonus caracs', 
            'Bonus agilité', 'Bonus sagesse', 'Bonus force', 'Bonus chance'
        ]
        
        # Using Playwright for web scraping
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle')
            
            # Extract items using JavaScript execution with exclusion logic
            build_items = page.evaluate('''() => {
                const tooltips = document.querySelectorAll('.CmpTooltip-text');
                const items = new Set();
                const excludeItems = %s;
                
                tooltips.forEach(tooltip => {
                    const details = tooltip.querySelectorAll('div');
                    details.forEach(detail => {
                        const text = detail.textContent.trim();
                        if (text.includes(':')) {
                            const item = text.split(':')[0].trim();
                            
                            // Check exclusion conditions
                            if (!excludeItems.includes(item) && !item.startsWith('Panoplie')) {
                                items.add(item);
                            }
                        }
                    });
                });
                
                return Array.from(items);
            }''' % json.dumps(exclude_items))
            
            browser.close()
            return build_items
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def main():
    url = 'https://d-bk.net/fr/d/1K4FD'
    build_items = scrape_dofus_build_items(url)
    for item in build_items:
        print(item)

if __name__ == '__main__':
    main()