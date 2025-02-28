import json
import os

from PIL import Image, ImageDraw


def calculate_polygon_area(points_list):
    n = len(points_list)
    if n < 3:
        return 0.0
    area = 0
    for i in range(n):
        x = points_list[i][0]
        y = points_list[i][1]
        area += x * points_list[(i + 1) % n][1] - y * points_list[(i + 1) % n][0]
    return area * 0.5


def show_point(points_list, image_name):
    image = Image.new("RGB", (100, 100), color='white')
    draw = ImageDraw.Draw(image)
    draw.line(points_list, fill="green", width=1)
    for index, point in enumerate(points_list):
        x, y, r = point[0], point[1], 2
        draw.text((x, y), str(index), fill="red")
        draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
    image.save(image_name)


def read_dirs(root):
    for dir_path, dir_names, files in os.walk(root):
        for f in files:
            file_type = os.path.splitext(f)[-1]
            if file_type.lower() == '.json':
                json_path = os.path.join(dir_path, f)
                # add_group_info(json_path)
                check_clockwise(json_path)
                # check_name(json_path)


def check_name(json_path):
    with open(json_path, encoding='utf-8') as f:
        json_data = json.load(f)
        shapes = json_data['shapes']
        len_shapes = len(shapes)
        if len_shapes % 2 == 0:
            i = 0
            while i < len_shapes:
                label_1 = shapes[i]['label']
                label_2 = shapes[i + 1]['label']
                group_id_1 = shapes[i]['group_id']
                if label_1 + '_key' != label_2:
                    if json_path not in error_dict:
                        error_dict[json_path] = [group_id_1 + '—名字不对应']
                    else:
                        error_dict[json_path].append(group_id_1 + '—名字不对应')
                i += 2
                # 0, 2, 4
        else:
            print(json_path, 'json内标签数是奇数，不成对')


def add_group_info(json_path):
    # print(json_path)
    with open(json_path, encoding='utf-8') as f:
        json_data = json.load(f)
        shapes = json_data['shapes']
        i = 1
        for shape in shapes:
            shape['group_id'] = str(i)
            shape['group_ids'] = [str(i)]
            i += 1
        write_to_json(json_path, json_data)


def write_to_json(json_path, json_data):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


def check_clockwise(json_path):
    with open(json_path, encoding='utf-8') as f:
        json_data = json.load(f)
        shapes = json_data['shapes']
        for shape in shapes:
            label = shape['label']
            point_list = shape['points']
            group_id = shape['group_id']
            if label not in not_check:
                area = calculate_polygon_area(point_list)
                if area < 0:  # 顺时针
                    print(json_path)
                    shape['points'] = point_list[0:1] + point_list[1:][::-1]
        # write_to_json(json_path, json_data)
        # f.close()
        # if json_path not in error_dict:
        #     error_dict[json_path] = [group_id + '—是顺时针']
        # else:
        #     error_dict[json_path].append(group_id + '—是顺时针')


'''
判断顺时针逆时针，是顺时针则改成逆时针，不检查人和人字梯两种。
检查名字是否对应，并将不对应的按json打印
'''
error_dict = {}
not_check = ['人_key', '人字梯_key']
root_1 = r'D:\##########\temp'
if __name__ == '__main__':
    read_dirs(root_1)
    # for k, v in error_dict.items():
    #     print(k)
    #     print(v)
