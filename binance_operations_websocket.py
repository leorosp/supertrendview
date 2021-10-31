from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC

from decimal import Decimal
import time
import math

from binance_functions_websocket import is_above_min, pause_mode
import binance_config_websocket


class BinanceOperationsWebsocket:
    def __init__(self, client):
        self.client = client
        self.minimum_price = None
        self.minimum_quantity = None

    def round_price(self, price):
        decimal_part = math.modf(self.minimum_price)
        if decimal_part[0] > 0:
            new_price = float(Decimal.from_float(price).quantize(Decimal(str(self.minimum_price))))
        else:
            new_price = int(price)
        return new_price

    def round_quantity(self, quantity):
        decimal_part = math.modf(self.minimum_quantity)
        if decimal_part[0] > 0:
            new_quantity = float(Decimal.from_float(quantity).quantize(Decimal(str(self.minimum_quantity))))
        else:
            new_quantity = int(quantity)
        return new_quantity

    async def get_quantity_order_and_new_price(self, price_order):
        new_price_order = price_order * (1 + binance_config_websocket.CONFIDENCE_ORDER)
        quantity = binance_config_websocket.VALUE_QUANTITY * (
                1 + binance_config_websocket.CONFIDENCE_QUANTITY) / new_price_order

        new_price_order = self.round_price(new_price_order)
        quantity_order = self.round_quantity(quantity)

        return quantity_order, new_price_order

    async def define_min_price_and_quantity(self):
        info = await self.client.get_symbol_info(symbol=binance_config_websocket.SYMBOL)
        self.minimum_price = float(info['filters'][0]['minPrice'])
        self.minimum_quantity = float(info['filters'][2]['minQty'])

    async def buy_or_sell(self, side, order_type, price, quantity, quote_order_qty, time_in_force):
        await self.client.create_test_order(
            symbol=binance_config_websocket.SYMBOL,
            side=side,
            type=order_type,
            price=price,
            quantity=quantity,
            quoteOrderQty=quote_order_qty,
            timeInForce=time_in_force,
            recvWindow=binance_config_websocket.RECVWINDOW
        )

    async def market_order(self, side):
        await self.buy_or_sell(side=side, order_type=ORDER_TYPE_MARKET, price=None, quantity=None,
                               quote_order_qty=binance_config_websocket.QUOTE_ORDER_QTY, time_in_force=None)

    async def limit_order(self, side, price_order):
        if self.minimum_price is None:
            await self.define_min_price_and_quantity()

        quantity_order, new_price_order = await self.get_quantity_order_and_new_price(price_order)

        await self.buy_or_sell(side=side, order_type=ORDER_TYPE_LIMIT,
                               price=new_price_order,
                               quantity=quantity_order,
                               quote_order_qty=None, time_in_force=TIME_IN_FORCE_GTC)

        return quantity_order, new_price_order

    # Retornar informações da conta do usuário
    async def get_values(self):
        return await self.client.get_isolated_margin_account()

    # Retorna o valor total em P1 ou P2: valor em conta + empréstimo
    async def get_balance(self, coin):
        values = await self.get_values()

        balance = None
        for asset in values['assets']:
            if asset['symbol'] == binance_config_websocket.SYMBOL:
                if coin == binance_config_websocket.SYMBOL_P1:
                    balance = asset['baseAsset']['free']
                    print('\t\t\t*** [P1 SALDO (' + balance + ')] ***')
                    break
                else:
                    balance = asset['quoteAsset']['free']
                    print('\t\t\t*** [P2 SALDO (' + balance + ')] ***')
                    break

        return float(balance)

    # Retorna o valor total emprestado em P1 ou P2
    async def get_balance_borrowed(self, coin):
        values = await self.get_values()

        balance_borrowed = None
        for asset in values['assets']:
            if asset['symbol'] == binance_config_websocket.SYMBOL:
                if coin == binance_config_websocket.SYMBOL_P1:
                    balance_borrowed = float(asset['baseAsset']['borrowed'])
                else:
                    balance_borrowed = float(asset['quoteAsset']['borrowed'])

        return self.round_quantity(balance_borrowed)

    # Retorna o valor atual de p1
    async def get_current_coin_price(self):
        current_coin_price = None
        for latest_prices in await self.client.get_all_tickers():
            if latest_prices['symbol'] == binance_config_websocket.SYMBOL:
                current_coin_price = latest_prices['price']

        print('\t\t\t*** Preço atual (%s): %s ***' % (binance_config_websocket.SYMBOL_P1, current_coin_price))

        return float(current_coin_price)

    # Retorna o saldo total que está disponível para empréstimo na moeda especificada
    async def get_total_borrow(self, coin):
        details = await self.client.get_max_margin_loan(asset=coin, isolatedSymbol=binance_config_websocket.SYMBOL)
        return self.round_quantity(float(details['amount']))

    # Retorna a quantidade, para compra ou venda, de acordo com o saldo disponível em P1 ou P2
    async def get_quantity(self, coin):
        if coin == binance_config_websocket.SYMBOL_P1:
            quantity = await self.get_balance(binance_config_websocket.SYMBOL_P1) * \
                       (1 - binance_config_websocket.FEE_BROKERAGE)
        else:
            quantity = await self.get_balance(binance_config_websocket.SYMBOL_P2) / \
                       await self.get_current_coin_price() * (1 - binance_config_websocket.FEE_BROKERAGE)
        return self.round_quantity(quantity)

    # Tomar empréstimo
    async def get_loan(self, coin, value):
        transaction = await self.client.create_margin_loan(asset=coin, amount=value, isIsolated=True,
                                                           symbol=binance_config_websocket.SYMBOL)
        print('\t\t\t*** tranId: ' + str(transaction['tranId']) + ', Symbol: ' + binance_config_websocket.SYMBOL +
              ', Amount: ' + str(value) + ' ***')

    # Fazer reembolso do valor emprestado
    async def repay_loan(self, coin, value):
        await self.client.repay_margin_loan(asset=coin, amount=value, isIsolated=True,
                                            symbol=binance_config_websocket.SYMBOL)

    async def buy_or_sell_margin(self, side, quantity):
        await self.client.create_margin_order(symbol=binance_config_websocket.SYMBOL, side=side, type=ORDER_TYPE_MARKET,
                                              quantity=quantity, recvWindow=binance_config_websocket.RECVWINDOW,
                                              isIsolated=True)

