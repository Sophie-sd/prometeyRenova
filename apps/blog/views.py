from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import BlogPost


class BlogListView(ListView):
    model = BlogPost
    template_name = 'pages/blog.html'
    context_object_name = 'page_obj'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Блог про веб-розробку та курси програмування'
        context['meta_description'] = 'Корисні статті про веб-розробку, курси програмування, створення сайтів під ключ та Telegram ботів. Читайте експертні поради та навчальні матеріали.'
        context['og_title'] = 'Блог про веб-розробку та курси програмування'
        context['keywords'] = 'блог веб-розробка, курси програмування, створення сайтів, розробка сайтів під ключ, telegram боти, python django'
        context['category'] = self.request.GET.get('category')
        
        # Додаємо популярні статті
        context['popular_posts'] = BlogPost.objects.filter(
            is_published=True
        ).order_by('-created_at')[:3]
        
        return context


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'pages/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # SEO мета-дані
        context['page_title'] = post.meta_title or post.title
        context['meta_description'] = post.meta_description or post.excerpt
        context['og_title'] = post.og_title or post.title
        context['og_description'] = post.og_description or post.excerpt
        context['keywords'] = post.keywords
        
        # Пов'язані статті
        related_posts = BlogPost.objects.filter(
            category=post.category,
            is_published=True
        ).exclude(id=post.id)[:3]
        context['related_posts'] = related_posts
        
        return context


def blog_search(request):
    """Пошук по блогу"""
    query = request.GET.get('q', '')
    posts = BlogPost.objects.filter(is_published=True)
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(keywords__icontains=query)
        )
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'page_title': f'Пошук: {query}' if query else 'Пошук по блогу',
        'meta_description': f'Результати пошуку "{query}" в блозі про веб-розробку та курси програмування',
        'og_title': f'Пошук: {query}' if query else 'Пошук по блогу',
        'keywords': 'пошук, блог, веб-розробка, курси програмування'
    }
    
    return render(request, 'pages/blog_search.html', context)
