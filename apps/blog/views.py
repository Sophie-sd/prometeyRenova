from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.views.generic import DetailView
from django.db.models import Q
from .models import BlogPost
from .slugs import LEGACY_SLUG_REDIRECTS


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
    from django.utils import translation
    if (translation.get_language() or '').startswith('en'):
        context.update({
            'page_title': 'Blog on web development and programming courses',
            'meta_description': 'Useful articles on web development, programming courses, turnkey websites and Telegram bots. Expert tips and learning materials.',
            'og_title': 'Blog on web development and programming courses',
            'keywords': 'web development blog, programming courses, website development, turnkey websites, telegram bots, python django',
        })
    return render(request, 'pages/blog.html', context)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'pages/blog_detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # Old Cyrillic slugs → Latin (data migration blog.0004). reverse() keeps /ru/ and /en/.
        new_slug = LEGACY_SLUG_REDIRECTS.get(kwargs.get('slug'))
        if new_slug:
            return redirect('blog:blog_detail', slug=new_slug, permanent=True)
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        try:
            return BlogPost.objects.filter(is_published=True)
        except Exception:
            return BlogPost.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        context['blog_posting_json_ld'] = blog_posting_ld(post)

        # SEO мета-дані
        context['page_title'] = post.meta_title or post.get_localized_title()
        context['meta_description'] = post.meta_description or post.get_localized_excerpt()
        context['og_title'] = post.og_title or post.get_localized_title()
        context['og_description'] = post.og_description or post.get_localized_excerpt()
        context['keywords'] = post.get_localized_keywords()
        
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


def blog_posting_ld(post):
    """BlogPosting JSON-LD; dates are the same values shown in the article header."""
    import json

    from django.templatetags.static import static
    from django.utils.html import strip_tags
    from django.utils.safestring import mark_safe
    from django.utils.timezone import localtime

    from apps.core.seo import ORGANIZATION_ID, SITE, current_lang

    if post.featured_image:
        image = post.featured_image.url
    else:
        image = static('images/og-image.jpg')
    if not image.startswith('http'):
        image = SITE + image
    url = SITE + post.get_absolute_url()
    data = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        'headline': strip_tags(post.get_localized_title() or '')[:110],
        'description': strip_tags(post.get_localized_excerpt() or '')[:300],
        'image': [image],
        'datePublished': localtime(post.created_at).isoformat(timespec='seconds'),
        'dateModified': localtime(post.updated_at).isoformat(timespec='seconds'),
        'author': {'@type': 'Organization', '@id': ORGANIZATION_ID, 'name': 'PrometeyLabs', 'url': SITE + '/'},
        'publisher': {'@id': ORGANIZATION_ID},
        'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
        'url': url,
        'inLanguage': current_lang(),
    }
    return mark_safe(json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
