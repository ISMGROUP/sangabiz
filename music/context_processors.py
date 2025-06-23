from .models import Genre

def genres(request):
    return {
        'all_genres': Genre.objects.all(),
    }