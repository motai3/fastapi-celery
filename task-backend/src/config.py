# -*- coding: utf-8 -*-
"""
选币策略框架 | 邢不行 | 2024分享会
author: 邢不行
微信: xbx6660

# 配置区域说明
1. 【全局】运行模式相关配置，设置并行数量，稳定币种，特殊币种，debug模式等
2. 【核心】账户及策略相关配置，设置账户名称，策略名称等
3. 【网络】交易所相关配置，设置交易所代理等
4. 【其他】文件系统相关配置，自动化创建文件夹
"""
import os
import time
# ====================================================================================================
# ** 运行模式及交易细节设置 **
# 设置系统的时差、并行数量，稳定币，特殊币种等等
# ====================================================================================================
# region 运行模式设置

# 是否使用数据API服务的开关。默认: False
use_data_api = False

# 个人中心里面的api_key配置。（网址：https://www.quantclass.cn/login）
api_key = ''

# 个人中心里面的葫芦id。（网址：https://www.quantclass.cn/login）
uuid = ''

# debug模式。模拟运行程序，不会去下单
is_debug = True

# 获取当前服务器时区，距离UTC 0点的偏差
utc_offset = int(time.localtime().tm_gmtoff / 60 / 60)  # 如果服务器在上海，那么utc_offset=8

# 现货稳定币名单，不参与交易的币种
stable_symbol = ['BKRW', 'USDC', 'USDP', 'TUSD', 'BUSD', 'FDUSD', 'DAI', 'EUR', 'GBP', 'USBP', 'SUSD', 'PAXG', 'AEUR',
                 'EURI']

# 特殊现货对应列表。有些币种的现货和合约的交易对不一致，需要手工做映射
special_symbol_dict = {
    'DODO': 'DODOX',  # DODO现货对应DODOX合约
    'LUNA': 'LUNA2',  # LUNA现货对应LUNA2合约
    '1000SATS': '1000SATS',  # 1000SATS现货对应1000SATS合约
}

# 现货下单最小金额限制，适当增加可以减少部分reb。
# 默认10，不建议小于10，这会让你的下单报错，10是交易所的限制。
order_spot_money_limit = 10

# 合约下单最小金额限制，适当增加可以减少部分reb。
# 默认5，不建议小于5，这会让你的下单报错，5是交易所的限制。
order_swap_money_limit = 5

# 全局报错机器人通知
# - 创建企业微信机器人 参考帖子: https://bbs.quantclass.cn/thread/10975
# - 配置案例  https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxxxxxxxxxxxxx
error_webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='
# endregion


# ====================================================================================================
# ** 账户及策略配置 **
# 【核心设置区域】设置账户API，策略详细信息，交易的一些特定参数等等
# * 注意，以下功能都是在config.py中实现
# ====================================================================================================

# ------ 框架重要功能 ------
# 支持“纯合约模式”：多头和空头都是合约。
# 支持“现货+合约模式”：多头可以包含现货、合约，空头包含合约。
# 纯多功能：全部仓位只买入策略的多头。不交易空头。
# 统一账户功能：可以在 `传统的非统一账户` 和 `统一账户`模式 之间选择。任何模式下，原有功能都保留
# 分钟偏移功能：支持任意时间开始的小时级别K线
# 多账户功能：一个程序可以同时在多个账户下运行策略。
# 多offset功能

# ------ 策略级别功能 ------
# 多策略融合功能（大杂烩）：一个账户下可以同时运行多个选币策略。例如可以在一个账户下，使用一份资金，运行策略A（参数1）、策略A（参数2）、策略A（参数3）、策略B（参数1）、策略B（参数2）。以此类推。
# 多策略资金配比功能：一个账户运行多个策略时，每个策略可以配置不同的资金比例。
# 多空分离选币：多头和空头可以使用不一样的策略。
# 多空分离过滤（前置）：多头和空头的前置过滤条件可以不同。
# 数据整理支持自定义数据：支持在策略中加入量价数据之外的任意第三方数据

# ------ 其他功能 ------
# 自动rebalance功能。默认开启，可以关闭后手动rebalance
# rebalance时，可以设定最小下单量。例如设置为50u，可以显著降低无效换手。
# 下单时动态拆单功能
# BNB抵扣手续费功能。开启BNB燃烧，抵扣手续费
# 小额资产自动兑换BNB功能。
# 企业微信机器人通知功能。开启企业微信机器人
# 交易黑名单与白名单功能。开启选币黑名单与白名单
# ====================================================================================================

