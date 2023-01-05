import config


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
