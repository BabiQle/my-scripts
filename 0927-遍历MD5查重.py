import hashlib
import os
import shutil

img_type = ['.jpg', '.png', '.bmp', '.tif', '.jpeg', '.webp', '.jfif']


def get_md5(full_path):
    file = open(full_path, "rb")
    md = hashlib.md5()
    md.update(file.read())
    res1 = md.hexdigest()
    file.close()
    return res1


def read_path_in_dir(file_path):
    count = 0
    for root, dir_names, files in os.walk(file_path):
        for f in files:
            suffix = os.path.splitext(f)[-1]
            if suffix.lower() in img_type:
                full_path = os.path.join(root, f)
                md5_img = get_md5(full_path)
                # md5_img = f
                if md5_img not in statistics_md5:
                    statistics_md5[md5_img] = [full_path]
                else:
                    count += 1
                    statistics_md5[md5_img].append(full_path)

    print(count)


root_1 = r'D:\##########\temp'
if __name__ == '__main__':
    statistics_md5 = {}
    read_path_in_dir(root_1)
    i = 0
    for k, v in statistics_md5.items():
        if len(v) > 1:
            i += 1
            print(v)
            # i = len(v) - 1
            # while i > 0:
            #     os.remove(v[i])
            #     i -= 1
    # print(i)