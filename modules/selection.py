# локальные пакеты
import config
from . import STL
from . import sqltools

# общие пакеты
import json


def put_last_selected_element_path(path_to_project_source_dir, element_path):
    project_config_file = json.load(open(path_to_project_source_dir))
    project_config_file['last_selected_element_path'] = element_path
    json.dump(project_config_file, open(path_to_project_source_dir, 'w'))


def get_element(connection, table_list: list, parent_element_path: [str, None], select_from: [str, None], last_selected_element: [str, None]) -> dict:
    print(connection, table_list, parent_element_path, select_from, last_selected_element)
    result = {}
    like_str = f'%%'                                                                            # Строка для добавления туда уже найденных родителей элемента, чтоб выбирать только из них
    like_str = like_str[:-1] + f'{parent_element_path}%' if parent_element_path else like_str   # Если есть конкретный элемент, который мы хотим найти - добавляем путь до него
    parent_name = None                                                                          # Родительский элемент
    addition_str = ''
    if last_selected_element:
        addition_to_score = 20
        addition_element = last_selected_element
        addition_str = f'case when element_path == "{addition_element}" then score + {addition_to_score} else score end as '
    if select_from:
        addition_to_score = 100
        addition_element = select_from
        addition_str = f'case when name == "{addition_element}" then score + {addition_to_score} else score end as '

    for num_table, name_table in enumerate(table_list):
        col_names = ['name', 'element_path', 'dependence', 'general_element_path']

        # Генерим строку запроса (Наверное стоит вынести это в отдельную функцию и разобраться получше, но пока работает так)
        select_str = f'SELECT {",".join(col_names)}, '
        select_str += addition_str
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
    params = STL.get_params(argv, main_cli_param)                                                                      # Параметры для модуля
    params['path_to_project'] = json.load(open(config.path_project_paths))[params['project']]                          # Путь до проекта
    params['path_to_project_source_dir'] = params['path_to_project'] + config.source_dir                               # Путь до папки с настройками проекта
    params['conn'] = sqltools.connect_sqlite(params['path_to_project_source_dir'] + params['project'] + '.db')         # Подключение к базе проекта
    params['path_to_project_config_file'] = params['path_to_project_source_dir'] + 'config.json'                       # Путь до конфигурационного файла проекта
    params = params | json.load(open(params['path_to_project_config_file']))
    params['header'] = json.load(open(params['path_to_project_source_dir'] + params['project'] + '.json'))['header']   # Список header для дерева элементов



    # Список таблиц для проверки и путь до элемента
    params['table_list'], params['parent_element_path'] = STL.get_table_list(connection=params['conn'],
                                                                             table_names_list=params['header'],
                                                                             element_name=params['select_from'])

    # Получаем элемент для изучения
    element = get_element(connection=params['conn'],
                          table_list=params['table_list'],
                          parent_element_path=params['parent_element_path'],
                          select_from=params['select_from'],
                          last_selected_element=params['last_selected_element_path'] if 'last_selected_element_path' in params else None)
    params['conn'].close()
    put_last_selected_element_path(params['path_to_project_config_file'], element['element_path'])
    print(f'Открываю папку с элементом {element["name"]}. Его счёт на данный момент {element["score"]} С учётом надбавок. Желаю провести время с пользой')
    STL.open_file(path=params['path_to_project'] + element['element_path'])
