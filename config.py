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


default_init_study = False
default_exam_complete = False
default_hours_spent = 0
default_importance = 1
default_required_number_of_hours = 7 * 1.5
default_score = default_importance*100 - default_hours_spent*default_importance*100/default_required_number_of_hours \
                if default_hours_spent != 0 \
                else 100 * default_importance

progress_file_data = {'init_study': default_init_study,
                      'exam_complete': default_exam_complete,
                      'hours_spent': default_hours_spent,
                      'importance': default_importance,
                      'required_number_of_hours': default_required_number_of_hours,
                      'score': default_score}
