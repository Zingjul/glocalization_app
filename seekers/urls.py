from django.urls import path
from seekers import views

app_name = "seekers"

urlpatterns = [
    # 🌍 Listing and filtering
    path("", views.SeekerPostListView.as_view(), name="seeker_list"),
    path("search/", views.SeekerPostListView.as_view(), name="seeker_search"),  # Accepts ?q=
    path("search/autocomplete/", views.location_autocomplete, name="location_autocomplete"),  # Optional autocomplete

    # 🧭 Personal seeker dashboard
    path("my-pending/", views.PendingSeekersByUserView.as_view(), name="my_pending_seekers"),

    # 🎯 Seeker creation selector
    path("create/", views.SeekerPostCreateView.as_view(), name="seeker_create"),
    path("create/product/", views.ProductCreateView.as_view(), name="create_product_request"),
    path("create/service/", views.ServiceCreateView.as_view(), name="create_service_request"),
    path("create/labor/", views.LaborCreateView.as_view(), name="create_labor_request"),

    # 🛠 Type-based editing
    path("edit/product/<int:pk>/", views.SeekerEditProductView.as_view(), name="seeker_edit_product"),
    path("edit/service/<int:pk>/", views.SeekerEditServiceView.as_view(), name="seeker_edit_service"),
    path("edit/labor/<int:pk>/", views.SeekerEditLaborView.as_view(), name="seeker_edit_labor"),

    # Response
    # path("respond/<int:pk>/", SeekerRespondView.as_view(), name="seeker_respond"),

    # 🔎 Detail, respond, update, delete
    path("<int:pk>/", views.SeekerPostDetailView.as_view(), name="seeker_detail"),
    path("<int:pk>/respond/", views.SeekerRespondView.as_view(), name="respond_to_seeker"),
    path("<int:pk>/edit/", views.SeekerPostUpdateView.as_view(), name="seeker_edit"),
    path("<int:pk>/delete/", views.SeekerPostDeleteView.as_view(), name="seeker_delete"),
]

