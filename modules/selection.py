# локальные пакеты
from time import sleep

import config
from . import STL
from . import sqltools

# общие пакеты
import json
import os
import platform
import subprocess


def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def get_table_list(connection, table_names_list, element_name):

    # Собираем все элементы с именем element_name из всех таблиц списка table_names_list
    elements = []
    for table_name in table_names_list:
        col_names = [row[1] for row in connection.execute(f'PRAGMA table_info("{table_name}")')]                                                # Получаем список названий столбцов таблицы table_name
        select_str = f'SELECT {", ".join(col_names)} FROM "{table_name}" WHERE exam_complete == 0 and name == "{element_name}"'                 # строка запроса
        response = [{col_names[i]: elem for i, elem in enumerate(response_row)} for response_row in connection.execute(select_str).fetchall()]  # ответ с названиями полей

        # Добавляем имя таблицы к каждому элементу, так будет проще определить какие таблицы нам не понадобятся
        for row in response:
            row['table_name'] = table_name
            elements.append(row)

    # Если элементов больше одного, нам стоит уточнить, какой же элемент интересует пользователя
    if len(elements) > 1:
        print('\nЭлементов больше одного, выберите один из списка:')
        for i, element in enumerate(elements):
            print(f'{element["name"]} c родителем {element["parent_name"]}.[{i}]')
        # Пока у пользователя не получится ввести корректные число. Мы продолжаем его спрашивать.
        user_input = -1
        while type(user_input) is str or user_input < 0 or user_input >= len(elements):
            user_input = input(f'Для выбора введите число от {0} до {len(elements)-1}: ')
            if user_input.isdigit():
                user_input = int(user_input)
            else:
                print(f'\nОчень смешно, попробуйте ещё раз... {user_input} это не число вообще.')
                continue
            if user_input < 0 or user_input >= len(elements):
                print(f'\nКажется элемента с номером {user_input} не существует, попробуйте ещё раз.')
        # Из списка элементов оставляем тот элемент, который пожелал пользователь.
        current_element = elements[user_input]
    elif len(elements) == 1:
        current_element = elements[0]
    else:
        current_element = None

    # Возвращаем список таблиц и путь до элемента выбранного пользователем
    if current_element:
        element_path = '/'.join(current_element['element_path'].split('/')[:-2])                     # Путь до найденного элемента без самого элемента
        table_names_list = table_names_list[table_names_list.index(current_element['table_name']):]  # Список таблиц, для поиска
        return table_names_list, element_path
    else:
        return table_names_list, None


def get_element(connection, table_list: list, element_path: [str, None], select_from: [str, None]) -> dict:
    result = {}
    like_str = f'%%'                                                             # Строка для добавления туда уже найденных родителей элемента, чтоб выбирать только из них
    like_str = like_str[:-1] + f'{element_path}%' if element_path else like_str  # Если есть конкретный элемент, который мы хотим найти - добавляем путь до него
    parent_name = None                                                           # Родительский элемент
    addition_to_score = 100 if select_from else 0                                # Для гибкой настройки выбора элементов используем добавку к счёту
    for num_table, name_table in enumerate(table_list):
        col_names = ['name', 'element_path', 'dependence', 'general_element_path']

        # Генерим строку запроса (Наверное стоит вынести это в отдельную функцию и разобраться получше, но пока работает так)
        select_str = f'SELECT {",".join(col_names)}, '
        if select_from:
            select_str += f'case when name == "{select_from}" then score + {addition_to_score} else score end as '
        select_str += f'score FROM "{name_table}" WHERE exam_complete == 0 and element_path LIKE "{like_str}"'
        if parent_name:
            select_str += f' and parent_name = "{parent_name}"'
        select_str += ' ORDER BY score DESC'
        col_names.append('score')  # Незабываем добавить score в список для подстановки имён полей
        response = [{col_names[i]: elem for i, elem in enumerate(response_row)} for response_row in connection.execute(select_str).fetchall()]

        if len(response) == 0:
            break

        for response_row in response:
            result = response_row

            # Проверяем элемент на зависимости. Если элемент зависим от элемента в котором не пройден экзамен, пропускаем такой элемент
            if response_row['dependence'] == 0:
                parent_name = response_row['name']
                break
            else:
                select_str = 'WITH ut as ('
                select_str += ' UNION '.join([f'SELECT element_path, exam_complete FROM "{table}"' for table in table_list])
                select_str += f') SELECT exam_complete FROM ut WHERE element_path = "{response_row["general_element_path"]}" and exam_complete == 1'
                sub_response = connection.execute(select_str).fetchone()
                if sub_response:
                    parent_name = response_row['name']
                    break
    return result


def run(argv, main_cli_param):
    params = STL.get_params(argv, main_cli_param)                                                                            # Параметры для модуля
    params['path_to_project'] = json.load(open(config.path_project_paths))[params['select_project']]                         # Путь до проекта
    params['path_to_project_source_dir'] = params['path_to_project'] + config.source_dir                                     # Путь до папки с настройками проекта
    params['conn'] = sqltools.connect_sqlite(params['path_to_project_source_dir'] + params['select_project'] + '.db')        # Подключение к базе проекта
    params['header'] = json.load(open(params['path_to_project_source_dir'] + params['select_project'] + '.json'))['header']  # Список header для дерева элементов
    params['table_list'], params['element_path'] = get_table_list(connection=params['conn'],                                 # Список таблиц для проверки и путь до элемента
                                                                  table_names_list=params['header'],
                                                                  element_name=params['select_from'])

    # Получаем элемент для изучения
    element = get_element(connection=params['conn'],
                          table_list=params['table_list'],
                          element_path=params['element_path'],
                          select_from=params['select_from'])
    params['conn'].close()
    print(f'Открываю папку с элементом {element["name"]}. Его счёт на данный момент {element["score"]} С учётом надбавок. Желаю провести время с пользой')
    sleep(1)
    open_file(path=params['path_to_project'] + element['element_path'])
    sleep(1)




