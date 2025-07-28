import os
import re

def natural_sort_key(s):
    """
    生成自然排序键，使文件名中的数字按数值大小排序
    例如：file1, file2, file10 而不是 file1, file10, file2
    """
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split(r'(\d+)', s)]

# 输入小说文件夹路径
source_dir = input("请输入文件夹的路径：")

# 获取所有文件并自然排序
all_files = sorted(os.listdir(source_dir), key=natural_sort_key)
print(f"找到 {len(all_files)} 个文件")

# 选择重命名模式
print("\n请选择重命名模式：")
print("1. 仅更改文件后缀")
print("2. 更改文件名和后缀")
choice = input("请输入选项 (1/2): ")

if choice == '1':
    # 仅更改后缀模式
    old_ext = input("请输入原文件后缀 (例如 nb): ").strip('.')
    new_ext = input("请输入新文件后缀 (例如 txt): ").strip('.')
    
    # 处理所有匹配后缀的文件
    for filename in all_files:
        if filename.endswith(f'.{old_ext}'):
            # 构建新文件名
            base_name = os.path.splitext(filename)[0]
            new_filename = f"{base_name}.{new_ext}"
            
            # 执行重命名
            old_path = os.path.join(source_dir, filename)
            new_path = os.path.join(source_dir, new_filename)
            os.rename(old_path, new_path)
            print(f"重命名: {filename} -> {new_filename}")

elif choice == '2':
    # 更改文件名和后缀模式
    old_ext = input("请输入原文件后缀 (例如 nb): ").strip('.')
    new_ext = input("请输入新文件后缀 (例如 txt): ").strip('.')
    prefix = input("请输入新文件名前缀 (例如 chapter): ")
    start_num = int(input("请输入起始编号 (例如 1): "))
    num_digits = int(input("请输入编号位数 (例如 3): "))
    
    # 创建编号格式字符串
    num_format = f"{{:0{num_digits}d}}"
    
    # 计数器
    count = 0
    
    # 处理所有匹配后缀的文件
    for filename in all_files:
        if filename.endswith(f'.{old_ext}'):
            # 生成新文件名
            new_filename = f"{prefix}{num_format.format(start_num + count)}.{new_ext}"
            
            # 执行重命名
            old_path = os.path.join(source_dir, filename)
            new_path = os.path.join(source_dir, new_filename)
            os.rename(old_path, new_path)
            print(f"重命名: {filename} -> {new_filename}")
            count += 1
    
    print(f"\n成功重命名 {count} 个文件")

else:
    print("无效选项，程序退出")

print("\n所有操作完成！")
