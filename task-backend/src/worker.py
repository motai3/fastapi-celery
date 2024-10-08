import os
import time

from src.core.binance.base_client import BinanceClient
from celery import Celery

cli = BinanceClient.get_dummy_client()

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True

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