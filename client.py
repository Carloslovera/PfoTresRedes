import socket
import json
import time

# Configuración (debe coincidir con el servidor)
HOST = '127.0.0.1'
PORT = 65432

def enviar_tarea(task_id, descripcion):
    """Conecta con el servidor, envía una tarea y espera el resultado."""
    tarea = {
        "id": task_id,
        "descripcion": descripcion,
        "timestamp": time.time()
    }
    
    print(f"[*] Enviando tarea {task_id} al servidor...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)  # Timeout de 10 segundos para evitar bloqueos infinitos
            s.connect((HOST, PORT))
            
            # Enviar la tarea serializada en JSON
            s.sendall(json.dumps(tarea).encode('utf-8'))
            
            # Recibir la respuesta del servidor
            data = s.recv(1024)
            if data:
                respuesta = json.loads(data.decode('utf-8'))
                print(f"[✓] Respuesta del servidor: {respuesta['estado']}")
                print(f"    Detalle: {respuesta.get('resultado', respuesta.get('mensaje'))}")
            else:
                print("[✗] El servidor no devolvió datos.")
                
    except ConnectionRefusedError:
        print("[✗] Error: No se pudo conectar. ¿Está el servidor encendido?")
    except socket.timeout:
        print("[✗] Error: Tiempo de espera agotado. El servidor tardó demasiado.")
    except Exception as e:
        print(f"[✗] Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    # Simulamos el envío de un par de tareas para probar la concurrencia
    enviar_tarea("TASK-001", "Procesar imagen de usuario y subir a S3")
    print("-" * 50)
    enviar_tarea("TASK-002", "Generar reporte mensual y guardar en PostgreSQL")