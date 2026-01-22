# web_app/app.py

import sys
import os
# AGREGAMOS 'session' a los imports
from flask import Flask, render_template, request, redirect, url_for, flash, session

# ... (Tus imports de path y DataManager siguen igual) ...
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.data_manager import DataManager

app = Flask(__name__)
app.secret_key = "techstore_secret"

manager = DataManager()

@app.route('/')
def index():
    products = manager.get_web_catalog()
    # Pasamos si el usuario está logueado para mostrar algo diferente en el HTML
    user_logged_in = 'client_id' in session
    return render_template('store.html', products=products, node=manager.current_node['key'], logged_in=user_logged_in)

@app.route('/buy/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    # 1. VERIFICAR SI EL USUARIO YA SE REGISTRÓ
    if 'client_id' not in session:
        session['pending_product_id'] = product_id
        flash("Por favor, regístrate antes de completar la compra.", "info")
        return redirect(url_for('register_view'))

    # 2. OBTENER ID DEL CLIENTE
    client_id = session['client_id']

    # 3. PROCESAR COMPRA CON EL CLIENTE
    # --- CAMBIO AQUÍ: Pasamos el client_id ---
    success, message = manager.process_web_purchase(product_id, client_id)
    
    if success:
        flash(f"¡Compra exitosa! {message}", "success")
        session.pop('pending_product_id', None)
    else:
        flash(f"Error: {message}", "danger")
        
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register_view():
    if request.method == 'POST':
        # Recopilar datos del formulario
        client_data = {
            "cedula": request.form['cedula'],
            "nombre": request.form['nombre'],
            "apellido": request.form['apellido'],
            "correo": request.form['email'],     # Ojo con el name en el HTML
            "telefono": request.form['telefono'],
            "direccion": request.form['direccion']
        }
        
        # Guardar en BD
        client_id = manager.register_web_client(client_data)
        
        if client_id:
            # Guardar en sesión (LOGIN EXITOSO)
            session['client_id'] = client_id
            session['client_name'] = client_data['nombre']
            flash(f"Bienvenido, {client_data['nombre']}. Registro exitoso.", "success")
            
            # ¿Tenía una compra pendiente?
            pending_prod = session.get('pending_product_id')
            if pending_prod:
                # Redirigir automáticamente a comprar el producto que quería
                # Usamos un truco para llamar a la ruta de compra (código 307 mantiene el POST)
                # O simplemente redirigimos a una ruta intermedia. Por simplicidad:
                return buy_product(pending_prod)
            
            return redirect(url_for('index'))
        else:
            flash("Error al registrar. Verifica los datos.", "danger")

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)