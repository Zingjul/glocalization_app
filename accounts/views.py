from django.shortcuts import render, redirect
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from .forms import CustomPasswordResetForm, CustomPasswordChangeForm
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic import CreateView, View
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from django.views.generic.edit import FormView

from rest_framework import generics
from .models import CustomUser
from .serializers import CustomUserSerializer
# api 
class UserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

# end api
class SignupView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('signup_success')  # URL name for success

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.virtual_id = user.virtual_id  # Store virtual_id for success template
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('signup_success') + f'?virtual_id={self.virtual_id}'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('some_redirect_url') #redirect authenticated users
        return super().get(request, *args, **kwargs)

def signup_success(request):
    virtual_id = request.GET.get('virtual_id')
    return render(request, 'signup_success.html', {'virtual_id': virtual_id})

class LogoutView(View):
    def get(self, request,):
        logout(request)
        return redirect('login')
#  password reset view  
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset_form.html'  # Create this template
    success_url = reverse_lazy('password_reset_done')  # Create this url and view.
    email_template_name = 'accounts/password_reset_email.html' #Create this template

    def form_valid(self, form):
        try:
            user = form.save()
            if user is None:
                print("User object is None after save()")
            login(self.request, user)
            self.virtual_id = user.virtual_id
            print(f"User {user.username} created successfully.")
            return super().form_valid(form)
        except Exception as e:
            print(f"Error creating user: {e}")
            return super().form_invalid(form)
    
# password change view
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change_form.html'  # Create this template
    success_url = reverse_lazy('password_change_done')