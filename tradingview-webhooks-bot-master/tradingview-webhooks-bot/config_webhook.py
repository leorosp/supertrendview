# Use este token para autenticar o agente ngrok. Após criar uma conta, pegue o seu Authtoken no endereço a seguir:
# <<https://dashboard.ngrok.com/get-started/your-authtoken>>.
YOUR_AUTHTOKEN = '206TR0fhA4xnrNwImctXOVUqhbt_3hMdKT4o5aZgVKyGQS8uT'

# Porta padrão. Não alterar!
PORT = 5000

# Caminho da pasta que armazena os alertas. 
PATH_ALERTS = 'C:\\Users\\LEA\\PycharmProjects\\tradingview-webhooks-bot-master\\tradingview-webhooks-bot\\alerts'

# Caminho da pasta que registra o url público do servidor. 
PATH_PUBLIC_URL = 'C:\\Users\\LEA\\PycharmProjects\\tradingview-webhooks-bot-master\\tradingview-webhooks-bot\\public_url'

# Estrutura padrão do alerta, ou seja, as chaves do dicionário.
# Ex. de alerta: {'recommendation': 'BUY', 'symbol': 'shibbusd', 'timeframe': '30s', 'indicator': 'Maior que Media Movel (8, close)', 'key': '99fb2f48c6af4761f904fc85f95eb56190e5d40b1f44ec3a9c1fa319'}
ALERT_KEYS = ['recommendation', 'symbol', 'timeframe', 'indicator', 'key']
