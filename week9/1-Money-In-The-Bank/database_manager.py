from client import Client
import sqlite3
import create_db
from settings import DB_NAME
import hashlib
import time


class BankDatabaseManager():

    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        create_db.generate_tables()

    def change_message(self, new_message, logged_user):

        update_sql = "UPDATE clients SET message = ? WHERE id = ?"
        self.cursor.execute(update_sql, (new_message, logged_user.get_id()))
        self.conn.commit()
        logged_user.set_message(new_message)

    def update_hash_password(self, email, hashed_password):
        update_sql = "UPDATE clients SET password = ? WHERE mail = ?"
        self.cursor.execute(update_sql, (email, hashed_password))
        self.conn.commit()
        return True

    def change_pass(self, new_pass, logged_user):
        if not BankDatabaseManager.check_password(new_pass, logged_user=logged_user):
            return
        new_pass = BankDatabaseManager.hash_password(new_pass)
        update_sql = "UPDATE clients SET password = ? WHERE id = ?"
        self.cursor.execute(update_sql, (new_pass, logged_user.get_id()))
        self.conn.commit()

    def set_pass_from_reset(self, username, new_password):

        new_password = BankDatabaseManager.hash_password(new_password)

        update_sql = "UPDATE clients SET password = ? WHERE username = ?"
        self.cursor.execute(update_sql, (new_password, username))
        self.conn.commit()

    def register(self, username, password, mail):
        if not BankDatabaseManager.check_password(password, username=username):
            return False
            print("something broke 1")
        HashedPassword = BankDatabaseManager.hash_password(password)

        cursor = self.conn.cursor()
        insert_sql = "insert into clients (username, password, mail) values (?, ?, ?)"
        cursor.execute(insert_sql, (username, HashedPassword, mail))
        self.conn.commit()
        return True

    def deposit(self, logged_user, sum):
        select_query = "SELECT balance FROM clients WHERE id = ?"
        self.cursor.execute(select_query, (logged_user.get_id(),))
        current_balance = float(self.cursor.fetchone()[0])

        total_money = float(current_balance + sum)
        update_query = """UPDATE clients SET balance = ? WHERE id = ?"""
        self.cursor.execute(update_query, (total_money, logged_user.get_id()))

        self.conn.commit()

    def login(self, username, password):
        cursor = self.conn.cursor()
        HashedPassword = BankDatabaseManager.hash_password(password)

        select_query = "SELECT id, username, balance, message, mail FROM clients WHERE username = ? AND password = ? LIMIT 1"

        cursor.execute(select_query, (username, HashedPassword))
        user = cursor.fetchone()

        if(user):
            return Client(user[0], user[1], user[2], user[3], user[4])
        else:
            return False

    @staticmethod
    def check_password(password, username="", logged_user=""):
        sPasswordInUserName = "Your password should not be part of your user name!"
        sPasswordTooShort = "Your current password is only {} symbols\n It should be above 8."
        sPasswordNotVarious = "Your password should have capital letters, number and special symbol"

        if len(password) < 9:
            print(sPasswordTooShort.format(len(password)))
            return False
        if username != "":
            if username.lower() in password.lower():
                print(sPasswordInUserName)
                return False
        else:
            if logged_user.get_username().lower() in password.lower():
                print(sPasswordInUserName)
                return False
        # Checking for capital letter, digit, lower letter and special char.
        if not(bool([char for char in password if (char.isupper())]) and bool([char for char in password if (char.isdigit())]) and bool([char for char in password if (char.islower())]) and bool(set('[~!@#$%^&*()_+.{}":;\']+$').intersection(password))):
            print(sPasswordNotVarious)
            return False

        return True

    @staticmethod
    def hash_password(password):
        pwd = hashlib.md5(password.encode())
        return pwd.hexdigest()

    @staticmethod
    def lock_database():

        z = 10
        while z > 0:
            time.sleep(1)
            print("{} minutes to unlocking!".format(z))
            z -= 1
        print("Database is now unlocked! Good luck!")

    def get_username_from_email(self, email):
        cursor = self.conn.cursor()
        select_query = "SELECT username FROM clients WHERE mail = ?"
        cursor.execute(select_query, (email,))
        user = cursor.fetchone()[0]

        if(user):
            return (user)
