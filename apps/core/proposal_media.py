"""Захищена віддача media: proposals/ — лише зображення + nosniff; proposal_imports/ — 404."""
from pathlib import PurePosixPath

from django.conf import settings
from django.http import Http404
from django.views.static import serve

PROPOSAL_IMAGE_EXT = {'.webp', '.jpg', '.jpeg', '.png'}
BLOCKED_EXT = {'.html', '.htm', '.svg', '.js', '.css', '.xml', '.xhtml', '.svgz'}


def protected_media_serve(request, path):
    norm = path.replace('\\', '/').lstrip('/')
    low = norm.lower()
    if low.startswith('proposal_imports/'):
        raise Http404
    if low.startswith('proposals/'):
        ext = PurePosixPath(low).suffix
        if ext in BLOCKED_EXT or ext not in PROPOSAL_IMAGE_EXT:
            raise Http404
        response = serve(request, norm, document_root=settings.MEDIA_ROOT)
        response['X-Content-Type-Options'] = 'nosniff'
        response['Content-Security-Policy'] = "default-src 'none'; img-src 'self'; sandbox"
        return response
    return serve(request, path, document_root=settings.MEDIA_ROOT)
