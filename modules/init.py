# локальные пакеты
import config
from . import STL

# общие пакеты
import datetime
import shutil
import os
import re
import json

from . import sqltools


# TODO Добавить sqllite для работы с данными


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
        data_dict = data_dict.setdefault(k, {})
    data_dict[map_list[-1]] = value


# Создание структуры папок по словарю, где ключ это название папки, значение это вложенный словарь с такой же структурой.
def make_dir_by_dict(data_dict, init_dir_path):
    for i in data_dict:
        if i not in os.listdir('.' + '/' + init_dir_path):
            os.makedirs(init_dir_path + i)
        make_dir_by_dict(data_dict[i], init_dir_path + i + '/')


def furnishing_frame(dir_path, file_name, source_path, project_name, list_lower_lvl_dirs=()):
    json_data = json.load(open(source_path + project_name + '.json'))['options']

    # Создаём файл file_name если папка не попадает под исключения
    current_dir_name = dir_path.split('/')[-2]
    current_json_data_key = '/'.join(dir_path.split('/')[2:])
    if current_dir_name not in config.exception_dirs and current_json_data_key != '':
        json.dump(json_data[current_json_data_key], open(dir_path + file_name, 'w'))

    # Получаем все папки не попавшие в исключения
    list_dir = [dir_name for dir_name in os.listdir(dir_path) if not os.path.isfile(dir_path + dir_name) and dir_name not in config.exception_dirs]

    # Если это конечная папка, создаём в ней список папок самого нижнего уровня
    if len(list_dir) == 0:
        for list_lower_lvl_dir in list_lower_lvl_dirs:
            os.makedirs(dir_path + list_lower_lvl_dir)

    # Рекурсивно проходим по всем папкам в каркасе
    for dir_name in list_dir:
        furnishing_frame(dir_path + dir_name + '/', file_name, source_path, project_name, list_lower_lvl_dirs)


def prepare_data(raw_data) -> dict:
    result = {}
    lvl_relation = raw_data['lvl_relation']
    dependencies = raw_data['dependencies']
    options = raw_data['options']
    for lvl_name, elements in lvl_relation.items():
        result[lvl_name] = []
        for option_name, option_value in options.items():
            if option_value['name'] in elements:
                if option_name in dependencies.keys():
                    option_value['dependence'] = True
                    option_value['general_element_path'] = dependencies[option_name]
                else:
                    option_value['dependence'] = False

                result[lvl_name].append(option_value)

    return result


