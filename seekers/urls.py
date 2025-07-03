from django.urls import path
from seekers import views

app_name = "seekers"

urlpatterns = [
    path("", views.seeker_list, name="seeker_list"),
    path("create/", views.seeker_create, name="seeker_create"),
    path("<int:pk>/", views.seeker_detail, name="seeker_detail"),
    path("<int:pk>/respond/", views.respond_to_seeker, name="respond_to_seeker"),
    path("create/product/", views.create_product_request, name="create_product_request"),
    path("create/service/", views.create_service_request, name="create_service_request"),
    path("create/labor/", views.create_labor_request, name="create_labor_request"),
    path("<int:pk>/edit/", views.edit_seeker_post, name="seeker_edit"),
]
