from binance import AsyncClient, BinanceSocketManager
from binance.enums import SIDE_BUY, SIDE_SELL
from binance.exceptions import BinanceAPIException

import aiohttp
import asyncio
import nest_asyncio
nest_asyncio.apply()

import json
import time

################################################
from binance_trend_websocket import get_trend_trandingview_summary
get_trend_with_p1_p2_p3 = get_trend_trandingview_summary
################################################
from binance_operations_websocket import BinanceOperationsWebsocket
from binance_functions_websocket import while_try_except, while_try_except_async, pause_mode, update_timer, \
                                        update_sleep_time
import binance_config_websocket
client = None
trade_operation = None

# Trades de Mercado: https://www.binance.com/pt-BR/trade/MINA_BNB
# Comprar/Vender: https://www.binance.com/pt-BR/trade/BTC_BRL?layout=pro
# Order Book: https://www.binance.com/pt-BR/orderbook/BTC_BRL


async def get_price(client):
    symbol_ticker = json.dumps(await client.get_symbol_ticker(symbol=binance_config_websocket.SYMBOL))
    price = float(json.loads(symbol_ticker)['price'])
    return price


async def start_trend(client):
    price_previous = await get_price(client)
    price_current = await get_price(client)
    print('Price(p): %f \t Price(c): %f' % (price_previous, price_current))

    while price_current == price_previous:
        price_current = await get_price(client)
        print('Price(p): %f \t Price(c): %f' % (price_previous, price_current))

    if price_current > price_previous:
        direction = True
        print('\n\t=== A tendência inicial é UP!', end='\n\n')
    else:
        direction = False
        print('\n\t=== A tendência inicial é DOWN!', end='\n\n')

    return direction


async def make_operations(trend, is_change, order_book):
    global trade_operation

    if (trend is True and is_change is True) or (trend is True and is_change is False):  # This is the new trend
        # Market order
        if binance_config_websocket.IS_MARKET_ORDER:
            await trade_operation.market_order(side=SIDE_BUY)
            print('\t\t=== BUY-market (quoteOrderQty: %.5f)' % binance_config_websocket.QUOTE_ORDER_QTY)

            if binance_config_websocket.IS_PAUSE_MODE:
                pause_mode()

        # Limit order
        if binance_config_websocket.IS_LIMIT_ORDER:
            for i in range(binance_config_websocket.NUMBER_ATTEMPTS_LIMIT):
                try:
                    price_order = float(order_book['bids'][binance_config_websocket.N_TH_ORDER - 1][0])
                    quantity_order, new_price_bid = await trade_operation.limit_order(SIDE_BUY, price_order)

                    print('\t\t=== BUY-limit  (price: %.5f, new_price_bid: %.5f, quantity: %.5f)' %
                          (price_order, new_price_bid, quantity_order))

                    if binance_config_websocket.IS_PAUSE_MODE:
                        pause_mode()

                    break
                except BinanceAPIException as binance_except:
                    print('\t\t=== ' + str(binance_except))

        # Margin order
        if binance_config_websocket.IS_MARGIN_ORDER:
            print('\t\t=== BUY-margin')
            await trade_operation.margin_order(side=SIDE_BUY)

    else:  # (trend is False and is_change is True) or (trend is False and is_change is False)
        # Market order
        if binance_config_websocket.IS_MARKET_ORDER:
            await trade_operation.market_order(side=SIDE_SELL)
            print('\t\t=== SELL-market (quoteOrderQty: %.5f)' % binance_config_websocket.QUOTE_ORDER_QTY)

            if binance_config_websocket.IS_PAUSE_MODE:
                pause_mode()

        # Limit order
        if binance_config_websocket.IS_LIMIT_ORDER:
            for i in range(binance_config_websocket.NUMBER_ATTEMPTS_LIMIT):
                try:
                    price_order = float(order_book['asks'][binance_config_websocket.N_TH_ORDER - 1][0])
                    quantity_order, new_price_ask = await trade_operation.limit_order(SIDE_SELL,
                                                                                      price_order)

                    print('\t\t=== SELL-limit  (price: %.5f, new_price_ask: %.5f, quantity: %.5f)' %
                          (price_order, new_price_ask, quantity_order))

                    if binance_config_websocket.IS_PAUSE_MODE:
                        pause_mode()

                    break
                except BinanceAPIException as binance_except:
                    print('\t\t=== ' + str(binance_except))

        # Margin order
        if binance_config_websocket.IS_MARGIN_ORDER:
            print('\t\t=== SELL-margin')
            await trade_operation.margin_order(side=SIDE_SELL)


