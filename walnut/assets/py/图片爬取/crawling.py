import os
import re
import requests
import time
import hashlib
import random
import argparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SimpleImageCrawler:
    def __init__(self):
        self.visited_urls = set()
        self.downloaded = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://www.google.com/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.max_retries = 2
        self.delay = (0.5, 1.5)

    def _get_hash(self, content):
        return hashlib.md5(content).hexdigest()

    def _find_next_page(self, current_url):
        # 自动识别数字分页（支持 page= / p= / 路径数字）
        patterns = [
            r'(page|p)=(\d+)',          # 匹配查询参数
            r'/page/(\d+)',
            r'/(\d+)(/|\.html|$)'       # 匹配路径末尾数字
        ]
        
        for pattern in patterns:
            match = re.search(pattern, current_url)
            if match:
                if '=' in pattern:  # 处理参数形式
                    param, num = match.groups()
                    new_num = int(num) + 1
                    return current_url.replace(f"{param}={num}", f"{param}={new_num}")
                else:  # 处理路径形式
                    num = match.group(1)
                    new_num = int(num) + 1
                    return current_url.replace(num, str(new_num), 1)
        return None

    def _fetch(self, url):
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        html = driver.page_source
        driver.quit()
        return html.encode('utf-8')

    def _extract_images(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                clean_url = urljoin(base_url, src.split('?')[0])
                if clean_url.startswith('http'):
                    urls.append(clean_url)
        return list(set(urls))

    def _download(self, img_url):
        if img_url in self.downloaded:
            return

        try:
            resp = self.session.get(img_url, stream=True, timeout=10)
            resp.raise_for_status()
            
            content = resp.content
            content_hash = self._get_hash(content)
            
            if content_hash in self.downloaded:
                return
                
            # 创建保存目录
            os.makedirs('images', exist_ok=True)
            
            # 生成安全文件名
            filename = re.sub(r'[^\w\-_.]', '', os.path.basename(img_url))[:100]
            save_path = os.path.join('images', filename)
            
            with open(save_path, 'wb') as f:
                f.write(content)
                
            self.downloaded.update([img_url, content_hash])
            print(f"✅ 已保存: {filename}")
            
        except Exception as e:
            print(f"❌ 下载失败 {img_url}: {str(e)}")

    def crawl(self, start_url, max_depth=5):
        current_url = start_url
        depth = 0
        
        while depth < max_depth:
            if current_url in self.visited_urls:
                break
                
            print(f"🔍 正在爬取: {current_url}")
            self.visited_urls.add(current_url)
            
            html = self._fetch(current_url)
            if not html:
                break
                
            # 下载当前页图片
            img_urls = self._extract_images(html, current_url)
            with ThreadPoolExecutor(max_workers=6) as executor:
                executor.map(self._download, img_urls)
            
            # 获取下一页
            next_page = self._find_next_page(current_url)
            if not next_page:
                break
                
            current_url = next_page
            depth += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=True, help='起始网址')
    parser.add_argument('--depth', type=int, default=100, help='最大深度')
    args = parser.parse_args()
    
    crawler = SimpleImageCrawler()
    crawler.crawl(start_url=args.url, max_depth=args.depth)
