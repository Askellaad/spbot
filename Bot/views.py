import hashlib
import hmac
import json
import threading
import time
import uuid
import requests
import ccxt
from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from SupermanBot.serializer import OrderSerializer
from .models import Orders
from pybit.unified_trading import HTTP
from Bot import config


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_orders(request, format=None):
    orders = Orders.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST', 'GET'])
def open_order(request):
    if request.method == 'GET':

        return get_orders(request)

    if request.method == 'POST':
        data = request.data
        secret = data.get('secret')

        if secret != config.secret:
            return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = extract_order_data(data)
            handler = BybitTestnet_WalletHandler()
            handler.place_order(order)
            save_order_to_db(order)

            return JsonResponse({
                "status": "success",
                "data": order
            }, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response({"error": f"Missing key: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def extract_order_data(data):
    return {
        "category": data['category'],
        "symbol": data['symbol'],
        "side": data['side'],
        "orderType": data['orderType'],
        "qty": data['qty'],
        "price": data.get('price'),
        "triggerPrice": data.get('triggerPrice'),
        "positionIdx": data.get('positionIdx', 0),
        "takeProfit": data.get('takeProfit'),
        "stopLoss": data.get('stopLoss'),
        "reduceOnly": data.get('reduceOnly', False),
        "botOrderType": 'open order',
        "Exchange": data['Exchange']
    }


def save_order_to_db(order):
    Orders.objects.create(
        category=order['category'],
        symbol=order['symbol'],
        side=order['side'],
        orderType=order['orderType'],
        quantity=order['qty'],
        triggerPrice=order['triggerPrice'],
        Exchange=order['Exchange'],
        takeProfit=order['takeProfit'],
        stopLoss=order['stopLoss'],
        reduceOnly=order['reduceOnly'],
        botOrderType=order['botOrderType']
    )


# @api_view(['POST'])
# def open_grid_orders(request):
#     if request.method == 'POST':
#         data = request.data
#         secret = data.get('secret')
#
#         if secret != config.secret:
#             return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             order = extract_order_data(data)
#             symbol = order['symbol']
#             order_type = order['orderType']
#             side = order['side']
#             qty = float(order['qty'])
#             price = float(order['price'])
#             favor_levels = order.get('favor_levels', [])
#             against_levels = order.get('against_levels', [])
#
#             # Open initial order
#             response = bybit.create_order(symbol, order_type, side, qty, price, {
#                 'stopLoss': order['stopLoss'],
#                 'timeInForce': 'GTC',
#                 'reduceOnly': order['reduceOnly']
#             })
#
#             # Open grid orders
#             for level in favor_levels:
#                 level_price = str(level)
#                 if side == 'Buy':
#                     # Place sell orders at favor levels
#                     bybit.create_order(symbol, 'limit', 'sell', qty, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#                 elif side == 'Sell':
#                     # Place buy orders at favor levels
#                     bybit.create_order(symbol, 'limit', 'buy', qty, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#
#             for level in against_levels:
#                 level_price = str(level)
#                 if side == 'Buy':
#                     # Place buy orders at against levels
#                     bybit.create_order(symbol, 'limit', 'buy', qty, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#                 elif side == 'Sell':
#                     # Place sell orders at against levels
#                     bybit.create_order(symbol, 'limit', 'sell', qty, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#
#             save_order_to_db(order)
#             return Response({'success': 'Grid orders created successfully'}, status=status.HTTP_201_CREATED)
#
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def monitor_grid_orders(symbol, side, qty, entry_price, favor_levels, against_levels, favor_qty_percentage,
#                         against_qty_percentage):
#     # cond = True
#     op = entry_price
#     cond = close_grid_orders(side, symbol)
#     while cond:
#         try:
#             current_price = bybit.fetch_ticker(symbol)['last']
#             print(f"Current price: {current_price}")
#             if side.lower() == 'buy':
#                 for level in favor_levels:
#                     if level >= current_price != op:
#                         # Place sell order at the favor level bcz its buy
#                         print('favor level', level, 'op', op)
#
#                         op = level
#                         quantity = qty * (favor_qty_percentage / 100)
#                         bybit.create_order(symbol, 'limit', 'sell', quantity, favor_levels[level - 1])
#                         print('order placed')
#
#                 for level in against_levels:
#                     if level <= current_price != op:
#                         # Place buy order at the breached level
#                         print('against level', level, 'op', op)
#                         op = level
#                         quantity = qty * (against_qty_percentage / 100)
#                         bybit.create_order(symbol, 'limit', 'buy', quantity, against_levels[level - 1])
#                         print('order placed')
#
#             if side.lower() == 'sell':
#                 for level in favor_levels:
#                     if level <= current_price != op:
#                         print('favor level', level, 'op', op)
#
#                         op = level
#                         quantity = qty * (favor_qty_percentage / 100)
#                         bybit.create_order(symbol, 'limit', 'buy', quantity, favor_levels[level - 1])
#                         print('order placed')
#
#                 for level in against_levels:
#                     if level >= current_price != op:
#                         print('against level', level, 'op', op)
#
#                         op = level
#                         quantity = qty * (against_qty_percentage / 100)
#                         bybit.create_order(symbol, 'limit', 'sell', quantity, against_levels[level - 1])
#                         print('order placed')
#
#             time.sleep(1.5)
#         except Exception as e:
#             print(f"Error: {str(e)}")
#             time.sleep(1)

# this opens order every second / loop iteration
# def monitor_grid_orders(symbol, side, qty, entry_price, favor_levels, against_levels, favor_qty_percentage,
#                         against_qty_percentage):
#     op = entry_price
#     levels = [entry_price] + favor_levels + against_levels
#     cond = close_grid_orders(side, symbol)
#     while cond:
#         try:
#             current_price = bybit.fetch_ticker(symbol)['last']
#             print(f"Current price: {current_price}")
#             if side.lower() == 'buy':
#                 for i, level in enumerate(levels):
#                     if level >= current_price != op:
#                         # Place sell order at the favor level because it's buy
#                         print('level', level, 'op', op)
#
#                         op = level
#                         quantity = qty * (favor_qty_percentage / 100)
#                         if i == 0:
#                             # Open opposite position at entry price
#                             bybit.create_order(symbol, 'limit', 'sell', quantity, entry_price)
#                         elif i == 1:
#                             # Open opposite order on the previous level
#                             bybit.create_order(symbol, 'limit', 'sell', quantity, levels[i - 1])
#                         else:
#                             # Open opposite order on the previous level
#                             bybit.create_order(symbol, 'limit', 'sell', quantity, levels[i - 1])
#                         print('order placed')
#                         break
#
#                 for i, level in enumerate(levels):
#                     if level <= current_price != op:
#                         # Place buy order at the breached level
#                         print('level', level, 'op', op)
#                         op = level
#                         quantity = qty * (against_qty_percentage / 100)
#                         if i == 0:
#                             # Open opposite position at entry price
#                             bybit.create_order(symbol, 'limit', 'buy', quantity, entry_price)
#                         elif i == 1:
#                             # Open opposite order on the previous level
#                             bybit.create_order(symbol, 'limit', 'buy', quantity, levels[i - 1])
#                         else:
#                             # Open opposite order on the previous level
#                             bybit.create_order(symbol, 'limit', 'buy', quantity, levels[i - 1])
#                         print('order placed')
#                         break
#
#             if side.lower() == 'sell':
#                 for i, level in enumerate(levels):
#                     if level <= current_price != op:
#                         # Place buy order at the favor level because it's sell
#                         print('level', level, 'op', op)
#
#                         op = level
#                         quantity = qty * (favor_qty_percentage / 100)
#                         if i == 0:
#                             # Open opposite position at entry price
#                             bybit.create_order(symbol, 'limit', 'buy', quantity, entry_price)
#                         elif i == 1:
#                             # Open opposite order on the previous level
#                             bybit.create_order(symbol, 'limit', 'buy', quantity, levels[i - 1])
#                         else:
#                             # Open opposite order on the previous level
#                             bybit.create_order(symbol, 'limit', 'buy', quantity, levels[i - 1])
#                         print('order placed')
#                         break
#
#                 for i, level in enumerate(levels):
#                     if level >= current_price != op:
#                         # Place sell order at the breached level
#                         print('level', level, 'op', op)
#                         op = level
#                         quantity = qty * (against_qty_percentage / 100)
#                         if i == 0:
#                             # Open opposite position at entry price
#                             bybit.create_order(symbol, 'limit', 'sell', quantity, entry_price)
#                         elif i == 1:
#                             # Open opposite order on the previous level
#                             bybit.create_order(symbol, 'limit', 'sell', quantity, levels[i - 1])
#                         else:
#                             # Open opposite order on the previous level
#                             bybit.create_order(symbol, 'limit', 'sell', quantity, levels[i - 1])
#                         print('order placed')
#                         break
#
#             time.sleep(1.5)
#         except Exception as e:
#             print(f"Error: {str(e)}")
#             time.sleep(1)


# def monitor_grid_orders(symbol, side, qty, entry_price, favor_levels, against_levels, percentage_difference_favor,
#                         percentage_difference_against):
#     while True:
#         try:
#             current_price = get_current_price(symbol)
#
#             for level in favor_levels:
#                 level_price = float(level)
#                 qty_percent = qty * (percentage_difference_favor / 100)
#
#                 if side == 'Buy' and current_price > level_price:
#                     # Place sell order at favor level
#                     bybit.create_order(symbol, 'limit', 'sell', qty_percent, level_price)
#
#                     # Open opposite buy order
#                     bybit.create_order(symbol, 'limit', 'buy', qty_percent, level_price)
#
#             for level in against_levels:
#                 level_price = float(level)
#                 qty_percent = qty * (percentage_difference_against / 100)
#
#                 if side == 'Sell' and current_price < level_price:
#                     # Place buy order at against level
#                     bybit.create_order(symbol, 'limit', 'buy', qty_percent, level_price)
#
#                     # Open opposite sell order
#                     bybit.create_order(symbol, 'limit', 'sell', qty_percent, level_price)
#
#             time.sleep(1)  # Check every 1 second
#
#         except Exception as e:
#             print(f"Error: {str(e)}")
#             time.sleep(1)  # Wait for 1 second before retrying


# @api_view(['POST'])
# def open_grid_orders(request):
#     if request.method == 'POST':
#         data = request.data
#         secret = data.get('secret')
#
#         if secret != config.secret:
#             return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             order = extract_grid_data(data)
#             symbol = order['symbol']
#             order_type = order['orderType']
#             side = order['side']
#             qty = float(order['qty'])
#             entry_price = float(order['price'])
#             favor_levels = [float(level) for level in order.get('favor_levels', [])]
#             against_levels = [float(level) for level in order.get('against_levels', [])]
#             percentage_difference_favor = order['percentage_difference_favor']
#             percentage_difference_against = order['percentage_difference_against']
#
#             if side.lower() == 'close':
#                 bybit.close_all_positions(params={'symbol': symbol})
#                 bybit.cancel_all_orders(symbol)
#             # Open initial order
#             bybit.create_order(symbol, order_type, side, qty, entry_price)
#             # favor_qtypercentage_qty = qty * (percentage_difference_favor / 100)
#             # against_percentage_qty = qty * (percentage_difference_against / 100)
#             # Start monitoring orders in a separate thread
#             monitoring_thread = threading.Thread(target=monitor_grid_orders, args=(
#                 symbol, side, qty, entry_price, favor_levels, against_levels, percentage_difference_favor,
#                 percentage_difference_against))
#             monitoring_thread.start()
#
#             save_order_to_db(order)
#             return Response({'success': 'Grid orders created and monitoring started successfully'},
#                             status=status.HTTP_201_CREATED)
#
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class BuyLowSellHighSystem:
#     def init(self, entry_price):
#         self.entry_price = entry_price
#         self.against_levels = [6, 7, 8, 9, 10]
#         self.favor_levels = [5, 4, 3, 2, 1]
#         self.favor_levels = [5, 4, 3, 2, 1]
#         self.against_levels = [6, 7, 8, 9, 10]
#         self.current_position = entry_price  # 5
#         self.bought_at = set()  # To track prices where a buy action has already been performed
#         self.sold_at = set()  # To track prices where a sell action has already been performed
#
#         # new price = current_price
#
#     def update_position(self, new_price):
#         if new_price > self.current_position:
#             if new_price in self.high_limits and new_price not in self.sold_at:
#                 print(f"Selling at {new_price} and buying at {new_price - 1}")
#                 self.current_position = new_price - 1
#                 self.sold_at.add(new_price)
#                 if new_price - 1 in self.bought_at:
#                     self.bought_at.remove(new_price - 1)
#             elif new_price - 1 in self.low_limits and new_price - 1 not in self.sold_at:
#                 print(f"Selling at {new_price} and buying at {new_price - 1}")
#                 self.current_position = new_price - 1
#                 self.sold_at.add(new_price - 1)
#                 if new_price in self.bought_at:
#                     self.bought_at.remove(new_price)
#         elif new_price < self.current_position:
#             if new_price in self.low_limits and new_price not in self.bought_at:
#                 print(f"Selling at {new_price} and buying at {new_price + 1}")
#                 self.current_position = new_price + 1
#                 self.bought_at.add(new_price)
#                 if new_price + 1 in self.sold_at:
#                     self.sold_at.remove(new_price + 1)
#             elif new_price + 1 in self.high_limits and new_price + 1 not in self.bought_at:
#                 print(f"Selling at {new_price} and buying at {new_price + 1}")
#                 self.current_position = new_price + 1
#                 self.bought_at.add(new_price + 1)
#                 if new_price in self.sold_at:
#                     self.sold_at.remove(new_price)


# couple of order on 1 order (latest)
# def monitor_grid_orders(symbol, side, qty, entry_price, favor_levels, against_levels, favor_qty_percentage,
#                         against_qty_percentage):
#
#     if side.lower() == 'buy':
#         high_level = favor_levels
#         low_level = against_levels
#     elif side.lower() == 'sell':
#         high_level = against_levels
#         low_level = entry_price + favor_levels
#
#     cond = close_grid_orders(side, symbol)
#     favor_quantity = qty * (favor_qty_percentage / 100)
#     against_quantity = qty * (against_qty_percentage / 100)
#     current_position = entry_price
#     last_action = None
#
#     while cond:
#         try:
#
#             current_price = bybit.fetch_ticker(symbol)['last']
#             print(f"Current price: {current_price}")
#             if side.lower() == 'buy':
#                 if current_price >= favor_levels[0] and current_price not in against_levels:
#                     # bybit.create_order(symbol, 'limit', 'sell', favor_quantity, current_price)
#                     if entry_price not in against_levels and entry_price not in favor_levels:
#                         against_levels.insert(0,entry_price)
#                     bybit.create_order(symbol, 'limit', 'buy', favor_quantity, against_levels[0])
#                     print('buy @', against_levels[1])
#
#                     # against_levels.insert(0,favor_levels[0])
#                     # favor_levels.remove(against_levels[0])
#                     # favor_levels.pop(0)
#                     against_levels.insert(0, favor_levels.pop(0))
#                     print('favor levels',favor_levels)
#                     print('\nagainst levels', against_levels)
#                     print(f'added {favor_levels[0]} in against_levels\lowlevel and removed from favor_levels/highlevel\n')
#
#                 if current_price <= against_levels[0] and current_price not in favor_levels:
#                     if entry_price not in favor_levels and entry_price not in against_levels:
#                         favor_levels.insert(0,entry_price)
#                     bybit.create_order(symbol, 'limit', 'sell', against_quantity, favor_levels[0])
#                     print('sell @', favor_levels[1])
#                     # favor_levels.insert(0,against_levels[0])
#                     # against_levels.remove(favor_levels[0])
#                     # against_levels.pop(0)
#                     favor_levels.insert(0, against_levels.pop(0))
#                     print('favor levels', favor_levels)
#                     print('\nagainst levels', against_levels)
#                     print(f'added {favor_levels[0]} in favor_levels/highlevel and removed from against_levels/lowlevel\n')
#             if side.lower() == 'sell':
#                 if current_price <= favor_levels[0] and current_price not in against_levels:
#                     # bybit.create_order(symbol, 'limit', 'sell', favor_quantity, current_price)
#                     if entry_price not in favor_levels and entry_price not in against_levels:
#                         against_levels.insert(0,entry_price)
#
#                     bybit.create_order(symbol, 'limit', 'sell', favor_quantity, against_levels[0])
#                     print('sell @', against_levels[1])
#                     # favor_levels.insert(0,against_levels[0])
#                     # against_levels.remove(favor_levels[0])
#                     # against_levels.pop(0)
#                     favor_levels.insert(0, against_levels.pop(0))
#
#                     print('favor levels', favor_levels)
#                     print('\nagainst levels', against_levels)
#                     print(f'added {favor_levels[0]} in against_levels/lowlevel and removed from favor_levels/highlevel\n')
#
#
#                 if current_price >= against_levels[0] and current_price not in favor_levels:
#                     if entry_price not in favor_levels and entry_price not in against_levels:
#                         favor_levels.insert(0,entry_price)
#
#                     bybit.create_order(symbol, 'limit', 'buy', against_quantity, favor_levels[0])
#                     print('buy @', favor_levels[1])
#                     # against_levels.insert(0,favor_levels[0])
#                     # favor_levels.remove(against_levels[0])
#                     # favor_levels.pop(0)
#                     against_levels.insert(0, favor_levels.pop(0))
#                     print('favor levels', favor_levels)
#                     print('\nagainst levels', against_levels)
#                     print(f'added {favor_levels[0]} in favor_levels/highlevel and removed from against_levels/lowlevel\n')
#
#             time.sleep(1.2)
#         except Exception as e:
#             print(f"Error: {str(e)}")
#             time.sleep(1)
#


def monitor_grid_orders(symbol, side, qty, entry_price, favor_levels, against_levels, favor_qty_percentage,
                        against_qty_percentage):
    if side.lower() == 'buy':
        high_level = favor_levels
        low_level = against_levels
    elif side.lower() == 'sell':
        high_level = against_levels
        low_level = favor_levels

    cond = close_grid_orders(side, symbol)
    favor_quantity = qty * (favor_qty_percentage / 100)
    against_quantity = qty * (against_qty_percentage / 100)

    last_favor_level = None
    last_against_level = None
    # 1.866452 1.8665
    while cond:
        try:
            current_price = bybit.fetch_ticker(symbol)['last']
            print(f"Current price: {current_price}")

            if side.lower() == 'buy':
                print("currentPrice: $", current_price)
                print("favor_levels: ", favor_levels)
                print("against_levels: ", against_levels)
                print("last_favor_level: ", last_favor_level)

                if favor_levels and current_price >= favor_levels[0] and current_price not in against_levels:
                    if last_favor_level is not None and current_price >= last_favor_level:
                        if entry_price not in against_levels and entry_price not in favor_levels:
                            against_levels.insert(0, entry_price)
                            bybit.create_order(symbol, 'limit', 'buy', favor_quantity, against_levels[0])
                            print('Buy @', against_levels[0])
                            last_favor_level = favor_levels.pop(0)
                            entry_price = last_favor_level
                    else:
                        if entry_price not in against_levels and entry_price not in favor_levels:
                            against_levels.insert(0, entry_price)
                            bybit.create_order(symbol, 'limit', 'buy', favor_quantity, against_levels[0])
                            print('Buy @', against_levels[0])
                            last_favor_level = favor_levels.pop(0)
                            entry_price = last_favor_level

                elif against_levels and current_price <= against_levels[0] and current_price not in favor_levels:
                    if last_against_level is not None and current_price <= last_against_level:
                        if entry_price not in favor_levels and entry_price not in against_levels:
                            favor_levels.insert(0, entry_price)
                            bybit.create_order(symbol, 'limit', 'sell', against_quantity, favor_levels[0])
                            print('Sell @', favor_levels[0])
                            last_against_level = against_levels.pop(0)
                            entry_price = last_against_level
                    else:
                        if entry_price not in favor_levels and entry_price not in against_levels:
                            favor_levels.insert(0, entry_price)
                            bybit.create_order(symbol, 'limit', 'sell', against_quantity, favor_levels[0])
                            print('Sell @', favor_levels[0])
                            last_against_level = against_levels.pop(0)
                            entry_price = last_against_level

            elif side.lower() == 'sell':
                print("currentPrice: $", current_price)
                print("favor_levels: ", favor_levels)
                print("against_levels: ", against_levels)
                print("last_against_level: ", last_against_level)

                if favor_levels and current_price <= favor_levels[0] and current_price not in against_levels:
                    if last_against_level is not None and current_price <= last_against_level:
                        if entry_price not in against_levels and entry_price not in favor_levels:
                            against_levels.insert(0, entry_price)
                            bybit.create_order(symbol, 'limit', 'sell', favor_quantity, against_levels[0])
                            print('Sell @', against_levels[0])
                            last_against_level = favor_levels.pop(0)
                            entry_price = last_against_level
                    else:
                        if entry_price not in against_levels and entry_price not in favor_levels:
                            against_levels.insert(0, entry_price)
                            bybit.create_order(symbol, 'limit', 'sell', favor_quantity, against_levels[0])
                            print('Sell @', against_levels[0])
                            last_against_level = favor_levels.pop(0)
                            entry_price = last_against_level

                elif against_levels and current_price >= against_levels[0] and current_price not in favor_levels:
                    if last_favor_level is not None and current_price >= last_favor_level:
                        if entry_price not in favor_levels and entry_price not in against_levels:
                            favor_levels.insert(0, entry_price)
                            bybit.create_order(symbol, 'limit', 'buy', against_quantity, favor_levels[0])
                            print('Buy @', favor_levels[0])
                            last_favor_level = against_levels.pop(0)
                            entry_price = last_favor_level
                    else:
                        if entry_price not in favor_levels and entry_price not in against_levels:
                            favor_levels.insert(0, entry_price)
                            bybit.create_order(symbol, 'limit', 'buy', against_quantity, favor_levels[0])
                            print('Buy @', favor_levels[0])
                            last_favor_level = against_levels.pop(0)
                            entry_price = last_favor_level

            time.sleep(1.1)
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(1)


# @permissions[IsAuthenticated]
@api_view(['POST'])
def open_grid_orders(request):
    if request.method == 'POST':
        data = request.data
        secret = data.get('secret')

        if secret != config.secret:
            return Response({'Dear User': 'Fuck OFF'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = extract_grid_data(data)
            symbol = order['symbol']
            order_type = order['orderType']
            side = order['side']
            qty = float(order['qty'])
            price = float(order['price'])
            favor_levels = [float(level) for level in order.get('favor_levels', [])]
            against_levels = [float(level) for level in order.get('against_levels', [])]
            percentage_difference_favor = order['percentage_difference_favor']
            percentage_difference_against = order['percentage_difference_against']
            # Open initial order
            bybit.create_order(symbol, order_type, side, qty, price)

            # Open grid orders
            for level in favor_levels:
                level_price = float(level)
                qty_percent = qty * (percentage_difference_favor / 100)

                # Place sell orders at favor levels
                bybit.create_order(symbol, 'limit', 'sell', qty_percent, level_price)

            for level in against_levels:
                level_price = float(level)
                qty_percent = qty * (percentage_difference_against / 100)

                # Place buy orders at against levels
                bybit.create_order(symbol, 'limit', 'buy', qty_percent, level_price)

            # Start monitoring orders in a separate thread
            monitoring_thread = threading.Thread(target=monitor_grid_orders, args=(
                symbol, side, qty, price, favor_levels, against_levels, percentage_difference_favor,
                percentage_difference_against))
            monitoring_thread.start()

            save_order_to_db(order)
            return Response({'success': 'Grid orders created and monitoring started successfully'},
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def open_calculated_grid_orders(request):
    if request.method == 'POST':
        data = request.data
        secret = data.get('secret')

        if secret != config.secret:
            return Response({'Dear User': 'Fuck off'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = extract_calculated_grid_data(data)
            symbol = order['symbol']
            order_type = order['orderType']
            side = order['side']
            qty = float(order['qty'])
            price = float(order['price'])
            favor_levels_no = data['favor_levels_no']  # [float(level) for level in order.get('favor_levels', [])]
            against_levels_no = data['against_levels_no']  # [float(level) for level in order.get('against_levels', [])]
            percentage_difference_favor = order['percentage_difference_favor']
            percentage_difference_against = order['percentage_difference_against']

            # Open initial order
            bybit.create_order(symbol, order_type, side, qty, price)
            favor_levels, against_levels = calculate_grids(side, percentage_difference_favor,
                                                           percentage_difference_against, favor_levels_no,
                                                           against_levels_no, price)

            # Open grid orders
            for level in favor_levels:
                level_price = float(level)
                qty_percent = qty * (percentage_difference_favor / 100)

                # Place sell orders at favor levels
                bybit.create_order(symbol, 'limit', 'sell', qty_percent, level_price)

            for level in against_levels:
                level_price = float(level)
                qty_percent = qty * (percentage_difference_against / 100)

                # Place buy orders at against levels
                bybit.create_order(symbol, 'limit', 'buy', qty_percent, level_price)

            # Start monitoring orders in a separate thread
            monitoring_thread = threading.Thread(target=monitor_grid_orders, args=(
                symbol, side, qty, price, favor_levels, against_levels, percentage_difference_favor,
                percentage_difference_against))
            monitoring_thread.start()

            save_order_to_db(order)
            return Response({'success': 'Grid orders created and monitoring started successfully'},
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def close_grid_orders(side, symbol):
    if side == 'close':

        bybit.cancel_all_orders(symbol)
        bybit.close_all_positions(params={'symbol': symbol})
        print('All positions closed')
        return False

    else:
        print('No close Order!!')
        return True


# @api_view(['POST'])
# def open_grid_orders(request):
#     if request.method == 'POST':
#         data = request.data
#         secret = data.get('secret')
#
#         if secret != config.secret:
#             return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             order = extract_grid_data(data)
#             symbol = order['symbol']
#             order_type = order['orderType']
#             side = order['side']
#             qty = float(order['qty'])
#             price = float(order['price'])
#             favor_levels = order.get('favor_levels', [])
#             against_levels = order.get('against_levels', [])
#             percentage_difference_favor = order['percentage_difference_favor']
#             percentage_difference_against = order['percentage_difference_against']
#             # Open initial order
#             response = bybit.create_order(symbol, order_type, side, qty, price, {
#                 'stopLoss': order['stopLoss'],
#                 'timeInForce': 'GTC',
#                 'reduceOnly': order['reduceOnly']
#             })
#
#             # Open grid orders
#             for level in favor_levels:
#                 level_price = str(level)
#                 if side == 'Buy':
#                     # # collect all previous opposite placed order
#                     # opposite_orders = Orders.objects.filter(symbol=symbol, side='Sell', price__gt=price)
#                     # # run loop and close all previous opposite order
#                     # for opposite_order in opposite_orders:
#                     #     bybit.cancel_order(symbol, opposite_order.id)
#                     #     opposite_order.delete()
#                     qtyPercent = int(qty) * (percentage_difference_favor / 100)
#                     # qtyPercent = str(qtyPercent)
#
#                     # Place sell orders at favor levels
#                     bybit.create_order(symbol, 'limit', 'sell', qtyPercent, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#                 elif side == 'Sell':
#                     # # collect all previous opposite placed order
#                     # opposite_orders = Orders.objects.filter(symbol=symbol, side='Buy', price__lt=price)
#                     # # run loop and close all previous opposite order
#                     # for opposite_order in opposite_orders:
#                     #     bybit.cancel_order(symbol, opposite_order.id)
#                     #     opposite_order.delete()
#                     qtyPercent = int(qty) * (percentage_difference_favor / 100)
#                     # qtyPercent = str(qtyPercent)
#                     # Place buy orders at favor levels
#                     bybit.create_order(symbol, 'limit', 'buy', qtyPercent, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#
#             for level in against_levels:
#                 level_price = str(level)
#                 if side == 'Buy':
#                     # # collect all previous opposite placed order
#                     # opposite_orders = Orders.objects.filter(symbol=symbol, side='Sell', price__gt=price)
#                     # # run loop and close all previous opposite order
#                     # for opposite_order in opposite_orders:
#                     #     bybit.cancel_order(symbol, opposite_order.id)
#                     #     opposite_order.delete()
#
#                     qtyPercent = int(qty) * (percentage_difference_against / 100)
#                     # qtyPercent = str(qtyPercent)
#                     # Place buy orders at against levels
#                     bybit.create_order(symbol, 'limit', 'buy', qtyPercent, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#                 elif side == 'Sell':
#                     # # collect all previous opposite placed order
#                     # opposite_orders = Orders.objects.filter(symbol=symbol, side='Buy', price__lt=price)
#                     # # run loop and close all previous opposite order
#                     # for opposite_order in opposite_orders:
#                     #     bybit.cancel_order(symbol, opposite_order.id)
#                     #     opposite_order.delete()
#                     qtyPercent = int(qty) * (percentage_difference_against / 100)
#                     # qtyPercent = str(qtyPercent)
#
#                     # Place sell orders at against levels
#                     bybit.create_order(symbol, 'limit', 'sell', qtyPercent, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#
#             save_order_to_db(order)
#             return Response({'success': 'Grid orders created successfully'}, status=status.HTTP_201_CREATED)
#
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# def get_trades(request):
#
#     if request.method == 'POST':
#         data = request.data
#         category = data['category']
#         symbol = data['symbol']
#         trades = bybit.fetch_trades(symbol)
#         return Response({'trades': trades}, status=status.HTTP_200_OK)


@api_view(['POST'])
def unified_order(request):
    if request.method == 'POST':
        data = request.data
        secret = data.get('secret')

        if secret != config.secret:
            return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = HTTP(testnet=True, api_key=config.api_key, api_secret=config.secret_key)
            orders = prepare_batch_orders(data)
            return Response({'orders': orders}, status=status)
        except Exception as e:
            return Response({"error": str(e)}, status=status)


# Initialize Bybit API client
bybit = ccxt.bybit({
    'apiKey': config.api_key,
    'secret': config.secret_key,
    'enableRateLimit': True,  # Rate limit can be enabled if required
    'options': {
        'defaultType': 'linear',  # Or 'linear' based on your account type
    }
})
bybit.set_sandbox_mode(True)


@api_view(['POST'])
def open_ccxt_order(request):
    if request.method == 'POST':
        data = request.data
        secret = data.get('secret')

        if secret != config.secret:
            return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        order = extract_order_data(data)
        response = bybit.create_order(order['symbol'], order['orderType'], order['side'], order['qty'],
                                      order['triggerPrice'], {
                                          'stopLoss': order['stopLoss'],
                                          'timeInForce': 'GTC',  # Adjust as per your requirements
                                          'reduceOnly': order['reduceOnly']
                                      })

        save_order_to_db(order)  # Save order to database

        # return JsonResponse(response, status=status.HTTP_201_CREATED)
        # except ccxt.BaseError as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # except KeyError as e:
        #     return Response({"error": f"Missing key: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def prepare_batch_orders(data):
    orders = []
    for order_data in data.get('orders', []):
        order = extract_order_data(order_data)
        orders.append(order)
    return orders


def extract_grid_data(data):
    return {
        'time': data['time'],
        'category': data['category'],
        'symbol': data['symbol'],
        'side': data['side'],
        'orderType': data['orderType'],
        'qty': data['qty'],
        'price': data['price'],
        'triggerPrice': data['triggerPrice'],
        'positionIdx': data['positionIdx'],
        'timeInForce': data['timeInForce'],
        'Exchange': data['Exchange'],
        'takeProfit': data['takeProfit'],
        'stopLoss': data['stopLoss'],
        'reduceOnly': data['reduceOnly'],
        'botOrderType': data['botOrderType'],
        'percentage_difference_favor': data['percentage_difference_favor'],
        'percentage_difference_against': data['percentage_difference_against'],
        'favor_levels': data['favor_levels'],
        'against_levels': data['against_levels']
    }


def extract_calculated_grid_data(data):
    return {
        # 'category': data['category'],
        # 'symbol': data['symbol'],
        'side': data['side'],
        # 'orderType': data['orderType'],
        # 'qty': data['qty'],
        'price': data['price'],
        'triggerPrice': data['triggerPrice'],
        # 'positionIdx': data['positionIdx'],
        # 'timeInForce': data['timeInForce'],
        # 'Exchange': data['Exchange'],
        'takeProfit': data['takeProfit'],
        'stopLoss': data['stopLoss'],
        # 'reduceOnly': data['reduceOnly'],
        # 'botOrderType': data['botOrderType'],
        # 'percentage_difference_favor': data['percentage_difference_favor'],
        # 'percentage_difference_against': data['percentage_difference_against'],
        # 'favor_levels_no': data['favor_levels_no'],
        # 'against_levels_no': data['against_levels_no']
    }


def save_grid_order_to_db(order):
    Orders.objects.create(
        category=order['category'],
        symbol=order['symbol'],
        side=order['side'],
        orderType=order['orderType'],
        qty=order['qty'],
        timeInForce=order['timeInForce'],
        triggerPrice=order['triggerPrice'],
        positionIdx=order['positionIdx'],
        Exchange=order['Exchange'],
        takeProfit=order['takeProfit'],
        stopLoss=order['stopLoss'],
        reduceOnly=order['reduceOnly'],
        botOrderType=order['botOrderType'],
        percentage_difference_favor=order['percentage_difference_favor'],
        percentage_difference_against=order['percentage_difference_against'],
        favor_levels=order['favor_levels'],
        against_levels=order['against_levels']
    )


@api_view(['GET', 'POST'])
def gg(request):
    if request.method == 'GET':
        result = bybit.fetch_open_orders('OPUSDT')
        return Response({'Grid orders': result})
    if request.method == 'POST':
        return Response({'message': 'grid stopped'}, status=status.HTTP_200_OK)


def calculate_grids(side, favor_diff, against_diff, favor_levels_no, against_levels_no, price):
    favor_levels = []
    against_levels = []
    if side.lower() == 'buy':
        for levels in range(favor_levels_no):
            # entryPrice * (1 + (i + 1) * perdiffav / 100))
            favor_levels.append(price * (1 + (levels + 1) * favor_diff / 100))
        for levels in range(against_levels_no):
            against_levels.append(price * (1 - (levels + 1) * against_diff / 100))

    if side.lower() == 'sell':
        for levels in range(favor_levels_no):
            # entryPrice * (1 + (i + 1) * perdiffav / 100))
            favor_levels.append(price * (1 - (levels + 1) * favor_diff / 100))
        for levels in range(against_levels_no):
            against_levels.append(price * (1 + (levels + 1) * against_diff / 100))

    print('\nfav levels: ', favor_levels)
    print('\nagainst levels: ', against_levels)
    return favor_levels, against_levels


class BybitTestnet_WalletHandler(APIView):
    permission_classes = [permissions.AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = config.api_key
        self.secret_key = config.secret_key
        self.secret = config.secret
        self.base_url = 'https://api-testnet.bybit.com'
        self.httpClient = requests.Session()
        self.recv_window = str(8000)
        self.endpoint = "/v5/order/create"

    def HTTP_Request(self, endpoint, method, data, Info):
        time_stamp = str(time.time() * 1000)
        print('time', time_stamp)
        print('time2', str(time.time() * 1000))
        data_json = json.dumps(data)
        signature = self.genSignature(data_json, time_stamp)
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': str(time_stamp),
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'Content-Type': 'application/json'
        }
        response = self.httpClient.request(method, self.base_url + endpoint, headers=headers, data=data_json)
        return Response({
            'Response text': response.text,
            'Response headers': response.headers,
            'Response.elapsed': response.elapsed
        })

    def genSignature(self, data, time_stamp):
        param_str = str(time_stamp) + self.api_key + self.recv_window + data
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    def place_order(self, data):
        endpoint = "/v5/order/create"
        method = "POST"
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
            'orderLinkId': orderLinkId,
            'reduceOnly': data['reduceOnly']
        }
        self.HTTP_Request(endpoint, method, params, "Create")

    def place_grid_orders(self, data):
        if data['side'].lower() == 'buy':
            self.place_order(data)
            self.create_grid_orders(data, data['favor_levels'], 'Sell')
            self.create_grid_orders(data, data['against_levels'], 'Buy')
        elif data['side'].lower() == 'sell':
            self.place_order(data)
            self.create_grid_orders(data, data['favor_levels'], 'Buy')
            self.create_grid_orders(data, data['against_levels'], 'Sell')

    def create_grid_orders(self, data, levels, side):
        for price in levels:
            order_data = data.copy()
            order_data['triggerPrice'] = price
            order_data['side'] = side
            self.place_order(order_data)
#
# @api_view(['POST'])
# def open_grid_orders(request):
#     if request.method == 'POST':
#         data = request.data
#         secret = data.get('secret')
#
#         if secret != config.secret:
#             return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             order = extract_order_data(data)
#             symbol = order['symbol']
#             order_type = order['orderType']
#             side = order['side']
#             qty = float(order['qty'])
#             price = float(order['price'])
#             favor_levels = order.get('favor_levels', [])
#             against_levels = order.get('against_levels', [])
#
#             # Open initial order
#             response = bybit.create_order(symbol, order_type, side, qty, price, {
#                 'stopLoss': order['stopLoss'],
#                 'timeInForce': 'GTC',
#                 'reduceOnly': order['reduceOnly']
#             })
#
#             # Open grid orders
#             for level in favor_levels:
#                 level_price = str(level)
#                 if side == 'Buy':
#                     # Place sell orders at favor levels
#                     bybit.create_order(symbol, 'limit', 'sell', qty, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#                 elif side == 'Sell':
#                     # Place buy orders at favor levels
#                     bybit.create_order(symbol, 'limit', 'buy', qty, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#
#             for level in against_levels:
#                 level_price = str(level)
#                 if side == 'Buy':
#                     # Place buy orders at against levels
#                     bybit.create_order(symbol, 'limit', 'buy', qty, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#                 elif side == 'Sell':
#                     # Place sell orders at against levels
#                     bybit.create_order(symbol, 'limit', 'sell', qty, level_price, {
#                         'timeInForce': 'GTC'
#                     })
#
#             save_order_to_db(order)
#             return Response({'success': 'Grid orders created successfully'}, status=status.HTTP_201_CREATED)
#
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
