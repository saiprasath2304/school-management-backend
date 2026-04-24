"""
Django admin site customisation — school branding.
Imported in eduverse/__init__.py so it runs on startup.
"""
from django.contrib import admin

admin.site.site_header  = "Eduverse Africa — School Management"
admin.site.site_title   = "Eduverse Admin"
admin.site.index_title  = "Welcome to the Admin Panel"
