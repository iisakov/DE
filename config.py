cli_params_dict = {('-i', '--init'): {'description':    'Первый запуск, создание базовой структуры',
                                      'import_path':    'modules.init',
                                      'sub_params':     {('if', 'init_file_path'):          {'description': "Путь до создаваемой базовой структуры курса",
                                                                                             'default':     './raw.txt'},
                                                         ('id', 'init_dir_path'):           {'description': 'Путь до создаваемой базовой структуры курса',
                                                                                             'default':     './default/'},
                                                         ('is', 'init_shift_value'):        {'description': 'Символ показывающий вложенность объекта',
                                                                                             'default':     '\t'},
                                                         ('in', 'init_max_nesting_level'):  {'description': 'Максимальная вложенность в файле',
                                                                                             'default':     '4'}
                                                         }
                                      }
                   }
