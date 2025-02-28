import os
import shutil

# 支持的图片文件类型
IMAGE_EXTENSIONS = ['.bmp', '.png', '.webp', '.gif', '.jpeg', '.tif', '.jpg']


def collect_files_by_name(directory, extensions):
    """
    收集指定目录下所有具有特定扩展名的文件，并按文件名（不带扩展名）进行索引。

    :param directory: 要搜索的目录
    :param extensions: 文件扩展名列表（如 ['.json'] 或图片扩展名列表）
    :return: 字典，键为文件名（不带扩展名），值为文件路径列表
    """
    file_dict = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                file_name = os.path.splitext(file)[0]
                file_path = os.path.join(root, file)
                if file_name not in file_dict:
                    file_dict[file_name] = [file_path]
                else:
                    file_dict[file_name].append(file_path)
    return file_dict


def move_files(source_dir, target_dir, match_direction='json_to_image'):
    """
    根据匹配方向，将文件从源目录复制到目标目录。

    :param source_dir: 源目录（包含 JSON 或图片文件）
    :param target_dir: 目标目录（包含图片或 JSON 文件）
    :param match_direction: 匹配方向，'json_to_image' 或 'image_to_json'
    """
    if match_direction == 'json_to_image':
        source_files = collect_files_by_name(source_dir, '.json')
        target_files = collect_files_by_name(target_dir, tuple(IMAGE_EXTENSIONS))
    elif match_direction == 'image_to_json':
        source_files = collect_files_by_name(source_dir, tuple(IMAGE_EXTENSIONS))
        target_files = collect_files_by_name(target_dir, '.json')
    else:
        raise ValueError("Invalid match_direction. Use 'json_to_image' or 'image_to_json'.")

    for file_name, source_paths in source_files.items():
        if file_name in target_files:
            for source_path in source_paths:
                source_file_name = os.path.basename(source_path)
                for target_path in target_files[file_name]:
                    target_dir_path = os.path.dirname(target_path)
                    shutil.copy2(source_path, os.path.join(target_dir_path, source_file_name))
                    print(f"已将 {source_path} 复制到 {target_dir_path}")


def get_user_input():
    """
    获取用户输入的路径和匹配方向。
    """
    print("欢迎使用文件匹配工具！")
    source_dir = input("请输入源文件夹路径（包含 JSON 或图片文件）：")
    target_dir = input("请输入目标文件夹路径（包含图片或 JSON 文件）：")

    print("\n请选择匹配方向：")
    print("1. 将 JSON 文件匹配给图片")
    print("2. 将图片匹配给 JSON 文件")
    choice = input("请输入数字选择（1 或 2）：")

    if choice == '1':
        match_direction = 'json_to_image'
    elif choice == '2':
        match_direction = 'image_to_json'
    else:
        print("输入错误，请重新运行程序并输入 1 或 2。")
        return None, None, None

    return source_dir, target_dir, match_direction


if __name__ == '__main__':
    source_dir, target_dir, match_direction = get_user_input()
    if source_dir and target_dir and match_direction:
        move_files(source_dir, target_dir, match_direction)
        print("\n文件匹配完成！")
