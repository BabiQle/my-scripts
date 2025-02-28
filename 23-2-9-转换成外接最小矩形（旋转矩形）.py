import json
import os
import cv2
import numpy as np

img_type_list = ['.jpg', '.bmp', '.png', '.webp', '.gif', '.jpeg', '.tif']


def is_clockwise(points):
    """
    Determine if the points are ordered in clockwise or counterclockwise direction.
    """
    area = 0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        area += (points[j][0] - points[i][0]) * (points[j][1] + points[i][1])
    return area >= 0


def get_rotate_rect(points_ori):
    box = cv2.minAreaRect(np.array([p for p in points_ori if p is not None], dtype=np.float32))
    n_points = cv2.boxPoints(box).tolist()

    clockwise = is_clockwise(points_ori)
    if clockwise:  # If original points are counterclockwise, reverse the order
        n_points = n_points[::-1]
    # Find the nearest point to the original points
    start_index = 0
    min_dist = float('inf')
    for i, p in enumerate(n_points):
        dist = sum((np.array(p) - np.array(points_ori[0])) ** 2)
        if dist < min_dist:
            min_dist = dist
            start_index = i

    # Reorder points starting from the nearest point
    n_points = n_points[start_index:] + n_points[:start_index]

    rotate_points = []

    for i in range(len(n_points)):
        rotate_points.append(n_points[i])
        next_index = (i + 1) % len(n_points)
        temp_p = [(n_points[i][0] + n_points[next_index][0]) / 2,
                  (n_points[i][1] + n_points[next_index][1]) / 2]
        rotate_points.append(temp_p)
    return rotate_points


def read_json(full_path, target_type):
    with open(full_path, encoding='utf-8') as f:
        try:
            json_data = json.load(f)
            shapes = json_data['shapes']
            for shape in shapes[::-1]:
                label = shape['label']
                points = shape['points']
                shape_type = shape['shape_type']
                if shape_type in target_type:
                    if shape_type == 'rectangle':
                        points = rect_to_polygon(points)
                    shape['points'] = get_rotate_rect(points)
                    shape['shape_type'] = 'rotaterect'
                    shape['is_rotate'] = True
            write_to_json(full_path, json_data)
        except json.decoder.JSONDecodeError:
            print('异常json', full_path)


def rect_to_polygon(r_points):
    x1, y1 = r_points[0]
    x2, y2 = r_points[1]
    x_abs = abs(x2 - x1)
    y_abs = abs(y2 - y1)
    if x_abs > y_abs:
        p_points = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
    else:
        p_points = [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]
    return p_points


def write_to_json(json_path, json_data):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


def read_path_in_dir(file_path, target_type):
    i = 0
    for root, dir_names, files in os.walk(file_path):
        for f in files:
            suffix = os.path.splitext(f)[-1]
            if suffix.lower() == '.json':
                i += 1
                full_path = os.path.join(root, f)
                # print(full_path)
                read_json(full_path, target_type)
    print('共修改json:', i)


if __name__ == '__main__':
    root_1 = r'D:\##########\temp\test\IV4'
    target_type = ['polygon', 'rectangle']  # 或者rectangle
    read_path_in_dir(root_1, target_type)
