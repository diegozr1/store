from flask import Flask, render_template, request, session, redirect, url_for
from forms import SignupForm, LoginForm, AddProduct, ProfileForm
from requests.exceptions import HTTPError
from werkzeug.utils import secure_filename

import pyrebase
import paypalrestsdk
import os, json

app = Flask(__name__)

firebaseConfig = {
  "apiKey": "AIzaSyBo7Dz-u1D50-NJJamr-07ed_nGCWhUsd4",
  "authDomain": " store-d5505.firebaseapp.com",
  "databaseURL": "https://store-d5505.firebaseio.com",
  "storageBucket": " store-d5505.appspot.com",
  "serviceAccount":"./store-2d561b9ee134.json"
}

app.secret_key = b"\xfe\xe8`'\xcd\x92Qh\xc4,v\xaaI9jN\x1eN\xa8\xaeo\xde\xf8`"

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

db = firebase.database()

#upload pictures
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'ico'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    info = db.child("stock").get().val()
    return render_template("index.html", info = info, login = login, admin =admin)

@app.route("/products/<category>")
def products(category):
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    info = db.child("stock").order_by_child("category").equal_to(category).get().val()
    return render_template("products.html", info = info, category = category, login = login, admin =admin)


@app.route("/account", methods = ['GET'])
def account():
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    form_login = LoginForm()
    form_signup = SignupForm()
    if request.method == 'GET':
        if "email" in session:
            return redirect(url_for('profile'))
        else:
            return render_template("account.html", form_login = form_login, form_signup = form_signup, login = login, admin =admin)
    
    
@app.route("/signup", methods = ["POST","GET"])    
def signup():
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    form_signup = SignupForm()
    form_login = LoginForm()
    if request.method == "POST":
        if form_signup.validate():
            try:
                user = auth.create_user_with_email_and_password(form_signup.email.data, form_signup.password.data)
                session['localId'] = user['localId']
                session['email'] = form_login.email.data
                session['user_type'] = 'regular'
                data = {
                    'fname': form_signup.first_name.data,
                    'lname': form_signup.last_name.data,
                    'address': form_signup.address.data,
                    'cp': form_signup.cp.data,
                    'email': form_signup.email.data,
                    'user_type': 'regular'
                }
                db.child('users').child(session['localId']).set(data)
                if "shoppingcart" not in session:
	                session['shoppingcart'] = []
                return redirect(url_for('index'))
            except HTTPError as e:
                return render_template("account.html", form_login = form_login, form_signup = form_signup, message = "Ese correo ya esta registrado", login = login, admin =admin)
                
        else:
            return render_template("account.html", form_login = form_login, form_signup = form_signup, login = login, admin =admin)
    else:
        return redirect(url_for("account"))
    
    
@app.route("/login", methods = ["POST", "GET"])    
def login():
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    form_login = LoginForm()
    form_signup = SignupForm()
    if request.method == 'POST':
        if form_login.validate():
            try:
                email = form_login.email.data
                password = form_login.password.data
                user = auth.sign_in_with_email_and_password(email, password)
                session['cart'] = []
                session['localId'] = user['localId']
                session['email'] = email
                info = db.child("users").child(session['localId']).get().val()
                session['fname'] = info['fname']
                session['lname'] = info['lname']
                session['user_type'] = info['user_type']
                if "shoppingcart" not in session:
	                session['shoppingcart'] = []
                return redirect(url_for('index'))
            except HTTPError as e:
                return render_template("account.html", form_login = form_login, form_signup = form_signup, message = 'Por favor revise sus datos', login = login, admin =admin)
        else:
             return render_template("account.html", form_login = form_login, form_signup = form_signup, login = login, admin =admin)
    else:
        return redirect(url_for("account"))

@app.route("/edit_stock/<pid>", methods = ["POST", "GET"])
def editStock(pid):
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    form_modify = AddProduct()
    info = db.child("stock").child(pid).get().val()
    if request.method == 'POST':
        try:
            pdata = {
                'pname': form_modify.product_name.data,
                'price': form_modify.price.data,
                'category': form_modify.category.data,
                'descrip': form_modify.description.data,
                'stock':  form_modify.stock.data
        	}
        	
            ndata={}
            
            for key in info:
                if info[key] != pdata[key]:
                    ndata[key] = pdata[key]
            if ndata:
                db.child("stock").child(pid).update(ndata)
                info = db.child("stock").child(pid).get().val()
                
            return render_template("edit_stock.html", pid = pid , info = info, form_modify = form_modify, success = "Los cambios han sido guardados", login = login, admin =admin)
        except HTTPError as e:
            return render_template("edit_stock.html", pid = pid ,info = info, form_modify = form_modify, message = "Ha ocurrido un error", login = login, admin =admin)
    else:
        if "email" in session:
            if session['user_type'] == "admin":
                return render_template("edit_stock.html", pid = pid, form_modify = form_modify, info = info , login = login, admin =admin)
            else:
                return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))

