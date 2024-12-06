import sqlite3
import traceback

DATABASE = 'database.db'



class DBConnection:
    def __init__(self):
        pass

    def init_db(self):
        try:
            self.conn = sqlite3.connect(DATABASE, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            print("""Initialize the database with a user table.""")
            conn = self.conn
            return conn
        except Exception as ex:
            print(traceback.print_exc())


