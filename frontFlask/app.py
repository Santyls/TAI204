from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

URL_FASTAPI = "http://localhost:5000/v1/usuarios/"

@app.route('/')
def inicio():
    try:
        respuesta = requests.get(URL_FASTAPI)

        datos = respuesta.json()

        lista_usuarios = datos.get("Usuarios",[])

    except:
        lista_usuarios = []
        print("Error: No se pudo conectar con FastAPI")
    
    return render_template('index.html', usuarios=lista_usuarios)

@app.route('/addUser', methods=['POST'])
def addUser():
    try:
        id_form = request.form['id']
        nombre_form = request.form['nombre']
        edad_form = request.form['edad']

        nuevoUsuario = {
            "id": int(id_form),
            "nombre": nombre_form,
            "edad": int(edad_form)
        }

        requests.post(URL_FASTAPI, json=nuevoUsuario)

    except Exception as e:
        print(f"Ocurrio un error al guardar: {e}")
    return redirect(url_for('inicio'))

@app.route('/deleteUser/<int:id>', methods=['POST'])
def deleteUser(id):
    try:
        requests.delete(f"{URL_FASTAPI}{id}")

    except Exception as e:
        print(f"Ocurrio un error al guardar: {e}")
    return redirect(url_for('inicio'))



if __name__ == '__main__':
    # Usamos el puerto 5001 para no chocar con FastAPI (que usa el 5000)
    app.run(debug=True, port=5001)
