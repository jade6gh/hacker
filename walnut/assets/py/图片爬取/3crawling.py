import os
import requests
import time
import hashlib
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

class ImageCrawler:
    def __init__(self):
        self.visited_urls = set()
        self.downloaded_images = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://www.google.com/',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.max_retries = 3
        self.delay = (1, 3)  # 随机延迟范围
        
    def get_content_hash(self, content):
        return hashlib.md5(content).hexdigest()

    def generate_page_urls(self, base_url, start, end, step=1):
        """生成分页URL"""
        for page in range(start, end + 1, step):
            yield base_url.format(page)

    def fetch_page(self, url):
        """获取页面内容，带有重试机制和随机延迟"""
        time.sleep(random.uniform(*self.delay))
        for _ in range(self.max_retries):
            try:
                resp = self.session.get(url, timeout=10)
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                print(f"请求失败: {url}, 重试中... 错误: {str(e)}")
                time.sleep(2)
        return None

    def extract_image_urls(self, html, base_url):
        """解析页面中的图片URL"""
        soup = BeautifulSoup(html, 'lxml')
        img_tags = soup.find_all('img')
        urls = []
        for img in img_tags:
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            # 转换为绝对URL
            absolute_url = urljoin(base_url, src.split('?')[0])  # 去除URL参数
            urls.append(absolute_url)
        return urls

    def download_image(self, img_url, save_dir='images'):
        """下载并保存图片，带有去重检查"""
        if img_url in self.downloaded_images:
            print(f"跳过重复图片: {img_url}")
            return

        try:
            response = self.session.get(img_url, stream=True, timeout=15)
            response.raise_for_status()
            
            # 内容哈希去重
            content = response.content
            content_hash = self.get_content_hash(content)
            if content_hash in self.downloaded_images:
                print(f"跳过重复内容: {img_url}")
                return

            # 创建保存目录
            os.makedirs(save_dir, exist_ok=True)
            
            # 从URL提取文件名
            filename = os.path.join(save_dir, img_url.split('/')[-1].split('?')[0][:100])
            
            # 保存文件
            with open(filename, 'wb') as f:
                f.write(content)
                
            # 记录已下载
            self.downloaded_images.add(img_url)
            self.downloaded_images.add(content_hash)
            print(f"成功下载: {filename}")
            
        except Exception as e:
            print(f"下载失败 {img_url}: {str(e)}")

    def crawl(self, base_url, start_page=1, end_page=10, workers=5):
        """启动爬虫"""
        page_urls = self.generate_page_urls(base_url, start_page, end_page)
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for page_url in page_urls:
                if page_url in self.visited_urls:
                    continue
                self.visited_urls.add(page_url)
                
                html = self.fetch_page(page_url)
                if not html:
                    continue
                
                img_urls = self.extract_image_urls(html, page_url)
                for img_url in img_urls:
                    executor.submit(self.download_image, img_url)

if __name__ == '__main__':
    crawler = ImageCrawler()
    
    # 示例配置（需要根据目标网站修改）
    base_url = "https://baijiahao.baidu.com/s?id=1699605419757109247？page={}"
    crawler.crawl(
        base_url=base_url,
        start_page=1,
        end_page=20,
        workers=8  # 根据网络情况调整线程数
    )
