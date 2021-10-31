import os
import glob
import ast

import binance_config_websocket
from binance_functions_websocket import clear_folder

from tradingview_ta import TA_Handler, Interval
handler = TA_Handler(symbol=binance_config_websocket.SYMBOL, exchange='binance', screener='crypto',
                     interval=Interval.INTERVAL_1_MINUTE, timeout=None)

# O caminho do servidor webhoook é adicionado ao path, a fim de importarmos o config_webhook.
import sys
sys.path.append(binance_config_websocket.PATH_WEBHOOK_SERVER)
import config_webhook


class IndicatorWebsocket:

    @staticmethod
    def tolerance_change(trend, price_current, price_change):
        difference_change = (price_current - price_change) / price_change

        trend_current = trend
        if abs(difference_change) >= binance_config_websocket.TOLERANCE_CHANGE:
            trend_current = not trend_current

        return trend_current, difference_change

    @staticmethod
    def tolerance(trend, price_current, price_previous):
        difference = (price_current - price_previous) / price_previous

        trend_current = trend
        if abs(difference) >= binance_config_websocket.TOLERANCE:
            if trend:   # UP
                if difference < 0:
                    trend_current = not trend_current
            else:       # DOWN
                if difference > 0:
                    trend_current = not trend_current

        return trend_current, difference

    @staticmethod
    def max_counts(trend, price_current, price_previous, counter_down_up):
        if price_current < price_previous:
            counter_down_up[0] += 1
            counter_down_up[1] = 0
        else:
            counter_down_up[0] = 0
            counter_down_up[1] += 1

        trend_current = trend
        if trend:   # UP
            if counter_down_up[0] >= binance_config_websocket.MAX_COUNTS:
                trend_current = not trend_current
        else:       # DOWN
            if counter_down_up[1] >= binance_config_websocket.MAX_COUNTS:
                trend_current = not trend_current

        return trend_current, counter_down_up

    @staticmethod
    def tradingview_summary(trend):
        analysis = handler.get_analysis()

        # Verifica a tendência com base na recomendação.
        recommend_summary = analysis.summary['RECOMMENDATION']
        if recommend_summary == 'BUY' or recommend_summary == 'STRONG_BUY':
            trend_summary = True    # UP
        elif recommend_summary == 'SELL' or recommend_summary == 'STRONG_SELL':
            trend_summary = False   # DOWN
        else:   # NEUTRAL
            trend_summary = trend   # Não há mudança de tendência caso a recomendação seja NEUTRAL.

        # Se a tendência do TradingView for diferente da tendência (trend), a tendência atual muda.
        trend_current = trend
        if trend_summary != trend:
            trend_current = not trend_current

        return trend_current, recommend_summary

    @staticmethod
    def tradingview_alerts(trend):
        # Se a pasta de alertas não estiver vazia, faça:
        if os.listdir(config_webhook.PATH_ALERTS):
            while True:
                try:
                    # Carrega o último alerta salvo.
                    list_of_files = glob.glob(config_webhook.PATH_ALERTS + '\\*')
                    latest_file = max(list_of_files, key=os.path.getctime)
                    with open(latest_file, 'r') as file:
                        file_content = file.read()

                    # Converte o string para dicionário.
                    alert = ast.literal_eval(file_content)
                    break
                except SyntaxError:
                    print('O alerta ainda está sendo gravado!...')
            '''
            while_try_except(code_block=['print()',
                                         'op = input("Você deseja continuar? [y/n]")',
                                         'if any(op == strings) is False: \n\traise ValueError',
                                         'if op == "n" or op == "N": \n\tsys.exit()',
                                         'print()'],
                             exception=ValueError,
                             print_except=False,
                             print_in_try=None,
                             print_in_except='Digite corretamente!',
                             strings=np.array(['y', 'Y', 'n', 'N']))
            '''

            # Se o alerta estiver fora do padrão, o código é finalizado e uma mensagem de erro é exibida.
            filename = latest_file[latest_file.find('alert__'):latest_file.find('.json')]
            if list(alert.keys()) != config_webhook.ALERT_KEYS:
                raise SyntaxError('Problema com a estrutura do alerta "%s"!' % filename)

            # Uma vez que se esteja de posse do alerta, corretamente carregado e padrão, todos os arquivos da pasta de
            # alertas são deletados, a fim de que não se incorra no risco de carregar o mesmo alerta novamente.
            clear_folder(config_webhook.PATH_ALERTS)

            # Obter a recomendação.
            recommend_alert = alert['recommendation']

            # Verifica a tendência com base na recomendação.
            if recommend_alert == 'BUY':
                trend_alert = True  # UP
            else:  # 'SELL'
                trend_alert = False  # DOWN

            # Se a tendência do TradingView for diferente da tendência (trend), a tendência atual muda.
            trend_current = trend
            if trend_alert != trend:
                trend_current = not trend_current

        else:
            trend_current = trend
            recommend_alert = 'empty'

        return trend_current, recommend_alert
