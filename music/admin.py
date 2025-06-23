from django.contrib import admin
from .models import Song, Album, Artist, Genre, Download, Favorite, News

class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'download_count', 'created_at')
    list_filter = ('artist', 'album', 'genre', 'is_featured')
    search_fields = ('title', 'artist__name', 'album__title')
    readonly_fields = ('download_count',)  # Fixed: added comma to make it a tuple

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date')
    list_filter = ('artist', 'release_date')
    search_fields = ('title', 'artist__name')
    filter_horizontal = ('genres',)

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('genres',)

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

class DownloadAdmin(admin.ModelAdmin):
    list_display = ('song', 'user', 'ip_address', 'downloaded_at')
    list_filter = ('downloaded_at', 'user')
    search_fields = ('song__title', 'user__username')

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'added_at')
    list_filter = ('added_at', 'user')
    search_fields = ('song__title', 'user__username')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_trending', 'published_date', 'views')
    list_filter = ('is_trending', 'published_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content', 'image')
        }),
        ('Options', {
            'fields': ('is_trending', 'published_date', 'author'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set author on first save
            obj.author = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Song, SongAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Download, DownloadAdmin)
admin.site.register(Favorite, FavoriteAdmin)
