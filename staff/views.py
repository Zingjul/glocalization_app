# staff/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.db import transaction
from django.db.models import Q

from posts.models import Post, PendingLocationRequest as PostPendingLocationRequest
from person.models import Person, PendingLocationRequest as PersonPendingLocationRequest
from seekers.models import SeekerPost, PendingSeekerLocationRequest
from comment.models import Comment
from accounts.models import CustomUser
from custom_search.models import Town
from .models import StaffBoardPost, AuditLog
from django.contrib.auth import get_user_model
from staff.utils import log_action
from subscription.models import UserSubscription, SubscriptionPlan
from django.utils import timezone
from notifications.hooks.person_notifications import notify_profile_approval, notify_profile_rejection

User = get_user_model()

def staff_check(user):
    """Allow only staff and superusers."""
    return user.is_staff or user.is_superuser

def staff_required(user):
    return user.is_authenticated and user.is_staff

def staff_login_view(request):
    if request.user.is_authenticated and staff_check(request.user):
        return redirect("staff:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Allow login by either username or email
        if "@" in username:
            try:
                from django.contrib.auth import get_user_model
                user_model = get_user_model()
                username = user_model.objects.get(email=username).username
            except user_model.DoesNotExist:
                username = None

        user = authenticate(request, username=username, password=password)

        if user is not None and staff_check(user):
            login(request, user)
            return redirect("staff:dashboard")
        else:
            messages.error(request, "Invalid credentials or access denied.")

    return render(request, "staff/login.html")


@login_required
@user_passes_test(staff_check)
def staff_logout_view(request):
    logout(request)
    return redirect("staff:login")


@login_required
@user_passes_test(staff_check)
def dashboard_view(request):
    """Staff dashboard showing key moderation stats."""
    pending_posts = Post.objects.filter(status="pending").count()
    pending_seekers = SeekerPost.objects.filter(status="pending").count()
    pending_profiles = Person.objects.filter(approval_status="pending").count()
    pending_locations = PostPendingLocationRequest.objects.filter(is_reviewed=False).count()
    pending_seeker_locations = PendingSeekerLocationRequest.objects.filter(is_reviewed=False).count()
    pending_person_locations = PersonPendingLocationRequest.objects.filter(is_reviewed=False).count()                 #person app
    sum_of_pending_locations = pending_locations + pending_seeker_locations + pending_person_locations
    spam_comments = Comment.objects.filter(is_spam=True).count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    pending_subscriptions = UserSubscription.objects.filter(payment_reported=True, is_active=False).count()

    context = {
        "pending_posts": pending_posts,
        "pending_seekers": pending_seekers,
        "pending_locations": sum_of_pending_locations,
        "pending_seeker_locations": pending_seeker_locations,
        "spam_comments": spam_comments,
        "active_users": active_users,
        "pending_subscriptions": pending_subscriptions,
        "pending_profiles": pending_profiles,
    }

    return render(request, "staff/dashboard.html", context)

# 🟢 Pending Posts List
@user_passes_test(staff_required)
def pending_posts_view(request):
    pending_posts = Post.objects.filter(status='pending').select_related('author')
    return render(request, "staff/posts_pending.html", {"pending_posts": pending_posts})

# 🟢 Detail Page for One Post
@user_passes_test(staff_required)
def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "staff/post_detail.html", {"post": post})

# 🟢 Approve Post
@user_passes_test(staff_required)
def approve_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = 'approved'
    post.save()
    # log staff action
    log_action(request, "Approved Post", post, f"Approved post '{post.product_name}' by {post.author.username}")
    
    messages.success(request, f"✅ Post '{post.product_name}' has been approved.")
    return redirect("staff:pending_posts")

# 🟢 Reject Post
@user_passes_test(staff_required)
def reject_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()

    log_action(request, "Rejected Post", post, f"Deleted post '{post.title}' by {post.author.username}")

    messages.warning(request, f"❌ Post '{post.title}' has been deleted.")
    return redirect("staff:pending_posts")

