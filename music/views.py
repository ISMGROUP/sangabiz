from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, F

from django.views.generic import DetailView, ListView


from django.views.decorators.cache import never_cache
from .models import Song, News, Like
import os

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from .models import Song, Album, Artist, Genre, Download, Favorite, Comment 
from django.db.models import Count, Prefetch
from .forms import UserRegisterForm, UserLoginForm, SongUploadForm, AlbumCreateForm, ArtistCreateForm, GenreCreateForm, SearchForm


def index(request):
    # Get featured songs
    featured_songs = Song.objects.filter(is_featured=True).order_by('-created_at')[:8]
    
    # Get popular artists based on song count
    popular_artists = Artist.objects.annotate(song_count=Count('songs')).order_by('-song_count')[:8]
    
    # Get new album releases
    new_releases = Album.objects.order_by('-release_date')[:6]
    
    # Get trending news (most recent 3 trending news items)
    trending_news = News.objects.filter(is_trending=True).order_by('-published_date')[:3]
    
    context = {
        'featured_songs': featured_songs,
        'popular_artists': popular_artists,
        'new_releases': new_releases,
        'trending_news': trending_news,  # Add trending news to context
    }
    return render(request, 'music/index.html', context)

class NewsDetailView(DetailView):
    model = News
    template_name = 'news/detail.html'
    context_object_name = 'news'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_views()
        return obj

