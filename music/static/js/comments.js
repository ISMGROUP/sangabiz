document.addEventListener('DOMContentLoaded', function() {
    // Initialize comment functionality
    initComments();
});

function initComments() {
    // Comment form submission
    const commentForms = document.querySelectorAll('.comment-form');
    if (commentForms.length) {
        commentForms.forEach(form => {
            form.addEventListener('submit', handleCommentSubmit);
        });
    }

    // Initial comments load
    loadComments();
    
    // Set up periodic refresh (optional)
    // setInterval(loadComments, 30000); // Refresh every 30 seconds
}

async function handleCommentSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    
    try {
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';
        
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Clear form
            form.reset();
            
            // Handle successful comment addition
            const commentsContainer = form.closest('.comments-section')?.querySelector('.comments-list');
            if (commentsContainer) {
                if (data.html) {
                    // Prepend new comment
                    commentsContainer.insertAdjacentHTML('afterbegin', data.html);
                    
                    // Scroll to new comment if needed
                    const newComment = commentsContainer.firstElementChild;
                    newComment.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    
                    // Initialize any new comment-specific JS
                    initCommentElements(newComment);
                }
            } else {
                // Fallback: reload if we can't find the container
                console.warn('Comments container not found, reloading page');
                window.location.reload();
            }
        } else {
            // Show error message to user
            showCommentError(form, data.error || 'Failed to post comment');
        }
    } catch (error) {
        console.error('Comment submission error:', error);
        showCommentError(form, 'An error occurred while posting your comment');
    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }
}

function showCommentError(form, message) {
    // Remove any existing error messages
    const existingErrors = form.querySelectorAll('.comment-error');
    existingErrors.forEach(el => el.remove());
    
    // Create and show new error message
    const errorElement = document.createElement('div');
    errorElement.className = 'comment-error alert alert-danger';
    errorElement.textContent = message;
    
    // Insert before the submit button
    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.parentNode.insertBefore(errorElement, submitButton);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorElement.remove();
    }, 5000);
}

async function loadComments() {
    const contentTypeInput = document.querySelector('[name="content_type"]');
    const objectIdInput = document.querySelector('[name="object_id"]');
    const commentsContainer = document.querySelector('.comments-list');
    
    // Validate we have all required elements
    if (!contentTypeInput || !objectIdInput || !commentsContainer) {
        return;
    }
    
    const contentType = contentTypeInput.value;
    const objectId = objectIdInput.value;
    
    // Validate parameters
    if (!contentType || !objectId) {
        console.warn('Missing content_type or object_id for comments');
        return;
    }
    
    try {
        // Show loading state
        commentsContainer.classList.add('loading');
        
        const response = await fetch(`/comments/load/?content_type=${encodeURIComponent(contentType)}&object_id=${encodeURIComponent(objectId)}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            if (data.html) {
                commentsContainer.innerHTML = data.html;
                // Initialize any comment-specific JS for new elements
                initCommentElements(commentsContainer);
            }
        } else {
            console.error('Failed to load comments:', data.error);
            showCommentsError(commentsContainer, data.error || 'Failed to load comments');
        }
    } catch (error) {
        console.error('Comments load error:', error);
        showCommentsError(commentsContainer, 'An error occurred while loading comments');
    } finally {
        commentsContainer.classList.remove('loading');
    }
}

function showCommentsError(container, message) {
    // Don't overwrite existing comments if we're just refreshing
    if (container.children.length === 0) {
        const errorElement = document.createElement('div');
        errorElement.className = 'comments-error alert alert-warning';
        errorElement.textContent = message;
        container.appendChild(errorElement);
    }
}

function initCommentElements(container) {
    // Initialize any interactive elements within comments
    // Example: reply buttons, like buttons, etc.
    
    // Like buttons
    container.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', handleLike);
    });
    
    // Delete buttons
    container.querySelectorAll('.delete-comment-btn').forEach(button => {
        button.addEventListener('click', handleDeleteComment);
    });
}

async function handleLike(e) {
    const button = e.currentTarget;
    const contentType = button.dataset.contentType;
    const objectId = button.dataset.objectId;
    
    try {
        button.disabled = true;
        
        const response = await fetch('/like/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                content_type: contentType,
                object_id: objectId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const likeCount = button.querySelector('.like-count');
            if (likeCount) {
                likeCount.textContent = data.likes_count;
            }
            button.classList.toggle('liked', data.liked);
        }
    } catch (error) {
        console.error('Like error:', error);
    } finally {
        button.disabled = false;
    }
}

async function handleDeleteComment(e) {
    if (!confirm('Are you sure you want to delete this comment?')) {
        return;
    }
    
    const button = e.currentTarget;
    const commentId = button.dataset.commentId;
    const commentElement = document.getElementById(`comment-${commentId}`);
    
    try {
        button.disabled = true;
        
        const response = await fetch(`/comments/delete/${commentId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        
        if (data.success && commentElement) {
            commentElement.remove();
        }
    } catch (error) {
        console.error('Delete comment error:', error);
    }
}

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