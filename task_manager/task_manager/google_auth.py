import os
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Escopo da API que define o que a aplicação pode acessar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    try:
        # O token.pickle armazena as credenciais de acesso após o primeiro login
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # Se não houver credenciais ou se estiverem inválidas/expiradas, solicita login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080)  # Use uma porta específica

            # Salva as credenciais para reutilização futura
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
                
    except Exception as e:
        print(f'Error obtaining credentials: {e}')

    return creds
