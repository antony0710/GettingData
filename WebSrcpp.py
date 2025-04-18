import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from urllib.parse import urljoin
import os
from requests.exceptions import RequestException

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, base_url, headers=None, delay=(1, 3)):
        """
        初始化爬蟲
        
        Args:
            base_url (str): 要爬取的基礎網址
            headers (dict, optional): 請求標頭
            delay (tuple, optional): 請求之間的隨機延遲範圍（秒）
        """
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }
        self.delay = delay
        self.session = requests.Session()
        self.data = []
        self.results = []
        self.INFO = {}
        self.images = {}
        self.printURL = "https://liquipedia.net"
    def fetch_page(self, url, params=None):
        """
        獲取網頁內容
        
        Args:
            url (str): 要獲取的頁面URL
            params (dict, optional): URL參數
            
        Returns:
            BeautifulSoup: 解析後的頁面內容
        """
        # 添加隨機延遲，避免被網站阻擋
        time.sleep(random.uniform(*self.delay))
        
        try:
            response = self.session.get(
                url, 
                headers=self.headers, 
                params=params,
                timeout=30
            )
            response.raise_for_status()  # 如果請求失敗則拋出異常
            
            # 檢查是否有重定向（可能是被阻擋的跡象）
            if len(response.history) > 0:
                logger.warning(f"Redirected from {url} to {response.url}")
                
            return BeautifulSoup(response.text, 'html.parser')
            
        except RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    # ...existing code...

    def parse_page(self, soup):
        """
        解析頁面，只提取特定的數據元素
        
        Args:
            soup (BeautifulSoup): 解析後的頁面內容
            
        Returns:
            list: 提取的特定數據列表
        """
        if not soup:
            return []
            
        
        try:
            # 使用CSS選擇器找到指定元素/html/body/div[3]/div[2]/main/div/div/div[3]/div/div[2]/div[1]/div[15]/div/table/tbody/tr[6]/td[1]
            print(self.base_url)
            table_selector = "body > div:nth-child(3) > div:nth-child(2) > main > div > div > div:nth-child(3) > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(15) > div > table > tbody"
            table_body = soup.select_one(table_selector)
            self.images['PLAYER_IMAGE'] = soup.select_one('.floatnone img').get('src')
            table_body = soup.select_one('table')
            # 取得 Name
            INFO = {}
            for div in soup.select('.infobox-cell-2.infobox-description'):
                if div.get_text(strip=True) == 'Name:':
                    name_div = div.find_next_sibling('div')
                    if name_div:
                        INFO['RealName'] = name_div.get_text(strip=True)
                        print(INFO)
                    break
            for div in soup.select('.infobox-cell-2.infobox-description'):
                if div.get_text(strip=True) == 'Role:':
                    name_div = div.find_next_sibling('div')
                    if name_div:
                        INFO['Role'] = name_div.get_text(strip=True)
                        print(INFO)
                        break
            self.INFO = INFO
            if not table_body:
                logger.warning("表格未找到，嘗試更寬鬆的選擇器")
                # 嘗試更寬鬆的選擇器
                table_body = soup.select_one("div.main table tbody")
            # <div class="infobox-cell-2 infobox-description">Role:</div>
            if table_body:
                # 找到表格後，獲取所有的連結元素
                links = table_body.select("a[title]")
                years = table_body.select("td[class]")
                role = table_body.select("div")
                print(role)
                years[0].get('>' ,'<')
                for i in range(len(links)):
                    href = links[i].get('href', '')
                    title = links[i].get('title', '')
                    self.results.append({
                        'year': years[i].text.strip(),
                        'href': href,
                        'title': title,
                    })
                
                
            if self.results:
                logger.info(f"Successfully extracted {len(self.results)} links with title attributes")
            else:
                logger.warning("No links with title attributes found")
                
            # search_button = soup.select_one('body > div > div > form > div > div > div > center > input[type="submit"]')
            # if search_button:
            #     # 提取按鈕的所有屬性信息
            #     button_attrs = dict(search_button.attrs)
                
            #     # 將按鈕信息添加到結果中
            #     results.append({
            #         'element_type': 'button',
            #         'value': button_attrs.get('value', ''),
            #         'aria_label': button_attrs.get('aria-label', ''),
            #         'name': button_attrs.get('name', ''),
            #         'role': button_attrs.get('role', ''),
            #         'type': button_attrs.get('type', ''),
            #         'class': ' '.join(button_attrs.get('class', [])) if isinstance(button_attrs.get('class'), list) else button_attrs.get('class', '')
            #     })
            #     logger.info("成功提取 Google 搜尋按鈕信息")
            # else:
            #     logger.warning("未找到 Google 搜尋按鈕")
                
            # 方法2: 通過類別提取第一個符合的元素
            # target_element = soup.select_one('.target-class')
            # if target_element:
            #     results.append({'data': target_element.text.strip()})
            
            # 方法3: 通過標籤屬性提取
            # target_element = soup.find('div', {'data-test': 'target-value'})
            # if target_element:
            #     results.append({'data': target_element.text.strip()})
            
            # 方法4: 通過XPath風格的CSS選擇器提取
            # target_element = soup.select_one('div.container > p.specific-info > span')
            # if target_element:
            #     results.append({'data': target_element.text.strip()})
                
        except Exception as e:
            logger.error(f"Error parsing specific element: {e}")
            
