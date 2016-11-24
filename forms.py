from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class SignupForm(FlaskForm):
    first_name = StringField('First name', validators = [DataRequired("Ingresa tu primer nombre")])
    last_name = StringField('Last name', validators = [DataRequired("Ingresa tu apellido")])
    email = StringField('Email', validators = [DataRequired("Ingresa tu correo"), Email("Ingresa tu correo correcto")])
    password = PasswordField('Password', validators = [DataRequired("Ingresa la contraseña"), Length(min=6, message="La contraseña tiene que ser de mínimo 6 caracteres"), EqualTo('confirm', message = 'Las contraseñas deben coincidir')])
    address = StringField('Address', validators = [DataRequired("Ingresa tu direccion")])
    cp = StringField('Postal Code', validators = [DataRequired("Ingresa tu codigo postal"), Length(5)])
    confirm = PasswordField('Repita su contraseña')
    submit = SubmitField('Registrarme')

class ProfileForm(FlaskForm):
    first_name = StringField('First name', validators = [DataRequired("Ingresa tu primer nombre")])
    last_name = StringField('Last name', validators = [DataRequired("Ingresa tu apellido")])
    address = StringField('Address', validators = [DataRequired("Ingresa tu direccion")])
    cp = StringField('Postal Code', validators = [DataRequired("Ingresa tu codigo postal")])
    submit = SubmitField('Editar Perfil')    

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired("Ingresa tu correo"), Email("Ingresa tu correo correcto")])
    password = PasswordField("Password", validators=[DataRequired("Ingresa la contraseña")])
    submit = SubmitField("Entrar")
    
class AddProduct(FlaskForm):
    product_name = StringField('Product name', validators = [DataRequired("Ingrese el nombre del producto")])
    price = IntegerField('Price', validators = [DataRequired("Ingrese el precio del producto")])
    category = SelectField('Category', choices = [("Hombre","Hombre"),("Mujer","Mujer"),("Niños","Niños")])
    description = StringField('Product Description', validators = [DataRequired("Ingrese la descripcion del producto")])
    stock = IntegerField('Stock', validators = [DataRequired("Ingrese el stock de producto")])
    submit = SubmitField("Agregar Articulo")
