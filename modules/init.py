import config
import os
import re
import json


# Читаем значение из многомерного словаря
# Формат спаска ключей [key, ...]
def get_from_dict(data_dict, map_list) -> any:
    for k in map_list:
        data_dict = data_dict[k]
    return data_dict


# Пишем значение в многомерный словарь - если ключи существуют
# Формат спаска ключей [key, ...]
def set_in_dict(data_dict, map_list, value) -> bool:
    try:
        for k in map_list[:-1]:
            data_dict = data_dict[k]
        data_dict[map_list[-1]] = value
        return True
    except KeyError:
        return False


# Создание структуры папок по словарю, где ключ это название папки, значение это вложенный словарь с такой же структурой.
def make_dir_by_dict(data_dict, init_dir_path):
    try:
        for i in data_dict:
            if i not in os.listdir('.' + '/' + init_dir_path):
                os.makedirs(init_dir_path + i)
            make_dir_by_dict(data_dict[i], init_dir_path + i + '/')
        return True
    except FileNotFoundError:
        return False


def read_raw_fp(init_file_path, init_shift_value, init_max_nesting_level):
    # Читаем файл с отступами расположенный по пути path_to_fp.
    with open(init_file_path) as fp:
        reader = fp.read()
        elem_list = reader.split('\n')  # Делим файл на строки
    result = {}
    root_lvl_list = []
    for elem in elem_list:
        for i, shift in enumerate([fr'^{init_shift_value}{{{x}}}\w' for x in range(int(init_max_nesting_level))]):
            if re.match(shift, elem) is not None:
                try:
                    root_lvl_list[i] = elem[i:]
                except IndexError:
                    root_lvl_list.append(elem[i:])
                root_lvl_list = root_lvl_list[:i + 1]

                set_in_dict(result, root_lvl_list, {})
    return result


def run(argv):
    # TODO Обработка параметров - спрашивать у пользователя подставлять значение по умолчанию
    # или использовать ручной ввод

    # Проверяем параметры в argv из консоли, подставляем параметры по умолчанию, если чего-то не хватает
    params = {}
    existing_sub_params = config.cli_params_dict[('-i', '--init')]['sub_params']
    for existing_sub_param_key, existing_sub_param_value in existing_sub_params.items():
        for real_sub_param_key, real_sub_param_value in argv.items() \
                                                     if len(argv) > 0 \
                                                     else existing_sub_params.items():
            if real_sub_param_key in existing_sub_param_key:
                params[existing_sub_param_key[1]] = real_sub_param_value
                break
            else:
                params[existing_sub_param_key[1]] = existing_sub_param_value['default']

    # Создание каркаса дерева предметов
    data_dict = read_raw_fp(init_file_path=params['init_file_path'],
                            init_shift_value=params['init_shift_value'],
                            init_max_nesting_level=params['init_max_nesting_level'])

    # Запись в файл
    if not os.path.isdir(params['init_dir_path']):
        os.makedirs(params['init_dir_path'])

    with open(params['init_dir_path'] + params['init_file_path'].split('.')[-2] + '.json', 'w') as fp:
        json.dump(data_dict, fp)

    make_dir_by_dict(data_dict=data_dict,
                     init_dir_path=params['init_dir_path'])