# ...existing code...

    def save_to_csv(self, filename='scraped_data.csv'):
        """
        將收集的數據保存為CSV
        
        Args:
            filename (str): 要保存的文件名
        """
        if not self.data:
            logger.warning("No data to save")
            return
            
        try:
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"Data saved to {filename} ({len(self.data)} records)")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    

    
    def crawl(self, num_pages=1):
            """
            爬取指定數量的頁面
            
            Args:
                num_pages (int): 要爬取的頁面數量
            """
            for page in range(1, num_pages + 1):
                logger.info(f"Crawling page {page}/{num_pages}")
                
                # 構建當前頁面的URL (需要根據實際網站修改)
                current_url = self.base_url
                params = {'page': page} if page > 1 else None
                
                # 獲取並解析頁面
                soup = self.fetch_page(current_url, params)
                page_data = self.parse_page(soup)
                
                if page_data:
                    self.data.extend(page_data)
                    logger.info(f"Got {len(page_data)} items from page {page}")
                else:
                    logger.warning(f"No data retrieved from page {page}")
                    
                # 檢查是否有下一頁 (選擇性實現)
                # next_link = soup.select_one('a.next-page')
                # if not next_link:
                #     logger.info("No more pages")
                #     break
import json
def save_to_json(results, filename='scraped_data.json'):
    """
    將收集的數據 append 保存為 JSON
    """
    data = []
    # 如果檔案已存在，先讀取舊資料
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    # 合併新資料
    data.extend(results)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Data saved to {filename} ({len(data)} records)")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

if __name__ == "__main__":
    with open('./GettingData/chinesePlayer.json', 'r', encoding='utf-8') as f:
        players = json.load(f)
    # 設置基本URL
    ToSave = []
    i = 0
    for player in players:
        ToSave = []
        i = i + 1
        target_url = player['href']
        # 使用範例
        print(target_url)
        scraper = WebScraper(target_url)
        
        # 爬取5頁內容
        scraper.crawl(num_pages=1)
        ToSave.append({
            'id': i,
            'Game ID': player['title'],
            'Name': scraper.INFO['RealName'],
            'Lane': scraper.INFO['Role'],
            'Image': scraper.printURL+scraper.images['PLAYER_IMAGE'],
            'Nationality': 'China',
            'Teams': scraper.results,
        })
        # 保存數據
        print(ToSave)
        save_to_json(ToSave) 