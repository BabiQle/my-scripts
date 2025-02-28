import os
import random
import shutil


def select_random_images_and_json(folder_path, n):
    # 获取文件夹中的所有文件
    files = os.listdir(folder_path)

    # 筛选出图像和 JSON 文件
    image_files = [f for f in files if f.endswith('.jpg') or f.endswith('.png')]
    json_files = [f for f in files if f.endswith('.json')]

    # 随机选择 n 个文件
    selected_image_files = random.sample(image_files, n)

    # 筛选出对应的 JSON 文件
    selected_json_files = [f.replace('.jpg', '.json').replace('.png', '.json') for f in selected_image_files]

    # 将选中的文件复制到新文件夹
    output_folder = r"D:\##########\temp\selected_files"
    os.makedirs(output_folder, exist_ok=True)
    for image_file, json_file in zip(selected_image_files, selected_json_files):
        shutil.copy2(os.path.join(folder_path, image_file), os.path.join(output_folder, image_file))
        shutil.copy2(os.path.join(folder_path, json_file), os.path.join(output_folder, json_file))
        print(os.path.join(output_folder, image_file))
    print(f"{n} 个图像和对应的 JSON 文件已被随机选中并复制到 '{output_folder}' 文件夹。")


# 指定文件夹路径和要选择的文件数
root_all = r"D:\##########\temp\药片_100"
num_files_to_select = 50

# 获取root_all路径下所有子文件夹的名称
dir_names = next(os.walk(root_all))[1]
# 找子文件夹名称
for dir_name in dir_names:
    folder_path = os.path.join(root_all, dir_name)
    select_random_images_and_json(folder_path, num_files_to_select)
