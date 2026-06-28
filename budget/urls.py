from django.urls import path
from . import views

urlpatterns = [
    path('budget/', views.budget_dashboard, name='budget_dashboard'),
    path('budget/create/', views.budget_create, name='budget_create'),
    path('budget/<int:pk>/', views.budget_detail, name='budget_detail'),
    path('budget/<int:pk>/categories/', views.budget_category_list, name='budget_category_list'),
    path('budget/<int:pk>/category/add/', views.budget_category_add, name='budget_category_add'),
    path('budget/category/<int:cat_pk>/edit/', views.budget_category_edit, name='budget_category_edit'),
    path('budget/category/<int:cat_pk>/delete/', views.budget_category_delete, name='budget_category_delete'),
    path('budget/category/<int:cat_pk>/monthly/', views.budget_monthly, name='budget_monthly'),
    path('budget/<int:pk>/activate/', views.budget_activate, name='budget_activate'),
    path('budget/<int:pk>/close/', views.budget_close, name='budget_close'),
    path('budget/<int:pk>/report/', views.budget_report, name='budget_report'),
    path('budget/alerts/', views.budget_alerts, name='budget_alerts'),
    path('budget/alerts/<int:alert_pk>/acknowledge/', views.budget_alert_acknowledge, name='budget_alert_acknowledge'),
]
