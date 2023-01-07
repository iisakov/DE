import config
from . import STL
from . import sqltools
import json


def get_db_elements(connection, table_list: list, parent_element_path: [str, None], select_from: [str, None], recursion: str) -> dict:
    recursion = recursion.lower() not in ['false', '0'] if type(recursion) is str else recursion #TODO переспрашивать пользователя, если он ввёл что-то невнятное
    result = {}
    like_str = f'%%'                                                                            # Строка для добавления уже найденных родителей элемента
    like_str = like_str[:-1] + f'{parent_element_path}%' if parent_element_path else like_str   # Если есть конкретный элемент, который мы хотим найти - добавляем путь до него
    like_element_path = None                                                                    # Родительский элемент
    for num_table, name_table in enumerate(table_list):
        result[name_table] = []
        col_names = [row[1] for row in connection.execute(f'PRAGMA table_info("{name_table}")')]

        # Генерим строку запроса (Наверное стоит вынести это в отдельную функцию и разобраться получше, но пока работает так)
        select_str = f'SELECT {",".join(col_names)} '
        select_str += f'FROM "{name_table}" WHERE element_path LIKE "{like_str}"'
        if like_element_path:
            select_str += f' and element_path like "{like_element_path}"'
        result[name_table] += [{col_names[i]: elem for i, elem in enumerate(response_row)} for response_row in connection.execute(select_str).fetchall()]

        for response_row in result[name_table]:
            if num_table == 0:
                if response_row['name'] == select_from:
                    result[name_table] = [response_row]
                    like_element_path = response_row['element_path']+'%'
            if not recursion:
                break
    return result


def get_file_elements(db_elements: dict, path_to_project: str) -> dict:
    file_elements = {}
    for table_name, db_elements_list in db_elements.items():
        file_elements[table_name] = []
        for db_element in db_elements_list:
            file_element = json.load(open(path_to_project + db_element['element_path'] + config.element_source_file['progress']))
            file_element['score'] = STL.compute_score(importance=file_element['importance'],
                                                      hours_spent=file_element['hours_spent'],
                                                      required_number_of_hours=file_element['required_number_of_hours'])
            for db_element_key, db_element_value in db_element.items():
                if db_element_key in file_element:
                    db_element[db_element_key] = file_element[db_element_key]
            file_elements[table_name].append(db_element)

    return file_elements


def run(argv, main_cli_param):
    params = STL.get_params(argv, main_cli_param)

    params = STL.get_params(argv, main_cli_param)                                                                     # Параметры для модуля
    params['path_to_project'] = json.load(open(config.path_project_paths))[params['project']]                         # Путь до проекта
    params['path_to_project_source_dir'] = params['path_to_project'] + config.source_dir                              # Путь до папки с настройками проекта
    params['conn'] = sqltools.connect_sqlite(params['path_to_project_source_dir'] + params['project'] + '.db')        # Подключение к базе проекта
    params['header'] = json.load(open(params['path_to_project_source_dir'] + params['project'] + '.json'))['header']  # Список header для дерева элементов
    params['table_list'], params['parent_element_path'] = STL.get_table_list(connection=params['conn'],
                                                                             table_names_list=params['header'],
                                                                             element_name=params['update_element'])

    db_elements = get_db_elements(connection=params['conn'],
                                  table_list=params['table_list'],
                                  parent_element_path=params['parent_element_path'],
                                  select_from=params['update_element'],
                                  recursion=params['update_recursion'])

    file_elements = get_file_elements(db_elements=db_elements,
                                      path_to_project=params['path_to_project'])

    sqltools.update_rows(update_data=file_elements,
                         conn=params['conn'])

    params['conn'].close()
