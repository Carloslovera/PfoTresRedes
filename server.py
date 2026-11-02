import socket
import threading
import json
import time
from concurrent.futures import ThreadPoolExecutor

# Configuración del servidor
HOST = '127.0.0.1'
PORT = 65432
MAX_WORKERS = 3  # Simula los "servidores workers" con pool de hilos

def procesar_tarea(task_id, descripcion):
    """Simula el procesamiento de una tarea por un worker."""
    print(f"[Worker] Procesando tarea {task_id}: {descripcion}")
    time.sleep(2)  # Simula tiempo de cómputo o consulta a DB/S3
    
    # Aquí iría la lógica real: enviar a RabbitMQ, guardar en PostgreSQL, etc.
    resultado = f"Tarea {task_id} completada con éxito. Datos procesados."
    return resultado

def manejar_cliente(conn, addr):
    """Maneja la comunicación con un cliente individual."""
    print(f"[Servidor] Conexión establecida con {addr}")
    try:
        with conn:
            # Recibir datos del cliente
            data = conn.recv(1024)
            if not data:
                return
            
            tarea = json.loads(data.decode('utf-8'))
            task_id = tarea.get('id', 'DESCONOCIDO')
            descripcion = tarea.get('descripcion', 'Sin descripción')
            
            # Distribuir la tarea al pool de workers
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futuro = executor.submit(procesar_tarea, task_id, descripcion)
                resultado = futuro.result()  # Espera el resultado del worker
            
            # Enviar respuesta al cliente
            respuesta = json.dumps({"estado": "exitoso", "resultado": resultado})
            conn.sendall(respuesta.encode('utf-8'))
            
    except json.JSONDecodeError:
        print(f"[Error] Datos JSON inválidos recibidos de {addr}")
        conn.sendall(json.dumps({"estado": "error", "mensaje": "JSON inválido"}).encode('utf-8'))
    except Exception as e:
        print(f"[Error] Fallo al procesar la tarea de {addr}: {e}")
    finally:
        print(f"[Servidor] Conexión cerrada con {addr}")

def iniciar_servidor():
    """Inicia el socket server y queda a la espera de conexiones."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Permitir reutilizar la dirección inmediatamente al reiniciar
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Servidor escuchando en {HOST}:{PORT}...")
        
        while True:
            conn, addr = s.accept()
            # Cada cliente se maneja en un hilo independiente para no bloquear el servidor
            thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    iniciar_servidor()