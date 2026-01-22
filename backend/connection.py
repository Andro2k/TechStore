import pyodbc
from backend.config import SERVER_ADDR, DB_USER, DB_PASS, CURRENT_NODE

def get_db_connection():
    """Genera y retorna la conexión ODBC."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER_ADDR};"
        f"DATABASE={CURRENT_NODE['db_name']};"
    )
    
    if DB_USER and DB_PASS:
        conn_str += f"UID={DB_USER};PWD={DB_PASS};"
    else:
        conn_str += "Trusted_Connection=yes;"
        
    return pyodbc.connect(conn_str)