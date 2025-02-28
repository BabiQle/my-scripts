import json
import os
import re
import math
import xlsxwriter as xw
import natsort


def calculate_triangle_area(point_a, point_b, point_c):
    return 0.5 * ((point_b[0] - point_a[0]) * (point_c[1] - point_a[1]) -
                  (point_b[1] - point_a[1]) * (point_c[0] - point_a[0]))


# 将矩形转换为多边形
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


def process_json(json_path, N):
    with open(json_path, encoding='utf-8') as f:
        json_data = json.load(f)

    shapes = json_data.get('shapes', [])
    # print(N*1.5)
    for shape in shapes[::-1]:
        label = shape['label']
        points = shape['points']
        shape_type = shape['shape_type']
        if shape_type == 'rectangle':
            points = rect_to_polygon(points)
        polygon_area = abs(sum(calculate_triangle_area(points[0], points[i], points[i + 1])
                               for i in range(1, len(points) - 1)))
        shape['label'] = shape['label'] + '_' + str(polygon_area)
        # print(polygon_area)
        # if polygon_area < 3000:
        #     #     shape['label'] = '完整椭圆片'
        #     # else:
        #     #     shape['label'] = '不完整椭圆片'
        #     # if polygon_area < 400:
        #     #     # print(1)
        #     print(polygon_area)
        #     shapes.remove(shape)

    write_to_json(json_path, json_data)


def write_to_json(json_path, json_data):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


def process_directory(root_directory, N):
    for dir_path, dir_names, files in os.walk(root_directory):
        sorted_files = natsort.os_sorted(files)
        for filename in sorted_files:
            if filename.lower().endswith('.json'):
                json_path = os.path.join(dir_path, filename)
                process_json(json_path, N)


if __name__ == "__main__":
    root_directory = r'D:\##########\temp\完成\IV4'
    N = 18500
    process_directory(root_directory, N)
