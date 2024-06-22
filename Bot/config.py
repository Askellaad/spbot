#  Put Your BYBIT APi keys here
api_key = "scgmzJDAWTOFwDWA8z"
secret_key = "ZH5S8cRcnHUhwTg9MRyZVgoWUUgJKewHrib2"

#  bot secret key
secret = "miraclebot"

# Grid Configuration

category = "linear"     # its account type. No need to change
symbol = "OPUSDT"       # pair on which you want to use the GRID
orderType = "Market"    # options (Market / limit). Use Market to place the order instantly, and limit to wait for the price to reach
qty = 20  # quatity     # quantity of the coin e.g. OP you want to use for initial trade

favor_levels = 4        # Number of Favor levels in the GRID
against_levels = 10     # Nnumber of Against levels in the GRID

percentage_difference_favor = 1    # minimum 0.2 / Percentage off the difference among favor levels
percentage_difference_against = 1  # minimum 0.2 / Percentage off the difference among against levels

botOrderType = "Grid_bot_order"     # dont change it
timeInForce = "GTC"     # dont change it
reduceOnly = "false",   # dont change it
Exchange = "Bybit",     # dont change it
