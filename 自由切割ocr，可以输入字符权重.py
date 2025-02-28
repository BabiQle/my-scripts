import json
import math
import os
from shapely.geometry import LineString

# 可以切割的形状类型
cut_shape_types = ['polygon', 'rotaterect', 'rectangle']


def calculate_distance(p1, p2):
    # 计算两点之间的距离
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def calculate_angle(p1, p2, p3):
    # 计算三点之间的夹角
    vector1 = (p1[0] - p2[0], p1[1] - p2[1])
    vector2 = (p3[0] - p2[0], p3[1] - p2[1])
    magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
    magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

    if magnitude1 == 0 or magnitude2 == 0:
        return 0  # 如果模长为零，角度无法计算，返回0度

    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    cosine_angle = dot_product / (magnitude1 * magnitude2)

    cosine_angle = max(min(cosine_angle, 1.0), -1.0)  # 处理余弦值超出范围的情况
    angle = math.degrees(math.acos(cosine_angle))
    return angle


def find_rectangle_vertices(points):
    # 找到长方形的四个顶点
    vertices = []
    for i in range(len(points)):
        point_1 = points[i]
        point_2 = points[(i + 1) % len(points)]
        point_3 = points[(i + 2) % len(points)]
        angle = calculate_angle(point_1, point_2, point_3)
        if angle < 150:
            vertices.append([(i + 1) % len(points), point_2])
    return vertices


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


def find_longest_distances_index_list(vertices, ori_points):
    fld_dict = {}
    # 找到距离最长的两组点,并补充完整line的其他点序号
    for i in range(len(vertices)):
        index_1 = vertices[i][0]
        index_2 = vertices[(i + 1) % len(vertices)][0]
        coordinate_1 = vertices[i][1]
        coordinate_2 = vertices[(i + 1) % len(vertices)][1]
        len_p = calculate_distance(coordinate_1, coordinate_2)
        fld_dict[(index_1, index_2)] = len_p
    sorted_dict = dict(sorted(fld_dict.items(), key=lambda x: x[1], reverse=True))
    keys = list(sorted_dict.keys())
    first_key = keys[0]
    second_key = keys[1]
    longest_1 = find_consecutive_indices(first_key, ori_points)
    longest_2 = find_consecutive_indices(second_key, ori_points)
    if longest_1[0] > longest_2[0]:
        longest_1, longest_2 = longest_2, longest_1

    if 0 in longest_2 and longest_2[-1] != 0:  # 确保0为首的长边是line1，这样字符顺序不错。
        longest_1, longest_2 = longest_2, longest_1
    return longest_1, longest_2


def find_consecutive_indices(indices, ori_points):
    # 找到一组索引中的连续整数
    n, m = indices
    if m >= n:
        my_list = list(range(n, m + 1))
    else:
        m_special = len(ori_points) - 1
        my_list = list(range(n, m_special + 1)) + list(range(0, m + 1))
    return my_list


def indices_to_points(index_list, index_points):
    # 将索引转换为点，不排序
    points = [index_points[it] for it in index_list]
    return points


