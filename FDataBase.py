import time
import sqlite3
import math


class FDataBase:

    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("ошибка")
        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM user WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO user VALUES(NULL, ?,?,?,NULL,NULL,?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("ошибка добавления пользователя в бд" + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM user WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("ошибка получения данных из бд" + str(e))
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM user WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("ошибка получения данных из бд" + str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE user SET file = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("ошибка обновления в бд"+str(e))
            return False
        return True

    def path_folder(self, user_id):
        try:
            self.__cur.execute(f"SELECT folder FROM user WHERE id = '{user_id}' LIMIT 1")
            path = self.__cur.fetchone()[0]
            if not path:
                print("путь не найден")
                return False
            return path
        except sqlite3.Error as e:
            print("ошибка получения данных из бд" + str(e))
        except Exception as e:
            print("Неожиданная ошибка: " + str(e))




