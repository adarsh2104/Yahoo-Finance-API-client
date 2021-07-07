from django.urls import path,include

from stocks_summary import views

urlpatterns = [
    path('', views.stocks_info, name='stocks_info'),
]