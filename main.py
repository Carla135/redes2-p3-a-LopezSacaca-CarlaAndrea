import requests
import csv
import json
from io import StringIO
from http.server import BaseHTTPRequestHandler, HTTPServer

# Paso 1: Descargar archivo desde URL
def descargar_datos():
    url = "https://mochila.laotra.red/public.php/dav/files/9TcBaPFWMQiEMsn/"
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response.text

# Paso 2: Parsear el contenido CSV a lista de diccionarios
def parsear_csv(texto_csv):
    csv_io = StringIO(texto_csv)
    lector = csv.DictReader(csv_io)
    datos = []

    for fila in lector:
        # Valores que pueden faltar
        fila["he_capa"] = fila.get("he_capa") or None
        fila["he_phy_capa"] = fila.get("he_phy_capa") or None
        # Extras opcionales si deseas puntos extra
        fila["channel utilisation"] = normalizar_channel(fila.get("channel utilisation"))
        fila["station count"] = convertir_entero(fila.get("station count"))
        datos.append(fila)

    return datos

def normalizar_channel(valor):
    try:
        val = float(valor)
        return round(val / 255, 3)
    except:
        return None

def convertir_entero(valor):
    try:
        return int(valor)
    except:
        return None

# Paso 3: Servidor HTTP que responde en /air
class Manejador(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/air":
            texto_csv = descargar_datos()
            datos_json = parsear_csv(texto_csv)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(datos_json, indent=2).encode("utf-8"))
        else:
            self.send_error(404, "Ruta no encontrada")

# Paso 4: Iniciar el servidor
if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Manejador)
    print("Servidor HTTP corriendo en puerto 8000...")
    server.serve_forever()