# LOT SIZE: 2473685.3
# MIN NOTIONAL: 10
# OK: 1000000

    async def margin_order(self, side):
        if self.minimum_price is None:
            await self.define_min_price_and_quantity()

        values = await self.get_values()
        if side == SIDE_BUY:  # BUY
            for asset in values['assets']:
                if asset['symbol'] == binance_config_websocket.SYMBOL:
                    print(f"\t\t\t=== MARGIN LEVEL: {float(asset['marginLevel'])}")
                    break

            # Tentativa de compra

            if is_above_min(binance_config_websocket.SYMBOL_P2,
                            await self.get_balance(binance_config_websocket.SYMBOL_P2),
                            await self.get_current_coin_price()):
                for id_attempt in range(binance_config_websocket.NUMBER_ATTEMPTS_MARGIN):
                    try:
                        print('\t\t\t=== Tentativa de Compra em P1 - max (%i/%i)'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        await self.buy_or_sell_margin(SIDE_BUY,
                                                      await self.get_quantity(binance_config_websocket.SYMBOL_P2))

                        print('\t\t\t=== Tentativa de Compra em P1 - max (%i/%i) [SUCCESS]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        if binance_config_websocket.IS_PAUSE_MODE:
                            pause_mode()

                        break

                    except Exception as binance_except:
                        print('\t\t\t=== ' + str(binance_except))
                        print('\t\t\t=== Tentativa de Compra em P1 - max (%i/%i) [ERROR]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

            # Tentativa de reembolso

            balance_borrowed_p1 = await self.get_balance_borrowed(binance_config_websocket.SYMBOL_P1)
            print('\t\t\t=== Total emprestado em P1: ' + str(balance_borrowed_p1))
            current_price = await self.get_current_coin_price()
            if is_above_min(binance_config_websocket.SYMBOL_P1, balance_borrowed_p1, current_price) is True and \
                    is_above_min(binance_config_websocket.SYMBOL_P1,
                                 await self.get_balance(binance_config_websocket.SYMBOL_P1), current_price) is True:
                for id_attempt in range(binance_config_websocket.NUMBER_ATTEMPTS_MARGIN):
                    try:
                        print('\t\t\t=== Tentativa de pagar empréstimo em P1 - max (%i/%i)'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        await self.repay_loan(binance_config_websocket.SYMBOL_P1, balance_borrowed_p1)
                        time.sleep(binance_config_websocket.SLEEP_TIME_MARGIN)

                        print('\t\t\t=== Tentativa de pagar empréstimo em P1 - max (%i/%i) [SUCCESS]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        if binance_config_websocket.IS_PAUSE_MODE:
                            pause_mode()

                        break

                    except Exception as binance_except:
                        print('\t\t\t=== ' + str(binance_except))
                        print('\t\t\t=== Tentativa de pagar empréstimo em P1 - max (%i/%i) [ERROR]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

            # Tentativa de empréstimo

            total_borrow_p2 = await self.get_total_borrow(binance_config_websocket.SYMBOL_P2)
            print('\t\t\t=== Total disponível para empréstimo em P2: ' + str(total_borrow_p2))
            if is_above_min(binance_config_websocket.SYMBOL_P2, total_borrow_p2,
                            await self.get_current_coin_price()):
                for id_attempt in range(binance_config_websocket.NUMBER_ATTEMPTS_MARGIN):
                    try:
                        print('\t\t\t=== Tentativa de empréstimo em P2 - max (%i/%i)'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        await self.get_loan(binance_config_websocket.SYMBOL_P2, total_borrow_p2)
                        time.sleep(binance_config_websocket.SLEEP_TIME_MARGIN)

                        print('\t\t\t=== Tentativa de empréstimo em P2 - max (%i/%i) [SUCCESS]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        if binance_config_websocket.IS_PAUSE_MODE:
                            pause_mode()

                        break

                    except Exception as binance_except:
                        print('\t\t\t=== ' + str(binance_except))
                        print('\t\t\t=== Tentativa de empréstimo em P2 - max (%i/%i) [ERROR]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

            # Tentativa de compra

            if is_above_min(binance_config_websocket.SYMBOL_P2,
                            await self.get_balance(binance_config_websocket.SYMBOL_P2),
                            await self.get_current_coin_price()):
                for id_attempt in range(binance_config_websocket.NUMBER_ATTEMPTS_MARGIN):
                    try:
                        print('\t\t\t=== Tentativa de Compra em P1 - max (%i/%i)'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        await self.buy_or_sell_margin(SIDE_BUY,
                                                      await self.get_quantity(binance_config_websocket.SYMBOL_P2))

                        print('\t\t\t=== Tentativa de Compra em P1 - max (%i/%i) [SUCCESS]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        if binance_config_websocket.IS_PAUSE_MODE:
                            pause_mode()

                        break

                    except Exception as binance_except:
                        print('\t\t\t=== ' + str(binance_except))
                        print('\t\t\t=== Tentativa de Compra em P1 - max (%i/%i) [ERROR]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

        else:  # SELL
            for asset in values['assets']:
                if asset['symbol'] == binance_config_websocket.SYMBOL:
                    print(f"\t\t\t=== MARGIN LEVEL: {float(asset['marginLevel'])}")
                    break

            # Tentativa de venda

            if is_above_min(binance_config_websocket.SYMBOL_P1,
                            await self.get_balance(binance_config_websocket.SYMBOL_P1),
                            await self.get_current_coin_price()):
                for id_attempt in range(binance_config_websocket.NUMBER_ATTEMPTS_MARGIN):
                    try:
                        print('\t\t\t=== Tentativa de Venda em P1 - max (%i/%i)'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        await self.buy_or_sell_margin(SIDE_SELL,
                                                      await self.get_quantity(binance_config_websocket.SYMBOL_P1))

                        print('\t\t\t=== Tentativa de Venda em P1 - max (%i/%i) [SUCCESS]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        if binance_config_websocket.IS_PAUSE_MODE:
                            pause_mode()

                        break

                    except Exception as binance_except:
                        print('\t\t\t=== ' + str(binance_except))
                        print('\t\t\t=== Tentativa de Venda em P1 - max (%i/%i) [ERROR]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

            # Tentativa de reembolso

            balance_borrowed_p2 = await self.get_balance_borrowed(binance_config_websocket.SYMBOL_P2)
            print('\t\t\t=== Total emprestado em P2: ' + str(balance_borrowed_p2))
            current_price = await self.get_current_coin_price()
            if is_above_min(binance_config_websocket.SYMBOL_P2, balance_borrowed_p2, current_price) is True and \
                    is_above_min(binance_config_websocket.SYMBOL_P2,
                                 await self.get_balance(binance_config_websocket.SYMBOL_P2), current_price) is True:
                for id_attempt in range(binance_config_websocket.NUMBER_ATTEMPTS_MARGIN):
                    try:
                        print('\t\t\t=== Tentativa de pagar empréstimo em P2 - max (%i/%i)'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        await self.repay_loan(binance_config_websocket.SYMBOL_P2, balance_borrowed_p2)
                        time.sleep(binance_config_websocket.SLEEP_TIME_MARGIN)

                        print('\t\t\t=== Tentativa de pagar empréstimo em P2 - max (%i/%i) [SUCCESS]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        if binance_config_websocket.IS_PAUSE_MODE:
                            pause_mode()

                        break

                    except Exception as binance_except:
                        print('\t\t\t=== ' + str(binance_except))
                        print('\t\t\t=== Tentativa de pagar empréstimo em P2 - max (%i/%i) [ERROR]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

            # Tentativa de empréstimo

            total_borrow_p1 = await self.get_total_borrow(binance_config_websocket.SYMBOL_P1)
            print('\t\t\t=== Total disponível para empréstimo em P1: ' + str(total_borrow_p1))
            if is_above_min(binance_config_websocket.SYMBOL_P1, total_borrow_p1,
                            await self.get_current_coin_price()):
                for id_attempt in range(binance_config_websocket.NUMBER_ATTEMPTS_MARGIN):
                    try:
                        print('\t\t\t=== Tentativa de empréstimo em P1 - max (%i/%i)'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        await self.get_loan(binance_config_websocket.SYMBOL_P1, total_borrow_p1)
                        time.sleep(binance_config_websocket.SLEEP_TIME_MARGIN)

                        print('\t\t\t=== Tentativa de empréstimo em P1 - max (%i/%i) [SUCCESS]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        if binance_config_websocket.IS_PAUSE_MODE:
                            pause_mode()

                        break

                    except Exception as binance_except:
                        print('\t\t\t=== ' + str(binance_except))
                        print('\t\t\t=== Tentativa de empréstimo em P1 - max (%i/%i) [ERROR]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

            # Tentativa de venda

            if is_above_min(binance_config_websocket.SYMBOL_P1,
                            await self.get_balance(binance_config_websocket.SYMBOL_P1),
                            await self.get_current_coin_price()):
                for id_attempt in range(binance_config_websocket.NUMBER_ATTEMPTS_MARGIN):
                    try:
                        print('\t\t\t=== Tentativa de Venda em P1 - max (%i/%i)'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        await self.buy_or_sell_margin(SIDE_SELL,
                                                      await self.get_quantity(binance_config_websocket.SYMBOL_P1))

                        print('\t\t\t=== Tentativa de Venda em P1 - max (%i/%i) [SUCCESS]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))

                        if binance_config_websocket.IS_PAUSE_MODE:
                            pause_mode()

                        break

                    except Exception as binance_except:
                        print('\t\t\t=== ' + str(binance_except))
                        print('\t\t\t=== Tentativa de Venda em P1 - max (%i/%i) [ERROR]'
                              % (id_attempt + 1, binance_config_websocket.NUMBER_ATTEMPTS_MARGIN))
