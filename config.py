
# Справочник аргументов CLI
cli_params_dict = {('-i', '--init'): {'description':    'Первый запуск, создание базовой структуры',
                                      'import_path':    'modules.init',
                                      'sub_params':     {('if', 'init_file_path'):          {'description': "Путь до создаваемой базовой структуры курса",
                                                                                             'default':     './raw.txt'},
                                                         ('id', 'init_dir_path'):           {'description': 'Путь до создаваемой базовой структуры курса',
                                                                                             'default':     './default/'},
                                                         ('is', 'init_shift_value'):        {'description': 'Символ показывающий вложенность объекта',
                                                                                             'default':     '\t'}
                                                         }
                                      }
                   }

# Обвес для каркасе
source_dir = 'source_files'
default_list_lower_lvl_dirs = ['prepared material']

# Папки попадающие в исключения
exception_dirs = [source_dir]
exception_dirs += default_list_lower_lvl_dirs

# Настройки файла с прогрессом по умолчанию
default_init_study = False
default_exam_complete = False
default_importance = 1

default_hours_spent = 0
default_required_number_of_hours = 7 * 1.5
percentage_of_completion = default_hours_spent*100/default_required_number_of_hours

default_score = default_importance*100 - percentage_of_completion*default_importance if default_hours_spent != 0 else 100 * default_importance

progress_file_data = {'init_study': default_init_study,
                      'exam_complete': default_exam_complete,
                      'hours_spent': default_hours_spent,
                      'importance': default_importance,
                      'required_number_of_hours': default_required_number_of_hours,
                      'score': default_score}
