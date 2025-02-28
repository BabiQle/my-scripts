import hashlib
import os
import shutil


def read_path_in_dir(file_path):
    files_set = set()
    for root, dir_names, files in os.walk(file_path):
        for f in files:
            # full_path = os.path.join(root, f)
            if f not in files_set:
                files_set.add(f)
            else:
                print(f)


root_1 = r'D:\##########\temp'
if __name__ == '__main__':
    read_path_in_dir(root_1)
