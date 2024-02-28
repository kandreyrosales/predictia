import os
import random
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import boto3
import colorsys
import jwt
from datetime import datetime
from functools import wraps

app = Flask(__name__)

app.secret_key = 'xaldigital!'
AWS_REGION_PREDICTIA = os.getenv("region_aws")
bucket_name = os.getenv("bucket_name")
accessKeyId = os.getenv("accessKeyId")
secretAccessKey = os.getenv("secretAccessKey")
arn_forecast_lambda=os.getenv("lambda_forecast_arn")
arn_ids_lambda=os.getenv("lambda_get_ids_arn")
arn_insights_lambda=os.getenv("lambda_get_insights")
arn_metrics_lambda=os.getenv("lambda_get_metrics")
CLIENT_ID_COGNITO =os.getenv("client_id")
USER_POOL_ID_COGNITO =os.getenv("user_pool")

# boto3 clients
cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION_PREDICTIA, aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey)
lambda_client = boto3.client('lambda', region_name=AWS_REGION_PREDICTIA, aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey)
s3_client = boto3.client('s3', region_name=AWS_REGION_PREDICTIA, aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey)

def lamdba_metrics():
    try:
        response = lambda_client.invoke(FunctionName=arn_metrics_lambda, InvocationType='RequestResponse')
        response_payload = response['Payload'].read()
        result = json.loads(response_payload.decode('utf-8'))
        return result
    except Exception as e:
        return {}

@app.route('/upload_to_server', methods=['POST'])
def upload_to_server():
    # Get the file from the request
    file = request.files['file']
    # Upload the file to S3
    try:
        s3_client.upload_fileobj(file, bucket_name, file.filename)
        return 'Archivo subido exitosamente. En unos minutos recibirá una notificación a su correo cuando el análisis de los datos haya terminado!'
    except Exception as e:
        return str(e)

def generate_chart_colors(num_colors):
    # Generate evenly spaced hues
    hues = [i / num_colors for i in range(num_colors)]
    saturation = 0.7  # Adjust saturation and value to get desired colorfulness
    value = 0.9
    # Convert HSL colors to RGB
    colors = [colorsys.hsv_to_rgb(hue, saturation, value) for hue in hues]
    # Scale RGB values to the range [0, 255]
    colors = [f"rgba{(int(r * 255), int(g * 255), int(b * 255))}" for (r, g, b) in colors]
    return colors

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("access_token")
        if not token:
            return render_template('login/login.html')
        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})  # Decode the token without verifying signature
            expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
            current_time = datetime.utcnow()
            if expiration_time > current_time:
                return f(*args, **kwargs)
            else:
                return render_template('login/login.html', error="Sesión Expirada")
        except jwt.ExpiredSignatureError:
            return render_template('login/login.html', error="Sesión Expirada")
    return decorated_function

@app.route('/metricas_error')
@token_required
def metricas_error():
    try:
        json_result = lamdba_metrics()
        mape_avg = round(json_result.get("average_mape", 0), 2)
        mape_last_month = 0
        bias_avg = round(json_result.get("average_bias", 0), 2)
        mape_data_list = list(json_result["mape_values_by_month"].values())
        mape_data_labels = list(json_result["mape_values_by_month"].keys())
        mape_data = {"labels": mape_data_labels, "datasets": [{"label": "MAPE", "data": mape_data_list, "backgroundColor": "rgba(254, 232, 0, 1)"}]}
        mape_last_month = round(mape_data_list[-1], 2)
        bias_data_list = list(json_result["bias_values_by_month"].values())
        bias_labels = list(json_result["bias_values_by_month"].keys())
        colors = ["rgba(127, 127, 127, 1)" if b < 0 else "rgba(254, 232, 0, 1)" for b in bias_data_list]
        bias_data = {"labels": bias_labels, "datasets": [{"label": "BIAS", "data": bias_data_list, 'borderColor': colors, 'backgroundColor': colors}]}
        bias_last_month = round(bias_data_list[-1], 2)
    except Exception as e:
        mape_avg =  0
        mape_last_month = 0
        bias_avg = 0
        bias_last_month= 0
        mape_data_labels = []
        mape_data = []
        bias_labels = []
        bias_data = []

    return render_template(
        'forecasting_panel.html',
        select_panel_name="select_forecasting_panel",
        boxname="Panel de Precisión de Pronósticos",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey,
        mape_avg=mape_avg,
        mape_last_month=mape_last_month,
        bias_avg=bias_avg,
        bias_last_month=bias_last_month,
        mape_data_labels=mape_data_labels,
        mape_data=mape_data,
        bias_labels=bias_labels,
        bias_data=bias_data
    )

