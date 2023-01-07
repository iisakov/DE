import config
import os
import platform
import subprocess
from time import sleep


def open_file(path):
    """
    Открыть папку в проводнике платформы
    :param path: Путь к папке.
    :return: Void
    """
    sleep(1)
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
    sleep(5)


def compute_score(importance, hours_spent, required_number_of_hours) -> float:
    percentage_of_completion = hours_spent * 100 / required_number_of_hours
    score = importance * 100 - percentage_of_completion * importance if hours_spent != 0 else 100 * importance
    return score


def get_params(sub_cli_param, main_cli_param) -> dict:
    """
    Проверяем параметры в sub_cli_param модуля в котором присутствует main_cli_param из консоли, подставляем параметры по умолчанию, если чего-то не хватает.
    :param sub_cli_param: Входящие от пользователя параметры модуля
    :param main_cli_param: Входящий от пользователя параметры, вызывающий модуль
    :return: Готовый пакет параметров от пользователя, если каких-то параметров не хватает, подставляются параметры по умолчанию.
    """

    existing_sub_params = {}
    result = {}

    for existing_main_param_key, existing_main_param_value in config.cli_params_dict.items():
        if main_cli_param in existing_main_param_key:
            existing_sub_params = existing_main_param_value['sub_params']
            break

    for existing_sub_param_key, existing_sub_param_value in existing_sub_params.items():
        for real_sub_param_key, real_sub_param_value in sub_cli_param.items() if len(sub_cli_param) > 0 else existing_sub_params.items():
            if real_sub_param_key in existing_sub_param_key:
                result[existing_sub_param_key[1]] = real_sub_param_value
                break
            else:
                result[existing_sub_param_key[1]] = existing_sub_param_value['default']

    return result


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
        element_path = '/'.join(current_element['element_path'].split('/')[:-2]) + '/'               # Путь до найденного элемента без самого элемента
        table_names_list = table_names_list[table_names_list.index(current_element['table_name']):]  # Список таблиц, для поиска
        return table_names_list, element_path
    else:
        return table_names_list, None