async def main():
    ##
    global client
    global trade_operation

    is_connection_error = True
    while is_connection_error:
        try:
            client = await AsyncClient.create(binance_config_websocket.BINANCE_API_KEY,
                                              binance_config_websocket.BINANCE_SECRET_KEY)
            is_connection_error = False
        except aiohttp.client_exceptions.ClientConnectorError as connector_except:
            print(connector_except)
            # is_connection_error = True

    trade_operation = BinanceOperationsWebsocket(client)

    ##
    await while_try_except_async(code_block=['client.get_symbol_ticker(symbol=binance_config_websocket.SYMBOL)'],
                                 exception=BinanceAPIException,
                                 print_except=False,
                                 print_in_try='O lançamento começou!\n',
                                 print_in_except='Ouvindo o websocket...',
                                 client=client)

    ##
    BSM = BinanceSocketManager(client)
    depth = BSM.depth_socket(symbol=binance_config_websocket.SYMBOL, depth=binance_config_websocket.N_TH_ORDER,
                             interval=binance_config_websocket.INTERVAL)

    ##
    if binance_config_websocket.IS_UP:  # True (inicia como Up) ou False (verifica a tendência)
        trend = True
        print('\t=== A tendência inicial é UP!', end='\n\n')
    else:
        trend = await start_trend(client)

    async with depth as ds:
        await make_operations(trend=trend, is_change=True, order_book=await ds.recv())

    price_previous = price_change = await get_price(client)
    counter_down_up = [0, 0]
    counter_changes = 0

    start_sleep_time = time.time()
    sleep_time = binance_config_websocket.INITIAL_SLEEP_TIME

    start_timer_operations = time.time()

    async with depth as ds:

        iteration = 1
        while counter_changes < binance_config_websocket.MAX_CHANGES:
            # Atualiza o timer sleep_time.
            if sleep_time < binance_config_websocket.MAX_SLEEP_TIME:
                is_time_sleep_time, diff_runtime_sleep_time = update_timer(start_sleep_time,
                                                                           binance_config_websocket.TIMER_SLEEP_TIME)
                # Se o timer sleep_time tiver chegado em 0, aumenta o sleep_time conforme o config.
                if is_time_sleep_time:
                    sleep_time = update_sleep_time(sleep_time)
                    start_sleep_time = time.time()

            # Atualiza o timer operations.
            is_time_operations, diff_runtime_operations = update_timer(start_timer_operations,
                                                                       binance_config_websocket.TIMER_OPERATIONS)

            print('\n================================================================================================='
                  '===========================================================')
            print('|%i|' % iteration)

            print('\nTrend: UP') if trend else print('\nTrend: DOWN')
            print('N. of changes: %i' % counter_changes)
            print('*** timer_sleep_time: %.2f (s), sleep time: %.2f (s) ***' % (diff_runtime_sleep_time, sleep_time))
            print('*** timer_operations: %.2f (s) ***' % diff_runtime_operations)

            # Obtém o preço atual da moeda.
            price_current = await get_price(client)

            # Se preço atual da moeda for diferente do anterior, verifique a tendência com os 3 indicadores.
            if price_current != price_previous:
                trend, is_change, counter_down_up, counter_changes = get_trend_with_p1_p2_p3(trend,
                                                                                             price_current,
                                                                                             price_previous,
                                                                                             counter_down_up,
                                                                                             counter_changes,
                                                                                             price_change)

                price_previous = price_current
            else:
                print('\n\tO preço não mudou: Price(p): %f, Price(curr): %f ' % (price_previous, price_current))
                is_change = False

            # Fazer operações em caso de mudança de tendência (is_change = True).
            if is_change:
                if trend:  # UP
                    print('\n\t=== A tendência mudou para UP!', end='\n\n')
                else:  # DOWN
                    print('\n\t=== A tendência mudou para DOWN!', end='\n\n')

                await make_operations(trend=trend, is_change=is_change, order_book=await ds.recv())

                # Atualiza o price_change com o preço atual.
                price_change = price_current

                # Reinicia o sleep_time com o valor inicial.
                sleep_time = binance_config_websocket.INITIAL_SLEEP_TIME

                # Reinicia os starts do timers sleep_time e operations.
                start_sleep_time = time.time()
                start_timer_operations = time.time()

            else:
                if is_time_operations:
                    print('\n\t=== A tendência não mudou e o tempo acabou!', end='\n\n')
                    await make_operations(trend=trend, is_change=is_change, order_book=await ds.recv())
                    start_timer_operations = time.time()

            # Tempo que se espera até a próxima iteração do código.
            time.sleep(sleep_time)

            # Incrementa iteration para aparecer no log.
            iteration += 1

        await client.close_connection()


if __name__ == "__main__":
    ##
    loop = asyncio.get_event_loop()
    while_try_except(code_block=['loop.run_until_complete(main())'],
                     exception=asyncio.TimeoutError,
                     print_except=False,
                     print_in_try=None,
                     print_in_except='TimeoutError!',
                     loop=loop,
                     main=main)
