import json
import os
import cv2
import numpy as np

img_type_list = ['.jpg', '.bmp', '.png', '.webp', '.gif', '.jpeg', '.tif']


def get_rotate_rect(points_ori):
    box = cv2.minAreaRect(np.array(points_ori, dtype=np.int32))
    n_points = cv2.boxPoints(box).tolist()
    i = 0
    rotate_points = []
    while i < len(n_points) - 1:
        rotate_points.append(n_points[i])
        i += 1
    rotate_points.append(n_points[-1])
    return rotate_points


def rect_to_poly(points_ori):
    x2 = points_ori[1][0]
    y2 = points_ori[1][1]
    x1 = points_ori[0][0]
    y1 = points_ori[0][1]
    poly_points = [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]
    return poly_points


def read_json(full_path):
    with open(full_path, encoding='utf-8') as f:
        try:
            json_data = json.load(f)
            shapes = json_data['shapes']
            f.close()
            for shape in shapes[::-1]:
                points = shape['points']
                shape_type = shape['shape_type']
                if shape_type == 'rotaterect':
                    shape['points'] = get_rotate_rect(points)
                    shape['shape_type'] = 'polygon'
                elif shape_type == 'rectangle':
                    shape['points'] = rect_to_poly(points)
                    shape['shape_type'] = 'polygon'
            write_to_json(full_path, json_data)
        except json.decoder.JSONDecodeError:
            print('异常json', full_path)
        f.close()


def write_to_json(json_path, json_data):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


def read_path_in_dir(file_path):
    i = 0
    for root, dir_names, files in os.walk(file_path):
        for f in files:
            suffix = os.path.splitext(f)[-1]
            if suffix.lower() == '.json':
                i += 1
                full_path = os.path.join(root, f)
                # print(full_path)
                read_json(full_path)
    print('共修改json:', i)


root_1 = r'D:\##########\temp\test'
if __name__ == '__main__':
    read_path_in_dir(root_1)
