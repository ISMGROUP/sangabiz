from django.urls import path
from . import views
from .views import NewsDetailView, NewsListView
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('browse/', views.browse_songs, name='browse'),
    path('search/', views.search, name='search'),
    path('popular/', views.popular, name='popular'),
    path('new_releases/', views.new_releases, name='new_releases'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('dmca/', views.dmca_view, name='dmca'),
    path('comment/add/', views.add_comment, name='add_comment'),
    path('news/', NewsListView.as_view(), name='news_list'), 
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('comment/add/', views.add_comment, name='add_comment'),
    path('comments/load/', views.load_comments, name='load_comments'),
 path('like/', views.like_object, name='like_object'),
    path('check-likes/', views.check_likes, name='check_likes'),    

    # Music content URLs
    path('song/<int:song_id>/download/', views.download_song, name='download_song'),
    path('song/<int:song_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('api/songs/<int:song_id>/stream/', views.stream_song, name='stream_song'),
    path('api/songs/<int:song_id>/play/', views.record_play, name='record_play'),
    # Detail pages (keep these after more specific URLs)
    path('artist/<slug:artist_slug>/', views.artist_detail, name='artist_detail'),
    path('artist/<slug:artist_slug>/<slug:album_slug>/', views.album_detail, name='album_detail'),
    path('artist/<slug:artist_slug>/<slug:album_slug>/<slug:song_slug>/', views.song_detail, name='song_detail'),

    # User accounts
    path('account/register/', views.register, name='register'),
    path('account/login/', views.user_login, name='login'),
    path('account/logout/', views.user_logout, name='logout'),
    path('account/profile/', views.profile, name='profile'),
    
    # Admin/content management
    path('admin/upload/', views.upload_song, name='upload_song'),
    path('admin/create-album/', views.create_album, name='create_album'),
    path('admin/create-artist/', views.create_artist, name='create_artist'),
    path('admin/create-genre/', views.create_genre, name='create_genre'),

     path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='account/password_reset.html',
             email_template_name='account/password_reset_email.html',
             subject_template_name='account/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done')
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='account/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ),
         name='password_reset_confirm'),
    
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='account/password_reset_complete.html'
         ),
         name='password_reset_complete'),

]


