from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic import CreateView, View
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from django.views.generic.edit import FormView

class SignupView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('signup_success')  # URL name for success

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.visual_id = user.visual_id  # Store visual_id for success template
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('signup_success') + f'?visual_id={self.visual_id}'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('some_redirect_url') #redirect authenticated users
        return super().get(request, *args, **kwargs)

def signup_success(request):
    visual_id = request.GET.get('visual_id')
    return render(request, 'signup_success.html', {'visual_id': visual_id})

class LogoutView(View):
    def get(self, request,):
        logout(request)
        return redirect('logged_out')
    
class LogoutSuccessful(View):
    template_name = 'logout_successful.html'