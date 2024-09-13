"""
2024分享会
author: 邢不行
微信: xbx6660
选币策略框架
"""
# ==================================================================================================
# !!! 前置非常重要说明
# !!! 前置非常重要说明
# !!! 前置非常重要说明
# ---------------------------------------------------------------------------------------------------
# ** 帐户说明 **
# spot：对于普通账户来说，是纯现货；对于统一账户来说是margin
# swap：对于普通账户和统一账户来说，都是 um swap
# ---------------------------------------------------------------------------------------------------
# ** 方法名前缀规范 **
# 1. load_* 从硬盘获取数据
# 2. fetch_* 从接口获取数据
# 3. get_* 从对象获取数据，可能从硬盘，也可能从接口
# ====================================================================================================

import math
import time
import traceback
from datetime import datetime, timedelta

import ccxt
import numpy as np
import pandas as pd
from src.core.utils.commons import retry_wrapper

from src.config import exchange_basic_config, utc_offset, stable_symbol


# 现货接口
# sapi

# 合约接口
# dapi：普通账户，包含币本位交易
# fapi，普通账户，包含U本位交易

# 统一账户
# papi, um的接口：U本位合约
# papi, cm的接口：币本位合约
# papi, margin：现货API，全仓杠杆现货

class BinanceClient:
    diff_timestamp = 0
    constants = dict()

    market_info = {}  # 缓存市场信息，并且自动更新，全局共享
    common_exchange = ccxt.binance(exchange_basic_config)

    def __init__(self, **config):
        self.api_key: str = config.get('apiKey', '')
        self.secret: str = config.get('secret', '')

        self.order_money_limit: dict = {
            'spot': config.get('spot_order_money_limit', 10),
            'swap': config.get('swap_order_money_limit', 5),
        }

        self.exchange = ccxt.binance(config.get('exchange_config', exchange_basic_config))
        self.wechat_webhook_url: str = config.get('wechat_webhook_url', '')


        self.swap_account = None

        self.coin_margin: dict = config.get('coin_margin', {})  # 用做保证金的币种

    # ====================================================================================================
    # ** 市场信息 **
    # ====================================================================================================
    def _fetch_swap_exchange_info_list(self) -> list:
        exchange_info = retry_wrapper(self.exchange.fapipublic_get_exchangeinfo, func_name='获取BN合约币种规则数据')
        return exchange_info['symbols']

    def _fetch_spot_exchange_info_list(self) -> list:
        exchange_info = retry_wrapper(self.exchange.public_get_exchangeinfo, func_name='获取BN现货币种规则数据')
        return exchange_info['symbols']

    # region 市场信息数据获取
    def fetch_market_info(self, symbol_type='swap', quote_symbol='USDT'):
        """
        加载市场数据
        :param symbol_type: 币种信息。swap为合约，spot为现货
        :param quote_symbol: 报价币种
        :return:
            symbol_list     交易对列表
            price_precision 币种价格精     例： 2 代表 0.01
                {'BTCUSD_PERP': 1, 'BTCUSD_231229': 1, 'BTCUSD_240329': 1, 'BTCUSD_240628': 1, ...}
            min_notional    最小下单金额    例： 5.0 代表 最小下单金额是5U
                {'BTCUSDT': 5.0, 'ETHUSDT': 5.0, 'BCHUSDT': 5.0, 'XRPUSDT': 5.0...}
        """
        # ===获取所有币种信息
        if symbol_type == 'swap':  # 合约
            exchange_info_list = self._fetch_swap_exchange_info_list()
        else:  # 现货
            exchange_info_list = self._fetch_spot_exchange_info_list()

        # ===获取币种列表
        symbol_list = []  # 如果是合约，只包含永续合约。如果是现货，包含所有数据
        full_symbol_list = []  # 包含所有币种信息

        # ===获取各个交易对的精度、下单量等信息
        min_qty = {}  # 最小下单精度，例如bnb，一次最少买入0.001个
        price_precision = {}  # 币种价格精，例如bnb，价格是158.887，不能是158.8869
        min_notional = {}  # 最小下单金额，例如bnb，一次下单至少买入金额是5usdt
        # 遍历获得想要的数据
        for info in exchange_info_list:
            symbol = info['symbol']  # 交易对信息

            # 过滤掉非报价币对 ， 非交易币对
            if info['quoteAsset'] != quote_symbol or info['status'] != 'TRADING':
                continue

            full_symbol_list.append(symbol)  # 添加到全量信息中

            if (symbol_type == 'swap' and info['contractType'] != 'PERPETUAL') or info['baseAsset'] in stable_symbol:
                pass  # 获取合约的时候，非永续的symbol会被排除
            else:
                symbol_list.append(symbol)

            for _filter in info['filters']:  # 遍历获得想要的数据
                if _filter['filterType'] == 'PRICE_FILTER':  # 获取价格精度
                    price_precision[symbol] = int(math.log(float(_filter['tickSize']), 0.1))
                elif _filter['filterType'] == 'LOT_SIZE':  # 获取最小下单量
                    min_qty[symbol] = int(math.log(float(_filter['minQty']), 0.1))
                elif _filter['filterType'] == 'MIN_NOTIONAL' and symbol_type == 'swap':  # 合约的最小下单金额
                    min_notional[symbol] = float(_filter['notional'])
                elif _filter['filterType'] == 'NOTIONAL' and symbol_type == 'spot':  # 现货的最小下单金额
                    min_notional[symbol] = float(_filter['minNotional'])

        self.market_info[symbol_type] = {
            'symbol_list': symbol_list,  # 如果是合约，只包含永续合约。如果是现货，包含所有数据
            'full_symbol_list': full_symbol_list,  # 包含所有币种信息
            'min_qty': min_qty,
            'price_precision': price_precision,
            'min_notional': min_notional,
            'last_update': int(time.time())
        }
        return self.market_info[symbol_type]

    def get_market_info(self, symbol_type, expire_seconds: int = 3600 * 12, require_update: bool = False,
                        quote_symbol='USDT') -> dict:
        if require_update:  # 如果强制刷新的话，就当我们系统没有更新过
            last_update = 0
        else:
            last_update = self.market_info.get(symbol_type, {}).get('last_update', 0)
        if last_update + expire_seconds < int(time.time()):
            self.fetch_market_info(symbol_type, quote_symbol)

        return self.market_info[symbol_type]
    


    @classmethod
    def get_dummy_client(cls) -> 'BinanceClient':
        return cls()

   