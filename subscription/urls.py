from django.urls import path
from .views import (
    SubscriptionListView,
    SubscribeView,
    PaymentPageView,
    ConfirmSubscriptionView,
    ReportPaymentView,
)

app_name = "subscription"

urlpatterns = [
    path("", SubscriptionListView.as_view(), name="plans"),
    path("choose/<int:plan_id>/", SubscribeView.as_view(), name="choose"),
    path("payment/<int:plan_id>/", PaymentPageView.as_view(), name="payment_page"),
    path("confirm/<int:user_id>/", ConfirmSubscriptionView.as_view(), name="confirm"),
    path('report/<int:plan_id>/', ReportPaymentView.as_view(), name='report_payment'),
]