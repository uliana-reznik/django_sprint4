from django.contrib import admin
from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'author', 'is_published')
    list_filter = ('is_published', 'category', 'location')
    search_fields = ('title', 'text')
    date_hierarchy = 'pub_date'
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'author', 'category', 'location', 'image')
        }),
        ('Дополнительные опции', {
            'fields': ('pub_date', 'is_published'),
            'description': 'Дополнительные настройки публикации'
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__username')