@app.route('/datoshistoricos')
@token_required
def datos_historicos():
    return render_template(
        'historical_data_panel.html',
        select_panel_name="select_datos_historicos_panel",
        boxname="Datos Históricos",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey,
    )

@app.route('/datospronosticados')
@token_required
def datos_pronosticados():
    return render_template(
        'forecasting_data_panel.html',
        select_panel_name="select_datos_historicos_panel",
        boxname="Datos Pronosticados",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

def lambda_get_ids_generic():
    try:
        response = lambda_client.invoke(FunctionName=arn_ids_lambda, InvocationType='RequestResponse')
        response_payload = response['Payload'].read()
        result = json.loads(response_payload.decode('utf-8'))
        unique_ids = []
        if result.get("statusCode") == 200:
            body = json.loads(result["body"])
            unique_ids = body["unique_ids"][:5]
            return unique_ids
        return []
    except Exception as e:
        return []
    
def lamdba_insights():
    try:
        response = lambda_client.invoke(FunctionName=arn_insights_lambda, InvocationType='RequestResponse')
        response_payload = response['Payload'].read()
        result = json.loads(response_payload.decode('utf-8'))
        if result.get("statusCode") == 200:
            body = json.loads(result["body"])
            return body["content"]
        return "No hay datos disponibles para mostrar todavía."
    except Exception as e:
        return "No hay datos disponibles para mostrar todavía."

@app.route('/')
@token_required
def index():
    unique_ids = lambda_get_ids_generic()
    return render_template(
        'index.html',
        bucket_name=bucket_name,
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey,
        unique_ids = unique_ids,
        info_text_insights = lamdba_insights()
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Accesing with Cognito using username and password.
        After login is redirected to reset password and login again
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            cognito_response = authenticate_user(username, password)
            if cognito_response.get("reason") is not None:
                return render_template('login/login.html', error=cognito_response.get("error_info"))
            else:
                challenge_name = cognito_response.get('ChallengeName', None)
                if challenge_name == 'NEW_PASSWORD_REQUIRED':
                    # User needs to set a new password
                    session_from_cognito=cognito_response["Session"]
                    return render_template('login/set_password.html', session=session_from_cognito, username=username)
                else:
                    auth_result = cognito_response["AuthenticationResult"]
                    if auth_result:
                        session['access_token'] = auth_result.get('AccessToken')
                        session['id_token'] = auth_result.get('IdToken')
                        return redirect(url_for('index'))
                    else:
                        return render_template('login/login.html', error=cognito_response)
        else:
            # Invalid credentials, show error message
            return render_template('login/login.html', error="Nombre de usuario y Contraseña obligatorios")
    else:
        return render_template(
            'login/login.html',
            accessKeyId=accessKeyId,
            secretAccessKey=secretAccessKey
        )
    
@app.route('/set_new_password', methods=['POST'])
def set_new_password():
    username = request.form['username']
    new_password = request.form['new_password']
    session_data=request.form['session']
    try:
        response = cognito_client.respond_to_auth_challenge(
            ClientId=CLIENT_ID_COGNITO,  # Replace 'your-client-id' with your Cognito app client ID
            ChallengeName='NEW_PASSWORD_REQUIRED',
            Session=session_data,  # Include the session token from the previous response
            ChallengeResponses={
                'USERNAME': username,
                'NEW_PASSWORD': new_password
            }
        )
        return redirect(url_for('index'))
    except cognito_client.exceptions.NotAuthorizedException as e:
        # Handle authentication failure
        return render_template('login/login.html', error="Hubo un problema al asignar una nueva contraseña")
    except Exception as e:
        # Handle other errors
        return render_template('login/login.html', error="Hubo un problema al asignar una nueva contraseña")

def authenticate_user(username, password):
    try:
        response = cognito_client.admin_initiate_auth(
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            },
            ClientId=CLIENT_ID_COGNITO,
            UserPoolId=USER_POOL_ID_COGNITO,
            ClientMetadata={
                  'username': username,
                  'password': password,
              }
        )
        return response
    except cognito_client.exceptions.NotAuthorizedException as e:
        # Handle invalid credentials
        return {"reason": "Credenciales Inválidas o Usuario No Encontrado", "error_info": e}
    except cognito_client.exceptions.ResourceNotFoundException as e:
        # Handle invalid credentials
        return {"reason": "Error General", "error_info": "Recurso no encontrado"}
    except Exception as e:
        # Handle other errors
        return {"reason": "Credenciales Inválidas o Usuario No Encontrado", "error_info": e}
    
@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    return redirect(url_for('login'))


@app.route('/invoke_lambda_ids', methods=["GET"])
def invoke_lambda_ids():
    try:
        response = lambda_client.invoke(FunctionName=arn_ids_lambda, InvocationType='RequestResponse')
        response_payload = response['Payload'].read()
        result = json.loads(response_payload.decode('utf-8'))
        if result.get("statusCode") == 200:
            body = json.loads(result["body"])
            return body["unique_ids"]
    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/invoke_lambda_metrics', methods=["GET"])
def invoke_lambda_metrics():
    try:
        response = lambda_client.invoke(FunctionName=arn_metrics_lambda, InvocationType='RequestResponse')
        response_payload = response['Payload'].read()
        result = json.loads(response_payload.decode('utf-8'))
        if result.get("statusCode") == 200:
            body = json.loads(result["body"])
            return body["unique_ids"]
    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/invoke_lambda_forecast', methods=["GET"])
def invoke_lambda_forecast():
    unique_ids = request.args.get('ids')
    payload = json.dumps({"unique_ids": unique_ids.split(",")})
    try:
        response = lambda_client.invoke(FunctionName=arn_forecast_lambda, InvocationType='RequestResponse', Payload=payload)
        response_payload = response['Payload'].read()
        result = json.loads(response_payload.decode('utf-8'))
        body = json.loads(result["body"])
        data_list = body["data"]
        
        # Initialize a dictionary to store unique_id and corresponding y values
        result = {}

        # Initialize a list to store all ds values
        ds_list = []

        num_colors = len(unique_ids.split(","))
        chart_colors = generate_chart_colors(num_colors)
        counter_colors = 0

        # Iterate through each item in data_list
        for item in data_list:
            unique_id = item['unique_id']
            y_value = item['y']
            ds_value = item['ds'].strip()  # Remove leading/trailing whitespace
            
            # Append ds_value to ds_list if it's not already there
            if ds_value not in ds_list:
                ds_list.append(ds_value)
            
            # Check if unique_id is already in result dictionary
            if unique_id in result:
                result[unique_id]['data'].append(y_value)
            else:
                color_selected = chart_colors[counter_colors]
                result[unique_id] = {'label': unique_id, 'data': [y_value], "backgroundColor": color_selected()}
                counter_colors += 1

        # Transform result dictionary to a list of dictionaries
        result_list = list(result.values())
        return {"unique_ids_data": result_list, "labels": ds_list}
    except Exception as e:
        return {"unique_ids_data": [], "labels": []}


@app.route('/invoke_lambda_historical', methods=["GET"])
def invoke_lambda_historical():
    unique_ids = request.args.get('ids')
    payload = json.dumps({"unique_ids": unique_ids.split(",")})
    try:
        response = lambda_client.invoke(FunctionName=arn_forecast_lambda, InvocationType='RequestResponse', Payload=payload)
        # Process the response from Lambda
        # For example, you can extract data from the response and return it as JSON
        response_payload = response['Payload'].read()
        result = json.loads(response_payload.decode('utf-8'))
        body = json.loads(result["body"])
        data_list = body["data"]
        
        # Initialize a dictionary to store unique_id and corresponding y values
        result = {}

        # Initialize a list to store all ds values
        ds_list = []

        num_colors = len(unique_ids.split(","))
        chart_colors = generate_chart_colors(num_colors)
        counter_colors = 0
        # Iterate through each item in data_list
        for item in data_list:
            if item["type"] != "forecast":
                unique_id = item['unique_id']
                y_value = item['y']
                ds_value = item['ds'].strip()  # Remove leading/trailing whitespace
                
                # Append ds_value to ds_list if it's not already there
                if ds_value not in ds_list:
                    ds_list.append(ds_value)
                
                # Check if unique_id is already in result dictionary
                if unique_id in result:
                    result[unique_id]['data'].append(y_value)
                else:
                    color_selected = chart_colors[counter_colors]
                    result[unique_id] = {
                            'label': str(unique_id), 
                            'data': [y_value], 
                            'backgroundColor': color_selected,
                            'borderColor': color_selected,
                            'fill': False
                        }
                    counter_colors += 1

        # Transform result dictionary to a list of dictionaries
        result_list = list(result.values())
        return {"unique_ids_data": result_list, "labels": ds_list}
    except Exception as e:
        return {"unique_ids_data": [], "labels": []}


@app.route('/invoke_lambda_forecasted_data', methods=["GET"])
def invoke_lambda_forecasted_data():
    """
        Datos Pronosticados data for chart in index.html page
        We are mixing forecasted and historical data overlapping
    """
    unique_ids = request.args.get('ids')
    payload = json.dumps({"unique_ids": unique_ids.split(",")})
    try:
        response = lambda_client.invoke(FunctionName=arn_forecast_lambda, InvocationType='RequestResponse', Payload=payload)
        response_payload = response['Payload'].read()
        result = json.loads(response_payload.decode('utf-8'))
        body = json.loads(result["body"])
        data_list = body["data"]
        
        # Initialize a dictionary to store unique_id and corresponding y values
        result_forecast = {}
        result_historical_data = {}

        # Initialize a list to store all ds values
        ds_list_forecast = []
        ds_list_historical = []
        general_label = []

        # Iterate through each item in data_list
        num_colors = len(unique_ids.split(","))
        chart_colors = generate_chart_colors(num_colors)
        counter_colors = 0
        for item in data_list:
            unique_id = item['unique_id']
            y_value = item['y']
            ds_value = item['ds'].strip()  # Remove leading/trailing whitespace
            general_label.append(ds_value)
            
            if item["type"] == "forecast":    
                # Check if unique_id is already in result dictionary
                if unique_id in result_forecast:
                    result_forecast[unique_id]['data'].append(y_value)
                else:
                    result_forecast[unique_id] = {
                            'label': str(unique_id), 
                            'data': [y_value], 
                            'backgroundColor': result_historical_data[unique_id]['backgroundColor'],
                            'borderColor': result_historical_data[unique_id]['backgroundColor'],
                            'fill': False,
                            'borderDash': [5,5],
                        }
            else:
                # Append ds_value to ds_list if it's not already there
                if ds_value not in ds_list_historical:
                    ds_list_historical.append(ds_value)
                
                # Check if unique_id is already in result dictionary
                if unique_id in result_historical_data:
                    result_historical_data[unique_id]['data'].append(y_value)
                else:
                    color_selected = chart_colors[counter_colors]
                    result_historical_data[unique_id] = {
                            'label': str(unique_id), 
                            'data': [y_value], 
                            'backgroundColor': color_selected,
                            'borderColor': color_selected,
                            'fill': False,
                        }
                    counter_colors += 1
        sorted_general_labels = sorted(list(set(general_label)))
        for key, value in result_forecast.items():
            size_actual_data = len(value["data"])
            size_historical_data = len(sorted_general_labels)
            result_size = (size_historical_data - size_actual_data)
            actual_data = value["data"]
            if size_actual_data < size_historical_data:
                result_forecast[key]["data"] = [None] * result_size + actual_data
        result_list = list(result_historical_data.values()) + list(result_forecast.values())
        return {"unique_ids_data": result_list, "labels": sorted_general_labels}
    except Exception as e:
        return {"unique_ids_data": [], "labels": []}
