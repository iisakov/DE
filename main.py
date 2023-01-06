#! /usr/bin/python3
# локальные пакеты
import config

# общие пакеты
import sys
from itertools import chain
from importlib import import_module

# todo добавить модуль calculate_progress для пересчёта прогресса


def main(cli_params):
    # Чтение параметров из консоли
    cli_params = cli_params[1:]
    for existing_param_tpl in config.cli_params_dict:       # Проходим по всем доступным параметрам приложения
        for num_param, cli_param in enumerate(cli_params):  # Сравниваем со всеми параметрами из консоли
            if cli_param in existing_param_tpl:

                # Получаем существующие ключи параметров для модуля из конфига
                existing_params = [existing_sub_param_tpl for existing_sub_param_tpl in config.cli_params_dict[existing_param_tpl]['sub_params'].keys()]
                existing_params = list(chain(*existing_params))

                # Собираем аргументы из консоли для модуля
                modul_args = tuple(x for x in cli_params if x.split(':')[0] in existing_params)
                modul_args = {x.split(':')[0]: x.split(':')[1] for x in modul_args}

                # Подключение модуля todo разделить подключение модуля и запуск модуля. В идеале добавить приоритетность запуска модулей
                module = import_module(config.cli_params_dict[existing_param_tpl]['import_path'])   # Подключаем необходимый модуль
                module.run(modul_args, cli_param)                                                   # Запускаем модуль


if __name__ == '__main__':
    main(cli_params=sys.argv)