# 🟢 Pending SeekerPosts List
@user_passes_test(staff_required)
def pending_seeker_posts_view(request):
    pending_seeker_posts = SeekerPost.objects.filter(status='pending').select_related('author')
    return render(request, "staff/seekers_pending.html", {"pending_seeker_posts": pending_seeker_posts})

# 🟢 Detail Page for One SeekerPost
@user_passes_test(staff_required)
def seeker_post_detail_view(request, pk):
    seeker_post = get_object_or_404(SeekerPost, pk=pk)
    return render(request, "staff/seeker_post_detail.html", {"seeker_post": seeker_post})

# 🟢 Approve SeekerPost
@user_passes_test(staff_required)
def approve_seeker_post(request, pk):
    seeker_post = get_object_or_404(SeekerPost, pk=pk)
    seeker_post.status = 'approved'
    seeker_post.save()

    # ✅ Log staff action
    log_action(request, "Approved SeekerPost", seeker_post, f"Approved seeker post '{seeker_post.title}' by {seeker_post.author.username}")

    messages.success(request, f"✅ SeekerPost '{seeker_post.title}' approved successfully.")
    return redirect("staff:pending_seeker_posts")

# 🟢 Reject SeekerPost
@user_passes_test(staff_required)
def reject_seeker_post(request, pk):
    seeker_post = get_object_or_404(SeekerPost, pk=pk)
    seeker_post.delete()

    log_action(request, "Rejected SeekerPost", seeker_post, f"Deleted seeker post '{seeker_post.title}' by {seeker_post.author.username}")

    messages.warning(request, f"❌ SeekerPost '{seeker_post.title}' has been deleted.")
    return redirect("staff:pending_seeker_posts")


# 🟢 View all spam comments
@user_passes_test(staff_required)
def spam_comments_view(request):
    spam_comments = Comment.objects.filter(is_spam=True).select_related("author", "content_type")
    return render(request, "staff/comments_spam.html", {"spam_comments": spam_comments})


# 🟢 Comment detail view
@user_passes_test(staff_required)
def comment_detail_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    return render(request, "staff/comment_detail.html", {"comment": comment})


# 🟢 Delete spam comment
@user_passes_test(staff_required)
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()

    log_action(request, "Deleted Comment", comment, f"Deleted comment '{comment.text[:30]}...' by {comment.author.username}")

    messages.warning(request, f"🗑️ Comment by '{comment.author.username}' deleted successfully.")
    return redirect("staff:spam_comments")


# 🟢 Restore (mark not spam)
@user_passes_test(staff_required)
def restore_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.is_spam = False
    comment.save()
    
    log_action(request, "Restored Comment", comment, f"Restored comment by '{comment.author.username}'")

    messages.success(request, f"✅ Comment by '{comment.author.username}' restored successfully.")
    return redirect("staff:spam_comments")

@user_passes_test(staff_required)
def pending_locations_view(request):
    """Display all unreviewed pending location requests (Posts + Seekers)."""
    post_requests = PostPendingLocationRequest.objects.filter(is_reviewed=False).select_related("post", "parent_state")
    seeker_requests = PendingSeekerLocationRequest.objects.filter(is_reviewed=False).select_related("post", "parent_state")
    person_requests = PersonPendingLocationRequest.objects.filter(is_reviewed=False).select_related("person", "parent_state")

    context = {
        "post_requests": post_requests,
        "seeker_requests": seeker_requests,
        "person_requests": person_requests,
    }
    return render(request, "staff/pending_locations.html", context)


