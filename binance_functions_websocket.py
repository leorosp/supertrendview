import binance_config_websocket

from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET

import numpy as np
import sys
import time
import os


def while_try_except(code_block, exception, print_except=True, print_in_try=None, print_in_except=None, **kwargs):
    for key, value in kwargs.items():
        exec(key + '= value')

    status_except = True
    while status_except:
        try:
            for code in code_block:
                exec(code)

            if print_in_try is not None:
                print(print_in_try)

            status_except = False

        except exception:
            if print_except:
                print(exception)

            if print_in_except is not None:
                print(print_in_except)

            # status_except = True


async def while_try_except_async(code_block, exception, print_except=True, print_in_try=None, print_in_except=None,
                                 **kwargs):
    for key, value in kwargs.items():
        exec(key + '= value')

    status_except = True
    while status_except:
        try:
            for code in code_block:
                await eval(code)

            if print_in_try is not None:
                print(print_in_try)

            status_except = False

        except exception:
            if print_except:
                print(exception)

            if print_in_except is not None:
                print(print_in_except)

            # status_except = True


def is_above_min(coin, value, current_price):
    reference_value = binance_config_websocket.MIN_VALUE_QUANTITY * (
            1 + binance_config_websocket.MIN_CONFIDENCE_QUANTITY)
    if coin == binance_config_websocket.SYMBOL_P1:
        return value * current_price > reference_value
    else:
        return value > reference_value


def pause_mode():
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


def update_timer(start_time, timer):
    end_time = time.time()
    runtime = end_time - start_time
    diff_runtime = timer - runtime
    is_time = (runtime >= timer)

    if is_time:
        diff_runtime = 0

    return is_time, diff_runtime


def update_sleep_time(sleep_time):
    sleep_time *= (1 + binance_config_websocket.RATE_SLEEP_TIME)

    if sleep_time > binance_config_websocket.MAX_SLEEP_TIME:
        sleep_time = binance_config_websocket.MAX_SLEEP_TIME

    return sleep_time


def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        os.remove(folder_path + '\\' + filename)
