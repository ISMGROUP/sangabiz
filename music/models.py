from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
from django.db.models import F
from django.urls import reverse
from django.core.validators import MinValueValidator, FileExtensionValidator

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify

class News(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to='news/')
    published_date = models.DateTimeField(default=timezone.now)
    is_trending = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "News"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key to associate with different content types
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.content_object}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return self.user.username

def song_upload_path(instance, filename):
    """Generate upload path for song audio files"""
    return os.path.join(
        'songs', 
        instance.artist.slug, 
        instance.album.slug, 
        filename
    )

def album_cover_upload_path(instance, filename):
    """Generate upload path for album covers"""
    return os.path.join(
        'covers',
        instance.artist.slug,
        slugify(instance.title),
        filename
    )

def artist_image_upload_path(instance, filename):
    """Generate upload path for artist images"""
    return os.path.join('artists', instance.slug, filename)

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'genre'
        verbose_name_plural = 'genres'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('genre_detail', kwargs={'slug': self.slug})

class Artist(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(
        upload_to=artist_image_upload_path,
        blank=True,
        null=True,
        help_text="Artist profile picture"
    )
    genres = models.ManyToManyField(Genre, related_name='artists')
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'artist'
        verbose_name_plural = 'artists'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'slug': self.slug})

class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='albums'
    )
    slug = models.SlugField(max_length=200, blank=True)
    cover = models.ImageField(
        upload_to=album_cover_upload_path,
        help_text="Album cover art"
    )
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre, related_name='albums')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-release_date']
        unique_together = ('artist', 'slug')
        verbose_name = 'album'
        verbose_name_plural = 'albums'
    
    def __str__(self):
        return f"{self.title} by {self.artist.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('album_detail', kwargs={
            'artist_slug': self.artist.slug,
            'album_slug': self.slug
        })

class Song(models.Model):
    QUALITY_CHOICES = [
        ('128', '128 kbps'),
        ('192', '192 kbps'),
        ('320', '320 kbps'),
        ('FLAC', 'Lossless FLAC'),
    ]

    title = models.CharField(max_length=200)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='songs'
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='songs'
    )
    slug = models.SlugField(max_length=200, blank=True)
    duration = models.PositiveIntegerField(
        help_text="Duration in seconds",
        validators=[MinValueValidator(1)]
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='songs'
    )
    audio_file = models.FileField(
        upload_to=song_upload_path,
        validators=[FileExtensionValidator(['mp3', 'wav', 'flac'])]
    )
    audio_file_quality = models.CharField(
        max_length=10,
        choices=QUALITY_CHOICES,
        default='320'
    )
    lyrics = models.TextField(blank=True)
    copyright = models.TextField(blank=True)
    is_explicit = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    play_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['title']
        unique_together = ('artist', 'album', 'slug')
        verbose_name = 'song'
        verbose_name_plural = 'songs'
    
    def __str__(self):
        return f"{self.title} by {self.artist.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('song_detail', kwargs={
            'artist_slug': self.artist.slug,
            'album_slug': self.album.slug,
            'song_slug': self.slug
        })
    
    def get_duration_display(self):
        """Format duration as MM:SS"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"
    
    def increment_download_count(self):
        """Atomically increment download count"""
        Song.objects.filter(id=self.id).update(download_count=F('download_count') + 1)
        self.refresh_from_db()
    
    def increment_play_count(self):
        """Atomically increment play count"""
        Song.objects.filter(id=self.id).update(play_count=F('play_count') + 1)
        self.refresh_from_db()

class Download(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='downloads'
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='downloads'
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-downloaded_at']
        verbose_name = 'download'
        verbose_name_plural = 'downloads'
    
    def __str__(self):
        return f"Download of {self.song.title} by {self.user.username if self.user else 'Anonymous'}"

class Play(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plays'
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='plays'
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255, blank=True)
    played_at = models.DateTimeField(auto_now_add=True)
    duration_played = models.PositiveIntegerField(
        default=0,
        help_text="Duration played in seconds"
    )
    
    class Meta:
        ordering = ['-played_at']
        verbose_name = 'play'
        verbose_name_plural = 'plays'
    
    def __str__(self):
        return f"Play of {self.song.title} by {self.user.username if self.user else 'Anonymous'}"

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'song')
        ordering = ['-added_at']
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
    
    def __str__(self):
        return f"{self.user.username} likes {self.song.title}"

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists'
    )
    songs = models.ManyToManyField(
        Song,
        through='PlaylistSong',
        related_name='playlists'
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'playlist'
        verbose_name_plural = 'playlists'
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('playlist_detail', kwargs={'pk': self.pk})

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='playlist_songs'
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='playlist_songs'
    )
    position = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
        unique_together = ('playlist', 'song')
        verbose_name = 'playlist song'
        verbose_name_plural = 'playlist songs'
    
    def __str__(self):
        return f"{self.song.title} in {self.playlist.name}"
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.user.username} likes {self.content_object}"