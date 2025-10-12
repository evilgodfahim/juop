import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

def scrape_jugantor_editorial():
    """
    Scrape editorial news from Jugantor website
    """
    url = "https://www.jugantor.com/editorial"
    
    try:
        # Send GET request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_list = []
        
        # Find all news items (both desktop and mobile versions)
        # Desktop version
        desktop_news = soup.select('.desktopSectionListMedia .media')
        
        # Mobile version
        mobile_news = soup.select('.sectionListMedia .media')
        
        # Combine and remove duplicates
        all_news = desktop_news + mobile_news
        
        # Also get lead news
        lead_news = soup.select('.desktopSectionLead, .sectionLead')
        all_news = lead_news + all_news
        
        seen_titles = set()
        
        for item in all_news:
            try:
                # Extract title
                title_elem = item.select_one('h1, h2, h3, h4')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                # Skip if already seen
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                # Extract link
                link_elem = item.select_one('a.linkOverlay')
                link = link_elem['href'] if link_elem else ''
                if link and not link.startswith('http'):
                    link = 'https://www.jugantor.com' + link
                
                # Extract image
                img_elem = item.select_one('img')
                image = ''
                if img_elem:
                    image = img_elem.get('data-src') or img_elem.get('src', '')
                
                # Extract summary (if available)
                summary_elem = item.select_one('.desktopSummary, p')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                # Extract time (if available)
                time_elem = item.select_one('.desktopTime')
                pub_time = time_elem.get_text(strip=True) if time_elem else ''
                
                news_list.append({
                    'title': title,
                    'link': link,
                    'image': image,
                    'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                    'published_time': pub_time,
                    'scraped_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"Error parsing item: {e}")
                continue
        
        return news_list
        
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []

def save_to_json(data, filename='editorial_news.json'):
    """
    Save scraped data to JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'total_news': len(data),
                'news': data
            }, f, ensure_ascii=False, indent=2)
        print(f"✓ Data saved to {filename}")
        print(f"✓ Total news scraped: {len(data)}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def main():
    print("Starting Jugantor Editorial News Scraper...")
    print("=" * 50)
    
    # Scrape news
    news_data = scrape_jugantor_editorial()
    
    if news_data:
        # Save to JSON
        save_to_json(news_data)
        
        # Print first few titles
        print("\nLatest Editorial News:")
        print("-" * 50)
        for i, news in enumerate(news_data[:5], 1):
            print(f"{i}. {news['title']}")
        
        if len(news_data) > 5:
            print(f"... and {len(news_data) - 5} more")
    else:
        print("No news data scraped!")

if __name__ == "__main__":
    main()