def browse_songs(request):
    songs = Song.objects.all().order_by('-created_at')
    genres = Genre.objects.all()
    
    # Filtering
    genre_filter = request.GET.get('genre')
    if genre_filter:
        songs = songs.filter(genre__id=genre_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        songs = songs.order_by('-download_count')
    elif sort_by == 'oldest':
        songs = songs.order_by('created_at')
    elif sort_by == 'a-z':
        songs = songs.order_by('title')
    elif sort_by == 'z-a':
        songs = songs.order_by('-title')
    else:  # newest
        songs = songs.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(songs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'songs': page_obj,
        'genres': genres,
        'selected_genre': int(genre_filter) if genre_filter else None,
        'sort_by': sort_by,
    }
    return render(request, 'music/browse.html', context)



def popular(request):
    sort_by = request.GET.get('sort', 'downloads')
    
    if sort_by == 'plays':
        songs = Song.objects.all().order_by(F('play_count').desc())
    else:
        songs = Song.objects.all().order_by(F('download_count').desc())
    
    paginator = Paginator(songs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'music/popular.html', {
        'page_obj': page_obj,
        'sort': sort_by
    })

def new_releases(request):
    # Get albums ordered by release date (newest first)
    new_albums = Album.objects.all().order_by('-release_date')
    
    # Pagination - 12 albums per page
    paginator = Paginator(new_albums, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'section': 'new-releases', 
        'title': 'New Releases'
    }
    return render(request, 'music/new_releases.html', context)

def search(request):
    form = SearchForm(request.GET)
    results = {'songs': [], 'albums': [], 'artists': []}
    query = ''
    
    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            results['songs'] = Song.objects.filter(
                Q(title__icontains=query) | 
                Q(artist__name__icontains=query) |
                Q(album__title__icontains=query)
            ).distinct()
            
            results['albums'] = Album.objects.filter(
                Q(title__icontains=query) |
                Q(artist__name__icontains=query)
            ).distinct()
            
            results['artists'] = Artist.objects.filter(
                Q(name__icontains=query)
            ).distinct()
    
    context = {
        'form': form,
        'query': query,
        'songs': results['songs'],
        'albums': results['albums'],
        'artists': results['artists'],
    }
    return render(request, 'music/search.html', context)

def song_detail(request, artist_slug, album_slug, song_slug):
    song = get_object_or_404(Song, artist__slug=artist_slug, album__slug=album_slug, slug=song_slug)
    related_songs = Song.objects.filter(artist=song.artist).exclude(id=song.id).order_by('?')[:6]
    
    # Increment view count (for popularity tracking)
    song.views += 1
    song.save()
    
    context = {
        'song': song,
        'related_songs': related_songs,
    }
    return render(request, 'music/song.html', context)

def album_detail(request, artist_slug, album_slug):
    album = get_object_or_404(Album, artist__slug=artist_slug, slug=album_slug)
    songs = album.songs.all().order_by('title')
    
    context = {
        'album': album,
        'songs': songs,
    }
    return render(request, 'music/album.html', context)

def artist_detail(request, artist_slug):
    artist = get_object_or_404(Artist, slug=artist_slug)
    popular_songs = artist.songs.order_by('-download_count')[:5]
    albums = artist.albums.order_by('-release_date')
    
    context = {
        'artist': artist,
        'popular_songs': popular_songs,
        'albums': albums,
    }
    return render(request, 'music/artist.html', context)

@never_cache
def download_song(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    
    # Verify the file exists
    if not song.audio_file:
        raise Http404("Audio file not found")
    
    file_path = song.audio_file.path
    if os.path.exists(file_path):
        # Increment download count
        song.increment_download_count()
        
        # Create download record
        if request.user.is_authenticated:
            Download.objects.create(
                user=request.user,
                song=song,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        # Prepare the file for download
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="audio/mpeg")
            filename = os.path.basename(file_path)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    
    raise Http404("File not found on server")
@login_required
def toggle_favorite(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, song=song)
    
    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed', 'count': song.favorited_by.count()})
    
    return JsonResponse({'status': 'added', 'count': song.favorited_by.count()})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    
    return render(request, 'music/account/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = UserLoginForm()
    
    return render(request, 'music/account/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def profile(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user).select_related('song')
    downloads = Download.objects.filter(user=user).select_related('song').order_by('-downloaded_at')[:20]
    
    return render(request, 'music/account/profile.html', {
        'user': user,
        'favorites': favorites,
        'downloads': downloads,
    })

# Admin views for content management
@login_required
def upload_song(request):
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.uploaded_by = request.user
            song.save()
            return redirect('song_detail', artist_slug=song.artist.slug, album_slug=song.album.slug, song_slug=song.slug)
    else:
        form = SongUploadForm()
    
    return render(request, 'music/admin/upload_song.html', {'form': form})

@login_required
def create_album(request):
    if request.method == 'POST':
        form = AlbumCreateForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save()
            return redirect('album_detail', artist_slug=album.artist.slug, album_slug=album.slug)
    else:
        form = AlbumCreateForm()
    
    return render(request, 'music/admin/create_album.html', {'form': form})

@login_required
def create_artist(request):
    if request.method == 'POST':
        form = ArtistCreateForm(request.POST, request.FILES)
        if form.is_valid():
            artist = form.save()
            return redirect('artist_detail', artist_slug=artist.slug)
    else:
        form = ArtistCreateForm()
    
    return render(request, 'music/admin/create_artist.html', {'form': form})

@login_required
def create_genre(request):
    if request.method == 'POST':
        form = GenreCreateForm(request.POST)
        if form.is_valid():
            genre = form.save()
            return redirect('browse')
    else:
        form = GenreCreateForm()
    
    return render(request, 'music/admin/create_genre.html', {'form': form})

def terms(request):
    context = {
        'title': 'Terms of Service',
        'last_updated': 'January 1, 2023',
        'company_name': 'Sangabiz',
        'contact_email': 'legal@sangabiz.com'
    }
    return render(request, 'music/terms.html', context)

def privacy_view(request):
    context = {
        'title': 'Privacy Policy',
        'last_updated': 'January 1, 2023',
        'company_name': 'Sangabiz',
        'contact_email': 'privacy@sangabiz.com'
    }
    return render(request, 'music/privacy.html', context)

def dmca_view(request):
    context = {
        'title': 'DMCA Policy',
        'last_updated': 'January 1, 2023',
        'company_name': 'Sangabiz',
        'contact_email': 'dmca@sangabiz.com',
        'mailing_address': '123 Copyright Lane, Music City, MC 12345'
    }
    return render(request, 'music/dmca.html', context)

from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Song, Album, Artist

def song_detail(request, artist_slug, album_slug, song_slug):
    # Get the song with related artist and album
    song = get_object_or_404(
        Song.objects.select_related('artist', 'album'),
        artist__slug=artist_slug,
        album__slug=album_slug,
        slug=song_slug
    )
    
    # Increment view count
    song.views += 1
    song.save()
    
    # Get related songs (from same album and artist)
    related_songs = Song.objects.filter(
        artist=song.artist
    ).exclude(
        id=song.id
    ).order_by(
        '-download_count'
    )[:6]
    
    # Get other albums by the same artist
    artist_albums = Album.objects.filter(
        artist=song.artist
    ).exclude(
        id=song.album.id
    ).annotate(
        song_count=Count('songs')
    ).order_by(
        '-release_date'
    )[:4]
    
    context = {
        'song': song,
        'related_songs': related_songs,
        'artist_albums': artist_albums,
        'page_title': f"{song.title} - {song.artist.name}",
    }
    return render(request, 'music/song_detail.html', context)

def artist_detail(request, artist_slug):
    # Get artist with prefetched albums and songs
    artist = get_object_or_404(
        Artist.objects.prefetch_related(
            Prefetch('albums', 
                    queryset=Album.objects.annotate(
                        song_count=Count('songs')
                    ).order_by('-release_date')
            ),
            Prefetch('albums__songs',
                    queryset=Song.objects.order_by('title'))
        ),
        slug=artist_slug
    )
    
    # Get popular songs (top 5 by downloads)
    popular_songs = artist.songs.order_by('-download_count')[:5]
    
    # Get all genres associated with this artist
    genres = artist.genres.all()
    
    # Get similar artists (by shared genres)
    similar_artists = Artist.objects.filter(
        genres__in=genres
    ).exclude(
        id=artist.id
    ).distinct().annotate(
        album_count=Count('albums')
    ).order_by('-album_count')[:4]
    
    context = {
        'artist': artist,
        'popular_songs': popular_songs,
        'albums': artist.albums.all(),
        'genres': genres,
        'similar_artists': similar_artists,
        'page_title': f"{artist.name} - Artist Profile",
    }
    return render(request, 'music/artist_detail.html', context)

from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Song
import os

@require_GET
def stream_song(request, song_id):
    """
    Stream song metadata including audio URL, cover art, and track information.
    """
    try:
        song = get_object_or_404(Song, pk=song_id)
        
        # Build response data
        response_data = {
            'audio_url': request.build_absolute_uri(song.audio_file.url),
            'title': song.title,
            'artist': song.artist.name,
            'duration': song.duration,
            'play_count': song.play_count,
        }
        
        # Add cover URL if available
        if song.album and song.album.cover:
            response_data['cover_url'] = request.build_absolute_uri(song.album.cover.url)
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def direct_stream(request, song_id):
    """
    Direct file streaming endpoint (alternative to metadata approach)
    """
    song = get_object_or_404(Song, pk=song_id)
    file_path = song.audio_file.path
    
    if not os.path.exists(file_path):
        raise Http404("Audio file not found")
    
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='audio/mpeg'
    )
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    return response

@require_POST
@csrf_exempt  # Only use this if you're having CSRF issues - consider proper CSRF handling for production
def record_play(request, song_id):
    """
    Increment play count for a song and return updated count
    """
    try:
        song = get_object_or_404(Song, pk=song_id)
        song.play_count += 1
        song.save()
        
        return JsonResponse({
            'status': 'success',
            'play_count': song.play_count
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def download(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    
    if not song.audio_file:
        raise Http404("Audio file not found")
    
    file_path = song.audio_file.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="audio/mpeg")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    raise Http404("File not found on server")


@login_required
def add_comment(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        content_type = request.POST.get('content_type')
        object_id = request.POST.get('object_id')
        
        if content and content_type and object_id:
            try:
                content_type = ContentType.objects.get(model=content_type)
                comment = Comment.objects.create(
                    user=request.user,
                    content=content,
                    content_type=content_type,
                    object_id=object_id
                )
                messages.success(request, 'Your comment has been posted!')
            except Exception as e:
                messages.error(request, f'Error posting comment: {str(e)}')
        
        # Redirect back to the previous page
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return redirect('/')



def load_comments(request):
    content_type = request.GET.get('content_type')
    object_id = request.GET.get('object_id')
    
    if not content_type or not object_id:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        content_type = ContentType.objects.get(model=content_type.lower())
        comments = Comment.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).select_related('user').order_by('-created_at')
        
        from django.template.loader import render_to_string
        html = render_to_string('comments/comments_list.html', {
            'comments': comments
        })
        
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'html': html,
            'count': comments.count()
        })
        
    except ContentType.DoesNotExist:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Invalid content type'}, status=400)

class NewsDetailView(DetailView):
    model = News
    template_name = 'news/detail.html'  # This should match your template path
    context_object_name = 'news'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class NewsListView(ListView):
    model = News
    template_name = 'news/list.html'  # Create this template
    context_object_name = 'news_list'
    ordering = ['-published_date']
    paginate_by = 10

from .models import Like

@login_required
def like_object(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        content_type = request.POST.get('content_type')
        object_id = request.POST.get('object_id')
        
        try:
            content_type = ContentType.objects.get(model=content_type)
            model_class = content_type.model_class()
            content_object = model_class.objects.get(pk=object_id)
            
            like, created = Like.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=object_id
            )
            
            if not created:
                like.delete()
                action = 'unliked'
            else:
                action = 'liked'
            
            return JsonResponse({
                'success': True,
                'action': action,
                'new_like_count': content_object.likes.count()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False}, status=400)

@login_required
def check_likes(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        items = request.POST.getlist('items[]')
        liked_items = []
        
        for item in items:
            try:
                content_type = ContentType.objects.get(model=item['content_type'])
                if Like.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    object_id=item['object_id']
                ).exists():
                    liked_items.append({
                        'content_type': item['content_type'],
                        'object_id': item['object_id']
                    })
            except:
                continue
        
        return JsonResponse({
            'success': True,
            'liked_items': liked_items
        })
    
    return JsonResponse({'success': False}, status=400)