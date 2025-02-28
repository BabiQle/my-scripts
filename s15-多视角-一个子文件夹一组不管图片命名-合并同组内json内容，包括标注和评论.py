import os
import json
from pathlib import Path
import natsort
import timeit

img_type_set = ('.jpg', '.bmp', '.png', '.webp', '.gif', '.jpeg', '.tif')


def produce_mutl_json(root_dir, json_path):
    # 存储所有图像文件路径的字典
    image_paths = {}
    # 递归遍历所有目录和文件
    for root, dirs, files in os.walk(root_dir):
        '''
        以下确认如何排序，以决定多视角组图如何排列。
        '''
        # print(files)
        filtered_files = [f for f in files if f.lower().endswith(img_type_set)]
        # sorted_files = sorted(filtered_files, key=lambda f: f.split('_')[4].split('-')[-1], reverse=True)
        # sorted_files = natsort.os_sorted(files)
        for file in filtered_files:
            # print(file.split('_')[7])
            suffix = os.path.splitext(file)[1]
            if suffix.lower() in img_type_set:
                file_path = Path(root) / file  # 总路径
                _, new_path = os.path.splitdrive(str(file_path))
                dir_check = os.path.dirname(new_path)

                # 如果该目录中没有记录过第一张图像文件的路径，则将其作为键，将空列表作为值
                if any(dir_check in k for k in image_paths.keys()):
                    for key in image_paths.keys():
                        if dir_check in key:  # 用dir_check去判断合并同一个文件夹的图片
                            image_paths[key]['otherwords'].append(str(file_path))
                            break
                else:
                    image_paths[str(file_path)] = {'otherwords': []}

    # 将图像路径字典写入JSON文件
    write_to_json(json_path, image_paths)
    return image_paths


def image_to_json(image_path):
    path_without_extension, _ = os.path.splitext(image_path)
    json_one_p = path_without_extension + ".json"
    return json_one_p


def merge_json_files(image_paths):
    for key, value in image_paths.items():
        json_one_p = image_to_json(key)
        merged_json = {"shapes": [], "comments": []}
        existing_json = None
        # 检查 json_one_p 是否存在
        if Path(json_one_p).exists():
            with open(json_one_p, "r", encoding="utf-8") as openfile:
                existing_json = json.load(openfile)

        found_data = False
        for other_img in value['otherwords']:
            other_json_p = image_to_json(other_img)
            if Path(other_json_p).exists():
                if existing_json is None:
                    with open(other_json_p, "r", encoding="utf-8") as openfile:
                        existing_json = json.load(openfile)
                        existing_json["imagePath"] = key.split('\\')[-1]
                        existing_json["imageMd5"] = None
                        existing_json["shapes"] = []
                        existing_json["comments"] = []

                with open(other_json_p, "r", encoding="utf-8") as openfile:
                    data = json.load(openfile)
                    merged_json["shapes"].extend(data.get("shapes", []))
                    merged_json["comments"].extend(data.get("comments", []))
                    found_data = True
                Path(other_json_p).unlink()  # 删除文件

        if found_data:
            existing_json["shapes"].extend(merged_json["shapes"])
            existing_json["comments"].extend(merged_json["comments"])
            write_to_json(json_one_p, existing_json)


def write_to_json(json_file_path, json_data):
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


'''
因为初始生成的多视角用的是完整带盘符路径，所以这里去除一下盘符，所有人都可以同路径打开，直接生成不带盘符的有点问题，所以绕一下。
'''


def remove_drive_from_dict_paths(json_p):
    with open(json_p, 'r', encoding='utf-8') as f:
        data = json.load(f)
        new_data = {}
        for key, value in data.items():
            # 去除 key 的盘符
            _, key_without_drive = os.path.splitdrive(key)

            # 去除 value['otherwords'] 列表中所有路径的盘符
            otherwords_without_drive = []
            for path in value['otherwords']:
                _, path_without_drive = os.path.splitdrive(path)
                otherwords_without_drive.append(path_without_drive)

            # 添加到新的字典中
            new_data[key_without_drive] = {'otherwords': otherwords_without_drive}
    write_to_json(json_p, new_data)


def check_futu_shuliang(json_path, correct_img_nums):
    try:
        with open(json_path, encoding='utf-8') as f:
            json_data = json.load(f)
            all_correct = True  # 标记是否所有条目都符合要求
            filtered_data = {k: v for k, v in json_data.items() if len(v["otherwords"]) == correct_img_nums}
            for k, v in json_data.items():
                if 'Station3' not in k:
                    len_s = len(v.get('otherwords', []))  # 使用get()避免KeyError
                    if len_s != correct_img_nums:
                        print(f"{k} 期望图像数量: {correct_img_nums} 实际图像数量: {len_s}")
                        all_correct = False
            # write_to_json(json_path, filtered_data)
            return all_correct
    except Exception as e:
        print(f"Error processing {json_path}: {e}")
        return False  # 返回False表示有错误


def main_function():
    root_all = r'D:\##########\temp'
    '''
    1. 按sorted排序后的首位图片为主图，其余为幅图，如果要限定某张图片为主图，且这张图片可能不是排序第一张，要修改脚本。
    2. 合并子文件夹内所有json，合并包括标注信息和备注信息。
    3. 删除幅图json 
    4. 只适用于子文件夹是一组图的情况，其他匹配多视角的方式不能用。
    '''
    # 获取root_all路径下所有子文件夹的名称
    dir_names = next(os.walk(root_all))[1]
    for dir_name in dir_names:
        root_dir = os.path.join(root_all, dir_name)
        json_p = os.path.join(root_all, dir_name + '.json')
        # 生成多视角
        image_paths = produce_mutl_json(root_dir, json_p)
        # print(f'已经生成：{json_p}')
        merge_json_files(image_paths)
        remove_drive_from_dict_paths(json_p)
        print(f'已经合并多视角内部json：{json_p}')


elapsed_time = timeit.timeit(main_function, number=1)
print(f"程序运行时间: {elapsed_time}秒")
