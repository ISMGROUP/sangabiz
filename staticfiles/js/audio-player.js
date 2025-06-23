document.addEventListener('DOMContentLoaded', function() {
    const audioPlayer = document.getElementById('audio-player');
    const playButtons = document.querySelectorAll('.play-btn');
    const playBtn = document.getElementById('play-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const progressBar = document.getElementById('progress-bar');
    const currentTimeDisplay = document.getElementById('current-time');
    const durationDisplay = document.getElementById('duration');
    const volumeSlider = document.getElementById('volume-slider');
    const nowPlayingTitle = document.getElementById('now-playing-title');
    const nowPlayingArtist = document.getElementById('now-playing-artist');
    const nowPlayingCover = document.getElementById('now-playing-cover');

    let currentSong = null;
    let songsQueue = [];
    let currentIndex = 0;

    // Initialize from featured songs
    const featuredSongs = Array.from(document.querySelectorAll('.song-card')).map(card => ({
        id: card.dataset.songId,
        title: card.querySelector('.song-info h3').textContent,
        artist: card.querySelector('.song-info p').textContent,
        cover: card.querySelector('.song-image img').src
    }));

    // Set volume
    audioPlayer.volume = volumeSlider.value;
    volumeSlider.addEventListener('input', function() {
        audioPlayer.volume = this.value;
    });

    // Update progress bar
    audioPlayer.addEventListener('timeupdate', function() {
        const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
        progressBar.style.width = `${progress}%`;
        currentTimeDisplay.textContent = formatTime(audioPlayer.currentTime);
    });

    // Update duration display
    audioPlayer.addEventListener('loadedmetadata', function() {
        durationDisplay.textContent = formatTime(audioPlayer.duration);
    });

    // Click on progress bar to seek
    document.querySelector('.progress-container').addEventListener('click', function(e) {
        const percent = e.offsetX / this.offsetWidth;
        audioPlayer.currentTime = percent * audioPlayer.duration;
    });

    // Play/pause toggle
    playBtn.addEventListener('click', function() {
        if (audioPlayer.paused) {
            audioPlayer.play();
            this.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            audioPlayer.pause();
            this.innerHTML = '<i class="fas fa-play"></i>';
        }
    });

    // Play song function
    function playSong(songId) {
        const song = featuredSongs.find(s => s.id === songId);
        if (!song) return;

        currentSong = song;
        songsQueue = featuredSongs;
        currentIndex = songsQueue.findIndex(s => s.id === songId);

        // Update UI
        nowPlayingTitle.textContent = song.title;
        nowPlayingArtist.textContent = song.artist;
        nowPlayingCover.src = song.cover;
        document.getElementById('audio-player-container').style.display = 'flex';

        // Fetch and play audio
        fetch(`/api/songs/${songId}/stream/`)
            .then(response => response.json())
            .then(data => {
                audioPlayer.src = data.url;
                audioPlayer.play();
                playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            })
            .catch(error => {
                console.error('Error playing song:', error);
            });
    }

    // Previous song
    prevBtn.addEventListener('click', function() {
        if (songsQueue.length === 0) return;
        currentIndex = (currentIndex - 1 + songsQueue.length) % songsQueue.length;
        playSong(songsQueue[currentIndex].id);
    });

    // Next song
    nextBtn.addEventListener('click', function() {
        if (songsQueue.length === 0) return;
        currentIndex = (currentIndex + 1) % songsQueue.length;
        playSong(songsQueue[currentIndex].id);
    });

    // Song ended
    audioPlayer.addEventListener('ended', function() {
        nextBtn.click();
    });

    // Format time (seconds to MM:SS)
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }

    // Add click handlers to all play buttons
    playButtons.forEach(button => {
        button.addEventListener('click', function() {
            const songId = this.dataset.songId;
            playSong(songId);
        });
    });
});