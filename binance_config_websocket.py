# ######################################################################################################################
# Credenciais do usuário
# ######################################################################################################################

BINANCE_API_KEY = 'UNYrOvKm5cZW1vokdQF21lPOOfd1zxYs3N5jjJXYT0XOI24jhXBpx6MxmXLl3ydb'
BINANCE_SECRET_KEY = 'r3jrLFMDa0x9vrZXxHDAmkpy68lkabHpCHC0r1tBBeYgFDIaBwqWP8n0Qy9liJiM'


# ######################################################################################################################
# Par de moedas (symbol)
# ######################################################################################################################

# Primeiro elemento do par.
SYMBOL_P1 = 'SHIB'

# Segundo elemento do par.
SYMBOL_P2 = 'BUSD'

# Par de moedas.
SYMBOL = SYMBOL_P1 + SYMBOL_P2


# ######################################################################################################################
# Execução
# ######################################################################################################################

# Se IS_UP = True, a direção começa como Up; se IS_UP = False, verifica-se a direção; default True.
IS_UP = True

# TIMER_SLEEP_TIME = 0.0,...,Inf; default 4.0 (s). Tempo necessário para aumentar o sleep_time de acordo com uma taxa.
# O aumento acontecerá depois de uma iteração, caso a tendência não mude. Em havendo mudança de tendência, o sleep_time
# é reiniciado como o valor inicial.
TIMER_SLEEP_TIME = 4.0

# INITIAL_SLEEP_TIME > 0.0,...,Inf; default 0.5 (s). sleep_time inicial, ou seja, o primeiro valor.
INITIAL_SLEEP_TIME = 0.5

# RATE_SLEEP_TIME > 0.0,...,Inf; default 0.1 (s). Taxa usada para o aumento do sleep_time.
RATE_SLEEP_TIME = 0.1

# MAX_SLEEP_TIME > 0.0,...,Inf; default 0.7 (s). Máximo valor assumido pelo sleep_time. Se o
# sleep_time == MAX_SLEEP_TIME, nada é alterado até que a tendência mude novamente.
MAX_SLEEP_TIME = 0.7

# TIMER_OPERATIONS = 0.0,...,Inf; default 20.0 (s). Tempo necessário para que as operações possam ser feitas caso a
# tendência não mude.
TIMER_OPERATIONS = 10.0


# ######################################################################################################################
# Modo de pausa
# ######################################################################################################################

# Se IS_PAUSE_MODE = True, o código faz uma parada após cada operação, então o usuário é consultado e decide se deseja
# continuar executando o código ou não. Se IS_PAUSE_MODE = False, o código roda normalmente, sem pausas.
IS_PAUSE_MODE = False


# ######################################################################################################################
# Operação
# ######################################################################################################################

# Se IS_MARKET_ORDER = True, fazer operações de market; senão, não fazer.
IS_MARKET_ORDER = False

# Se IS_LIMIT_ORDER = True, fazer operações de limit; senão, não fazer.
IS_LIMIT_ORDER = False

# Se IS_MARGIN_ORDER = True, fazer operações de margin; senão, não fazer.
IS_MARGIN_ORDER = True

# RECVWINDOW = 1,...,Inf; default 3000 (seconds).
RECVWINDOW = 3000


# ######################################################################################################################
# Critérios de mudança de tendência (change)
# ######################################################################################################################

# TOLERANCE = 0.0,...,Inf; default 0.0001. Se a diferença percentual absoluta entre o preço anterior e atual for maior
# ou igual à TOLERANCE, considera-se que houve uma mudança de direção.
TOLERANCE = 0.0001

# MAX_COUNTS = 1,...,Inf; default 3. Se o número de mudanças sucessivas, desconsiderando estagnação do preço, for igual
# a MAX_COUNTS, considera que houve uma mudança de direção.
MAX_COUNTS = 8

# TOLERANCE_CHANGE = 0.0,...,Inf; default 0.0001. Se a diferença percentual absoluta entre o preço anterior e atual do
# CHANGE for maior ou igual à TOLERANCE_CHANGE, considera-se que houve uma mudança de direção.
TOLERANCE_CHANGE = 0.05


# ######################################################################################################################
# Critério de parada
# ######################################################################################################################

# MAX_CHANGES = 1,...,float('inf'); default float('inf'). Quando o número de mudanças de tendência é igual a
# MAX_CHANGES, o código é encerrado.
MAX_CHANGES = float('inf')


# ######################################################################################################################
# Ordem Market
# ######################################################################################################################

# QUOTE_ORDER_QTY = 10,...,Inf; default 10. Quantidade de P2 para operar em market.
QUOTE_ORDER_QTY = 10


# ######################################################################################################################
# Ordem Limit
# ######################################################################################################################

# N_TH_ORDER = 1,...,10; default 5. É a "N_TH_ORDER"-ésima ordem do order book.
N_TH_ORDER = 5

# CONFIDENCE_ORDER = 0,...,Inf; default 0.01. CONFIDENCE_ORDER é um fator que aumenta o preço da ordem.
CONFIDENCE_ORDER = 0.01

# VALUE_QUANTITY = 10,...,Inf; default 10. Quantidade de P2 para operar em limit.
VALUE_QUANTITY = 10

# CONFIDENCE_QUANTITY = 0,...,Inf; default 0.05. CONFIDENCE_QUANTITY é um fator que aumenta o preço da ordem.
CONFIDENCE_QUANTITY = 0.05

# NUMBER_ATTEMPTS_LIMIT = 1,...,Inf; default 1. Número máximo de tentativas para se consolidar uma operação em limit.
NUMBER_ATTEMPTS_LIMIT = 2

# "Must be 0, None (1s) or 100 (100ms)"; default 100. Frequência com a qual as requisições são respondidas pelo servidor
# no tocante ao order book, de modo que "100" implica numa maior velocidade de resposta.
INTERVAL = 100


# ######################################################################################################################
# Ordem Margin
# ######################################################################################################################

# MIN_VALUE_QUANTITY = 10,...,Inf; default 10 (USDT). Mínimo permitido pela Binance para efetuar transações.
MIN_VALUE_QUANTITY = 10

# CONFIDENCE_QUANTITY = 0,...,Inf; default 0.05. MIN_CONFIDENCE_QUANTITY é um fator que aumenta a quantidade mínima
# permitida pela Binance.
MIN_CONFIDENCE_QUANTITY = 0.05

# FEE_BROKERAGE = 0,...,Inf; default 0.01. É o valor da taxa entre 0 e 1 sobre o total operado.
FEE_BROKERAGE = 0.01

# NUMBER_ATTEMPTS_LIMIT = 1,...,Inf; default 1. Número máximo de tentativas para se consolidar uma operação em margin.
NUMBER_ATTEMPTS_MARGIN = 3

# SLEEP_TIME_MARGIN > 0.0,...,Inf; default 0.5 (s). Valor esperado após cada operação de reembolso ou empréstimo.
SLEEP_TIME_MARGIN = 0.25


# ######################################################################################################################
# TradingView
# ######################################################################################################################

# Caminho do servidor webhook.
PATH_WEBHOOK_SERVER = 'C:\\Users\\LEA\\PycharmProjects\\tradingview-webhooks-bot-master\\tradingview-webhooks-bot'
