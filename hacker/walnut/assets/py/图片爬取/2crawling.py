import os
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin
from colorama import Fore, init

# 初始化彩色终端
init(autoreset=True)

class HackerCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bing.com/'
        }
        self.save_path = os.path.join(os.getcwd(), 'CyberWallpapers')
        os.makedirs(self.save_path, exist_ok=True)
        
        # 风格界面
        print(Fore.GREEN + r"""
         _____       _      ______ _           _    
        |  __ \     | |    |  ____| |         | |   
        | |__) |   _| | ___| |__  | | __ _ ___| | __
        |  ___/ | | | |/ _ \  __| | |/ _` / __| |/ /
        | |  | |_| | |  __/ |    | | (_| \__ \   < 
        |_|   \__,_|_|\___|_|    |_|\__,_|___/_|\_\
        """)
        print(Fore.CYAN + "\n[+] 初始化量子爬虫引擎...")
        print(Fore.YELLOW + f"[!] 存储路径已加密至: {self.save_path}\n")

    def get_links(self, base_url, max_depth=3):
        """获取图片链接，支持深度爬取"""
        image_links = []
        current_page = 1
        
        with tqdm(total=max_depth, desc=Fore.MAGENTA + "深度扫描进度", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)) as pbar:
            while current_page <= max_depth:
                try:
                    # 模拟分页参数
                    url = f"{base_url}/page/{current_page}"
                    response = requests.get(url, headers=self.headers, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 查找图片链接（根据实际网站结构调整）
                    for img in soup.find_all('img'):
                        img_url = img.get('src')
                        if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg']):
                            full_url = urljoin(base_url, img_url)
                            image_links.append(full_url)
                    
                    current_page += 1
                    pbar.update(1)
                    time.sleep(1)  # 防止触发反爬
                except Exception as e:
                    print(Fore.RED + f"\n[!] 量子隧道中断: {str(e)}")
                    break
        return image_links

    def download_images(self, urls):
        """下载图片并显示进度"""
        total = len(urls)
        print(Fore.CYAN + f"\n[+] 发现{total}个数字艺术品...")
        
        with tqdm(total=total, desc=Fore.BLUE + "下载进度", unit="img", 
                 bar_format="{l_bar}%s{bar}%s| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]" % (Fore.GREEN, Fore.RESET)) as pbar:
            for idx, url in enumerate(urls, 1):
                try:
                    start_time = time.time()
                    response = requests.get(url, headers=self.headers, stream=True, timeout=15)
                    file_name = os.path.join(self.save_path, f"cyber_{int(time.time())}.jpg")
                    
                    # 计算下载速度
                    file_size = int(response.headers.get('content-length', 0))
                    chunk_size = 1024
                    
                    with open(file_name, 'wb') as f:
                        for data in response.iter_content(chunk_size):
                            f.write(data)
                            speed = chunk_size / (time.time() - start_time + 1e-9)
                            pbar.set_postfix_str(f"{speed/1024:.1f}KB/s")
                    
                    pbar.update(1)
                    time.sleep(0.5)  # 限速防止封禁
                except Exception as e:
                    print(Fore.RED + f"\n[!] 下载失败: {str(e)}")
                    continue

if __name__ == "__main__":
    # 使用示例（请替换实际壁纸网站URL）
    crawler = HackerCrawler()
    target_url = "https://www.bilibili.com/opus/847402368983105569/?from=readlist"  # 替换为真实网址
    
    print(Fore.YELLOW + "[!] 启动反爬虫规避协议...")
    image_urls = crawler.get_links(target_url, max_depth=2)
    
    if image_urls:
        crawler.download_images(image_urls)
        print(Fore.GREEN + "\n[+] 所有数字艺术品已安全存储至母舰！")
    else:
        print(Fore.RED + "\n[!] 未检测到可用数字资源")
