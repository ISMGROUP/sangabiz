from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User  # Add this import
from .models import Song, Album, Artist, Genre

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SongUploadForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'album', 'genre', 'audio_file', 'audio_file_quality', 'lyrics', 'copyright', 'is_explicit']
        widgets = {
            'lyrics': forms.Textarea(attrs={'rows': 5}),
            'copyright': forms.Textarea(attrs={'rows': 3}),
        }

class AlbumCreateForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'artist', 'cover', 'release_date', 'genres', 'description']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ArtistCreateForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name', 'bio', 'image', 'genres', 'website', 'facebook', 'twitter', 'instagram']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
        }

class GenreCreateForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100, required=False, 
                        widget=forms.TextInput(attrs={'placeholder': 'Search for songs, artists, albums...'}))