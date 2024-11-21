# Propuestas de Chatbots para Cámara de comercio de Bogotá
# Desarrollado por: Carlos Andrés Sierra 
# Librerias generales para ejecutar todos los desarrollos
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, send_from_directory

# Librerias para ejecutar asistente para programadores con API ChatGPT
#import openai
import time

#Codigo sin usar
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


# Librerias de acceso a las base de datos MySQL
import pymysql
from flask_mysqldb import MySQL
import mysql.connector

# Librerias para generación y descarga de archivos PDF
from io import BytesIO
from fpdf import FPDF, HTMLMixin

# Librería para lectura e iteracción de audios
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

# Librerias para subir archivos al servidor
import os
from werkzeug.utils import secure_filename

# Para interactuar audios se requiere instalar libreria FFMPEG
#AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"

# Instrucciones para conectar a la base de datos MySQL
# Conexión a la base de datos opción 1
#db = pymysql.connect(
#    host="servidor",
#    user="usuario",
#    password="clave",
#    database="base de datos"
#)

# Conexión a la base de datos opción 2
#db_config = {
#    'host': 'servidor',
#    'user': 'usuario',
#    'password': 'clave',
#    'database': 'base de datos'
#}

# Conexión a la base de datos opción 3
app = Flask(__name__)
#app.config['MYSQL_HOST'] = 'servidor'
#app.config['MYSQL_USER'] = 'usuario'
#app.config['MYSQL_PASSWORD'] = 'clave'
#app.config['MYSQL_DB'] = 'base de datos'
#mysql = MySQL(app)


# Funcion que se emplea en chatbot de audio para consulta a la base de datos para obtener respuesta segun consulta enviada
def obtener_respuesta(texto_usuario):
    try:
        # Usamos mysql.connection de flask_mysqldb
        conexion = mysql.connection
        cursor = conexion.cursor()

        # Consulta a la base de datos
        cursor.execute("SELECT respuesta FROM respuestas_chatbot WHERE palabra_clave LIKE %s", (f"%{texto_usuario}%",))
        resultado = cursor.fetchone()
        
        if resultado:
            return resultado[0]  # Devolver la respuesta encontrada
        else:
            return "Lo siento, no entendí tu pregunta."
    except Exception as err:
        print(f"Error en la conexión a la base de datos: {err}")
        return "Hubo un problema con la base de datos."
    finally:
        # Cerrar el cursor siempre que sea posible
        if cursor:
            cursor.close()


