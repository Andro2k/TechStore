import socket

# Credenciales y Configuración Global
SERVER_ADDR = "localhost"
DB_USER = "sa"
DB_PASS = "P@ssw0rd"

SUPPORTED_TABLES = [
    "SUCURSAL", "PRODUCTO", "INVENTARIO", 
    "CLIENTE", "EMPLEADO", "FACTURA", "DETALLE_FACTURA"
]

NODES = {
    "GUAYAQUIL": {
        "hostnames": ["MiniPC"],
        "db_name": "TechStore_Guayaquil",
        "role": "Publicador (Matriz)",
        "id_sucursal": 1
    },
    "QUITO": {
        "hostnames": ["LAPTOP"], 
        "db_name": "TechStore_Quito",
        "role": "Suscriptor (Sucursal)",
        "id_sucursal": 2
    }
}

def get_current_node_config():
    """Detecta la PC y retorna la configuración del nodo actual."""
    pc_name = socket.gethostname()
    print(f"DEBUG: Nombre de tu PC detectado: '{pc_name}'")
    
    for node_key, config in NODES.items():
        if pc_name.upper() in [h.upper() for h in config["hostnames"]]:
            print(f"DEBUG: Configuración cargada para {node_key}")
            return {"key": node_key, **config}
            
    print(f"ALERTA: PC '{pc_name}' no reconocida. Usando GUAYAQUIL por defecto.")
    return {"key": "GUAYAQUIL", **NODES["GUAYAQUIL"]}

# Ejecutamos esto una vez al importar
CURRENT_NODE = get_current_node_config()