def deal_with_json(json_path):
    # 读取JSON文件并处理
    with open(json_path, encoding='utf-8') as f:
        big_char_dict = {
            'A': 1, 'B': 1, 'C': 1, 'D': 1, 'E': 1,
            'F': 1, 'G': 1, 'H': 1, 'I': 1, 'J': 1,
            'K': 1, 'L': 1, 'M': 1, 'N': 1, 'O': 1,
            'P': 1, 'Q': 1, 'R': 1, 'S': 1, 'T': 1,
            'U': 1, 'V': 1, 'W': 1, 'X': 1, 'Y': 1,
            'Z': 1, '1': 0.8, '9': 1, ' ': 0.3, '2': 1,
            '3': 1, '4': 1, '5': 1, '6': 1, '7': 1,
            '8': 1, '0': 1,
            'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1,
            'f': 1, 'g': 1, 'h': 1, 'i': 1, 'j': 1,
            'k': 1, 'l': 1, 'm': 1, 'n': 1, 'o': 1,
            'p': 1, 'q': 1, 'r': 1, 's': 1, 't': 1,
            'u': 1, 'v': 1, 'w': 1, 'x': 1, 'y': 1,
            'z': 1, '.': 1, '/': 1, '-': 1, '(': 0.5, ')': 0.5, '@': 1.4
        }

        temp_list = []
        json_data = json.load(f)
        shapes = json_data['shapes']
        for shape in shapes:
            shape_type = shape['shape_type']
            label = shape['label']
            points = shape['points']
            if shape_type in cut_shape_types:
                if shape_type == 'rectangle':  # 转换方框的点坐标，支持后面计算
                    points = rect_to_polygon(points)
                four_top_points_dict = find_rectangle_vertices(points)  # 找到顶点的序号和对应的坐标
                # print(four_top_points_dict)
                indices_list_1, indices_list_2 = find_longest_distances_index_list(
                    four_top_points_dict, points)  # 根据顶点坐标算成最长边，并找到最长边的坐标序号列表。
                # print(indices_list_1)
                # print(indices_list_2)
                line_1 = indices_to_points(indices_list_1, points)  # indices_to_points，不排序
                line_2 = indices_to_points(indices_list_2, points)  # indices_to_points，不排序
                # print(line_1)
                # print(line_2)
                temp_list.extend(split_lines(line_1, line_2, label, big_char_dict))  # 分割line组合成要的多边形
            else:
                temp_list.extend(shape)  # 不是line的也加进去，不然非line的框会消失
        json_data['shapes'] = temp_list
        write_to_json(json_path, json_data)


def write_to_json(json_path, json_data):
    # 将JSON数据写回文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


def split_line_points_with_weights(points_t_s, labels_t_s, char_weights):
    # 创建 Shapely 折线对象
    line = LineString(points_t_s)
    total_length = line.length
    # 计算总权重
    total_weight = sum(char_weights.get(char, 1) for char in labels_t_s)
    split_points = []
    accumulated_length = 0
    for char in labels_t_s:
        char_length = (char_weights.get(char, 1) / total_weight) * total_length
        accumulated_length += char_length
        split_points.append(line.interpolate(accumulated_length))
    # 将折线切割成N段
    split_n_lines = [LineString([point1, point2]) for point1, point2 in
                     zip([line.coords[0]] + split_points, split_points)]
    return split_n_lines


# 在split_lines函数中，不再需要计算char_list
def split_lines(line_1, line_2, labels_t_s, char_weights):
    temp_shapes = []
    char_list = list(labels_t_s)

    if line_1[0][0] < line_1[1][0]:
        line_2 = sorted(line_2, key=lambda x: x[0])
    else:
        line_2 = sorted(line_2, key=lambda x: x[0], reverse=True)
    # print(line_1)
    # print(line_2)
    split_lines_1 = split_line_points_with_weights(line_1, labels_t_s, char_weights)
    split_lines_2 = split_line_points_with_weights(line_2, labels_t_s, char_weights)
    for i, split_line in enumerate(split_lines_1):
        points_temp_1 = list(split_line.coords)
        points_temp_2 = list(split_lines_2[i].coords)
        result_list = points_temp_1 + [points_temp_2[1], points_temp_2[0]]
        label = char_list[i]
        temp_dict = {
            "label": label,
            "labels": [label],
            "shape_type": "polygon",
            "image_name": None,
            "mask": None,
            "points": result_list,
            "group_id": None,
            "group_ids": [None],
            "annotator": {},
            "flags": {}
        }
        temp_shapes.append(temp_dict)
    return temp_shapes


def read_file_get_paths(file_path):
    # 递归遍历文件夹并处理JSON文件
    for dir_path, dir_names, files in os.walk(file_path):
        for f in files:
            file_type = os.path.splitext(f)[1]
            if file_type.lower() == '.json':
                json_path = os.path.join(dir_path, f)
                deal_with_json(json_path)


if __name__ == '__main__':
    root_directory = r'D:\##########\temp\examples\新建文件夹 (9)'
    read_file_get_paths(root_directory)
