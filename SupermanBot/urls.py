"""
URL configuration for SupermanBot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import urls
from Bot.views import get_orders, open_order, open_grid_orders, unified_order, open_ccxt_order, open_calculated_grid_orders, gg
# from Bot.views1 import s
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include('Bot.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('open_order/', open_order, name='open_order'),
    path('get_orders/', get_orders, name='get_orders'),
    path('grid_order/', open_grid_orders, name='open_grid_order'),
    path('calculated-grid-orders/', open_calculated_grid_orders, name='open_calculated_grid_orders'),
    path('unified_orders/', unified_order, name='unified_orders'),
    path('open_ccxt/', open_ccxt_order, name='open_ccxt'),
    path('gg/', gg, name='grid'),

] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
