// like-system.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all like buttons
    const likeButtons = document.querySelectorAll('.like-button');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const contentType = this.dataset.contentType;
            const objectId = this.dataset.objectId;
            const heartIcon = this.querySelector('i');
            const likeCount = this.querySelector('.like-count');
            
            // Check if user is authenticated
            if (!isUserAuthenticated()) {
                showLoginAlert();
                return;
            }
            
            // Visual feedback during request
            this.classList.add('processing');
            heartIcon.classList.replace('fa-heart', 'fa-spinner', 'fa-spin');
            
            // Send like/unlike request
            fetch('/like/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    content_type: contentType,
                    object_id: objectId
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Update like count and icon
                    likeCount.textContent = data.new_like_count;
                    
                    if (data.action === 'liked') {
                        heartIcon.classList.replace('far', 'fas');
                        this.classList.add('liked');
                        showToast('Liked!');
                    } else {
                        heartIcon.classList.replace('fas', 'far');
                        this.classList.remove('liked');
                        showToast('Removed like');
                    }
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error: ' + error.message, 'error');
            })
            .finally(() => {
                this.classList.remove('processing');
                heartIcon.classList.remove('fa-spinner', 'fa-spin');
                heartIcon.classList.add('fa-heart');
            });
        });
    });
    
    // Check if user has already liked items (on page load)
    if (isUserAuthenticated()) {
        checkExistingLikes();
    }
    
    // Helper Functions
    
    function isUserAuthenticated() {
        return document.body.classList.contains('user-authenticated');
    }
    
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    function showLoginAlert() {
        // You could redirect to login or show a modal
        showToast('Please log in to like content', 'warning');
        
        // Alternatively, trigger a login modal:
        // const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
        // loginModal.show();
    }
    
    function showToast(message, type = 'success') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Remove after delay
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    async function checkExistingLikes() {
        const likeableItems = Array.from(document.querySelectorAll('.like-button')).map(button => ({
            contentType: button.dataset.contentType,
            objectId: button.dataset.objectId,
            element: button
        }));
        
        if (likeableItems.length === 0) return;
        
        try {
            const response = await fetch('/check-likes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    items: likeableItems.map(item => ({
                        content_type: item.contentType,
                        object_id: item.objectId
                    }))
                })
            });
            
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            
            if (data.success) {
                data.liked_items.forEach(likedItem => {
                    const button = document.querySelector(`.like-button[data-content-type="${likedItem.content_type}"][data-object-id="${likedItem.object_id}"]`);
                    if (button) {
                        button.querySelector('i').classList.replace('far', 'fas');
                        button.classList.add('liked');
                    }
                });
            }
        } catch (error) {
            console.error('Error checking likes:', error);
        }
    }
});