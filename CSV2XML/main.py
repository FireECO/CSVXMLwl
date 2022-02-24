import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename

# Répretoire local
localDir = "files/"
# Extensions autorisés
extensions = {"txt", "csv"}
# Nom du fichier de sortie XML
xmlFileName = "ConfigSBC.xml"

# SYNTAXE XML
xmlStart = "<?xml version='1.0' standalone='yes'?>\n<oracleSbcFraudProtectionApi version='1.0'>\n\t<call-whitelist/>\n\t<call-blacklist>\n"
xmlInnerStart = "\t\t<userEntry>\n\t\t\t<from-phone-number>"
xmlInnerEnd = "</from-phone-number>\n\t\t\t<realm>*</realm>\n\t\t</userEntry>\n"
xmlEnd = "\t</call-blacklist>\n\t<call-redirect/>\n\t<call-rate-limit/>\n</oracleSbcFraudProtectionApi>"

# Application web
app = Flask(__name__)
app.config["localDir"] = localDir
app.secret_key = "do_not_tell_anyone_this_key_please"

# Transformer les fichiers csv en blacklist xml
def csv2xml(csvFileName):
    # Ouvrir le fichier avec le format csv
    with open(localDir + csvFileName, 'r') as csvFile:
        # Lire toutes les lignes du fichier
        listLines = csvFile.readlines()
    # Retirer l"entête du fichier
    listLines.pop(0)
    # Contenu du fichier xml à réaliser
    xmlFile = xmlStart
    # Pour chaque numéro :
    for line in listLines:
        line = line.strip("\n")
        line = line.split(';')
        number = line[0]
        if len(number) > 0:
            xmlFile += xmlInnerStart
            xmlFile += number
            xmlFile += xmlInnerEnd
    xmlFile += xmlEnd
    # Créer un fichier .xml contenant la blacklist
    with open(localDir + xmlFileName, 'w') as file:
        # L"ajouter au fichier
        file.write(xmlFile)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@app.route('/', methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["localDir"], filename))
            csv2xml(filename)
            return redirect(url_for("download"))
    return render_template("page.html")

@app.route("/download", methods=["GET", "POST"])
def download():
    return send_file(localDir + xmlFileName, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
