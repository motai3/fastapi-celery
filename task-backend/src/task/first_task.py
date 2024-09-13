import time
from src.worker import celery
from src.core.binance.base_client import BinanceClient

cli = BinanceClient.get_dummy_client()

@celery.task(name="print_symbol")
def print_symbol(task_type):
    swap_market_info = cli.get_market_info(symbol_type='swap', require_update=True)
    swap_symbol_list = swap_market_info.get('symbol_list', [])
    print(swap_symbol_list)
    # =加载现货交易对信息
    spot_market_info = cli.get_market_info(symbol_type='spot', require_update=True)
    spot_symbol_list = spot_market_info.get('symbol_list', [])
    print(spot_symbol_list)
    return True