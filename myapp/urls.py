from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sales/',views.sales, name='sales'),
    path('charts/',views.charts, name='charts'),
    path('report/',views.report, name='report'),
    path('About', views.About, name='About'),
    path('search/', views.search, name='search'),
]
