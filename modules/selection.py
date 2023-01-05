# локальные пакеты
import config
from . import STL
from . import sqltools

# общие пакеты
import json

# TODO Переписать на долее читабельный вид функции  get_table_list и get_element

def get_table_list(connection, header, element_name):
    elements = []
    for table_name in header:
        col_names = [row[1] for row in connection.execute(f'PRAGMA table_info("{table_name}")')]
        select_str = f'SELECT {", ".join(col_names)} FROM "{table_name}" WHERE exam_complete == 0 and name == "{element_name}"'
        response = [{col_names[i]: elem for i, elem in enumerate(response_row)} for response_row in connection.execute(select_str).fetchall()]
        for row in response:
            row['table_name'] = table_name
            elements.append(row)
    if len(elements) > 1:
        print('\nЭлементов больше одного, выберите один из списка:')
        for i, element in enumerate(elements):
            print(f'{element["name"]} c родителем {element["parent_name"]}.[{i}]')
        user_input = -1
        while user_input <= -1 or user_input >= len(elements):
            if user_input != -1:
                print(f'\nКажется элемента с номером {user_input} не существует, попробуйте ещё раз.')
            try:
                user_input = int(input(f'Для выбора введите число от {0} до {len(elements)-1}: '))
            except ValueError:
                print('\nОчень смешно, попробуйте ещё раз.')
                user_input = -1
        elements = elements[user_input]

    elif len(elements) == 1:
        elements = elements[0]

    if len(elements) > 0:
        element_path = '/'.join(elements['element_path'].split('/')[:-2])
        return header[header.index(elements['table_name']):], element_path
    else:
        return header, None


def get_element(connection, table_list: list, element_path: [str, None], select_from: [str, None]) -> dict:
    result = {}
    like_str = f'%%'
    like_str = like_str[:-1] + f'{element_path}%' if element_path else like_str
    parent_name = ''
    for num_table, name_table in enumerate(table_list):
        col_names = ['name', 'element_path', 'dependence', 'general_element_path']
        select_str = f'SELECT {",".join(col_names)} FROM "{name_table}" WHERE exam_complete == 0 and element_path LIKE "{like_str}"'
        if parent_name:
            select_str += f' and parent_name = "{parent_name}"'
        select_str += ' ORDER BY score DESC'
        response = [{col_names[i]: elem for i, elem in enumerate(response_row)} for response_row in connection.execute(select_str).fetchall()]
        if len(response) == 0:
            break
        for response_row in response:
            result = response_row
            if num_table == 0 and response_row['name'] != select_from:
                continue
            if response_row['dependence'] == 0:
                parent_name = response_row['name']
                break
            else:

                select_str = 'WITH ut as ('
                select_str += ' UNION '.join([f'SELECT element_path, exam_complete FROM "{table}"' for table in table_list])
                select_str += f') SELECT exam_complete FROM ut WHERE element_path = "{response_row["general_element_path"]}"'
                sub_response = connection.execute(select_str).fetchone()[0]
                if sub_response == 1:
                    parent_name = response_row['name']
                    break
    return result


def run(argv, main_cli_param):
    params = STL.get_params(argv, main_cli_param)                                                                            # Параметры для модуля
    params['path_to_project'] = json.load(open(config.path_project_paths))[params['select_project']]                         # Путь до проекта
    params['path_to_project_source_dir'] = params['path_to_project'] + config.source_dir                                     # Путь до папки с настройками проекта
    params['conn'] = sqltools.connect_sqlite(params['path_to_project_source_dir'] + params['select_project'] + '.db')        # Подключение к базе проекта
    params['header'] = json.load(open(params['path_to_project_source_dir'] + params['select_project'] + '.json'))['header']  # Список header для дерева элементов
    params['table_list'], params['element_path'] = get_table_list(params['conn'], params['header'], params['select_from'])   # Список таблиц для проверки и путь до элемента

    # Получаем элемент для изучения
    element = get_element(connection=params['conn'],
                          table_list=params['table_list'],
                          element_path=params['element_path'],
                          select_from=params['select_from'])

    print(element)



