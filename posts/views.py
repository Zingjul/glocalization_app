from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from .models import Post, PostImage  # Import PostImage
from .forms import PostForm, PostImageFormSet  # Import PostImageFormSet

class PostView(ListView):
    model = Post
    template_name = 'post_home.html'
    context_object_name = 'posts'

class PostDetailedView(DetailView):
    model = Post
    template_name = 'post_detailed.html'
    context_object_name = 'post'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_create_new.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = PostImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = PostImageFormSet()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)  # Save the Post instance first
        self.object.author = self.request.user
        self.object.save()  # Now save the Post to the DB

        image_formset = self.get_context_data()['image_formset']
        if image_formset.is_valid():
            image_formset.instance = self.object  # Link images to the Post
            image_formset.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detailed', kwargs={'pk': self.object.pk})

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = PostImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['image_formset'] = PostImageFormSet(instance=self.object) #This line is critical.
        return context

    def form_valid(self, form):
        self.object = form.save()

        image_formset = self.get_context_data()['image_formset']
        if image_formset.is_valid():
            image_formset.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detailed', kwargs={'pk': self.object.pk})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_home')