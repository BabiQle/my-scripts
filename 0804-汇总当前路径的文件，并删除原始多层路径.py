import os
import shutil

file_type_list = ['.jpg', '.bmp', '.png', '.webp', '.gif', '.jpeg', '.json']


def remove_all_child_dir(file_path):
    for root, dirs, files in os.walk(file_path):
        for file in files:
            suffix = os.path.splitext(file)[-1]
            if suffix.lower() in file_type_list:
                old_path = os.path.join(root, file)
                new_path = os.path.join(file_path, file)
                if old_path != new_path:
                    if not os.path.exists(new_path):
                        shutil.move(old_path, new_path)
                    else:
                        print('有重复名称图片')


def remove_dir(root):
    dir_list = [dI for dI in os.listdir(root) if os.path.isdir(os.path.join(root, dI))]
    for dir_it in dir_list:
        dir_path = os.path.join(root, dir_it)
        shutil.rmtree(dir_path)


root_1 = r'D:\##########\temp\IV4'  # 如果不确定图片名称是否有重复，不能用！
if __name__ == '__main__':
    remove_all_child_dir(root_1)
    remove_dir(root_1)
