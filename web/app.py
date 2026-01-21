# web_app/app.py

import sys
import os
from flask import Flask, render_template, request, redirect, url_for, flash

# --- Truco para importar desde la carpeta hermana 'backend' ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.data_manager import DataManager

app = Flask(__name__)
app.secret_key = "techstore_secret"  # Necesario para mostrar mensajes (flash)

# Instanciamos el manager (Se conectará a la BD configurada en tu PC)
manager = DataManager()

@app.route('/')
def index():
    # Obtenemos los productos con su stock real
    products = manager.get_web_catalog()
    return render_template('store.html', products=products, node=manager.current_node['key'])

@app.route('/buy/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    # Procesar la compra
    success, message = manager.process_web_purchase(product_id)
    
    if success:
        flash(f"¡Éxito! {message}", "success")
    else:
        flash(f"Error: {message}", "danger")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ejecutar en modo debug para ver cambios al instante
    app.run(debug=True, port=5000)