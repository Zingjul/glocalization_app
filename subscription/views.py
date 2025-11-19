from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.conf import settings

from .models import SubscriptionPlan, UserSubscription


class SubscriptionListView(LoginRequiredMixin, View):
    """Display all available subscription plans."""
    template_name = "subscription/plans.html"

    def get(self, request):
        plans = SubscriptionPlan.objects.all().order_by("price")
        return render(request, self.template_name, {"plans": plans})


class SubscribeView(LoginRequiredMixin, View):
    """Handle manual selection of a plan before payment."""
    template_name = "subscription/subscribe.html"

    def get(self, request, plan_id):
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        return render(request, self.template_name, {"plan": plan})

    def post(self, request, plan_id):
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        # Create or update user subscription record
        user_sub, created = UserSubscription.objects.get_or_create(user=request.user)
        user_sub.plan = plan
        user_sub.start_date = timezone.now()
        user_sub.is_active = False  # Wait for manual confirmation
        user_sub.save()

        messages.info(
            request,
            f"You selected the {plan.get_level_display()} plan. "
            "Please make payment and wait for staff confirmation."
        )
        return redirect("subscription:payment_page", plan_id=plan.id)


class PaymentPageView(LoginRequiredMixin, View):
    """Render manual payment instructions for the selected plan."""
    template_name = "subscription/payment_page.html"

    def get(self, request, plan_id):
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        user_sub = UserSubscription.objects.filter(user=request.user).first()
        return render(
            request,
            self.template_name,
            {
                "plan": plan,
                "user_sub": user_sub,
                "instructions": "Transfer payment to our official account and wait for confirmation.",
            },
        )


class ConfirmSubscriptionView(UserPassesTestMixin, View):
    """Accessible by staff to manually confirm a user's payment."""
    
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, user_id):
        user_sub = get_object_or_404(UserSubscription, user__id=user_id)
        user_sub.is_active = True
        user_sub.save(update_fields=["is_active"])

        messages.success(request, f"✅ Subscription for {user_sub.user.username} has been activated.")
        return redirect("subscription:plans")


class ReportPaymentView(LoginRequiredMixin, View):
    def post(self, request, plan_id):
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        subscription, _ = UserSubscription.objects.get_or_create(user=request.user, plan=plan)
        subscription.payment_reported = True
        subscription.save()


        messages.success(request, "✅ Your payment has been reported. Our team will verify and activate your plan soon.")
        return redirect("subscription:plans")