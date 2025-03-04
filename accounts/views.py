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