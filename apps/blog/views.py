from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Post
from django.utils.text import slugify
from django.contrib import messages


# Create View
class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    fields = ['title', 'category', 'content', 'status']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:post_list')
    success_message = "Post created successfully!"

    def form_valid(self, form):
        # Automatically assign the logged-in user as author
        form.instance.author = self.request.user
        
        # Generate slug from title if not provided
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
            
        return super().form_valid(form)


# Update View
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Post
    fields = ['title', 'category', 'content', 'status']
    template_name = 'blog/post_form.html'
    success_message = "Post updated successfully!"

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'slug': self.object.slug})

    def test_func(self):
        # Only allow author or staff to edit
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff

    def form_valid(self, form):
        # Update slug if title changed
        if form.instance.title != form.initial.get('title'):
            form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)


# Delete View
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')
    success_message = "Post deleted successfully!"

    def test_func(self):
        # Only allow author or staff to delete
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)