@user_passes_test(staff_required)
def approve_location(request, pk):
    """
    Approve a pending location for either a Post or Seeker request.
    Automatically creates a Town if not found, links it, and approves the related post.
    """
    pending = (
        PostPendingLocationRequest.objects.select_related("post", "parent_state").filter(pk=pk).first()
        or PendingSeekerLocationRequest.objects.select_related("post", "parent_state").filter(pk=pk).first()
    )

    if not pending:
        messages.error(request, "❌ Pending location request not found.")
        return redirect("staff:pending_locations")

    typed_town = (pending.typed_town or "").strip().title()
    parent_state = pending.parent_state

    if not typed_town or not parent_state:
        messages.warning(request, "⚠️ Cannot approve — missing typed town or parent state.")
        return redirect("staff:pending_locations")

    try:
        with transaction.atomic():
            # 1️⃣ Check for existing Town under the same state
            town = Town.objects.filter(
                Q(state=parent_state) & Q(name__iexact=typed_town)
            ).first()

            # 2️⃣ Create a new Town if it doesn’t exist
            if not town:
                last_town = Town.objects.order_by("-id").first()
                next_id = (last_town.id + 1) if last_town else 1
                prefix = typed_town[:2].lower()
                code = f"{prefix}{next_id}"

                town = Town.objects.create(
                    id=next_id,
                    code=code,
                    name=typed_town,
                    state=parent_state,
                )

            # 3️⃣ Link the Town to the related post (Post or Seeker)
            related_post = pending.post
            related_post.post_town = town
            related_post.status = "approved"
            related_post.save(update_fields=["post_town", "status"])

            # 4️⃣ Mark the request as reviewed and approved
            pending.is_reviewed = True
            pending.approved = True
            pending.save()

            # Optional staff activity log
            log_action(request, "Approved Location", pending, f"Approved town '{typed_town}' under {parent_state.name}")

            # 5️⃣ Success message depending on type
            model_name = "Post" if isinstance(pending, PostPendingLocationRequest) else "Seeker"
            messages.success(request, f"✅ '{typed_town}' approved and linked to {model_name} #{related_post.id}")

    except Exception as e:
        messages.error(request, f"❌ Error approving request: {e}")

    return redirect("staff:pending_locations")


@user_passes_test(staff_required)
def reject_location(request, pk):
    """
    Reject a pending location request (Post or Seeker).
    Sets the post status back to pending and marks the request reviewed.
    """
    pending = (
        PostPendingLocationRequest.objects.filter(pk=pk).first()
        or PendingSeekerLocationRequest.objects.filter(pk=pk).first()
    )

    if not pending:
        messages.error(request, "❌ Location request not found.")
        return redirect("staff:pending_locations")

    try:
        with transaction.atomic():
            related_post = pending.post
            related_post.status = "pending"
            related_post.save(update_fields=["status"])

            pending.is_reviewed = True
            pending.approved = False
            pending.save()

            log_action(request, "Rejected Location", pending, f"Rejected town '{pending.typed_town}' under {pending.parent_state}")

            messages.warning(
                request,
                f"🚫 Rejected '{pending.typed_town}' for {pending.parent_state.name if pending.parent_state else 'Unknown State'}."
            )
    except Exception as e:
        messages.error(request, f"❌ Error rejecting request: {e}")

    return redirect("staff:pending_locations")
    
@user_passes_test(staff_required)
def manage_users(request):
    """List all users with search and filter options."""
    query = request.GET.get("q")
    users = User.objects.all().order_by("-date_joined")

    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query) | users.filter(phone_number__icontains=query)

    context = {
        "users": users,
        "query": query or "",
    }
    return render(request, "staff/manage_users.html", context)

@user_passes_test(staff_required)
def toggle_user_status(request, pk):
    """Activate/Deactivate user accounts safely."""
    from django.shortcuts import get_object_or_404
    user = get_object_or_404(User, pk=pk)
    # ⚠️ Prevent staff from modifying themselves
    if user == request.user:
        messages.warning(request, "⚠️ You cannot deactivate your own account.")
        return redirect("staff:manage_users")

    # ⚠️ Prevent any superuser from being modified
    if user.is_superuser:
        messages.warning(request, "⚠️ Superuser accounts cannot be deactivated or modified here.")
        return redirect("staff:manage_users")

    # Toggle status
    user.is_active = not user.is_active
    user.save()

    action = "activated" if user.is_active else "deactivated"

    # ✅ Log the action safely
    log_action(
        request,
        "Toggled User Status",
        user,
        f"User '{user.username}' has been {action} by staff '{request.user.username}'"
    )

    messages.success(request, f"✅ User '{user.username}' has been {action}.")
    return redirect("staff:manage_users")


