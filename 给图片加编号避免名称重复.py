import os
import json
import shutil
import numpy as np
from PIL import Image
import natsort
import time
import random
import pprint

img_type_list = ['.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif', '.tiff', '.webp']


def read_path_in_dir(file_path):
    i = 1
    for dir_path, dir_names, files in os.walk(file_path):
        sorted_files = natsort.os_sorted(files)
        for f in sorted_files:
            suffix = os.path.splitext(f)[1]
            if suffix.lower() in img_type_list:
                img_path = os.path.join(dir_path, f)
                # new_img_name = str(i) + '_____' + f
                new_img_name = f.split('_____')[1]
                i += 1
                new_img_path = os.path.join(dir_path, new_img_name)
                os.rename(img_path, new_img_path)
                json_path = os.path.join(dir_path, os.path.splitext(f)[0] + '.json')
                if os.path.exists(json_path):
                # # print(json_path)
                    new_json_path = os.path.join(dir_path, os.path.splitext(new_img_name)[0] + '.json')
                    os.rename(json_path, new_json_path)
                    modify_json(new_json_path, new_img_name)
                # else:
                #     modify_json(json_path, new_img_name)


def modify_json(json_path, new_img_name):
    with open(json_path, encoding='utf-8') as f:
        json_data = json.load(f)
        json_data['imageData'] = None
        json_data['imagePath'] = new_img_name
        write_to_json(json_path, json_data)


def write_to_json(json_path, json_data):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


root_1 = r'D:\##########\temp\IV4'
if __name__ == '__main__':
    read_path_in_dir(root_1)
