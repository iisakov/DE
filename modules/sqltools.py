import sqlite3
import config
import datetime


def connect_sqlite(path_to_db):
    return sqlite3.connect(database=path_to_db)


# Основные столбцы в таблицах проекта в каждом элементе
def create_table_columns_list(module_name):
    table_columns_list = []
    for cli_params_key, cli_params_value in config.cli_params_dict.items():
        if f'--{module_name}' in cli_params_key:
            table_columns_list = cli_params_value['main_columns']
            break

    return table_columns_list


def create_table(table_names: list, table_columns: dict, conn: sqlite3.Connection):
    table_columns = [f'"{col_name}" {col_options}' for col_name, col_options in table_columns.items()]
    table_names = ['\"' + x + '\"' for x in table_names]
    for table_name in table_names:
        create_str = f"CREATE TABLE {table_name}({', '.join(table_columns)})"
        conn.cursor().execute(create_str)
        conn.commit()


def insert_in_table(insert_data: dict, conn: sqlite3.Connection):
    """
    Множественная запись в БД.
    :param table_names: Список таблиц
    :param insert_data: Словарь информации, которую нужно записать. Ключи словаря - имя таблицы, значение словаря информация по столбцам. Если в значениях
    неуказан какой-то столбец, он заполняется значением NULL
    :param conn: Соединение с базой данных
    :return:
    """

    for table_name, row_list in insert_data.items():
        col_list = [row[1] for row in conn.execute(f'PRAGMA table_info("{table_name}")')]
        records = []
        for row in row_list:
            records.append(tuple([row[col] if col in row.keys() else None for col in col_list]))

        insert_str = f'INSERT INTO "{table_name}" VALUES({",".join(["?"]*len(col_list))});'
        conn.executemany(insert_str, records)

    conn.commit()


def update_rows(update_data: dict, conn: sqlite3.Connection):
    for table_name, elements in update_data.items():
        for row in elements:
            row['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
            row['update_by'] = 'user'
            update_cols_str = ", ".join([f"{col} = ?" for col in row if col != "id"])
            update_str = f'UPDATE "{table_name}" SET {update_cols_str} WHERE id = ?'
            element_date = [col for col in list(row.values())[1:]]
            element_date.append(row['id'])
            conn.execute(update_str, element_date)
            conn.commit()

if __name__ == '__main__':
    pass
