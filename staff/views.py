from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

@login_required
@staff_required
def dashboard(request):
    return render(request, 'staff/dashboard.html')

@login_required
@staff_required
def pending_posts(request):
    return render(request, 'staff/pending_posts.html')

@login_required
@staff_required
def flagged_comments(request):
    return render(request, 'staff/flagged_comments.html')

@login_required
@staff_required
def manage_users(request):
    return render(request, 'staff/manage_users.html')

@login_required
@staff_required
def support_inbox(request):
    return render(request, 'staff/support_inbox.html')
