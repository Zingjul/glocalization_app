from django.urls import path, include
from .views import (
    SeekerPostListView,
    SeekerPendingPostsByUserView,
    SeekerPostCreateView,
    SeekerProductPostCreateView,
    SeekerServicePostCreateView,
    SeekerLaborPostCreateView,
    SeekerPostEditProductView,
    SeekerPostEditServiceView,
    SeekerPostEditLaborView,
    SeekerPostDetailView,
    SeekerPostDeleteView,
)

app_name = "seekers"

urlpatterns = [
    # 🌍 Listing and filtering
    path("", SeekerPostListView.as_view(), name="seeker_list"),
    path("search/autocomplete/", 
         SeekerPostListView.as_view(), 
         name="location_autocomplete"),  # optional autocomplete

    # 🧭 Personal seeker dashboard
    path("my-pending/", 
         SeekerPendingPostsByUserView.as_view(), 
         name="my_pending_seekers"),

    # 🎯 Seeker creation selector
    path("create/", SeekerPostCreateView.as_view(), name="seeker_create"),
    path("create/product/", SeekerProductPostCreateView.as_view(), name="create_product_request"),
    path("create/service/", SeekerServicePostCreateView.as_view(), name="create_service_request"),
    path("create/labor/", SeekerLaborPostCreateView.as_view(), name="create_labor_request"),

    # 🛠 Type-based editing
    path("edit/product/<int:pk>/", SeekerPostEditProductView.as_view(), name="seeker_edit_product"),
    path("edit/service/<int:pk>/", SeekerPostEditServiceView.as_view(), name="seeker_edit_service"),
    path("edit/labor/<int:pk>/", SeekerPostEditLaborView.as_view(), name="seeker_edit_labor"),

    # 🔎 Detail, delete
    path("<int:pk>/", SeekerPostDetailView.as_view(), name="seeker_detail"),
    path("<int:pk>/delete/", SeekerPostDeleteView.as_view(), name="seeker_delete"),

    # 💬 Comments (reuse comment app’s URLs)
    path("comments/", include("comment.urls")),
]
