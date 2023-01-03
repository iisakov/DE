
# Справочник аргументов CLI
cli_params_dict = {('-i', '--init'): {'description':    'Первый запуск, создание базовой структуры',
                                      'import_path':    'modules.init',
                                      'sub_params':     {('if', 'init_file_path'):              {'description': "Путь до создаваемой базовой структуры курса",
                                                                                                 'default':     './raw.txt'},
                                                         ('id', 'init_dir_path'):               {'description': 'Путь до создаваемой базовой структуры курса',
                                                                                                 'default':     './default/'},
                                                         ('io', 'init_offset_value'):           {'description': 'Символ показывающий вложенность объекта',
                                                                                                 'default':     '\t'},
                                                         ('is', 'init_separation_value'):       {'description': 'Символ разделения объектов, зависимость',
                                                                                                 'default':     ':!:'},
                                                         ('ios', 'init_option_start_value'):    {'description': 'Символ начала дополнительных опций,'
                                                                                                                ' символы подставляются в регулярное выражение,'
                                                                                                                ' используйте символ экранирования по правилам'
                                                                                                                ' регулярных вырожений',
                                                                                                 'default':     r'\(:'},
                                                         ('ioe', 'init_option_end_value'):      {'description': 'Символ конца дополнительных опций,'
                                                                                                                ' символы подставляются в регулярное выражение,'
                                                                                                                ' используйте символ экранирования по правилам'
                                                                                                                ' регулярных вырожений',
                                                                                                 'default':     r':\)'}
                                                         },
                                      'options':        {'importance':                  {'description': "Важность в освоении курса, по умолчанию 1.0",
                                                                                         'default': 1.0},
                                                         'init_study':                  {'description': "Были ли проведены первичные исследования,"
                                                                                                        " по умолчанию False",
                                                                                         'default': False},
                                                         'exam_complete':               {'description': "Сдан экзамен по элементу, по умолчанию False",
                                                                                         'default': False},
                                                         'hours_spent':                 {'description': "Проведено часов за элементом, по умолчанию 0.0",
                                                                                         'default': 0.0},
                                                         'required_number_of_hours':    {'description': "Рекомендуемое время для изучения элемента"
                                                                                                        "по умолчанию 20.0",
                                                                                         'default': 20.0}
                                                         }
                                      }
                   }
# Системные пути
path_project_paths = './project_paths.json'

# Обвес для каркасе
source_dir = 'source_files'
default_list_lower_lvl_dirs = ['prepared material']

# Название папок, попадающих в исключения
exception_dirs = [source_dir]
exception_dirs += default_list_lower_lvl_dirs
