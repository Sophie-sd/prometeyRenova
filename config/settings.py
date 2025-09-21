"""
Settings config for prometey_project - Workaround for Render Dashboard override

This module redirects to the actual settings in prometey_project.
Created because Render might look for config.settings
"""

# Import all settings from the actual settings module
from prometey_project.settings import *
