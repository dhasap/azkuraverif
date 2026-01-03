// Main JavaScript for SheerID Verification System

// Global functions
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        showLoading();
        $.ajax({
            url: '/api/auth/logout',
            method: 'POST',
            success: function(response) {
                showToast('Logout successful', 'success');
                setTimeout(function() {
                    window.location.href = '/';
                }, 500);
            },
            error: function() {
                showToast('Logged out', 'info');
                setTimeout(function() {
                    window.location.href = '/';
                }, 500);
            }
        });
    }
    return false;
}

function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    const toastContainer = $('.toast-container');
    if (toastContainer.length === 0) {
        $('body').append('<div class="toast-container position-fixed top-0 end-0 p-3"></div>');
    }
    
    $('.toast-container').append(toastHtml);
    const toastElement = $('.toast-container .toast:last');
    const toast = new bootstrap.Toast(toastElement[0]);
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function showLoading() {
    if ($('.spinner-overlay').length === 0) {
        $('body').append(`
            <div class="spinner-overlay">
                <div class="spinner-border text-light" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `);
    }
}

function hideLoading() {
    $('.spinner-overlay').remove();
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }, function(err) {
        showToast('Failed to copy', 'danger');
    });
}

// AJAX setup
$.ajaxSetup({
    error: function(xhr, status, error) {
        if (xhr.status === 401) {
            window.location.href = '/login';
        } else if (xhr.status === 403) {
            showToast('Access denied', 'danger');
        } else if (xhr.status === 500) {
            showToast('Server error. Please try again later.', 'danger');
        }
    }
});

// Initialize tooltips
$(document).ready(function() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Service verification functions
function verifyService(serviceName, endpoint, url) {
    if (!url) {
        showToast('Please enter a SheerID URL', 'warning');
        return;
    }
    
    showLoading();
    
    $.ajax({
        url: `/api/verify/${endpoint}`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ url: url }),
        success: function(response) {
            hideLoading();
            if (response.success) {
                showToast(response.message, 'success');
                if (response.result && response.result.redirect_url) {
                    setTimeout(() => {
                        window.open(response.result.redirect_url, '_blank');
                    }, 1000);
                }
                // Refresh balance
                loadUserBalance();
            } else {
                showToast(response.message, 'danger');
            }
        },
        error: function(xhr) {
            hideLoading();
            const response = xhr.responseJSON || {};
            showToast(response.message || 'Verification failed', 'danger');
        }
    });
}

function loadUserBalance() {
    $.ajax({
        url: '/api/user/balance',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                $('.user-balance').text(response.balance);
            }
        }
    });
}

// Check-in function
function dailyCheckin() {
    $.ajax({
        url: '/api/user/checkin',
        method: 'POST',
        success: function(response) {
            if (response.success) {
                showToast(response.message, 'success');
                loadUserBalance();
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON || {};
            showToast(response.message || 'Check-in failed', 'danger');
        }
    });
}

// Redeem code function
function redeemCode() {
    const code = $('#redeemCodeInput').val();
    if (!code) {
        showToast('Please enter a code', 'warning');
        return;
    }
    
    $.ajax({
        url: '/api/user/redeem',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ code: code }),
        success: function(response) {
            if (response.success) {
                showToast(response.message, 'success');
                $('#redeemCodeInput').val('');
                loadUserBalance();
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON || {};
            showToast(response.message || 'Redemption failed', 'danger');
        }
    });
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Global AJAX error handler
$(document).ajaxError(function(event, jqxhr, settings, thrownError) {
    if (jqxhr.status === 401) {
        // Authentication required - redirect to login
        showToast('Session expired. Please login again.', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
    } else if (jqxhr.status === 403) {
        // Forbidden
        showToast('Access denied. Insufficient permissions.', 'danger');
    } else if (jqxhr.status === 500) {
        // Server error
        const response = jqxhr.responseJSON || {};
        showToast(response.message || 'Server error occurred. Please try again.', 'danger');
    }
});

// Export functions to global scope
window.logout = logout;
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.formatDate = formatDate;
window.copyToClipboard = copyToClipboard;
window.verifyService = verifyService;
window.loadUserBalance = loadUserBalance;
window.dailyCheckin = dailyCheckin;
window.redeemCode = redeemCode;
window.formatNumber = formatNumber;
window.debounce = debounce;
