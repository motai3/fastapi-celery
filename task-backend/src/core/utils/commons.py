import os
import traceback

import time
import pandas as pd
from datetime import datetime, timedelta


def retry_wrapper(func, params=None, func_name='', retry_times=5, sleep_seconds=5, if_exit=True):
    """
    需要在出错时不断重试的函数，例如和交易所交互，可以使用本函数调用。
    :param func:            需要重试的函数名
    :param params:          参数
    :param func_name:       方法名称
    :param retry_times:     重试次数
    :param sleep_seconds:   报错后的sleep时间
    :param if_exit:         报错是否退出程序
    :return:
    """
    if params is None:
        params = {}
    for _ in range(retry_times):
        try:
            if 'timestamp' in params:
                from core.binance.base_client import BinanceClient
                params['timestamp'] = int(time.time() * 1000) - BinanceClient.diff_timestamp
            result = func(params=params)
            return result
        except Exception as e:
            print(e)
            msg = str(e).strip()
            print(msg)
    else:
        if if_exit:
            raise ValueError(func_name, '报错重试次数超过上限，程序退出。')