document.addEventListener('DOMContentLoaded', function() {
    const audioPlayer = new Audio();
    let currentSongId = null;
    
    // Play button functionality
    document.querySelectorAll('.play-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const songId = this.getAttribute('data-song-id');
            
            try {
                // If same song, toggle play/pause
                if (currentSongId === songId) {
                    if (audioPlayer.paused) {
                        await audioPlayer.play();
                        this.innerHTML = '<i class="fas fa-pause"></i>';
                    } else {
                        audioPlayer.pause();
                        this.innerHTML = '<i class="fas fa-play"></i>';
                    }
                    return;
                }
                
                // New song - fetch song data
                currentSongId = songId;
                const response = await fetch(`/api/songs/${songId}/stream/`);
                const songData = await response.json();
                
                // Update player with new song
                audioPlayer.src = songData.audio_url;
                audioPlayer.currentTime = 0;
                
                // Update UI
                document.querySelectorAll('.play-btn').forEach(btn => {
                    btn.innerHTML = '<i class="fas fa-play"></i>';
                });
                this.innerHTML = '<i class="fas fa-pause"></i>';
                
                // Play the song
                await audioPlayer.play();
                
                // Record play count
                fetch(`/api/songs/${songId}/play/`, { 
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });
                
            } catch (error) {
                console.error('Error playing song:', error);
                alert('Error playing song. Please try again.');
            }
        });
    });
    
    // Handle audio ended event
    audioPlayer.addEventListener('ended', function() {
        document.querySelectorAll(`.play-btn[data-song-id="${currentSongId}"]`).forEach(btn => {
            btn.innerHTML = '<i class="fas fa-play"></i>';
        });
        currentSongId = null;
    });
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});