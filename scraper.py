import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime

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
        
        # Find all news items (desktop + mobile versions)
        desktop_news = soup.select('.desktopSectionListMedia .media')
        mobile_news = soup.select('.sectionListMedia .media')
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
                
                # Skip duplicates
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
                
                # Extract summary
                summary_elem = item.select_one('.desktopSummary, p')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                # Extract time
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

def save_to_xml(data, filename='editorial_news.xml'):
    """
    Save scraped data as a valid RSS 2.0 feed
    """
    try:
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')

        # Channel metadata
        ET.SubElement(channel, 'title').text = 'Jugantor Editorials'
        ET.SubElement(channel, 'link').text = 'https://www.jugantor.com/editorial'
        ET.SubElement(channel, 'description').text = 'Latest editorials from Jugantor newspaper'
        ET.SubElement(channel, 'language').text = 'bn-BD'
        ET.SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        ET.SubElement(channel, 'generator').text = 'Jugantor Editorial Scraper'

        # Add each news item
        for news in data:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = news.get('title', '')
            ET.SubElement(item, 'link').text = news.get('link', '')
            ET.SubElement(item, 'guid').text = news.get('link', '')
            ET.SubElement(item, 'pubDate').text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
            
            # description supports HTML via CDATA
            desc = ET.SubElement(item, 'description')
            summary_text = news.get('summary', '') or ''
            image_url = news.get('image', '')
            if image_url:
                summary_text = f'<![CDATA[<img src="{image_url}" /><br>{summary_text}]]>'
            else:
                summary_text = f'<![CDATA[{summary_text}]]>'
            desc.text = summary_text

        # Write to file
        tree = ET.ElementTree(rss)
        ET.indent(tree, space="  ")  # For Python 3.9+
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        print(f"✓ RSS feed saved to {filename}")
        print(f"✓ Total news items: {len(data)}")

    except Exception as e:
        print(f"Error saving RSS feed: {e}")

def main():
    print("Starting Jugantor Editorial News Scraper...")
    print("=" * 50)
    
    news_data = scrape_jugantor_editorial()
    
    if news_data:
        save_to_xml(news_data)
        
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
