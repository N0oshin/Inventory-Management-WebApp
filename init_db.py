import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO Admin (username, password,a_id) VALUES ('arjun','b200714cs',1)")
cur.execute("INSERT INTO Admin (username, password,a_id) VALUES ('shyama','b200698cs',2)")
cur.execute("INSERT INTO Admin (username, password,a_id) VALUES ('karthik','b200718cs',3)")
cur.execute("INSERT INTO Admin (username, password,a_id) VALUES ('nooshin','b200690cs',4)")
cur.execute("INSERT INTO Admin (username, password,a_id) VALUES ('vaishali','b200774cs',5")

cur.execute("INSERT INTO User (u_username, u_password,u_id) VALUES ('abc','123',1)")
cur.execute("INSERT INTO User (u_username, u_password,u_id) VALUES ('a','1',2)")
cur.execute("INSERT INTO User (u_username, u_password,u_id) VALUES ('b','2',3)")

cur.execute('INSERT INTO Orders (u_id,item_id,quantity,price) VALUES (1,1,4,40)')
cur.execute('INSERT INTO Orders (u_id,item_id,quantity,price) VALUES (1,2,4,40)')
cur.execute('INSERT INTO Orders (u_id,item_id,quantity,price) VALUES (2,2,4,40)')

cur.execute("INSERT INTO Items (name, weight, price_per_unit, c_id) VALUES (?, ?, ?, ?)",
            ('Apple', 20, 30, 1)
            )

cur.execute("INSERT INTO Items (name, weight, price_per_unit, c_id) VALUES (?, ?, ?, ?)",
            ('Orange', 23, 30, 1)
            )
cur.execute("INSERT INTO Items (name, weight, price_per_unit, c_id) VALUES (?, ?, ?, ?)",
            ('Carrot', 23, 30, 2)
            )
cur.execute("INSERT INTO Categories (c_name,c_id) VALUES (?,?)",
            ('Fruits',1)	
            )
cur.execute("INSERT INTO Categories (c_name,c_id) VALUES (?,?)",
            ('Vegitables',2)	
            )

connection.commit()
connection.close()

