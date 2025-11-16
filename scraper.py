import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime

def scrape_url(url):
    """
    Scrape one Jugantor editorial page
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        news_list = []
        seen_titles = set()

        desktop_news = soup.select('.desktopSectionListMedia .media')
        mobile_news = soup.select('.sectionListMedia .media')
        all_news = desktop_news + mobile_news

        lead_news = soup.select('.desktopSectionLead, .sectionLead')
        all_news = lead_news + all_news

        for item in all_news:
            try:
                title_elem = item.select_one('h1, h2, h3, h4')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                if title in seen_titles:
                    continue
                seen_titles.add(title)

                link_elem = item.select_one('a.linkOverlay')
                link = link_elem['href'] if link_elem else ''
                if link and not link.startswith('http'):
                    link = 'https://www.jugantor.com' + link

                img_elem = item.select_one('img')
                image = ''
                if img_elem:
                    image = img_elem.get('data-src') or img_elem.get('src', '')

                summary_elem = item.select_one('.desktopSummary, p')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''

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

            except:
                continue

        return news_list

    except:
        return []

def save_to_xml(data, filename):
    """
    Save scraped data as a valid RSS 2.0 feed
    """
    try:
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')

        ET.SubElement(channel, 'title').text = 'Jugantor Editorials'
        ET.SubElement(channel, 'link').text = 'https://www.jugantor.com'
        ET.SubElement(channel, 'description').text = 'Latest editorials'
        ET.SubElement(channel, 'language').text = 'bn-BD'
        ET.SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        ET.SubElement(channel, 'generator').text = 'Jugantor Editorial Scraper'

        for news in data:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = news.get('title', '')
            ET.SubElement(item, 'link').text = news.get('link', '')
            ET.SubElement(item, 'guid').text = news.get('link', '')
            ET.SubElement(item, 'pubDate').text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

            desc = ET.SubElement(item, 'description')
            summary_text = news.get('summary', '') or ''
            image_url = news.get('image', '')
            if image_url:
                summary_text = f'<![CDATA[<img src="{image_url}" /><br>{summary_text}]]>'
            else:
                summary_text = f'<![CDATA[{summary_text}]]>'
            desc.text = summary_text

        tree = ET.ElementTree(rss)
        ET.indent(tree, space="  ")
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        print(f"Saved: {filename} ({len(data)} items)")

    except Exception as e:
        print(e)

def main():
    print("Scraping...")

    editorial = scrape_url("https://www.jugantor.com/editorial")
    tp_editorial = scrape_url("https://www.jugantor.com/tp-editorial")

    save_to_xml(editorial, "editorial_news.xml")
    save_to_xml(tp_editorial, "tp_editorial_news.xml")

if __name__ == "__main__":
    main()