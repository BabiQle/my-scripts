import json
import os
from concurrent.futures import ThreadPoolExecutor

# 图片类型列表
img_type_list = ['.jpg', '.bmp', '.png', '.webp', '.gif', '.jpeg', '.tif']


def read_json(json_path):
    with open(json_path, encoding='utf-8') as f:
        try:
            # 读取 JSON 数据
            json_data = json.load(f)
            shapes = json_data['shapes']
            imagePath = json_data['imagePath']
            # 清空 imageData，防止文件变大
            json_data['imageData'] = None
            f.close()
            # 标记是否需要删除该 JSON 文件
            remove_flag = False
            for shape in shapes[::-1]:
                label = shape['label']
                if label in data_to_handle:
                    # 如果存在需要删除的标签，标记为需要删除
                    remove_flag = True
            if remove_flag:
                # 如果需要删除，删除对应的 JSON 文件和图片文件
                json_dir = os.path.dirname(json_path)
                img_path = os.path.join(json_dir, imagePath)
                os.remove(json_path)
                if os.path.exists(img_path):
                    os.remove(img_path)
        except json.decoder.JSONDecodeError:
            print('解析异常', json)


def read_file_get_path(root1):
    for dir_path, dir_names, files in os.walk(root1):
        for f in files:
            file_type = os.path.splitext(f)[-1]
            if file_type.lower() == '.json':
                json_path = os.path.join(dir_path, f)
                # json_path = os.path.join(dir_path, f.replace(file_type, '.json'))
                read_json(json_path)


data_to_handle = ['shanchu']  # 修改为你要删除的标签
if __name__ == '__main__':
    # 根路径
    root_1 = r'D:\##########\temp\IV4'  # 修改为你的根路径
    read_file_get_path(root_1)