# ++++ 多账户多策略 ++++
# 多账户功能：一个程序可以同时在多个账户下运行策略。同时兼容不同的账户类型。
account_config = {
    "账户1": {
        # 交易所API配置
        'apiKey': '',
        'secret': '',

        # ++++ 策略配置 ++++
        # 多策略融合功能（大杂烩）：一个账户下可以同时运行多个选币策略。例如可以在一个账户下，使用一份资金，运行策略A（参数1）、策略A（参数2）、策略A（参数3）、策略B（参数1）、策略B（参数2）。以此类推。
        # 多策略资金配比功能：一个账户运行多个策略时，每个策略可以配置不同的资金比例。
        # 多空分离选币：多头和空头可以使用不一样的策略。
        # 多空分离过滤（前置）：多头和空头的前置过滤条件可以不同。
        # 数据整理支持自定义数据：支持在策略中加入量价数据之外的任意第三方数据
        "strategy_list": [
            # ===========================================================
            # !!! 实盘前先回测一下，不要无脑跑案例策略，没人能保证案例策略能赚钱 !!!
            # 以下配置非官方提供的案例策略，这里只是举例如何配置，具体配置请自行处理
            # ===========================================================
            {
                # 策略名称。与strategy目录中的策略文件名保持一致。
                "strategy": "Strategy_Spot_80",
                # ++++ 多offset功能 ++++
                # 可以使用1个或者多个offset。可以看 https://bbs.quantclass.cn/thread/36188 了解什么是offset？
                "offset_list": [0],
                # 资金权重。程序会自动根据这个权重计算你的策略占比，具体可以看1.8的直播讲解
                "cap_weight": 1,
            },
            {
                "strategy": "Strategy_Spot_100",
                "offset_list": [0],
                "cap_weight": 1,
            },
            {
                "strategy": "Strategy_Spot_151",
                "offset_list": [0],
                "cap_weight": 1,
            },
            {
                "strategy": "Strategy_Spot_168",
                "offset_list": [0],
                "cap_weight": 1,
            },
            {
                "strategy": "Strategy_Spot_320",
                "offset_list": [0],
                "cap_weight": 1,
            },
        ],

        # ++++ 切换“纯合约模式”和“现货+合约模式” ++++
        # False - 支持“纯合约模式”：多头和空头都是合约。
        # True  - 支持“现货+合约模式”：多头可以包含现货、合约，空头包含合约。
        "use_spot": True,  # 是否使用现货交易

        # ++++ 纯多功能 ++++
        # 全部仓位只买入策略的多头。不交易空头。
        "is_pure_long": False,  # 纯多设置(https://bbs.quantclass.cn/thread/36230)

        # ++++ 统一账户功能 ++++
        # 可以在 `传统的非统一账户` 和 `统一账户`模式 之间选择。任何模式下，原有功能都保留
        # 支持账户类型：统一账户，普通账户
        'account_type': '普通账户',
        # 套利底仓设置。例：['ETHUSDT'].
        # - 底仓默认为空，当底仓为空的时候，可以开启现货+合约模式
        # - 当底仓不为空的时候，程序默认自动启动纯合约模式
        # - 如果真的需要，可以diy注释相关逻辑代码
        'seed_coins': ['ETHUSDT', 'BTCUSDT'],
        # 指定币种当保证金。例：{'ETHUSDT': {'amount': 1, 'usdt': 1000},}
        # - 普通账户需要将保证金币种，手动划转到合约账户才会生效，如果在现货账户，程序会帮你卖掉
        # - 统一账户将保证金币种放在杠杆钱包即可，不需要划转
        # - 如果账户指定币种数量不足，不会计算保证金
        # - 保证金对应usdt，自己可以diy修改
        'coin_margin': {
            'ETHUSDT': {'amount': 0, 'usdt': 0},
            'BTCUSDT': {'amount': 0, 'usdt': 0},
        },

        # ++++ 分钟偏移功能 ++++
        # 支持任意时间开始的小时级别K线
        "hour_offset": '5m',  # 分钟偏移设置，可以自由设置时间，配置必须是kline脚本中interval的倍数。默认：0m，表示不偏移。15m，表示每个小时偏移15m下单。

        # ++++ 自动rebalance功能 ++++
        "if_rebalance": True,  # 是否开启rebalance模式，默认True，表示开启，False表示不开启。
        # 可以设定下单时的最小下单量。例如设置为50u，可以显著降低无效换手。
        'order_spot_money_limit': order_spot_money_limit,
        'order_swap_money_limit': order_swap_money_limit,

        # ++++ 下单时动态拆单功能 ++++
        "max_one_order_amount": 100,  # 最大拆单金额。
        "twap_interval": 2,  # 下单间隔

        # ++++ BNB抵扣手续费功能 ++++
        "if_use_bnb_burn": True,  # 是否开启BNB燃烧，抵扣手续费
        "buy_bnb_value": 11,  # 买多少U的bnb来抵扣手续费。建议最低11U，现货最小下单量限制10U

        # ++++ 小额资产自动兑换BNB功能 ++++
        # 当且仅当 `if_use_bnb_burn` 为 True 时生效
        "if_transfer_bnb": False,  # 是否开启小额资产兑换BNB功能。仅现货模式下生效

        # ++++ 企业微信机器人功能 ++++
        "wechat_webhook_url": 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=',
        # 创建企业微信机器人 参考帖子: https://bbs.quantclass.cn/thread/10975
        # 配置案例  https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxxxxxxxxxxxxx

        # ++++ 交易黑名单与白名单功能 ++++
        "black_list": ['BTCUSDT', 'ETHUSDT', 'BTSUSDT'],  # 黑名单。不参与策略的选币，如果持有黑名单币种，将会自动清仓
        "white_list": [],  # 白名单。只参与策略的选币

        # ++++ 其他账户设置 ++++
        "leverage": 1,  # 杠杆。现货模式下：最大杠杆限制1.3倍。合约模式不做限制。
        "get_kline_num": 999,  # 获取多少根K线。这里跟策略日频和小时频影响。日线策略，代表999根日线k。小时策略，代表999根小时k
        "min_kline_size": 168,  # 最低要求b中有多少小时的k线。这里与回测一致。168：表示168小时
    },
}

# ====================================================================================================
# ** 交易所配置 **
# ====================================================================================================
# 如果使用代理 注意替换IP和Port
proxy = {}
# proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}  # 如果你用clash的话
exchange_basic_config = {
    'timeout': 30000,
    'rateLimit': 30,
    'enableRateLimit': False,
    'options': {
        'adjustForTimeDifference': True,
        'recvWindow': 10000,
    },
    'proxies': proxy,
    'is_pure_long': False
}

# ====================================================================================================
# ** 文件系统相关配置 **
# - 获取一些全局路径
# - 自动创建缺失的文件夹们
# ====================================================================================================
# region 文件系统相关
root_path = os.path.abspath(os.path.dirname(__file__))  # 返回当前文件路径
# endregion
