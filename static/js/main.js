// Main JavaScript file for Inventory Manager

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add event listener to any real-time search inputs with class 'search-input'
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
    
    // Handle mobile-specific behavior
    setupMobileNavigation();
});

// Debounce function to prevent excessive API calls during search
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

// Function to handle search input changes
function handleSearch(e) {
    const searchValue = e.target.value.trim();
    const resultsContainer = document.getElementById(e.target.dataset.results);
    const isInventorySearch = e.target.id === 'inventorySearch';
    
    if (!resultsContainer) return;
    
    if (searchValue.length < 1) {
        resultsContainer.innerHTML = '';
        return;
    }
    
    // Fetch search results from API
    fetch(`/api/products/search?q=${encodeURIComponent(searchValue)}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                resultsContainer.innerHTML = '<div class="alert alert-info">No products found</div>';
                return;
            }
            
            let html = '<div class="list-group">';
            data.forEach(product => {
                // Different URL and display based on which search is being used
                const url = isInventorySearch ? 
                    `/inventory/edit/${product.id}` : 
                    `/sales/sell/${product.id}`;
                
                const quantityDisplay = product.quantity > 0 ? 
                    `<span class="badge rounded-pill ${product.quantity < 5 ? 'bg-danger' : product.quantity < 10 ? 'bg-warning' : 'bg-success'}">${product.quantity}</span>` : 
                    '<span class="badge bg-danger">Out of stock</span>';
                
                html += `
                <a href="${url}" class="list-group-item list-group-item-action bg-dark">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">${product.name}</h5>
                        <small>$${product.price.toFixed(2)}</small>
                    </div>
                    <p class="mb-1">In stock: ${quantityDisplay}</p>
                </a>`;
            });
            html += '</div>';
            
            resultsContainer.innerHTML = html;
            
            // Add click event for search buttons
            if (isInventorySearch) {
                document.getElementById('inventorySearchButton').addEventListener('click', function() {
                    if (data.length > 0) {
                        window.location.href = `/inventory/edit/${data[0].id}`;
                    }
                });
            } else {
                document.getElementById('searchButton').addEventListener('click', function() {
                    if (data.length > 0 && data[0].quantity > 0) {
                        window.location.href = `/sales/sell/${data[0].id}`;
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
            resultsContainer.innerHTML = '<div class="alert alert-danger">Error fetching results</div>';
        });
}

// Function to enhance mobile navigation experience
function setupMobileNavigation() {
    // Close navbar dropdown/collapse when an item is clicked on mobile
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbarCollapse) return;
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                bsCollapse.toggle();
            }
        });
    });
    
    // Add swipe gestures for mobile if needed
    if ('ontouchstart' in window) {
        enableSwipeNavigation();
    }
}

// Function to enable swipe navigation on mobile devices
function enableSwipeNavigation() {
    let touchstartX = 0;
    let touchendX = 0;
    
    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    }, false);
    
    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        handleSwipeGesture();
    }, false);
    
    function handleSwipeGesture() {
        const swipeThreshold = 100; // Minimum pixels for a swipe
        
        // Swipe right (to open drawer/menu)
        if (touchendX - touchstartX > swipeThreshold) {
            const navbarToggler = document.querySelector('.navbar-toggler');
            const navbarCollapse = document.querySelector('.navbar-collapse');
            
            if (navbarToggler && navbarCollapse && !navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        }
        
        // Swipe left (to close drawer/menu)
        if (touchstartX - touchendX > swipeThreshold) {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                bsCollapse.toggle();
            }
        }
    }
}
