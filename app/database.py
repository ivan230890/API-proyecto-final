import mysql.connector

class DatabaseConnection:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls._connection = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                port="3306",
                password='root',
                database='registro_usuarios'
            )
        return cls._connection
    
    @classmethod
    def fetch_one(cls, query, params=None):  
        cursor = cls.get_connection().cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()  
        return result
    
    @classmethod
    def fetch_all(cls, query, params=None):  
        cursor = cls.get_connection().cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()  
        return results
    
    @classmethod
    def execute(cls, query, params=None):
        cursor = cls.get_connection().cursor()
        cursor.execute(query, params)
        cls._connection.commit()
        cursor.close()  
    
    
    @classmethod
    def execute_query(cls, query, params=None):
        cursor = cls.get_connection().cursor()
        cursor.execute(query, params)
        cls._connection.commit()
        cursor.close()  
    
    @classmethod
    def close_connection(cls):
        if cls._connection is not None:
            cls._connection.close()
            cls._connection = None
