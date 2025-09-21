"""
WSGI config for prometey_project - Workaround for Render Dashboard override

This module redirects to the actual WSGI application in prometey_project.
Created because Render Dashboard has hardcoded 'config.wsgi:application'
"""

# Import the actual WSGI application
from prometey_project.wsgi import application

# Make it available as 'application' for gunicorn
__all__ = ['application']
