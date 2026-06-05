import sqlite3

def get_user_data(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # INSECURE: Vulnerable to SQL Injection
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    
    return cursor.fetchall()