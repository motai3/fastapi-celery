import dolphindb as ddb

from DBConnection import DatabaseConnection

class DolphinAdapter(DatabaseConnection):
    def __init__(self):
        s = ddb.Session()
        s.connect(host, port)
        s.login(userid="admin", password="123456")
        import mysql_module
        self.db = mysql_module.MySQLDB()

    def connect(self):
        self.db.connect()

    def query(self, query):
        return self.db.execute_query(query)