@app.route("/add_stock", methods = ["POST", "GET"])
def product():
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    form_addstock = AddProduct()
    if "email" in session:
        if session['user_type'] == 'admin':
            if request.method == "POST":
                if form_addstock.validate():
                    try:
                        pname = form_addstock.product_name.data
                        price = form_addstock.price.data
                        category = form_addstock.category.data
                        descrip = form_addstock.description.data
                        stock = form_addstock.stock.data
                        
                        # file upload  
                        if 'file' not in request.files:
                            return redirect(request.url)
                        file = request.files['file']
                        # if user does not select file, browser also
                        # submit a empty part without filename
                        if file.filename == '':
                            return redirect(request.url)
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            #return redirect(url_for('uploaded_file',filename=filename))
                        data = {
                            'pname' : pname,
                            'price' : price,
                            'category': category,
                            'descrip' : descrip,
                            'stock' : stock,
                            'image': filename
                        }
                        db.child('stock').push(data)
                        return render_template("admin.html", form_addstock = form_addstock, success = 'El articulo se agrego de manera exitosa', login = login, admin =admin)
                    except HTTPError as e:
                        return render_template("admin.html", form_addstock = form_addstock, request_error = 'Ocurrio un error al realizar la operacion', login = login, admin =admin)
                else:
                    return render_template("admin.html", form_addstock = form_addstock, request_error = 'Ocurrio un error al realizar la operacion', login = login, admin =admin)
            else:
                return render_template("admin.html", form_addstock = form_addstock, login = login, admin =admin)
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
        
@app.route("/checkout")
def checkout():
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    if request.method == "GET":
        if "email" in session:
            cart = db.child("cart/"+session["localId"]).get().val()
            if cart is None:
                return render_template("checkout.html", login = login, admin =admin)
            else :
                return render_template("checkout.html", cart = cart, login = login, admin =admin)
                
        else:
            return redirect(url_for("login"))
    elif request.method == "POST":
        return redirect(url_for("checkout")) 
        
@app.route("/add_cart/<name>/<price>/<amount>")
def add(name, price, amount):
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    if "email" in session:
        data = {'name':name, 'price':price, 'amount':amount}
        db.child("cart/"+session["localId"]).push(data)
        return redirect(url_for("checkout"))
    else:
        return redirect(url_for("index"))

	
@app.route("/single/<pid>", methods = ["GET", "POST"])
def single(pid):
    info = db.child("stock").child(pid).get().val()
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    
    if request.method == "POST":
        
        amount = request.form.get('amount')
        if info['stock'] < int(amount):
            message = "No hay suficientes articulos en almacen. La cantidad disponible es " + str(info['stock'])
            return render_template("single.html", pid = pid, info = info, message = message, login = login, admin =admin)
        else:
            data = {
                'name' : info['pname'],
                'price' : info['price'],
                'amount' : amount
            }
            db.child("cart").child(session['localId']).push(data)
            return redirect(url_for('index'))
    else:
        return render_template("single.html", pid = pid, info = info, login = login, admin =admin)

@app.route("/recent")
def recent():
    
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    
    return render_template("recent.html", login = login, admin =admin)
 
@app.route("/profile", methods = ['GET', 'POST']) 
def profile():
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    form_profile = ProfileForm()
    info = db.child("users").child(session['localId']).get().val()
    if request.method == 'POST':
        try:
            pdata = {
                'fname': form_profile.first_name.data,
                'lname': form_profile.last_name.data,
                'address': form_profile.address.data,
                'cp': form_profile.cp.data,
                'email': session['email'],
                'user_type': info['user_type']
        	}
        	
            ndata={}
            
            for key in info:
                if info[key] != pdata[key]:
                    ndata[key] = pdata[key]
            if ndata:
                db.child("users").child(session['localId']).update(ndata)
                info = db.child("users").child(session['localId']).get().val()
                
            return render_template("profile.html", info = info, form_profile = form_profile, success = "Los cambios han sido guardados", login = login, admin =admin)
        except HTTPError as e:
            return render_template("profile.html", info = info, form_profile = form_profile, message = "Ha ocurrido un error", login = login, admin =admin)
    else:
        if "email" in session:
            return render_template("profile.html", info = info, form_profile = form_profile, login = login, admin =admin)
        else:
            return redirect(url_for('account'))
    
@app.route("/manage_stock")
def manage_stock():
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    if "email" in session:
        if session['user_type'] == 'admin':
            info = db.child("stock").get().val()
            return render_template("controlpanel.html", info = info, login = login, admin =admin)
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
   
@app.route("/delete_product/<pid>")
def delete_product(pid):
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    if "email"in session:
        if session['user_type'] == "admin":
            db.child("stock").child(pid).remove()
            return redirect(url_for('manage_stock'))
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    
@app.route("/delete_car/<product>")
def delete_car(product):
    if "email" in session:
        login = 1
        if session['user_type'] == "admin":
            admin = -1
        else:
            admin =0
    else:
        login = 0
        admin = 0
    if "email"in session:
        if session['user_type'] == "admin":
            db.child("cart").child(session["localId"]).child(product).remove()
            return redirect(url_for('checkout'))
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))    
    
@app.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("localId", None)
    session.pop("fname", None)
    session.pop("lname", None)
    session.pop("user_type", None)
    session.pop("cart", None)
    return redirect(url_for('index'))
    
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404        


if __name__ == "__main__":
    app.run(host=os.getenv('IP'), port = int(os.getenv('PORT', 8080)))