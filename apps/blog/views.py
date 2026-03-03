from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils.text import slugify
from .models import Post


# PUBLIC VIEWS
class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        queryset = (
            Post.objects
            .filter(status='published')
            .select_related('author', 'category')
        )

        category_slug = self.request.GET.get('category')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        # Security: Only show published posts to public
        # Authors can see their own drafts via the edit view
        return (
            Post.objects
            .filter(status='published')
            .select_related('author', 'category')
        )


# AUTHOR/ADMIN VIEWS
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