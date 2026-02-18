import pymysql
from config import Config


def get_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        port=3307,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        db=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,  # to return results as dictionaries instead of tuples
        connect_timeout=5
    )
