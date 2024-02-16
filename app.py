from flask import Flask, render_template

app = Flask(__name__)

@app.route('/panel-precision-pronotiscos')
def panel_precision_pronosticos():
    accessKeyId = 'TU_ACCESS_KEY_ID'
    secretAccessKey = 'TU_SECRET_ACCESS_KEY'
    BUCKET_NAME = "examplebucket"
    return render_template(
        'forecasting_panel.html',
        select_panel_name="select_forecasting_panel",
        boxname="Panel de Precisión de Pronósticos",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

@app.route('/datoshistoricos')
def datos_historicos():
    accessKeyId = 'TU_ACCESS_KEY_ID'
    secretAccessKey = 'TU_SECRET_ACCESS_KEY'
    return render_template(
        'historical_data_panel.html',
        select_panel_name="select_datos_historicos_panel",
        boxname="Datos Históricos",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

@app.route('/datospronosticados')
def datos_pronosticados():
    accessKeyId = 'TU_ACCESS_KEY_ID'
    secretAccessKey = 'TU_SECRET_ACCESS_KEY'
    return render_template(
        'forecasting_data_panel.html',
        select_panel_name="select_datos_historicos_panel",
        boxname="Datos Pronosticados",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

@app.route('/login')
def login():
    accessKeyId = 'TU_ACCESS_KEY_ID'
    secretAccessKey = 'TU_SECRET_ACCESS_KEY'
    return render_template(
        'login/login.html',
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )


@app.route('/')
def index():
    accessKeyId = 'TU_ACCESS_KEY_ID'
    secretAccessKey = 'TU_SECRET_ACCESS_KEY'
    BUCKET_NAME = "examplebucket"
    return render_template(
        'index.html',
        bucket_name=BUCKET_NAME,
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

