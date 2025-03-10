from django.urls import path
from .views import PersonList, PersonDetail, toggle_business_name

urlpatterns = [
    path('', PersonList.as_view(), name='person-list'),
    path('<int:pk>/', PersonDetail.as_view(), name='person-detail'),
    path('toggle_business_name/', toggle_business_name, name='toggle-business-name'),
]