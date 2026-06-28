from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .api_views import *

router = DefaultRouter()
router.register(r'institute', InstituteViewSet, basename='institute')
urlpatterns = [
    path('student/list_testmonial/', list_testmonial, name='list_testmonial'),
    path('generate_testimonial_report/', generate_testimonial_report, name='generate_testimonial_report'),
    path('testimonial_info_add/<int:pk>/', testimonial_info_add, name='testimonial_info_add'),

    path('institute/', institute ,name='institute' ),
    path('ins/<int:id>', institute_edit, name='institute_edit'),

    path('academic_event/event/', event, name='event'),
    path('eventlist/', eventview, name='eventlist'),
    path('add_event/', add_event, name='add_event'),
    path('edit_event/<int:id>', edit_event, name='edit_event'),
    path('del_event/<int:id>', del_event, name='del_event'),
    path('update_event/', update_event, name='update_event'),
    path('remove_event/', remove_event, name='remove_event'),
    path('academic_event/event_detail/', eventdetail, name='event_detail'),
    path('settings/list_weekend_config/', list_weekend_config, name='list_weekend_config'),

    path('api/', include(router.urls)),
    path('events/', EventListAPIView.as_view(), name='event-list'),


]
