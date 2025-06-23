// Mobile Menu Toggle
document.querySelector('.mobile-menu-btn').addEventListener('click', function() {
    document.querySelector('.mobile-menu').classList.toggle('active');
});

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const mobileMenu = document.querySelector('.mobile-menu');
    const menuBtn = document.querySelector('.mobile-menu-btn');
    
    if (mobileMenu.classList.contains('active') && 
        !mobileMenu.contains(event.target) && 
        !menuBtn.contains(event.target)) {
        mobileMenu.classList.remove('active');
    }
});

// Play button functionality
document.addEventListener('DOMContentLoaded', function() {
    const playButtons = document.querySelectorAll('.play-btn');
    
    playButtons.forEach(button => {
        button.addEventListener('click', function() {
            const songId = this.getAttribute('data-song-id');
            // Here you would implement audio playback functionality
            console.log(`Playing song with ID: ${songId}`);
            // This would be connected to your audio player API
        });
    });
});

// Search functionality
const searchForm = document.querySelector('.search-bar form');
if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = this.querySelector('input').value.trim();
        if (query) {
            window.location.href = `/search/?q=${encodeURIComponent(query)}`;
        }
    });
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// Sticky navbar on scroll
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }
});

// Play button functionality
document.querySelectorAll('.btn-play, .play-btn').forEach(button => {
    button.addEventListener('click', function() {
        const songId = this.getAttribute('data-song-id');
        // Implement your audio player functionality here
        console.log(`Playing song with ID: ${songId}`);
    });
});

// Favorite button functionality
document.querySelectorAll('.btn-favorite').forEach(button => {
    button.addEventListener('click', function() {
        if (!userAuthenticated) {  // Replace with your auth check
            window.location.href = '/login/';
            return;
        }
        
        const songId = this.getAttribute('data-song-id');
        // Implement favorite functionality via AJAX
        console.log(`Toggling favorite for song ID: ${songId}`);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const searchToggle = document.querySelector('.search-toggle');
    const searchBar = document.querySelector('.search-bar');
    
    if (searchToggle && searchBar) {
        searchToggle.addEventListener('click', function() {
            searchBar.classList.toggle('expanded');
            
            // Focus the input when expanded
            if (searchBar.classList.contains('expanded')) {
                const searchInput = searchBar.querySelector('input');
                searchInput.focus();
            }
        });
        
        // Close search when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchBar.contains(e.target) && !searchToggle.contains(e.target)) {
                searchBar.classList.remove('expanded');
            }
        });
    }
});
document.addEventListener('DOMContentLoaded', function() {
    // Comment form submission
    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // For AJAX response
                    const commentsList = this.closest('.comments-section').querySelector('.comments-list');
                    if (commentsList) {
                        commentsList.insertAdjacentHTML('afterbegin', data.html);
                        this.reset();
                    } else {
                        window.location.reload();
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
    
    // Load comments
    function loadComments() {
        const contentType = document.querySelector('[name="content_type"]').value;
        const objectId = document.querySelector('[name="object_id"]').value;
        
        fetch(`/comments/load/?content_type=${contentType}&object_id=${objectId}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector('.comments-list').innerHTML = data.html;
            }
        });
    }
    
    // Initial load
    loadComments();
});