# Funcion que se emplea en chatbot de audio para procesar audio a texto
def audio_a_texto(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            texto = recognizer.recognize_google(audio_data, language="es-ES")
            return texto
        except sr.UnknownValueError:
            return "No se pudo entender el audio."
        except sr.RequestError as e:
            return f"Error en el servicio de reconocimiento: {e}"

# Funcion que se emplea en chatbot de audio para generar respuesta en audio
def generar_audio(texto, output_path):
    tts = gTTS(text=texto, lang='es')
    tts.save(output_path)

# Funcion que se emplea en chatbot de audio para convertir audio a WAV si es necesario
def convertir_audio_a_wav(audio_path, output_path):
    audio = AudioSegment.from_file(audio_path, format="m4a")
    audio.export(output_path, format="wav")   

# Funcion que se emplea en chatbot de audio es configuración para manejar archivos grandes y la carpeta de subida de audios
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar a 16 MB
app.config['ALLOWED_EXTENSIONS'] = {'m4a'}

# Instrucciones que se emplea en chatbot de audio que asegurarse de que la carpeta 'uploads' exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Funcion que se emplea en chatbot de audio para carga y generación de respuesta
@app.route('/audio', methods=['GET', 'POST'])
def audio_chatbot():
    if request.method == 'POST':
        # Verificar si el archivo está presente en la solicitud
        if 'audio' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        audio_file = request.files['audio']
        
        # Verificar que el archivo tenga un nombre y que sea del tipo permitido
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if audio_file and allowed_file(audio_file.filename):
            # Asegurarse de que el nombre del archivo sea seguro
            filename = secure_filename(audio_file.filename)
            original_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(original_audio_path)
            
            # Convertir el archivo m4a a wav
            wav_audio_path = os.path.splitext(original_audio_path)[0] + ".wav"
            try:
                convertir_audio_a_wav(original_audio_path, wav_audio_path)
            except Exception as e:
                return jsonify({'error': f"Error al convertir el audio: {e}"}), 500
            
            # Convertir audio a texto
            texto_usuario = audio_a_texto(wav_audio_path)
            
            # Buscar respuesta en la base de datos
            respuesta = obtener_respuesta(texto_usuario)
            
            # Generar audio para la respuesta
            audio_respuesta_path = os.path.join('static', 'respuesta.mp3')
            generar_audio(respuesta, audio_respuesta_path)
            
            return jsonify({
                'texto_usuario': texto_usuario,
                'respuesta_texto': respuesta,
                'respuesta_audio': url_for('static', filename='respuesta.mp3')
            })
        else:
            return jsonify({'error': 'Archivo no permitido. Solo archivos .m4a'}), 400

    # Si es un GET, simplemente renderizamos la página de carga de audio
    return render_template('audio.html')

# Funcion que se emplea en chatbot de audio cuando finaliza la sesión
@app.route('/cerrar', methods=['POST'])
def cerrar():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asistente en audio</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    <style>
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        header {
            background-color: #0d6efd;
            color: white;
            padding: 15px 0;
        }
        header h1 {
            margin: 0;
        }
        footer {
            background-color: #0d6efd;
            color: white;
            text-align: center;
            padding: 10px 0;
            margin-top: auto;
        }
        .btn {
            width: 100%;
            margin-top: 10px;
        }
        .container {
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <!-- Encabezado -->
    <header class="text-center">
        <div class="container">
            <h1>Desarrollos CCB</h1>
            <p>Tu plataforma de asistentes inteligentes</p>
        </div>
    </header>
 
    <!-- Contenido principal -->
    <div class="container">
        <div class="row">
            <div class="col-12 text-center mb-4">
                <h1>Sesión finalizada del asistente por audio</h1>
                <a href="/" class="btn btn-primary">Volver a la página de inicio</a>
           </div>
                           
        </div>
    </div>

    <!-- Pie de página -->
    <footer>
        <div class="container">
            <p>&copy; 2024 Desarrollos CCB. Todos los derechos reservados.</p>
        </div>
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
</body>
</html>        


</body>

    """

# API KEY de ChatGPT para asistente para programadores
openai.api_key = 'Aqui va el api de chatgpt'

# Funcion que se emplea en chatbot dinámico (respuestas dinámicas)
def obtener_respuestas():
    # Usamos mysql.connection para obtener la conexión
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute("SELECT palabra_clave, respuesta FROM respuestas_chatbot")
    # Creamos un diccionario con palabras clave separadas por comas
    respuestas = {}
    for palabra_clave, respuesta in cursor.fetchall():
        claves = palabra_clave.split(",")  # Dividir palabras clave por comas
        claves = [clave.strip().lower() for clave in claves]  # Limpiar espacios y poner en minúsculas
        respuestas[",".join(claves)] = respuesta
    cursor.close()
    return respuestas

# Funcion que se emplea en chatbot dinámico (respuestas dinámicas)
@app.route('/api/respuestas', methods=['GET'])
def api_respuestas():
    respuestas = obtener_respuestas()
    return jsonify(respuestas)

# Funcion para servir el archivo index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# Funcion que se emplea en chatbot dinámico (respuestas dinámicas) para servir el archivo dinamico.html
@app.route('/dinamico')
def dinamico():
    return send_from_directory('templates', 'dinamico.html')

# Configuración para servir archivos estáticos (CSS, JS, etc.)
@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# Clase personalizada para soportar HTML
class PDFWithHTML(FPDF, HTMLMixin):
    pass

# Funcion que se emplea en chatbot estático (respuestas predefinidas) Ruta para generar y decargar el archivo PDF
@app.route("/generar_reporte_pdf", methods=["GET"])
def generar_reporte_pdf():
    periodo = request.args.get("periodo", "Desconocido")  # Obtener el periodo de la URL
    
    # Contenido en HTML
    html_content = f"""    
            <!-- Encabezado -->
            <header class='text-center'>
                <div class='container'>
                    <h1>Desarrollos CCB</h1>
                    <p>Tu plataforma de asistentes inteligentes</p>
                </div>
            </header>

            <!-- Contenido principal -->
            <div class='container text-center'>
                <h1>Certificado</h1>
                <p>El usuario con periodo <strong>{periodo}</strong> es afiliado de la organización hasta la fecha.</p>
                <p class='highlight'>Este es un documento generado automáticamente.</p>
            </div>

            <!-- Pie de página -->
            <footer>
                <div class='container'>
                    <p>&copy; 2024 Desarrollos CCB. Todos los derechos reservados.</p>
                </div>
            </footer>

    """

    # Crear el documento PDF
    pdf = PDFWithHTML()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Agregar contenido HTML al PDF
    pdf.write_html(html_content)

    # Crear un objeto BytesIO en memoria para guardar el archivo PDF
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    
    pdf_output.seek(0)  # Volver al inicio del flujo para enviarlo

    # Enviar el archivo PDF al cliente directamente
    return send_file(pdf_output, as_attachment=True, download_name=f"Certificado {periodo}.pdf", mimetype='application/pdf')

# Función del asistente para programadores
def asistente_programacion(pregunta, lenguajes=None, reintentos=3):
    if "error" in pregunta.lower():
        pregunta = f"Analiza el siguiente error técnico: {pregunta}. Proporcióname las causas y posibles soluciones."

    if lenguajes:
        mensaje_lenguajes = f" Proporcióname la solución en los siguientes lenguajes: {', '.join(lenguajes)}."
        pregunta += mensaje_lenguajes

    for intento in range(reintentos):
        try:
            respuesta = openai.ChatCompletion.create(
                #model="gpt-3.5-turbo",
                #messages=[
                    {"role": "system", "content": "Eres un asistente de programación experto en múltiples lenguajes."},
                    {"role": "user", "content": pregunta}
                ]
            )
            return respuesta['choices'][0]['message']['content'].strip()
        #except openai.error.RateLimitError as e:
            print(f"Error de límite de tasa: {e}. Reintentando...")
            time.sleep(2 ** intento)
    return "No se pudo completar la solicitud debido a un límite de tasa."

# Función de asistente para programadores, ruta para guardar consultas técnicas en la base de datos
@app.route('/guardar', methods=['POST'])
def guardar():
    pregunta = request.form.get('pregunta_hidden')
    lenguajes = request.form.get('lenguajes_hidden', None)
    respuesta = request.form.get('respuesta_hidden')

    # Guardar la consulta generada en la base de datos
    conexion = None
    try:
        conexion = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="ccb_dev"
        )
        with conexion.cursor() as cursor:
            query = """
                INSERT INTO dev_query (devquery, devlanguage, devanswer) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (pregunta, lenguajes, respuesta))
            conexion.commit()
        return redirect(url_for('asistente', success='true'))
    except Exception as e:
        print(f"Error al guardar en la base de datos: {e}")
        return redirect(url_for('asistente', success='false'))
    finally:
        if conexion:
            conexion.close()

# Función de asistente para programadores, ruta para eliminar consultas "innecesarias"
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conexion = None
    try:
        conexion = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="ccb_dev"
        )
        with conexion.cursor() as cursor:
            query = "DELETE FROM dev_query WHERE iddev = %s"
            cursor.execute(query, (id,))
            conexion.commit()
        return redirect(url_for('asistente', success='true'))
    except Exception as e:
        print(f"Error al eliminar el registro: {e}")
        return redirect(url_for('asistente', success='false'))
    finally:
        if conexion:
            conexion.close()

