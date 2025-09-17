import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    # sqlite3.Row factory allows you to access columns by name, which makes the code more readable.
 
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM Items WHERE id = ?',(post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post
    
    
       
app = Flask(__name__) 
# initializes your Flask application.
app.config['SECRET_KEY']= 'your secret key'


@app.route('/')
def index():
 return render_template('index.html')
	
	
@app.route('/sign_in' ,methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        conn=sqlite3.connect("database.db")
        c=conn.cursor() 
        c.execute("SELECT * FROM Admin WHERE username = '"+username+"' and password = '"+password+"'") 
        r = c.fetchall()
        for i in r:
            
            if(username == i[1] and password == i[2]):
                session["logedin"] = True
                session["username"]=username
                return redirect(url_for('category'))
            else:
                flash('Title is required!')

        conn.commit()
        conn.close    
    return render_template('sign_in.html')

	
# This route correctly retrieves and displays categories and handles the creation of new ones.
@app.route('/category',methods=('GET','POST'))
def category():
        conn = get_db_connection()
        categories = conn.execute('SELECT * FROM Categories').fetchall()
        conn.close()
        if request.method == 'POST':
            category_name = request.form['category_name']
            if not category_name:
                flash('Category name is required!')
            else:
                conn=get_db_connection()
                conn.execute('INSERT INTO Categories (c_name) VALUES (?)',(category_name,))
                conn.commit()
                conn.close()
                return redirect(url_for('category'))
        return render_template('category.html',categories=categories) 


# This route handles updating a category's name.
@app.route('/<int:c_id>/c_edit', methods=('GET', 'POST'))
def c_edit(c_id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM Categories WHERE c_id=?',(c_id,)).fetchone()
    conn.close()
	
    if request.method == 'POST':
        category_name = request.form['category_name']
        if not category_name:
            flash('Name is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE Categories SET c_name = ? WHERE c_id = ?',(category_name,c_id))
            conn.commit()
            conn.close()
            return redirect(url_for('category'))
    return render_template('c_edit.html',category=category)
        
        

# This route deletes a category.
@app.route('/<int:c_id>/c_delete', methods=('GET', 'POST'))
def c_delete(c_id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM Categories WHERE c_id=?',(c_id,)).fetchone()
    conn.execute('DELETE from Categories WHERE c_id = ?',(c_id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(category['c_name']))
    return redirect(url_for('category'))      
        
        

# This route handles item creation and retrieval.
@app.route('/category/<int:c_id>/items_list', methods=('GET', 'POST'))
def items_list(c_id):
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Items WHERE c_id=?',(c_id,)).fetchall()
    conn.close()
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_wt = request.form['item_wt']
        price_per_unit= request.form['price_per_unit']
        if not item_name:
            flash('Category name is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO Items (name, weight, price_per_unit, c_id) VALUES (?, ?, ?, ?)',(item_name, item_wt, price_per_unit, c_id))
            conn.commit()
            conn.close()
            return redirect(url_for('items_list',c_id=c_id))
    return render_template('items_list.html',items=items)
    
    

# /add_stock, /item_edit, /delete: These routes handle stock updates and item deletions. 

@app.route('/<int:c_id>/<int:id>/add_stock', methods=('GET', 'POST'))
def add_stock(c_id,id):
	item=get_post(id)
	if request.method == 'POST':
		newstock_wt = request.form['newstock_wt']
		if not newstock_wt:
			flash('Enter valid input!')
		else:
			conn = get_db_connection()
			add = float(newstock_wt) + float(item['weight'])
			conn.execute('UPDATE Items SET weight=? WHERE id = ?',(add, id))
			conn.commit()
			conn.close()
			return redirect(url_for('items_list',c_id=c_id))
	return render_template('add_stock.html',item=item)   
    
   
   	
@app.route('/<int:c_id>/<int:id>/item_edit', methods=('GET', 'POST'))
def item_edit(c_id,id):
    item=get_post(id)
    if request.method == 'POST':
        item_name=request.form['item_name']
        price_per_unit=request.form['price_per_unit']
        if not item_name:
            flash('Error!')
        else:
                conn = get_db_connection()
                conn.execute('UPDATE Items SET name = ?,price_per_unit= ? WHERE id = ?',(item_name,price_per_unit, id))
                conn.commit()
                conn.close()
                return redirect(url_for('items_list',c_id=c_id))
    return render_template('item_edit.html',item=item)  	
   	
   	
   	 	
@app.route('/<int:c_id>/<int:id>/delete', methods=('GET', 'POST'))
def delete(c_id,id):
	item=get_post(id)
	conn = get_db_connection()
	conn.execute('DELETE from Items  WHERE id = ?',(id,))
	conn.commit()
	conn.close()
	flash('"{}" was successfully deleted!'.format(item['name']))
	return redirect(url_for('items_list',c_id=c_id))  	
   	
   	
   	
@app.route('/user_signin', methods=['GET', 'POST'])
def user_signin():
    if request.method == 'POST':
        username=request.form['u_username']
        password=request.form['u_password']
        conn=sqlite3.connect("database.db")
        c=conn.cursor() 
        c.execute("SELECT * FROM User WHERE u_username = '"+username+"' and u_password = '"+password+"'") 
        r = c.fetchall()
        for i in r:
            
            if(username == i[1] and password == i[2]):
                session["logedin"] = True
                session["username"]=username
                session["id"]=i[0]
                return redirect(url_for('u_category'))
            else:
                flash('Title is required!')

        conn.commit()
        conn.close    
    return render_template('user_signin.html')
	


# /u_category, /u_items_list: These routes are for the user to browse categories and items. They correctly fetch data.
@app.route('/u_category',methods=('GET','POST'))
def u_category():
        conn = get_db_connection()
        categories = conn.execute('SELECT * FROM Categories').fetchall()
        conn.close()
        return render_template('u_category.html',categories=categories)  
        
        
        
@app.route('/u_category/<int:c_id>/u_items_list', methods=('GET', 'POST'))
def u_items_list(c_id):
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Items WHERE c_id=?',(c_id,)).fetchall()
    conn.close()
    return render_template('u_items_list.html',items=items,c_id=c_id)
    


# his route handles placing an order. It checks for stock availability and updates the database accordingly.
@app.route('/u_category/<int:c_id>/u_items_list/<int:i_id>/pre_book',methods=['GET','POST'])
def pre_book(c_id,i_id):
	item=get_post(i_id)
	print(item['weight'])
	if item['weight'] == 0:
		flash('Out of stock!')
		return redirect(url_for('u_items_list',c_id=c_id))
	if request.method=='POST':
		item_wt=request.form['item_wt']
		if not item_wt:
			flash('weight is required!')
		else:
			conn = get_db_connection()
			add = float(item['weight']) - float(item_wt)
			price = float(item_wt) * item['price_per_unit']
			if add<0:
				flash('only "{}" is available!'.format(item['weight']))
			else:
				conn.execute('UPDATE Items SET weight=? WHERE id = ?',(add,i_id))
				conn.commit()
				conn.close()
				conn=get_db_connection()
				print("sdfdgsdfgsdfgsdfg")
				conn.execute('INSERT INTO Orders (u_id,item_id,quantity,price) VALUES (?,?,?,?)',(session["id"],i_id, item_wt, price))
				conn.commit()
				conn.close()
				return redirect(url_for('u_items_list',c_id=c_id))
	return render_template('pre_book.html',item=item)





@app.route('/orders', methods=('GET', 'POST'))
def orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM( Orders inner join Items on item_id=id)inner join User on User.u_id=Orders.u_id').fetchall()
    conn.close()
    if request.method == 'POST':
        u_id=request.form['u_id']
        if not u_id:
            flash('user_id is required!')
        else:
            conn=get_db_connection()
            u_orders=conn.execute('SELECT * FROM( Orders inner join Items on item_id=id)inner join User on User.u_id=Orders.u_id WHERE Orders.u_id = ?',(u_id,)).fetchall()
            return render_template('orders.html',orders=u_orders,u_id=u_id)
    return render_template('orders.html',orders=orders)
    



@app.route('/<int:order_id>/collected', methods=('GET', 'POST'))
def collected(order_id):
    conn=get_db_connection()
    order= conn.execute('SELECT * FROM Orders WHERE order_id = ?',(order_id,)).fetchone()
    conn.close()
    conn=get_db_connection()
    conn.execute('INSERT INTO History (order_id,u_id,item_id,quantity,price) VALUES (?,?,?,?,?)',(order['order_id'],order['u_id'],order['item_id'], order['quantity'],order['price']))
    conn.commit()
    conn.close()
    conn=get_db_connection()
    conn.execute('DELETE from Orders WHERE order_id = ?',(order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('orders'))
    



@app.route('/<int:order_id>/delete_order', methods=('GET', 'POST'))
def delete_order(order_id):
    conn=get_db_connection()
    order= conn.execute('SELECT * FROM Orders WHERE order_id = ?',(order_id,)).fetchone()
    conn.close()
    item=get_post(order['item_id'])
    q=order['quantity']
    add=float(q)+float(item['weight'])
    conn=get_db_connection()
    conn.execute('UPDATE Items SET weight=? WHERE id = ?',(add, order['item_id']))
    conn.commit()
    conn.close()
    conn=get_db_connection()
    conn.execute('DELETE from Orders  WHERE order_id = ?',(order_id,))
    conn.commit()
    conn.close()
    flash('order_id = "{}" was successfully deleted!'.format(order['order_id']))
    return redirect(url_for('orders'))
    



    
@app.route('/history', methods=('GET', 'POST'))
def history():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM (History inner join User on History.u_id=User.u_id) inner join Items on Items.id=item_id').fetchall()
    conn.close()
    if request.method == 'POST':
        u_id=request.form['u_id']
        if not u_id:
            flash('user_id is required!')
        else:
            conn=get_db_connection()
            u_orders=conn.execute('SELECT * FROM( History inner join Items on item_id=id)inner join User on User.u_id=History.u_id WHERE History.u_id = ?',(u_id,)).fetchall()
            return render_template('history.html',orders=u_orders,u_id=u_id)
    return render_template('history.html',orders=orders)
    
    
@app.route('/user_orders', methods=('GET', 'POST'))
def user_orders(): 
    conn=get_db_connection()
    user_orders= conn.execute('SELECT * FROM Orders inner join Items on item_id=id WHERE u_id=?',(session["id"],)).fetchall()
    conn.close()
    return render_template('user_orders.html',orders=user_orders)
    
@app.route('/<int:order_id>/cancel_order', methods=('GET', 'POST'))
def cancel_order(order_id):
    conn=get_db_connection()
    order= conn.execute('SELECT * FROM Orders WHERE order_id = ?',(order_id,)).fetchone()
    conn.close()
    item=get_post(order['item_id'])
    q=order['quantity']
    add=float(q)+float(item['weight'])
    conn=get_db_connection()
    conn.execute('UPDATE Items SET weight=? WHERE id = ?',(add, order['item_id']))
    conn.commit()
    conn.close()
    conn=get_db_connection()
    conn.execute('DELETE from Orders  WHERE order_id = ?',(order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('user_orders'))



@app.route('/user_history', methods=('GET', 'POST'))
def user_history():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM History inner join Items on item_id=id where u_id = ?',(session['id'],)).fetchall()
    print(session['id'])
    conn.close()
    return render_template('user_history.html',orders=orders)
    
    
@app.route('/out_of_stock', methods=('GET', 'POST'))
def out_of_stock():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Items WHERE weight=?',(0,)).fetchall()
    conn.close()
    return render_template('out_of_stock.html',items=items)



@app.route('/<int:id>/add_stock', methods=('GET', 'POST'))
def out_of_stock_add(id):
	item=get_post(id)
	if request.method == 'POST':
		newstock_wt = request.form['newstock_wt']
		if not newstock_wt:
			flash('weight is required!')
		else:
			conn = get_db_connection()
			add = float(newstock_wt) + float(item['weight'])
			conn.execute('UPDATE Items SET weight=? WHERE id = ?',(add, id))
			conn.commit()
			conn.close()
			return redirect(url_for('out_of_stock'))
	
	return render_template('out_of_stock_add.html',item=item)
	
@app.route('/add_user' ,methods=['GET', 'POST'])  	
def add_user():
    if request.method == 'POST':
        username=request.form['u_username']
        password=request.form['u_password']
        email=request.form["u_email"]
        conn=get_db_connection()
        conn.execute('INSERT INTO User (u_username,u_password) VALUES(?,?)',(username,password))
        conn.commit()
        conn.close()
        return render_template('add_user.html')
    return render_template('add_user.html')
