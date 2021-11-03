"""
Tradingview-webhooks-bot is a python bot that works with tradingview's webhook alerts!
This bot is not affiliated with tradingview and was created by @robswc

You can follow development on github at: github.com/robswc/tradingview-webhook-bot

I'll include as much documentation here and on the repo's wiki!  I
expect to update this as much as possible to add features as they become available!
Until then, if you run into any bugs let me know!
"""

# https://br.tradingview.com/symbols/SHIBUSD/
# https://stackoverflow.com/questions/51121901/ngrok-session-expired-raspberry-project
# https://ngrok.com/docs#authtoken
# https://dashboard.ngrok.com/get-started/your-authtoken

# Guide: https://github.com/Robswc/tradingview-webhooks-bot/wiki/Quick-Start-Guide

from actions import send_order, parse_webhook
from auth import get_token
from flask import Flask, request, abort, got_request_exception

from pyngrok import ngrok
from datetime import datetime
import json
import os
import subprocess
import config_webhook

# Create Flask object called app.
app = Flask(__name__)


# Create root to easily let us know its on/working.
@app.route('/')
def root():
    return 'online'


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Parse the string data from tradingview into a python dict
        data = parse_webhook(request.get_data(as_text=True))
        # Check that the key is correct
        if get_token() == data['key']:
            print(' [Alert Received] ')
            print('POST Received:', data)

            filename = datetime.now().strftime('alert__%d_%m_%Y__%H_%M_%S')
            with open(config_webhook.PATH_ALERTS + '\\' + filename + '.json', 'w') as file:
                json.dump(data, file)

            return '', 200
        else:
            abort(403)
    else:
        abort(400)


def generate_public_url():
    # Matar o processo "ngrok.exe" caso ele já exista.
    subprocess.run('taskkill /f /im  ngrok.exe', capture_output=True)

    # Setar o arquivo de configurações com o token.
    ngrok.set_auth_token(config_webhook.YOUR_AUTHTOKEN)

    # Estabelecer um novo túnel ngrok para a porta fornecida.
    ngrok_tunnel = ngrok.connect(config_webhook.PORT)

    # Salvar a url pública na pasta especificada.
    with open(config_webhook.PATH_PUBLIC_URL + '\\public_url.json', 'w') as file:
        json.dump(ngrok_tunnel.data['public_url'] + '/webhook', file)


def clear_alerts_folder():
    for filename in os.listdir(config_webhook.PATH_ALERTS):
        os.remove(config_webhook.PATH_ALERTS + '\\' + filename)


if __name__ == '__main__':
    clear_alerts_folder()
    generate_public_url()
    app.run()

# Docs: https://pyngrok.readthedocs.io/en/latest/index.html

'''
from pyngrok import ngrok
ngrok.set_auth_token("206TR0fhA4xnrNwImctXOVUqhbt_3hMdKT4o5aZgVKyGQS8uT")
ngrok_tunnel = ngrok.connect(5000)
print(ngrok_tunnel.data['public_url'])
'''

# tradingview-webhooks-bot\ngrok http -host-header=C:\Users\LEA\.ngrok2\ngrok.yml 5000
# tradingview-webhooks-bot\ngrok start C:\Users\LEA\.ngrok2\ngrok.yml 5000
