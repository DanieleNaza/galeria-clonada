import os

from bson import ObjectId
from flask import Flask, redirect, render_template, request
from flask_mail import Mail, Message
from pymongo import MongoClient
from werkzeug.utils import secure_filename


"""
HOLA , he intentado de varias formas hacer el trabajo  el cual me costo un poco, 
me parecio mejor opcino, poder comentar  y usar el trabajo de la carpeta de solucion
por que me quedaba mas claro a mi, poder entenderlo,  mejor ordenado, y el cual para seguir practicando me es mejor.
he logrado entender el codigo del trabajo soluicion, entendi su funcionalidad y a que se refiere en cada linea,
lo que me da tranquilidad a pesar de haberlo intentado de vairas maneras, doonde me quedaba un codigo
bastante extenso, incomprendible y que no me  iba ayudar en algun momento entender las lineas de codigo que esribi.
"""




EXTENSIONES = ["png", "jpg", "jpeg"]
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./static/fondos"

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.fondos_flask
misfondos = db.fondos

app.config["MAIL_SERVER"]= "mail.cepibase.int"
app.config["MAIL_PORT"] = 25
app.config["MAIL_USERNAME"] = "USUARIO"
app.config["MAIL_PASSWORD"] = "PASSWORD"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = False
mail= Mail(app)

def archivo_permitido(nombre):
    return "." in nombre and nombre.rsplit(".", 1)[1] in EXTENSIONES
#definimos que tipos de archivos seran permitidos

@app.route("/", methods=["GET", "POST"])
@app.route("/galeria")
def galeria():
    t=request.values.get("tema")
    estilos={}
    if t == None: 
        l=misfondos.find() #se buscara el tema introducido, donde indicamos que l sera igual patron que busque en la subcadena de misfondos """
        estilos["todos"]="active" 
    else:
        l=misfondos.find({"tags": {"$in":[t]}}) #si l es igual al patron que "t"
        estilos[t]="active"  #se activara en estilos
    return render_template("index.html",activo=estilos,lista=l) #retornando  el template index con lo encontrado

@app.route("/aportar")
def aportar():
    return render_template("aportar.html")  #llamamos al template aportar

@app.route("/insertar", methods=["POST"])
def insertar():
    f = request.files["archivo"]
    if f.filename == "":
         return render_template("aportar.html",mensaje="Hay que indicar un archivo de fondo")
    else:
        if archivo_permitido(f.filename):
            archivo = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], archivo))
        else:
             return render_template("aportar.html",mensaje="¡El archivo indicado no es una imagen!")

    tit = request.values.get("titulo")
    desc = request.values.get("descripcion")
    tags=[]
    if request.values.get("animales"):
        tags.append("animales")
    if request.values.get("naturaleza"):
        tags.append("naturaleza")
    if request.values.get("ciudad"):
        tags.append("ciudad")
    if request.values.get("deporte"):
        tags.append("deporte")
    if request.values.get("personas"):
        tags.append("personas")
    misfondos.insert_one({"titulo":tit, "descripcion":desc, "fondo": archivo, "tags":tags})
    return redirect("/")
 
#con esas lineas de codigo
#le añadimos las etiquetas de caracteristicas a los archivos que se añadan


@app.route("/form_email")
def formulario_email():
    id=request.values.get("_id")  #la variable id tiene que ser igual a la del usuario 
    documento=misfondos.find_one({"_id":ObjectId(id)}) #le indicamos que documento sera igual al archivo que busque con el id 
    return render_template("form_email.html", id=id, fondo=documento["fondo"], #retornandole  el tempplate de email con su fopndo y las caracteristicas
     titulo=documento["titulo"], descripcion=documento["descripcion"])

@app.route("/email", methods=["POST"])
def enviaemail():
    id=request.values.get("_id")
    documento=misfondos.find_one({"_id":ObjectId(id)})
    msg = Message("Fondos de pantalla Flask", sender = "alumno@cepibase.int")
    msg.recipients = [request.values.get("email")]
    msg.body = "Este es el fondo de pantalla seleccionado de nuestra galería."
    msg.html = render_template("email.html", titulo=documento["titulo"], descripcion=documento["descripcion"])
    with app.open_resource("./static/fondos/" + documento["fondo"]) as adj:
        msg.attach(documento["fondo"], "image/jpeg", adj.read())
    mail.send(msg)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

