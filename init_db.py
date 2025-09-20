import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("database.db")

with open("schema.sql") as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Hashing the password for security

admin_username = "admin"
admin_password_plain = "admin123"
admin_password_hashed = generate_password_hash(admin_password_plain)
admin_id = 1

cur.execute(
    "INSERT INTO Admin (a_id, username, password) VALUES (?, ?, ?)",
    (admin_id, admin_username, admin_password_hashed),
)

connection.commit()
connection.close()

print("Database initialized successfully with a new admin user.")
