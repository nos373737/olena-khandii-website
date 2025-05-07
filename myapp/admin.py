from django.contrib import admin
from .models import Post, Comment, Contact, Category
# Register your models here.

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Category)



admin.site.site_header = 'OLENAKHANDII | ADMIN PANEL'
admin.site.site_title = 'OLENAKHANDII | BLOGGING WEBSITE'
admin.site.index_title= 'OLENAKHANDII Site Administration'
