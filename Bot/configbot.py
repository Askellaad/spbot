class Config:
    API_KEY = "scgmzJDAWTOFwDWA8z"
    SECRET_KEY = "ZH5S8cRcnHUhwTg9MRyZVgoWUUgJKewHrib2"

    SYMBOL = "OP/USDT:USDT"
    POSITION_SIZE = 1000
    POSITION_SIDE = 'SHORT'

    LONG_SIZE = 200
    SHORT_SIZE = 200

    PC_LONG = 1.0 # In percentage for long orders
    PC_SHORT = 1.0 # Percentage for short orders

    NUM_BUY_GRID_LINES = 20
    NUM_SELL_GRID_LINES = 20

    #GRID_SIZE = 200

    CHECK_ORDERS_FREQUENCY = 1 # Check order after 1 second
    FILLED_ORDER_STATUS = 'Filled'

    LOG_FILE = 'trading.log'

    ORDER_LOG = 'orders.json'
