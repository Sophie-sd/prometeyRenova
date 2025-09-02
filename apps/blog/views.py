from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import DetailView
from django.db.models import Q
from .models import BlogPost


def blog_list(request):
    """Список статей блогу з фільтрацією"""
    try:
        posts = BlogPost.objects.filter(is_published=True)
        category = request.GET.get('category')
        if category:
            posts = posts.filter(category=category)
        
        # Пагінація
        paginator = Paginator(posts, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Популярні статті
        popular_posts = BlogPost.objects.filter(
            is_published=True
        ).order_by('-created_at')[:3]
        
    except Exception:
        # Fallback якщо таблиці не існують
        paginator = Paginator([], 9)
        page_obj = paginator.get_page(1)
        popular_posts = []
        category = None
    
    context = {
        'page_obj': page_obj,
        'popular_posts': popular_posts,
        'category': category,
        'page_title': 'Блог про веб-розробку та курси програмування',
        'meta_description': 'Корисні статті про веб-розробку, курси програмування, створення сайтів під ключ та Telegram ботів. Читайте експертні поради та навчальні матеріали.',
        'og_title': 'Блог про веб-розробку та курси програмування',
        'keywords': 'блог веб-розробка, курси програмування, створення сайтів, розробка сайтів під ключ, telegram боти, python django',
    }
    return render(request, 'pages/blog.html', context)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'pages/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        try:
            return BlogPost.objects.filter(is_published=True)
        except Exception:
            return BlogPost.objects.none()
    
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
    try:
        posts = BlogPost.objects.filter(is_published=True)
        
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(keywords__icontains=query)
            )
    except Exception:
        posts = BlogPost.objects.none()
    
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
