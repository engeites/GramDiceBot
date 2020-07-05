import sqlite3
from data_to_sql import DataProcesser


class Sqliter:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def get_all_users(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM 'users'").fetchall()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchall()
            print(f"Exists: {bool(len(result))}")
            return bool(len(result))

    def user_got_money(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE start_balance=?", (100,)).fetchall()
            print(f"Looking for guys with money:")
            print(f"Found this id: {result}")
            return bool(len(result))

    def add_user(self, data):
        """
        пока добавляет только айди нового пользователя.
        В дальшейшем должен будет добавлять все данные о пользователе
        :param user_id:
        :return:
        """
        new_user = DataProcesser(data)
        user_data = new_user.get_data()
        with self.connection:
            return self.cursor.execute("INSERT INTO 'users' ('user_id', 'first_name', 'last_name', 'username', 'chat_id') VALUES (?,?,?,?,?)",
                                       user_data)

    def get_user_info(self, user_id):
        """Получаем все данные пользователя для игры - его имя и баланс"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()

    def set_new_balance(self, user_id, balance):
        """Записываем новый баланс игрока после ставки"""
        with self.connection:
            return self.cursor.execute("UPDATE users SET current_balance = ? WHERE user_id = ?", (balance, user_id))

    def check_balance(self, user_id):
        with self.connection:
            return (self.cursor.execute("SELECT current_balance FROM users WHERE  user_id = ?", (user_id,)).fetchall())[0][0]

    def add_money_won(self, user_id, points):
        """Записываем новый баланс игрока после ставки"""
        with self.connection:
            current = self.cursor.execute("SELECT current_balance FROM users WHERE  user_id = ?", (user_id,)).fetchall()
            print(current)
            print(type(current))
        with self.connection:
            new_balance = current[0][0] + int(points)
            return self.cursor.execute("UPDATE users SET current_balance = ? WHERE user_id = ?", (new_balance, user_id))

    def close(self):
        self.connection.close()
