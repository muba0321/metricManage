# custom_db.py
import pymysql

# Replace these with your own database connection details
DB_CONFIG = {
    'host': '192.168.50.30',
    'user': 'root',
    'password': '56ZS66xdQit_',
    'database': 'MonitorCenter',
    'port': 3306
}


def get_third_party_data(query):
    connection = pymysql.connect(**DB_CONFIG)

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()
        