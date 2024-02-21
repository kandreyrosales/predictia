import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import boto3
import jwt
from datetime import datetime
from functools import wraps



app = Flask(__name__)

app.secret_key = 'xaldigital!'

COGNITO_REGION = 'us-east-1'
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
client_id_cognito =str(os.getenv("client_id"))
user_pool_cognito =str(os.getenv("user_pool"))

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
        except Exception as e:
            return render_template('login/login.html', error="Token inválido. Contacta por favor al admnistrador.")

    return decorated_function

@app.route('/panel-precision-pronotiscos')
@token_required
def panel_precision_pronosticos():
    accessKeyId = os.getenv("accessKeyId")
    secretAccessKey = os.getenv("secretAccessKey")
    return render_template(
        'forecasting_panel.html',
        select_panel_name="select_forecasting_panel",
        boxname="Panel de Precisión de Pronósticos",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

@app.route('/datoshistoricos')
@token_required
def datos_historicos():
    accessKeyId = os.getenv("accessKeyId")
    secretAccessKey = os.getenv("secretAccessKey")
    return render_template(
        'historical_data_panel.html',
        select_panel_name="select_datos_historicos_panel",
        boxname="Datos Históricos",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )

@app.route('/datospronosticados')
@token_required
def datos_pronosticados():
    accessKeyId = os.getenv("accessKeyId")
    secretAccessKey = os.getenv("secretAccessKey")
    return render_template(
        'forecasting_data_panel.html',
        select_panel_name="select_datos_historicos_panel",
        boxname="Datos Pronosticados",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )


@app.route('/')
@token_required
def index():
    accessKeyId = str(os.getenv("accessKeyId"))
    secretAccessKey = str(os.getenv("secretAccessKey"))
    bucket_name = str(os.getenv("bucket_name"))
    return render_template(
        'index.html',
        bucket_name="predictiaxaldigital",
        accessKeyId=accessKeyId,
        secretAccessKey=secretAccessKey
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
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
        accessKeyId = os.getenv("accessKeyId")
        secretAccessKey = os.getenv("secretAccessKey")
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
    
    client = boto3.client('cognito-idp', region_name=COGNITO_REGION)  # Replace 'your-region' with your AWS region
    try:
        response = client.respond_to_auth_challenge(
            ClientId=client_id_cognito,  # Replace 'your-client-id' with your Cognito app client ID
            ChallengeName='NEW_PASSWORD_REQUIRED',
            Session=session_data,  # Include the session token from the previous response
            ChallengeResponses={
                'USERNAME': username,
                'NEW_PASSWORD': new_password
            }
        )
        return redirect(url_for('index'))

    except client.exceptions.NotAuthorizedException as e:
        # Handle authentication failure
        return render_template('login/login.html', error="Hubo un problema al asignar una nueva contraseña")
    except Exception as e:
        # Handle other errors
        return render_template('login/login.html', error="Hubo un problema al asignar una nueva contraseña")

def authenticate_user(username, password):
    client_id_cognito =str(os.getenv("client_id"))
    user_pool_cognito =str(os.getenv("user_pool"))
    try:
        response = cognito_client.admin_initiate_auth(
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            },
            ClientId=client_id_cognito,
            UserPoolId=user_pool_cognito,
            ClientMetadata={
                  'username': username,
                  'password': password,
              }
        )
        return response
    except cognito_client.exceptions.NotAuthorizedException as e:
        # Handle invalid credentials
        return {"reason": "Credenciales Inválidas o Usuario No Encontrado", "error_info": f"{e} {username} {password} {client_id_cognito} {user_pool_cognito} 1"}
    except Exception as e:
        # Handle other errors
        return {"reason": "Credenciales Inválidas o Usuario No Encontrado", "error_info": f"{e} {username} {password} {client_id_cognito} {user_pool_cognito} 2"}
    
@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    return redirect(url_for('login'))


