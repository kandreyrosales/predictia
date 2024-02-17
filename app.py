import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/panel-precision-pronotiscos')
def panel_precision_pronosticos():
    accessKeyId = os.environ.get("accessKeyId")
    secretAccessKey = os.environ.get("secretAccessKey")
    return render_template(
        'forecasting_panel.html',
        select_panel_name="select_forecasting_panel",
        boxname="Panel de Precisión de Pronósticos",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

@app.route('/datoshistoricos')
def datos_historicos():
    accessKeyId = os.environ.get("accessKeyId")
    secretAccessKey = os.environ.get("secretAccessKey")
    return render_template(
        'historical_data_panel.html',
        select_panel_name="select_datos_historicos_panel",
        boxname="Datos Históricos",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

@app.route('/datospronosticados')
def datos_pronosticados():
    accessKeyId = os.environ.get("accessKeyId")
    secretAccessKey = os.environ.get("secretAccessKey")
    return render_template(
        'forecasting_data_panel.html',
        select_panel_name="select_datos_historicos_panel",
        boxname="Datos Pronosticados",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

@app.route('/login')
def login():
    accessKeyId = os.environ.get("accessKeyId")
    secretAccessKey = os.environ.get("secretAccessKey")
    return render_template(
        'login/login.html',
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )


@app.route('/')
def index():
    accessKeyId = os.environ.get("accessKeyId")
    secretAccessKey = os.environ.get("secretAccessKey")
    bucket_name = os.environ.get("bucket_name")
    return render_template(
        'index.html',
        bucket_name=bucket_name,
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

