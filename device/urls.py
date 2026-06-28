from django.urls import path
from . import views

urlpatterns = [
    path('device/list/', views.device_list, name='device_list'),
    path('device/add/', views.device_add, name='device_add'),
    path('device/<int:device_id>/edit/', views.device_edit, name='device_edit'),
    path('device/<int:device_id>/delete/', views.device_delete, name='device_delete'),
    path('device/<int:device_id>/test/', views.test_connection, name='device_test_connection'),
    path('device/<int:device_id>/sync/', views.trigger_sync, name='device_trigger_sync'),

    # optional ADMS push webhook (machine NIJE post korle)
    path('iclock/cdata', views.device_push_webhook, name='device_push_webhook'),
]
