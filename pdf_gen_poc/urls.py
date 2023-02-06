from django.contrib import admin
from django.urls import path

admin.site.site_header = 'PDF generator poc Admin'
admin.site.site_title = 'PDF generator poc Admin Portal'
admin.site.index_title = 'Welcome to PDF generator poc Portal'

urlpatterns = [
    path('admin/', admin.site.urls),
]
