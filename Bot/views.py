import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime
import requests
import ccxt
from django.http import JsonResponse
# import uuid
# from datetime import datetime
# from decimal import Decimal

from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from SupermanBot.serializer import OrderSerializer
from .models import Orders
from rest_framework.views import APIView
# from SupermanBot import
from pybit.unified_trading import HTTP

from Bot import config
import pytz


@api_view(['GET'])
def get_orders(request, format=None):
    orders = Orders.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST', 'GET'])
def open_order(request):
    if request.method == 'GET':
        orders = Orders.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        try:
            data = request.data
            print(data)
            """
            necessary
            
            category
            symbol
            side
            orderType
            qty
            price
            triggerPrice
            positionIdx = 0
            reduceOnly = false
            
            # for bot 
            time,
            Exchange
            takeProfit
            stopLoss
            botOrderType
            """

            tiime = data['time']   # it will be calculated automatically from the function
            secret = data['secret']
            # time = pytz.utc.localize(datetime.utcnow())
            category = data['category']  # string
            symbol = data['symbol']
            side = data['side']
            orderType = data['orderType']
            qty = data['qty']  # string
            Exchange = data['Exchange']
            # timeInForce = data['timeInForce']
            """
            Optional but better
            """
            price = data['price']
            triggerPrice = data['triggerPrice']
            positionIdx = data['positionIdx']
            takeProfit = data['takeProfit']
            stopLoss = data['stopLoss']
            reduceOnly = data['reduceOnly']
            botOrderType = 'open order'

            order = {

                "time": int(round(time.time() * 1000)),
                "category": category,  # string
                "symbol": symbol,
                "side": side,
                "orderType": orderType,
                "qty": qty,  # string
                "Exchange": Exchange,
                "price": price,
                "triggerPrice": triggerPrice,
                "positionIdx": "0",
                "takeProfit": takeProfit,
                "stopLoss": stopLoss,
                "reduceOnly": reduceOnly,
                # "botOrderType": botOrderType
            }
            print('mod', order)

            if secret == config.secret:


                handler = BybitTestnet_WalletHandler()
                handler.place_order(order)
                print(order, "Order Placed Successfully")

                new_order = Orders.objects.create(
                    category=category,
                    symbol=symbol,
                    side=side,
                    orderType=orderType,
                    quantity=qty,
                    triggerPrice=triggerPrice,
                    Exchange=Exchange,
                    takeProfit=takeProfit,
                    stopLoss=stopLoss,
                    reduceOnly=reduceOnly,
                    botOrderType=botOrderType
                )
                serializer = OrderSerializer(order)
                print(new_order, "saved to database")
                # json.dumps(new_order, indent=4)
                return JsonResponse({
                    "status": "success",
                    "data": serializer.data

                }, status=status.HTTP_201_CREATED)
                # except Exception as e:
                #     return Response({"error": f"Missing Key: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)
            # balance = get_balance(wallet, currency_type)
        except KeyError as e:
            return Response({"error": f"Missing key: {e}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
def open_grid_order(request):
    if request.method == 'GET':
        orders = Orders.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        try:
            data = request.data
            print(data)
            """
            necessary

            category
            symbol
            side
            orderType
            qty
            price
            triggerPrice
            positionIdx = 0
            reduceOnly = false

            # for bot 
            time,
            Exchange
            takeProfit
            stopLoss
            botOrderType
            """

            secret = data['secret']
            if secret != config.secret:
                return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)

            # Extract data from the request
            time = data['time']
            category = data['category']
            symbol = data['symbol']
            side = data['side']
            orderType = data['orderType']
            qty = data['qty']
            if not qty or qty == "0":
                qty = config.qty
            timeInForce = data['timeInForce']
            price = data['price']
            triggerPrice = data['triggerPrice']
            positionIdx = data['positionIdx']
            reduceOnly = data['reduceOnly']
            Exchange = data['Exchange']
            takeProfit = data['takeProfit']
            stopLoss = data['stopLoss']
            botOrderType = data['botOrderType']
            percentage_difference_favor = data['percentage_difference_favor']
            percentage_difference_against = data['percentage_difference_against']
            favor_levels = data['favor_levels']
            against_levels = data['against_levels']

            print('mod', data)
            """
                    necessary
            category
            symbol
            side
            orderType
            qty
            price
            triggerPrice
            positionIdx = 0
            reduceOnly = false
            """
            # Save the order
            order = Orders.objects.create(
                time=pytz.utc.localize(datetime.utcnow()),
                category=category,
                symbol=symbol,
                side=side,
                orderType=orderType,
                qty=qty,
                timeInForce=timeInForce,
                triggerPrice=float(triggerPrice) if triggerPrice else price,
                positionIdx=positionIdx,

                Exchange=Exchange,
                takeProfit=takeProfit,
                stopLoss=stopLoss,
                reduceOnly=reduceOnly,
                botOrderType=botOrderType,

                percentage_difference_favor=percentage_difference_favor,
                percentage_difference_against=percentage_difference_against,
                favor_levels=favor_levels,
                against_levels=against_levels
            )
            print('mod', order)

            if secret == config.secret:
                try:
                    handler = BybitTestnet_WalletHandler()
                    handler.place_grid_orders(order)
                    print(order, "Order Placed Successfully")

                    new_order = Orders.objects.create(
                        # time=pytz.utc.localize(datetime.utcnow()),
                        category=category,
                        symbol=symbol,
                        side=side,
                        orderType=orderType,
                        quantity=float(qty),
                        triggerPrice=float(triggerPrice) if triggerPrice else None,
                        Exchange=Exchange,
                        takeProfit=takeProfit,
                        stopLoss=stopLoss,
                        reduceOnly=reduceOnly,
                        botOrderType=botOrderType
                    )
                    print(new_order, "Order saved  Successfully")
                    return Response({'message': 'Order Placed Successfully'}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({"error": f"Missing key: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError as e:
            return Response({"error": f"Invalid JSON format in levels: {e}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def unified_order(request):
    if request.method == 'POST':
        data = request.data
        print(data)

        # Fetch and validate the secret
        secret = data.get('secret')
        if secret != config.secret:
            return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Initialize session with Bybit's API
            session = HTTP(
                testnet=True,
                api_key=config.api_key,
                api_secret=config.secret_key,
            )

            # Extract order details from the request data
            category = 'linear'
            symbol = data.get('symbol')
            side = data.get('side')
            order_type = data.get('orderType')
            qty = data.get('qty')
            time_in_force = data.get('timeInForce')
            take_profit = data.get('takeProfit')
            stop_loss = data.get('stopLoss')
            reduce_only = data.get('reduceOnly')
            bot_order_type = data.get('botOrderType')
            favor_levels = data.get('favor_levels')
            against_levels = data.get('against_levels')

            # Check for missing essential fields
            required_fields = ['symbol', 'side', 'orderType', 'qty', 'timeInForce', 'favor_levels',
                               'against_levels']
            for field in required_fields:
                if field not in data:
                    return Response({"error": f"Missing field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

            # Prepare batch orders for favor levels
            orders = []
            for price in favor_levels:
                order = {
                    "symbol": symbol,
                    "side": side,
                    "orderType": order_type,
                    "isLeverage": 0,  # Assuming it's not a leveraged order
                    "qty": qty,
                    "price": price,
                    "timeInForce": time_in_force
                }
                orders.append(order)

            # Place batch orders
            response = session.place_batch_order(category=category, request=orders)
            print(response)

            # Handle the response and provide feedback
            if 'ret_msg' in response and response['ret_msg'] == 'OK':
                return Response({'message': 'Orders placed successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to place orders", "details": response},
                                status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            return Response({"error": f"Missing key: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Couldn't place unified orders: {e}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def grid_ccxt(request):

    if request.method == 'POST':
        exchange_class = getattr(ccxt, "bybit")
        exchange = exchange_class({
            'apiKey': config.api_key,
            'secret': config.secret_key,
        })

        exchange.set_sandbox_mode(True)  # for testnet
        exchange.options['defaultType'] = 'future'
        exchange.load_markets()
class BybitTestnet_WalletHandler(APIView):
    permission_classes = [permissions.AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = config.api_key
        self.secret_key = config.secret_key
        self.secret = config.secret
        self.base_url = 'https://api-testnet.bybit.com'
        self.httpClient = requests.Session()
        self.recv_window = str(7000)
        self.endpoint = "/v5/order/create"

    def HTTP_Request(self, endpoint, method, data, Info):

        time_stamp = str(int((time.time() * 1000) - 2000))
        data_json = json.dumps(data)

        signature = self.genSignature(data_json,time_stamp)
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': str(time_stamp),
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'Content-Type': 'application/json'
        }
        if method == "POST":
            response = self.httpClient.request(method, self.base_url + endpoint, headers=headers, data=data_json)
        else:
            response = self.httpClient.request(method, self.base_url + endpoint + "?" + data_json, headers=headers)
        print(response.text)
        print(response.headers)
        print(Info + " Elapsed Time : " + str(response.elapsed))
        return Response({'Response text': response.text,
                         'Response headers': response.headers,
                         'Response.elapsed': response.elapsed
                         })

    def genSignature(self, data,time_stamp):
        param_str = str(time_stamp) + self.api_key + self.recv_window + data
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    def place_order(self, data):
        # from pybit.unified_trading import HTTP
        # session = HTTP(
        #     testnet=True,
        #     api_key=config.api_key,
        #     api_secret=config.secret_key,
        # )
        # print("-----------------------------------------------",session.place_order(
        #     category="spot",
        #     symbol="BTCUSDT",
        #     side="Buy",
        #     orderType="Limit",
        #     qty="0.1",
        #     price="15600",
        #     timeInForce="PostOnly",
        #     orderLinkId="spot-test-postonly",
        #     isLeverage=0,
        #     orderFilter="Order",
        # ))
        endpoint = "/v5/order/create"
        method = "POST"
        timestamp = datetime.now()
        orderLinkId = uuid.uuid4().hex
        params = {
            'category': data['category'],
            'symbol': data['symbol'],
            'side': data['side'],
            'orderType': data['orderType'],
            'positionIdx': data['positionIdx'],
            'qty': data['qty'],
            'price': data['price'],
            'triggerPrice': data['triggerPrice'],
            'Exchange': data['Exchange'],
            # 'takeProfit': data['takeProfit'],
            # 'stopLoss': data['stopLoss'],
            'orderLinkId': orderLinkId,
            'reduceOnly': data['reduceOnly']
        }
        self.HTTP_Request(endpoint, method, params, "Create")

    def place_grid_orders(self, data):  # entry_price, high_levels, low_levels, side, qty, percentage_diff, symbol, favor_count, against_count):

        grid_order = {
            # 'time': data['time'],
            'category': data['category'],
            'symbol': data['symbol'],
            'side': data['side'],
            'orderType': data['orderType'],
            'qty': data['qty'],
            'price': data['triggerPrice'],
            'positionIdx': data['positionIdx'],
            'timeInForce': data['timeInForce'],
            # 'Exchange': data['Exchange'],
            'takeProfit': data['takeProfit'],
            'stopLoss': data['stopLoss'],
            'reduceOnly': data['reduceOnly'],
            'botOrderType': data['botOrderType']
        }

        # exchange.load_time_difference()
        #
        #
        # 'options': {
        #     'adjustForTimeDifference': True,

        percentage_difference_favor = data['percentage_difference_favor']
        percentage_difference_against = data['percentage_difference_against']
        favor_levels = data['favor_levels']
        against_levels = data['against_levels']
        # category = 'linear'

        orders = []
        if grid_order['side'].lower() == 'buy':
            self.place_order(grid_order)
            for trigger_price in favor_levels:
                grid_order['triggerPrice'] = trigger_price
                grid_order['orderType'] = 'Limit'
                grid_order['side'] = 'Sell'

                self.place_order(grid_order)
                # Orders.objects.Create(grid_order)

            for trigger_price in against_levels:
                grid_order['triggerPrice'] = trigger_price
                grid_order['orderType'] = 'Limit'
                grid_order['side'] = 'Buy'
                self.place_order(grid_order)

        elif grid_order['side'].lower() == 'sell':
            self.place_order(grid_order)
            for trigger_price in favor_levels:
                grid_order['triggerPrice'] = trigger_price
                grid_order['side'] = 'Buy'
                grid_order['orderType'] = 'Limit'
                self.place_order(grid_order)

            for trigger_price in against_levels:
                grid_order['triggerPrice'] = trigger_price
                grid_order['side'] = 'Sell'
                grid_order['orderType'] = 'Limit'
                self.place_order(grid_order)
                # Orders.objects.Create(grid_order)

        # # if side.lower() == 'buy':
        # for i in range(favor_levels):
        #     # price = entry_price * (1 + ((i + 1) * percentage_diff / 100))
        #     triggerPrice = favor_levels[i]
        #     print('triggerPrice', triggerPrice)
        #     grid_orders = grid_order.copy()  # Create a copy of the base template
        #     print('grid_orders', grid_orders)
        #     grid_orders['triggerPrice'] = triggerPrice
        #
        #     self.place_order(grid_orders)
        # for i in range(against_levels):
        #     # price = entry_price * (1 - ((i + 1) * percentage_diff / 100))
        #     triggerPrice = against_levels[i]
        #     print('triggerPrice', triggerPrice)
        #     grid_orders = grid_order.copy()  # Create a copy of the base template
        #     print('grid_orders', grid_orders)
        #     grid_orders['triggerPrice'] = triggerPrice
        #     self.place_order(grid_orders)


        # elif side.lower() == 'sell':
        #     for i in range(high_levels):
        #         price = entry_price * (1 - ((i + 1) * percentage_diff / 100))
        #         orders.append({
        #             'side': 'Buy',
        #             'price': price,
        #             'qty': qty
        #         })
        #         self.place_order(orders)
        #     for i in range(low_levels):
        #         price = entry_price * (1 + ((i + 1) * percentage_diff / 100))
        #         orders.append({
        #             'side': 'Sell',
        #             'price': price,
        #             'qty': qty
        #         })
        #         self.place_order(orders)
        # else:
        #     raise ValueError("Invalid side. Expected 'buy' or 'sell'.")

        # for order in orders:
        #     self.place_order(order)

    def Get_unfilled_Orders(self):
        endpoint = "/v5/order/realtime"
        method = "GET"
        params = 'category=linear&settleCoin=USDT'
        self.HTTP_Request(endpoint, method, params, "UnFilled")

    # def getresponse(self, *args, **kwargs):
    #     response = self._old_getresponse(*args, **kwargs)
    #     if self.sock:
    #         self.peer = self.sock.getpeername()
    #         response._peer = self.sock.getpeername()
    #         response._client = self.sock
    #     else:
    #         response.peer = None
    #     return response


"""
category	true	string	Product type
Unified account: spot, linear, inverse, option
Classic account: spot, linear, inverse
symbol	true	string	Symbol name, like BTCUSDT, uppercase only
isLeverage	false	integer	Whether to borrow. Valid for Unified spot only. 0(default): false then spot trading, 1: true then margin trading
side	true	string	Buy, Sell
orderType	true	string	Market, Limit
qty	true	string	Order quantity
UTA account
Spot: set marketUnit for market order qty unit, quoteCoin for market buy by default, baseCoin for market sell by default
Perps, Futures & Option: always use base coin as unit
Classic account
Spot: the unit of qty is quote coin for market buy order, for others, it is base coin
Perps, Futures: always use base coin as unit
Perps & Futures: if you pass qty="0" and specify reduceOnly=true&closeOnTrigger=true, you can close the position up to maxMktOrderQty or maxOrderQty shown on Get Instruments Info of current symbol
marketUnit	false	string	The unit for qty when create Spot market orders for UTA account. Currently, TP/SL and conditional orders are not supported.
baseCoin: for example, buy BTCUSDT, then "qty" unit is BTC
quoteCoin: for example, sell BTCUSDT, then "qty" unit is USDT
price	false	string	Order price
Market order will ignore this field
Please check the min price and price precision from instrument info endpoint
If you have position, price needs to be better than liquidation price
triggerDirection	false	integer	Conditional order param. Used to identify the expected direction of the conditional order.
1: triggered when market price rises to triggerPrice
2: triggered when market price falls to triggerPrice
Valid for linear & inverse
orderFilter	false	string	If it is not passed, Order by default.
Order
tpslOrder: Spot TP/SL order, the assets are occupied even before the order is triggered
StopOrder: Spot conditional order, the assets will not be occupied until the price of the underlying asset reaches the trigger price, and the required assets will be occupied after the Conditional order is triggered
Valid for spot only
triggerPrice	false	string	
For Perps & Futures, it is the conditional order trigger price. If you expect the price to rise to trigger your conditional order, make sure:
triggerPrice > market price
Else, triggerPrice < market price
For spot, it is the TP/SL and Conditional order trigger price
triggerBy	false	string	Trigger price type, Conditional order param for Perps & Futures. LastPrice, IndexPrice, MarkPrice
Valid for linear & inverse
orderIv	false	string	Implied volatility. option only. Pass the real value, e.g for 10%, 0.1 should be passed. orderIv has a higher priority when price is passed as well
timeInForce	false	string	Time in force
Market order will use IOC directly
If not passed, GTC is used by default
positionIdx	false	integer	Used to identify positions in different position modes. Under hedge-mode, this param is required (USDT perps & Inverse contracts have hedge mode)
0: one-way mode
1: hedge-mode Buy side
2: hedge-mode Sell side
orderLinkId	false	string	User customised order ID. A max of 36 characters. Combinations of numbers, letters (upper and lower cases), dashes, and underscores are supported.
Futures & Perps: orderLinkId rules:
optional param
always unique
option orderLinkId rules:
required param
always unique
takeProfit	false	string	Take profit price
linear & inverse: support UTA and classic account
spot(UTA): Spot Limit order supports take profit, stop loss or limit take profit, limit stop loss when creating an order
stopLoss	false	string	Stop loss price
linear & inverse: support UTA and classic account
spot(UTA): Spot Limit order supports take profit, stop loss or limit take profit, limit stop loss when creating an order
tpTriggerBy	false	string	The price type to trigger take profit. MarkPrice, IndexPrice, default: LastPrice. Valid for linear & inverse
slTriggerBy	false	string	The price type to trigger stop loss. MarkPrice, IndexPrice, default: LastPrice. Valid for linear & inverse
reduceOnly	false	boolean	What is a reduce-only order? true means your position can only reduce in size if this order is triggered.
You must specify it as true when you are about to close/reduce the position
When reduceOnly is true, take profit/stop loss cannot be set
Valid for linear, inverse & option
closeOnTrigger	false	boolean	What is a close on trigger order? For a closing order. It can only reduce your position, not increase it. If the account has insufficient available balance when the closing order is triggered, then other active orders of similar contracts will be cancelled or reduced. It can be used to ensure your stop loss reduces your position regardless of current available margin.
Valid for linear & inverse
smpType	false	string	Smp execution type. What is SMP?
mmp	false	boolean	Market maker protection. option only. true means set the order as a market maker protection order. What is mmp?
tpslMode	false	string	TP/SL mode
Full: entire position for TP/SL. Then, tpOrderType or slOrderType must be Market
Partial: partial position tp/sl (as there is no size option, so it will create tp/sl orders with the qty you actually fill). Limit TP/SL order are supported. Note: When create limit tp/sl, tpslMode is required and it must be Partial
Valid for linear & inverse
tpLimitPrice	false	string	The limit order price when take profit price is triggered
linear & inverse: only works when tpslMode=Partial and tpOrderType=Limit
Spot(UTA): it is required when the order has takeProfit and tpOrderType=Limit
slLimitPrice	false	string	The limit order price when stop loss price is triggered
linear & inverse: only works when tpslMode=Partial and slOrderType=Limit
Spot(UTA): it is required when the order has stopLoss and slOrderType=Limit
tpOrderType	false	string	The order type when take profit is triggered
linear & inverse: Market(default), Limit. For tpslMode=Full, it only supports tpOrderType=Market
Spot(UTA):
Market: when you set "takeProfit",
Limit: when you set "takeProfit" and "tpLimitPrice"
slOrderType	false	string	The order type when stop loss is triggered
linear & inverse: Market(default), Limit. For tpslMode=Full, it only supports slOrderType=Market
Spot(UTA):
Market: when you set "stopLoss",
Limit: when you set "stopLoss" and "slLimitPrice"
"""
