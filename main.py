import psycopg2


def create_db(conn):
    with conn.cursor() as cursor:
        try:
            cursor.execute("""
            DROP TABLE IF EXISTS phones;
            DROP TABLE IF EXISTS users;
            """)
            conn.commit()
        except Exception as _ex:
            print(f'Error drop table, {_ex}. Reason - ', type(_ex))
            print()

        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id SERIAL PRIMARY KEY,
                name VARCHAR(30) NOT NULL,
                surname VARCHAR(30) NOT NULL,
                email VARCHAR(60) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS phones(
                phone_id SERIAL PRIMARY KEY,
                number VARCHAR(11) NOT NULL UNIQUE,
                user_id INT REFERENCES users(user_id)
            );
            """)
            conn.commit()
            print('Таблицы успешно созданы.\n')
        except Exception as _ex:
            print(f'Error creating table, {_ex}. Reason - ', type(_ex))
            print()


def add_client(conn, name, surname, email):
    with conn.cursor() as cursor:
        try:
            cursor.execute("""
            INSERT INTO users(name, surname, email) VALUES 
            (%s, %s, %s);
            """, (name, surname, email))
            print(f'Клиент {name} {surname}, email - {email} успешно добавлен.\n')
        except Exception as _ex:
            print(f'Ошибка добавления клиента, {_ex}. Причина - ', type(_ex))
            print()


def isint(number):
    number_without_replace = number
    number_with_replace = number.replace(' ', '').replace(':', '').replace('-', '').replace('+', '')
    if len(number_with_replace) != 11:
        print("Количество символов в номере не совпадает с форматом телефонных номеров РФ.")
        print()
        return
    try:
        number = int(number_with_replace)
        return True, number_without_replace, number_with_replace
    except (TypeError, ValueError):
        print(f'Неверный формат номера телефона - {number_without_replace}. Проверьте вводимые данные.')
        print()
        return False, number_without_replace, number_with_replace


def add_phone(conn, number, user_id):
    isint_status, number_without_replace, number_with_replace = isint(number)
    if isint_status:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT number from phones
                WHERE user_id = %s AND number = %s
                """, (user_id, number_with_replace))
                available_status = cursor.fetchone()
        except Exception as _ex:
            print(f'Ошибка добавления номера, {_ex}. Причина - ', type(_ex))
            print()

        if available_status is None:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                    INSERT INTO phones(number, user_id) VALUES
                    (%s, %s);
                    """, (number_with_replace, user_id))
                conn.commit()
                print(f'Номер телефона {number} успешно добавлен для USER ID - {user_id}.\n')
            except Exception as _ex:
                print(f'Ошибка добавления номера, {_ex}. Причина - ', type(_ex))
                print()

    else:
        print('Номер в базу данных не добавлен.\n')
        return


def change_client(conn, client_id, name, surname, email):
    with conn.cursor() as cursor:
        if name is None or len(name) == 0:
            cursor.execute("""
                SELECT name FROM users
                WHERE user_id = %s;
                """, (client_id,))
            name = cursor.fetchone()
        if surname is None or len(surname) == 0:
            cursor.execute("""
                SELECT surname FROM users
                WHERE user_id = %s;
                """, (client_id,))
            surname = cursor.fetchone()
        if email is None or len(email) == 0:
            cursor.execute("""
                SELECT email FROM users
                WHERE user_id = %s;
                """, (client_id,))
            email = cursor.fetchone()
        try:
            cursor.execute("""
                UPDATE users
                SET name = %s, surname = %s, email = %s
                WHERE user_id = %s;
                """, (name, surname, email, client_id))
            conn.commit()
            print('Данные клиента успешно обновлены.\n')
        except Exception as _ex:
            print(f'Ошибка изменения данных, {_ex}. Причина - ', type(_ex))
            print()


def delete_phone(conn, user_id, number):
    isint_status, number_without_replace, number_with_replace = isint(number)
    with conn.cursor() as cursor:
        try:
            cursor.execute("""
            SELECT number FROM phones
            WHERE user_id = %s AND number = %s;
            """, (user_id, number_with_replace))
            data = cursor.fetchone()

            if data is not None and len(data) != 0:
                print('Номер телефона присутствует в базе данных.')
                available_status = True
            else:
                print('Номер телефона отсутствует в базе данных!\n')
                return
        except Exception as _ex:
            print(f'Ошибка удаления номера, {_ex}. Причина - ', type(_ex))
            print()

        if available_status:
            try:
                cursor.execute("""
                DELETE FROM phones
                WHERE user_id = %s AND number = %s;
                """, (user_id, number_with_replace))
                print('Номер телефона успешно удален из базы данных.\n')
                conn.commit()
            except Exception as _ex:
                print(f'Ошибка удаления номера, {_ex}. Причина - ', type(_ex))
                print()


def delete_client(conn, user_id):
    with conn.cursor() as cursor:
        try:
            cursor.execute("""
            SELECT user_id FROM users
            WHERE user_id = %s;
            """, (user_id,))
            data = cursor.fetchone()
            if data is not None:
                print(f'Клиент с USER ID - {user_id} присутствует в базе данных.')
                available_status = True
            else:
                print(f'Клиент с USER ID - {user_id} отсутствует в базе данных!\n')
                print()
                return
            if available_status:
                try:
                    cursor.execute("""
                    DELETE FROM phones
                    WHERE user_id = %s;
                    """, (user_id,))

                    cursor.execute("""
                    DELETE FROM users
                    WHERE user_id = %s;
                    """, (user_id,))

                    conn.commit()
                    print(f'Клиент с USER ID - {user_id} успешно удален из базы данных.\n')
                except Exception as _ex:
                    print(f'Ошибка удаления клиента, {_ex}. Причина - ', type(_ex))
                    print()
        except Exception as _ex:
            print(f'Ошибка удаления клиента, {_ex}. Причина - ', type(_ex))
            print()


def find_client(conn, name=None, surname=None, email=None, number=None):
    with conn.cursor() as cursor:

        if number is not None and len(number) != 0:
            isint_status, number_without_replace, number_with_replace = isint(number)

            if isint_status:
                cursor.execute("""
                SELECT * FROM phones
                WHERE number = %s;
                """, (number_with_replace,))
                phone_result = cursor.fetchall()
                if phone_result is not None and len(phone_result) != 0:
                    cursor.execute("""
                    SELECT * FROM users
                    WHERE user_id = %s;
                    """, (phone_result[0][2],))
                    user_result = cursor.fetchall()

                    cursor.execute("""
                    SELECT number FROM phones
                    WHERE user_id = %s;
                    """, (phone_result[0][2],))
                    phone_result = cursor.fetchall()

                    print(f'Данные клиента - ID - {user_result[0][0]}\n'
                          f'Имя - {user_result[0][1]}\n'
                          f'Фамилия - {user_result[0][2]}\n'
                          f'Email - {user_result[0][3]}\n'
                          f'Номер телефона - {phone_result}\n')
                    return
                else:
                    print('Такого номера телефона в базе данных не найдено!\n')
            else:
                print(f'Неверный формат номера телефона - {number}. Проверьте вводимые данные.')
                return
        elif name is not None and len(name) != 0 \
                or surname is not None and len(surname) != 0 \
                or email is not None and len(email) != 0:
            try:
                cursor.execute("""
                SELECT * FROM users
                WHERE name = %s OR surname = %s OR email = %s;
                """, (name, surname, email))
                result = cursor.fetchall()

                if result is not None and len(result) != 0:

                    cursor.execute("""
                    SELECT number FROM phones
                    WHERE user_id = %s;
                    """, (result[0][0],))
                    phone_result = cursor.fetchall()

                    if len(phone_result) != 0:
                        phone_number = phone_result
                    else:
                        phone_number = 'отсутствуют в базе данных.'

                    print(f'Данные клиента - ID - {result[0][0]}\n'
                          f'Имя - {result[0][1]}\n'
                          f'Фамилия - {result[0][2]}\n'
                          f'Email - {result[0][3]}\n'
                          f'Номер телефона - {phone_number}\n')

                else:
                    print('Клиент не найден!\n')

            except Exception as _ex:
                print(f'Ошибка поиска клиента, {_ex}. Причина - ', type(_ex))
                print()
        else:
            print(f'Клиента с данными:'
                  f'Имя - {name}'
                  f'Фамилия - {surname}'
                  f'Email - {email}'
                  f'Номер телефона - {number}'
                  f'Не найден!')


with psycopg2.connect(database="clients_db", user="postgres", password="123") as conn:
    create_db(conn)
    add_client(conn, "Sergey", "Belokon", "ultraspa@ya.ru")
    add_client(conn, "Serg", "Belov", "u1@ya.ru")
    add_client(conn, "Sergye", "Beloveee", "u12@ya.ru")
    add_client(conn, "To", "Delete", "del@ya.ru")
    add_client(conn, "Get", "Delete", "delete@ya.ru")
    add_phone(conn, "+7 888 888 88 88", "1")
    add_phone(conn, "8-999-999-99-99", "1")
    add_phone(conn, "+7 666 666 66 66", "4")
    add_phone(conn, "8-777-777-77-77", "5")
    change_client(conn, "1", "Serg", "", "")
    change_client(conn, "1", "Sergrerrry", None, None)
    delete_phone(conn, "4", "+7 666 666 66 66")
    delete_client(conn, "5")
    find_client(conn, "", "", "", "8-999-999-99-99")
    find_client(conn, "Sergye", "", "", "")
    find_client(conn, "Sergy", "", "", "")
    find_client(conn, "", "", "", "8-111-111-11-11")

conn.close()

status = conn.closed
if status == 0:
    print('Соединение с базой данных не закрыто!')
else:
    print('Соединение с базой данных закрыто.')