@user_passes_test(staff_required)
def staff_board(request):
    """Staff coordination board."""
    posts = StaffBoardPost.objects.select_related("author").all()

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title and content:
            StaffBoardPost.objects.create(author=request.user, title=title, content=content)
            AuditLog.objects.create(
                staff=request.user,
                action="Posted on Board",
                target_type="Board",
                description=f"Created post '{title}'"
            )
            messages.success(request, "Post added to staff board ✅")
            return redirect("staff:staff_board")
        else:
            messages.warning(request, "Please fill in all fields.")

    return render(request, "staff/staff_board.html", {"posts": posts})


@user_passes_test(staff_required)
def audit_log(request):
    """View the staff activity log."""
    logs = AuditLog.objects.select_related("staff").all()[:100]
    return render(request, "staff/audit_log.html", {"logs": logs})


# 🟢 Pending Subscriptions
@user_passes_test(staff_required)
def pending_subscriptions_view(request):
    pending_subs = UserSubscription.objects.filter(payment_reported=True, is_active=False).select_related('user', 'plan')
    return render(request, "staff/pending_subscriptions.html", {"pending_subs": pending_subs})

# 🟢 Approve Subscription
@user_passes_test(staff_required)
def approve_subscription(request, pk):
    user_sub = get_object_or_404(UserSubscription, pk=pk)
    user_sub.is_active = True
    user_sub.start_date = timezone.now()
    user_sub.payment_reported = False
    user_sub.save()

    # ✅ Optional: deactivate other old subscriptions for same user
    UserSubscription.objects.filter(user=user_sub.user).exclude(pk=pk).update(is_active=False)

    log_action(request, "Approved Subscription", user_sub, f"Approved subscription for {user_sub.user.username}")
    messages.success(request, f"✅ Subscription for '{user_sub.user.username}' activated.")
    return redirect("staff:pending_subscriptions")

# 🟢 Reject Subscription
@user_passes_test(staff_required)
def reject_subscription(request, pk):
    user_sub = get_object_or_404(UserSubscription, pk=pk)
    user_sub.payment_reported = False
    user_sub.save()

    log_action(request, "Rejected Subscription", user_sub, f"Rejected subscription for {user_sub.user.username}")
    messages.warning(request, f"❌ Subscription submission for '{user_sub.user.username}' rejected.")
    return redirect("staff:pending_subscriptions")

# 🟢 Pending Profiles
@user_passes_test(staff_required)
def pending_profiles_view(request):
    pending_profiles = Person.objects.filter(approval_status="pending").select_related("user", "country", "state", "town")
    return render(request, "staff/pending_profiles.html", {"pending_profiles": pending_profiles})


# 🟢 Approve Profile
@user_passes_test(staff_required)
def approve_profile(request, pk):
    person = get_object_or_404(Person, pk=pk)
    person.approval_status = "approved"
    person.save(update_fields=["approval_status"])

    # Optionally log action
    log_action(request, "Approved Profile", person, f"Approved profile for {person.user.username}")

    notify_profile_approval(person)  # or notify_profile_rejection(person)

    messages.success(request, f"✅ Profile for '{person.user.username}' approved.")
    return redirect("staff:pending_profiles")


# 🟢 Reject Profile
@user_passes_test(staff_required)
def reject_profile(request, pk):
    person = get_object_or_404(Person, pk=pk)
    person.approval_status = "rejected"
    person.save(update_fields=["approval_status"])

    log_action(request, "Rejected Profile", person, f"Rejected profile for {person.user.username}")


    notify_profile_approval(person)  # or notify_profile_rejection(person)


    messages.warning(request, f"❌ Profile for '{person.user.username}' rejected.")
    return redirect("staff:pending_profiles")
