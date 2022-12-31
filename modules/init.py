import shutil
import config
import os
import re
import json


# todo добавить в каждую конечную папку(предмет) папку с названием "prepared material"

# todo добавить модуль calculate_progress для пересчёта прогресса
# todo добавить модуль selection для выбора предмета для изучения сегодня

# Читаем значение из многомерного словаря
# Формат спаска ключей [key, ...]
def get_from_dict(data_dict, map_list) -> any:
    for k in map_list:
        data_dict = data_dict[k]
    return data_dict


# Пишем значение в многомерный словарь - если ключи существуют
# Формат списка ключей [key, ...]
def set_in_dict(data_dict, map_list, value):
        for k in map_list[:-1]:
            data_dict = data_dict[k]
        data_dict[map_list[-1]] = value


# Создание структуры папок по словарю, где ключ это название папки, значение это вложенный словарь с такой же структурой.
def make_dir_by_dict(data_dict, init_dir_path):
    for i in data_dict:
        if i not in os.listdir('.' + '/' + init_dir_path):
            os.makedirs(init_dir_path + i)
        make_dir_by_dict(data_dict[i], init_dir_path + i + '/')


def furnishing_frame(dir_path, file_name, json_data, list_lower_lvl_dirs=()):
    # Создаём файл file_name если папка не попадает под исключения
    current_dir_name = dir_path.split('/')[-2]
    if current_dir_name not in config.exception_dirs:
        json.dump(json_data, open(dir_path + file_name, 'w'))

    # Получаем все папки не попавшие в исключения
    list_dir = [dir_name for dir_name in os.listdir(dir_path) if '.' not in dir_name and dir_name not in config.exception_dirs]

    # Если это конечная папка, создаём в ней список папок самого нижнего уровня
    if len(list_dir) == 0:
        for list_lower_lvl_dir in list_lower_lvl_dirs:
                os.makedirs(dir_path + list_lower_lvl_dir)

    # Рекурсивно проходим по всем папкам в каркасе
    for dir_name in list_dir:
        furnishing_frame(dir_path + dir_name + '/', file_name, json_data, list_lower_lvl_dirs)


def read_raw_fp(init_file_path, init_shift_value):
    # Читаем файл с отступами расположенный по пути path_to_fp.
    with open(init_file_path) as fp:
        header = fp.readline().rstrip('\n').split(init_shift_value)
        body = fp.read()
        elem_list = body.split('\n')  # Делим файл на строки
    result = {'header': header,
              'body': {}}
    root_lvl_list = []
    for elem in elem_list:
        for i, shift in enumerate([fr'^{init_shift_value}{{{x}}}\w' for x in range(len(header))]):
            if re.match(shift, elem) is not None:
                try:
                    root_lvl_list[i] = elem[i:]
                except IndexError:
                    root_lvl_list.append(elem[i:])
                root_lvl_list = root_lvl_list[:i + 1]

                set_in_dict(result['body'], root_lvl_list, {})
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
    params['source_path'] = params['init_dir_path'] + config.source_dir + '/'

    # Создание каркаса дерева предметов
    data_dict = read_raw_fp(init_file_path=params['init_file_path'],
                            init_shift_value=params['init_shift_value'])

    # Создание папки для каркаса
    if os.path.isdir(params['init_dir_path']):  # Если папка была создана
        shutil.rmtree(params['init_dir_path'])
    if not os.path.isdir(params['init_dir_path']):
        os.makedirs(params['source_path'])


    # Запись в json файла для каркаса
    with open(params['source_path'] + params['init_file_path'].split('.')[-2] + '.json', 'w') as fp:
        json.dump(data_dict, fp)

    make_dir_by_dict(data_dict=data_dict['body'],
                     init_dir_path=params['init_dir_path'])

    furnishing_frame(dir_path=params['init_dir_path'],
                     file_name='progress.json',
                     json_data=config.progress_file_data,
                     list_lower_lvl_dirs=config.default_list_lower_lvl_dirs)
