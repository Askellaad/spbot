from django.db import models


# Create your models here.

class Orders(models.Model):
    # necessary
    time = models.DateTimeField(null=True, blank=True,auto_now_add=True)
    category = models.CharField(max_length=15, null=True, blank=True)
    symbol = models.CharField(max_length=50, null=True, blank=True)
    side = models.CharField(max_length=10, null=True, blank=True)
    orderType = models.CharField(max_length=20, null=True, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)

    # Optional but better
    triggerPrice = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    Exchange = models.CharField(max_length=50, null=True, blank=True)
    takeProfit = models.CharField(max_length=50, null=True, blank=True)
    stopLoss = models.CharField(max_length=50, null=True, blank=True)
    reduceOnly = models.CharField(max_length=50, null=True, blank=True)
    botOrderType = models.CharField(max_length=50, null=True, blank=True)
    # price = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    # market_position = models.CharField(max_length=50, null=True, blank=True)
    # position_size = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    # prev_market_position = models.CharField(max_length=10, null=True, blank=True)
    # amount = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    # currency_type = models.CharField(max_length=5, null=True, blank=True)

