DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS History;

CREATE TABLE Admin (
    a_id INTEGER PRIMARY KEY ,
    username varchar(20) not null,
    password varchar(20) not null
    
);

CREATE TABLE User (
    u_id INTEGER PRIMARY KEY ,
    u_username varchar(20) not null,
    u_password varchar(20) not null
    
);

CREATE TABLE Categories (
    c_id INTEGER PRIMARY KEY AUTOINCREMENT,
    c_name varchar(20) not null
);


CREATE TABLE Items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(20) not null,
    weight integer not null,
    price_per_unit int not null,
    c_id INTEGER not null,
    FOREIGN KEY (c_id) REFERENCES Categories(c_id)
);

CREATE TABLE Orders(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    u_id INTEGER not null,
    item_id  integer not null,
    quantity INTEGER not null,
    price INTEGER not null,
    order_dateandtime TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (u_id) REFERENCES User(u_id)
    FOREIGN KEY (item_id) REFERENCES Items(id)
);

CREATE TABLE History(
    order_id INTEGER PRIMARY KEY,
    u_id INTEGER not null,
    item_id  integer not null,
    quantity INTEGER not null,
    price INTEGER not null,
    dat TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (u_id) REFERENCES User(u_id),
    FOREIGN KEY (item_id) REFERENCES Items(id),
	FOREIGN KEY (dat) REFERENCES Orders(order_dateandtime)
  
);
