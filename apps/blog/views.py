from django.views.generic import ListView, DetailView
from .models import Post


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
            queryset =  queryset.filter(category_slug=category_slug)

        return queryset