def read_raw_fp(init_file_path, init_shift_value, init_separation_value, init_option_start_value, init_option_end_value):
    # Читаем файл с отступами расположенный по пути path_to_fp.
    with open(init_file_path) as fp:
        header = fp.readline().rstrip('\n').split(init_shift_value)
        body = fp.read()
        elem_list = body.split('\n')  # Делим файл на строки
    result = {'header': header,
              'body': {},
              'lvl_relation': {x: [] for x in header},
              'dependencies': {},
              'options': {}}
    root_lvl_list = []
    for elem in elem_list:
        for i, shift in enumerate([fr'^{init_shift_value}{{{x}}}\w' for x in range(len(header))]):
            root_lvl_path = '/'.join(root_lvl_list[:i]) + '/' if len(root_lvl_list[:i]) > 0 else ''
            if re.match(shift, elem) is not None:

                # Получение дополнительных настроек (options)
                options_pattern = fr"{init_option_start_value}(.*){init_option_end_value}$"
                options = []
                if re.match('.*'+options_pattern, elem) is not None:
                    options = re.search(options_pattern, elem).group()
                    options = re.sub(init_option_start_value + '|' + init_option_end_value, '', options).split(',')
                elem = re.sub(options_pattern, '', elem).strip(' ')

                # Получение зависимостей
                if re.match(fr".*{init_separation_value}.*", elem) is not None:
                    elem_list = elem.split(init_separation_value)
                    elem, general_elem = elem_list
                    result['dependencies'][root_lvl_path + elem[i:] + '/'] = root_lvl_path + general_elem + '/'

                # Запись дополнительных настроек в result['options']
                elem_path = root_lvl_path + re.sub(options_pattern, '', elem[i:]).strip(' ') + '/'
                result['options'][elem_path] = {'name': elem[i:]}
                for exist_option, exist_options_value in config.cli_params_dict[('-i', '--init')]['options'].items():
                    result['options'][elem_path][exist_option] = exist_options_value['default']
                    for option in options:
                        option_name, option_value = option.split(':')
                        if str(option_name).strip(' ') in exist_option:
                            if option_value.lower() in ('true', 'false'):
                                option_value = bool(option_value)
                            elif re.match(r'^\-?[1-9][0-9]*(\.[0-9]+)?$|^[\-]?[0-9](\.[0-9]+)?$', option_value):
                                option_value = float(option_value)
                            result['options'][elem_path][exist_option] = option_value

                # Пишем расчётные поля в options
                score = STL.compute_score(importance=result['options'][elem_path]['importance'],
                                          hours_spent=result['options'][elem_path]['hours_spent'],
                                          required_number_of_hours=result['options'][elem_path]['required_number_of_hours'])

                try: result['options'][elem_path]['parent_name'] = elem_path.split('/')[-3]
                except IndexError: result['options'][elem_path]['parent_name'] = None

                result['options'][elem_path]['element_path'] = elem_path
                result['options'][elem_path]['score'] = score

                # Добавляем системные поля create/update_time/by
                result['options'][elem_path]['create_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
                result['options'][elem_path]['create_by'] = 'system'
                result['options'][elem_path]['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
                result['options'][elem_path]['update_by'] = 'system'

                # определяем вложенность
                try:
                    root_lvl_list[i] = elem[i:]
                except IndexError:
                    root_lvl_list.append(elem[i:])
                result['lvl_relation'][result['header'][i]].append(root_lvl_list[i])
                root_lvl_list = root_lvl_list[:i + 1]
                set_in_dict(result['body'], root_lvl_list, {})
    return result


def run(argv, main_cli_param):
    # TODO Обработка параметров - спрашивать у пользователя подставлять значение по умолчанию или использовать ручной ввод

    # Проверяем параметры в argv из консоли, подставляем параметры по умолчанию, если чего-то не хватает
    params = STL.get_params(argv, main_cli_param)

    # Записываем системных параметры, не изменяемые пользователем
    params['source_path'] = params['init_dir_path'] + config.source_dir + '/'
    params['project_name'] = params['init_dir_path'].split('/')[-2]

    # Создание каркаса дерева предметов
    data_dict = read_raw_fp(init_file_path=params['init_file_path'],
                            init_shift_value=params['init_offset_value'],
                            init_separation_value=params['init_separation_value'],
                            init_option_start_value=params['init_option_start_value'],
                            init_option_end_value=params['init_option_end_value'])

    # Создание папки для каркаса - Только папки
    if os.path.isdir(params['init_dir_path']):  # Если папка была создана
        shutil.rmtree(params['init_dir_path'])
    if not os.path.isdir(params['init_dir_path']):
        os.makedirs(params['source_path'])

    # Запись технических файлов
    json.dump(data_dict, open(params['source_path'] + params['project_name'] + '.json', 'w'))
    json.dump(params, open(params['source_path'] + 'config.json', 'w'))

    # Добавление пути к проекту в файл со всеми путями к проектам
    if not os.path.isfile(config.path_project_paths):
        open(config.path_project_paths, 'w').write('{}')
    path_project = json.load(open(config.path_project_paths, 'r'))
    path_project[params['project_name']] = params['init_dir_path']
    json.dump(path_project, open(config.path_project_paths, 'w'))

    # Создание дерева папок по каркасу
    make_dir_by_dict(data_dict=data_dict['body'],
                     init_dir_path=params['init_dir_path'])

    # Обвес проекта разными прелестями
    furnishing_frame(dir_path=params['init_dir_path'],
                     file_name=config.element_source_file['progress'],
                     list_lower_lvl_dirs=config.default_list_lower_lvl_dirs,
                     source_path=params['source_path'],
                     project_name=params['project_name'])

    # Создание базы данных для проекта
    table_columns = sqltools.create_table_columns_list('init')
    conn = sqltools.connect_sqlite(params['source_path'] + f'{params["project_name"]}.db')
    sqltools.create_table(conn=conn,
                          table_names=data_dict['header'],
                          table_columns=table_columns)

    # Запись первоначальной информации
    insert_data = prepare_data(raw_data=data_dict)
    sqltools.insert_in_table(conn=conn,
                             insert_data=insert_data)

    STL.open_file(params['init_dir_path'])
    conn.close()
