# web_app/app.py (Actualizado)

import sys
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.data_manager import DataManager

app = Flask(__name__)
app.secret_key = "techstore_secret"

manager = DataManager()

# --- RUTAS DE TIENDA ---

@app.route('/')
def index():
    products = manager.get_web_catalog()
    # Inicializar carrito si no existe
    if 'cart' not in session:
        session['cart'] = {}
    return render_template('store.html', products=products, node=manager.current_node['key'])

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    cantidad = int(request.form.get('cantidad', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    # Si ya existe, sumamos; si no, creamos.
    if product_id in cart:
        cart[product_id] += cantidad
    else:
        cart[product_id] = cantidad
    
    session.modified = True # Importante para guardar cambios en diccionarios de sesión
    flash(f"Producto agregado al carrito.", "success")
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total=0)
    
    # Recuperamos detalles completos de productos para mostrar nombres y precios
    all_products = manager.get_web_catalog()
    cart_items = []
    total_general = 0
    
    for prod in all_products:
        p_id = str(prod['id'])
        if p_id in session['cart']:
            qty = session['cart'][p_id]
            subtotal = prod['precio'] * qty
            total_general += subtotal
            cart_items.append({
                "id": p_id,
                "nombre": prod['nombre'],
                "marca": prod['marca'],
                "precio": prod['precio'],
                "qty": qty,
                "subtotal": subtotal
            })
            
    return render_template('cart.html', cart_items=cart_items, total=total_general)

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = {}
    session.modified = True
    return redirect(url_for('index'))

@app.route('/checkout', methods=['POST'])
def checkout():
    # 1. Verificar Login
    if 'client_id' not in session:
        flash("Debes iniciar sesión para finalizar la compra.", "info")
        return redirect(url_for('register_view')) # O login
    
    # 2. Obtener items
    cart = session.get('cart', {})
    if not cart:
        flash("El carrito está vacío.", "warning")
        return redirect(url_for('index'))
    
    # Convertir formato para el backend: [{'id': 1, 'qty': 2}, ...]
    items_to_buy = [{"id": int(k), "qty": v} for k, v in cart.items()]
    client_id = session['client_id']
    
    # 3. Procesar
    success, message = manager.process_web_cart(client_id, items_to_buy)
    
    if success:
        flash(f"¡Éxito! {message}", "success")
        session['cart'] = {} # Vaciar carrito
        session.modified = True
    else:
        flash(f"Error: {message}", "danger")
        
    return redirect(url_for('index'))

# --- RUTAS DE USUARIO ---

@app.route('/register', methods=['GET', 'POST'])
def register_view():
    if request.method == 'POST':
        # (TU LÓGICA DE REGISTRO PREVIA SE MANTIENE IGUAL)
        client_data = {
            "nombre": request.form['nombre'],
            "apellido": request.form['apellido'],
            "correo": request.form['email'],
            "telefono": request.form['telefono'],
            "direccion": request.form['direccion']
        }
        c_id = manager.register_web_client(client_data)
        if c_id:
            session['client_id'] = c_id
            session['client_name'] = client_data['nombre']
            flash(f"Bienvenido {client_data['nombre']}", "success")
            # Si venía del carrito, lo mandamos al carrito
            return redirect(url_for('view_cart'))
        else:
            flash("Error en registro", "danger")
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        email = request.form['email']
        
        # Buscamos al usuario
        user = manager.login_web_client(email)
        
        if user:
            # ¡Exito! Guardamos en sesión
            session['client_id'] = user['id']
            session['client_name'] = user['nombre']
            flash(f"¡Hola de nuevo, {user['nombre']}!", "success")
            
            # Si tenía algo en el carrito, vamos al carrito
            if 'cart' in session and session['cart']:
                return redirect(url_for('view_cart'))
            
            return redirect(url_for('index'))
        else:
            flash("Ese correo no está registrado. Por favor regístrate primero.", "warning")
            return redirect(url_for('register_view'))

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)