# Función de asistente para programadores, ruta de carga del asistente y su historial
@app.route('/asistente', methods=['GET', 'POST'])
def asistente():
    respuesta = ""
    consultas = []
    mensaje = None
    conexion = None

    if request.method == 'POST':
        pregunta = request.form['pregunta']
        lenguajes_input = request.form['lenguajes']
        lenguajes = [lang.strip() for lang in lenguajes_input.split(',')] if lenguajes_input else None
        respuesta = asistente_programacion(pregunta, lenguajes)

    # Obtener historial de consultas
    try:
        conexion = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="ccb_dev"
        )
        with conexion.cursor() as cursor:
            query = "SELECT devquery, devlanguage, devanswer, iddev FROM dev_query ORDER BY iddev DESC"
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Procesar resultados
            if resultados:
                for fila in resultados:
                    consultas.append({
                        "consulta": fila[0],
                        "lenguaje": fila[1] if fila[1] else "N/A",
                        "respuesta": fila[2],
                        "id": fila[3]
                    })
            else:
                mensaje = "No hay consultas guardadas"
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        mensaje = "Error al obtener los datos"
    finally:
        if conexion:
            conexion.close()        
        
    return render_template('asistente.html', respuesta=respuesta, consultas=consultas, mensaje=mensaje)

# Funcion que se emplea en chatbot estático (respuestas predefinidas)
@app.route("/estatico", methods=["GET", "POST"])
def estatico():
    return render_template("estatico.html")

@app.route("/procesar", methods=["POST"])
def procesar():
    option = request.form.get("option")
    
    if option == "1":  # Consultar saldo
        cuenta = request.form.get("cuenta")
        cur = mysql.connection.cursor()
        cur.execute("SELECT saldo FROM cuentas WHERE numero_cuenta = %s", [cuenta])
        saldo = cur.fetchone()
        cur.close()
        
        if saldo:
            message = f"El saldo de la cuenta {cuenta} es de $ {saldo[0]}"
        else:
            message = f"No se encontró la cuenta {cuenta}."
    
    elif option == "2":  # Calcular préstamo
        monto = float(request.form.get("monto"))
        plazo = int(request.form.get("plazo"))
        tasa_interes = 0.05
        pago_mensual = (monto * tasa_interes) / (1 - (1 + tasa_interes) ** -plazo)
        message = f"Para un préstamo de ${monto} a {plazo} meses, el pago mensual será de: ${pago_mensual:.2f}"
    
    elif option == "3":  # Generar reporte
        periodo = request.form.get("periodo")
        message = f"Reporte generado para el usuario {periodo}."
    
    else:
        message = "Opción no válida."

    return jsonify({"message": message})

# Ejecutar la aplicación
if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static', exist_ok=True)    
    app.run(debug=True)