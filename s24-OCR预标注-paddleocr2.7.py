from paddleocr import PaddleOCR
import os
import cv2
import json
import numpy as np

# 整体介绍，包括文件夹内各个子文件夹的功能，配置等。
# https://wenku.baidu.com/view/4293db1513661ed9ad51f01dc281e53a580251b1.html


__all__ = ['cv2', 'imencode']
ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, det_db_thresh=0.95,
                lang="en")  # need to run only once to download and load model into memory

img_type = ['.jpg', '.png', '.bmp', '.tif', '.jpeg', '.webp', '.jfif']


def transfer_to_json(label_info, full_path, suffix):
    img_name = full_path.split('\\')[-1]
    json_full_path = full_path.replace(suffix, '.json')
    img = cv2.imdecode(np.fromfile(full_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    H, W, C = img.shape
    json_data = {'version': '1.0.0.rc1', 'flags': {}, 'shapes': [], 'imagePath': img_name,
                 'imageData': None, 'imageHeight': H, 'imageWidth': W}
    for row in label_info[0]:
        ajson = json.dumps(row, ensure_ascii=False)
        items = json.loads(ajson)
        points = items[0]
        tag_label = items[1][0]
        temp_shape = {'label': tag_label, 'labels': [tag_label], 'group_id': None, 'shape_type': 'polygon', 'flags': {},
                      'points': points}
        json_data['shapes'].append(temp_shape)
    write_to_json(json_full_path, json_data)


def write_to_json(json_path, json_data):
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)


def get_ocr_info(full_path, suffix):
    label_info = ocr.ocr(full_path, cls=True)
    if label_info[0] is not None:
        transfer_to_json(label_info, full_path, suffix)
    else:
        print('未识别', full_path)


def read_all_imgs(file_path):
    for root, dir_names, files in os.walk(file_path):
        for f in files:
            suffix = os.path.splitext(f)[-1]
            if suffix.lower() in img_type:
                img_path = os.path.join(root, f)
                get_ocr_info(img_path, suffix)


img_root = r'D:\##########\temp\examples'
if __name__ == '__main__':
    read_all_imgs(img_root)
