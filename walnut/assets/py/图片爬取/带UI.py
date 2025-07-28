import os
import time
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
from PIL import ImageTk, Image
from io import BytesIO
from urllib.parse import urljoin

class ImageDownloader:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("图片下载器 v2.0")
        self.window.geometry("800x600")

        # 支持的图片格式
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        
        self.create_widgets()
        self.save_path = ""
        self.image_urls = []
        self.downloaded = 0
        self.start_time = 0
        self.total_size = 0

    def create_widgets(self):
        """创建界面控件"""
        # 路径选择
        path_frame = tk.Frame(self.window)
        path_frame.pack(pady=10)
        
        tk.Label(path_frame, text="保存路径:").pack(side=tk.LEFT)
        self.path_entry = tk.Entry(path_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(path_frame, text="选择路径", command=self.choose_path).pack(side=tk.LEFT)

        # URL输入
        tk.Label(self.window, text="网页URL:").pack()
        self.url_entry = tk.Entry(self.window, width=60)
        self.url_entry.pack(pady=5)

        # 进度显示
        progress_frame = tk.Frame(self.window)
        progress_frame.pack(pady=10)
        
        self.progress = ttk.Progressbar(progress_frame, length=500)
        self.progress.pack(side=tk.LEFT)
        
        self.speed_label = tk.Label(progress_frame, text="0 KB/s")
        self.speed_label.pack(side=tk.LEFT, padx=10)

        # 状态标签
        self.status_label = tk.Label(self.window, text="准备就绪")
        self.status_label.pack()

        # 开始按钮
        tk.Button(self.window, text="开始下载", command=self.start_download).pack()

        # 图片显示区域
        self.image_label = tk.Label(self.window)
        self.image_label.pack(pady=20)

    def choose_path(self):
        """选择保存路径"""
        self.save_path = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.save_path)

    def get_images(self, url):
        """获取网页图片链接（过滤SVG）"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img')
            valid_images = []
            for img in images:
                if 'src' in img.attrs:
                    img_url = urljoin(url, img['src'])
                    # 过滤SVG和其他不支持格式
                    if img_url.lower().endswith(self.supported_formats):
                        valid_images.append(img_url)
            return valid_images
        except Exception as e:
            return []

    def download_image(self, url):
        """下载单个图片并计算速度"""
        try:
            start_time = time.time()
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # 获取文件大小（字节）
                file_size = int(response.headers.get('content-length', 0))
                filename = os.path.join(self.save_path, url.split('/')[-1])
                
                # 记录下载数据量
                downloaded = 0
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 计算实时速度
                        elapsed = time.time() - start_time
                        speed = downloaded / elapsed / 1024 if elapsed > 0 else 0
                        self.update_speed(speed)
                
                # 显示缩略图
                img_data = requests.get(url).content
                img = Image.open(BytesIO(img_data))
                img.thumbnail((200, 200))
                photo = ImageTk.ImageTk(img)
                self.image_label.config(image=photo)
                self.image_label.image = photo
                
                self.downloaded += 1
                self.progress['value'] = (self.downloaded/len(self.image_urls))*100
                self.status_label.config(text=f"已下载 {self.downloaded}/{len(self.image_urls)}")
                self.window.update_idletasks()
        except Exception as e:
            pass

    def update_speed(self, speed):
        """更新速度显示"""
        self.speed_label.config(text=f"{speed:.1f} KB/s")
        self.window.update_idletasks()

    def start_download(self):
        """开始下载"""
        if not self.save_path:
            return
        
        url = self.url_entry.get()
        if not url.startswith('http'):
            url = 'http://' + url
        
        self.image_urls = self.get_images(url)
        if not self.image_urls:
            return
        
        self.progress['value'] = 0
        self.downloaded = 0
        self.status_label.config(text=f"开始下载 {len(self.image_urls)} 张图片")
        
        Thread(target=self.download_all_images).start()

    def download_all_images(self):
        """下载所有图片"""
        self.start_time = time.time()
        for img_url in self.image_urls:
            self.download_image(img_url)
        self.status_label.config(text="下载完成")

    def run(self):
        """运行程序"""
        self.window.mainloop()

if __name__ == "__main__":
    downloader = ImageDownloader()
    downloader.run()