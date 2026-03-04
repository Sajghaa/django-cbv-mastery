from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name ='users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('blog:post_list')
