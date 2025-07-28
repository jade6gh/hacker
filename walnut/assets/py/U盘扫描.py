import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ctypes
import sys

# 获取U盘路径（Windows系统）
def get_usb_drive():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if bitmask & 1:
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(f"{letter}:\\")
            if drive_type == 2:  # DRIVE_REMOVABLE
                drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives[0] if drives else None

class FileSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("jade-U盘文件搜索工具")
        self.root.geometry("800x600")
        
        # 创建界面组件
        self.create_widgets()
        self.search_path = None
        
        # 自动检测U盘
        self.auto_detect_usb()

    def create_widgets(self):
        # 路径选择框
        path_frame = ttk.Frame(self.root)
        path_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(path_frame, text="搜索路径:").pack(side=tk.LEFT)
        self.path_entry = ttk.Entry(path_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="浏览", command=self.browse_path).pack(side=tk.LEFT)

        # 搜索框
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(search_frame, text="搜索内容:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="开始搜索", command=self.start_search).pack(side=tk.LEFT)

        # 结果列表
        self.result_tree = ttk.Treeview(self.root, columns=('type', 'path'), show='headings')
        self.result_tree.heading('#0', text='文件名')
        self.result_tree.heading('type', text='类型')
        self.result_tree.heading('path', text='路径')
        self.result_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # 状态栏
        self.status = ttk.Label(self.root, text="就绪", anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定双击事件
        self.result_tree.bind("<Double-1>", self.open_file)

    def auto_detect_usb(self):
        usb_path = get_usb_drive()
        if usb_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, usb_path)
        else:
            messagebox.showwarning("警告", "未检测到U盘，请手动选择路径！")

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def start_search(self):
        keyword = self.search_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if not keyword or not path:
            messagebox.showwarning("警告", "请先输入搜索内容和选择路径！")
            return

        # 清空结果列表
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        # 开始搜索
        self.status.config(text="正在搜索...")
        self.root.update()
        
        try:
            count = 0
            for root_dir, dirs, files in os.walk(path):
                # 搜索目录名
                if keyword in os.path.basename(root_dir):
                    self.result_tree.insert('', 'end', text=os.path.basename(root_dir), 
                                           values=('文件夹', root_dir))
                    count += 1
                
                # 搜索文件名
                for file in files:
                    if keyword in file:
                        full_path = os.path.join(root_dir, file)
                        self.result_tree.insert('', 'end', text=file,
                                              values=('文件', full_path))
                        count += 1
                    
                    # 搜索文件内容（仅限文本文件）
                    if file.lower().endswith(('.txt', '.md', '.csv')):
                        full_path = os.path.join(root_dir, file)
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if keyword in content:
                                    self.result_tree.insert('', 'end', text=file,
                                                          values=('内容匹配', full_path))
                                    count += 1
                        except:
                            continue
            
            self.status.config(text=f"搜索完成，找到 {count} 个结果")
        except Exception as e:
            messagebox.showerror("错误", f"搜索过程中发生错误：{str(e)}")

    def open_file(self, event):
        item = self.result_tree.selection()[0]
        path = self.result_tree.item(item, 'values')[1]
        
        if os.path.isfile(path):
            try:
                os.startfile(path)
            except:
                os.startfile(os.path.dirname(path))
        elif os.path.isdir(path):
            os.startfile(path)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchApp(root)
    root.mainloop()
