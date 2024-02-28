import os
import boto3
import json


COGNITO_REGION = os.getenv("region_aws")
cognito_pool_id = os.getenv("pool_id")
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

def get_last_created_user(pool_id):
    usernames = []
    users_resp = cognito_client.list_users (
            UserPoolId = pool_id,
            AttributesToGet = ['email'])

    # iterate over the returned users and extract username and email
    for user in users_resp['Users']:
        user_record = {'username': user['Username'], 'email': None}
        for attr in user['Attributes']:
            if attr['Name'] == 'email':
                user_record['email'] = attr['Value']
                usernames.append(user_record)
                break
    return usernames

def lambda_handler(event, context):
    user_pool_id = cognito_pool_id
    last_user = get_last_created_user(user_pool_id)
    if last_user:
        # To get the data of the email: [{'username': 'kandreyrosales', 'email': 'kandreyrosales@gmail.com'}]
        # Put here the code to send email with AWS SES
        email = last_user[0]["email"]
        filename_processed = event.get('file_name')
        message = f"Proceso de análisis finalizado para el archivo {filename_processed}. Abra la aplicación o recargue la página para ver los datos actualizados."
        response = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Email enviado exitosamente'})
        }
    else:
        response = {
            'statusCode': 400,
            'body': json.dumps({'message': 'Usuario No Encontrado. Correo no enviado'})
        }
    return response
    
