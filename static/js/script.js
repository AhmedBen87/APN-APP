
// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // ===== Form validation =====
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // ===== Search flow logic =====
    
    // Step 1: Customer Selection
    const customerButtons = document.querySelectorAll('.customer-btn');
    const customerInput = document.getElementById('customerInput');
    const carlineSelection = document.getElementById('carlineSelection');
    
    customerButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Reset previously selected buttons
            customerButtons.forEach(btn => {
                btn.classList.remove('active', 'btn-primary');
                btn.classList.add('btn-outline-primary');
            });
            
            // Mark this button as selected
            this.classList.remove('btn-outline-primary');
            this.classList.add('active', 'btn-primary');
            
            // Store selected customer value
            const selectedCustomer = this.getAttribute('data-customer');
            customerInput.value = selectedCustomer;
            
            // Fetch car lines for this customer
            fetchCarLines(selectedCustomer);
            
            // Show car line selection
            carlineSelection.classList.remove('d-none');
            
            // Hide CP input until car line is selected
            document.getElementById('cpInputSection').classList.add('d-none');
        });
    });
    
    // Step 2: Car Line Selection - Fetch car lines for selected customer
    function fetchCarLines(customer) {
        fetch(`/get_carlines/${encodeURIComponent(customer)}`)
            .then(response => response.json())
            .then(carlines => {
                const carlineButtons = document.getElementById('carlineButtons');
                carlineButtons.innerHTML = '';
                
                // Create button for each car line
                carlines.forEach(carline => {
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'btn btn-outline-secondary carline-btn';
                    button.setAttribute('data-carline', carline);
                    button.textContent = carline;
                    
                    button.addEventListener('click', function() {
                        // Reset previously selected buttons
                        const allCarlineButtons = document.querySelectorAll('.carline-btn');
                        allCarlineButtons.forEach(btn => {
                            btn.classList.remove('active', 'btn-secondary');
                            btn.classList.add('btn-outline-secondary');
                        });
                        
                        // Mark this button as selected
                        this.classList.remove('btn-outline-secondary');
                        this.classList.add('active', 'btn-secondary');
                        
                        // Store selected car line value
                        document.getElementById('carlineInput').value = carline;
                        
                        // Show CP input section
                        document.getElementById('cpInputSection').classList.remove('d-none');
                        
                        // Initialize CP input autocomplete
                        const cpInput = document.getElementById('cpName');
                        const suggestionsList = document.createElement('ul');
                        suggestionsList.className = 'suggestions-list list-group position-absolute w-100 d-none';
                        cpInput.parentNode.style.position = 'relative';
                        cpInput.parentNode.appendChild(suggestionsList);
                        
                        let typingTimer;
                        cpInput.addEventListener('input', function() {
                            clearTimeout(typingTimer);
                            const searchTerm = this.value.trim();
                            
                            if (searchTerm.length < 1) {
                                suggestionsList.classList.add('d-none');
                                return;
                            }
                            
                            typingTimer = setTimeout(() => {
                                fetch(`/search_suggestions?customer=${customerInput.value}&carline=${carline}&term=${searchTerm}`)
                                    .then(response => response.json())
                                    .then(suggestions => {
                                        suggestionsList.innerHTML = '';
                                        if (suggestions.length > 0) {
                                            suggestions.forEach(suggestion => {
                                                const li = document.createElement('li');
                                                li.className = 'list-group-item list-group-item-action';
                                                li.textContent = suggestion.cp;
                                                li.addEventListener('click', () => {
                                                    cpInput.value = suggestion.cp;
                                                    suggestionsList.classList.add('d-none');
                                                });
                                                suggestionsList.appendChild(li);
                                            });
                                            suggestionsList.classList.remove('d-none');
                                        } else {
                                            suggestionsList.classList.add('d-none');
                                        }
                                    });
                            }, 300);
                        });
                        
                        // Hide suggestions when clicking outside
                        document.addEventListener('click', (e) => {
                            if (!cpInput.contains(e.target) && !suggestionsList.contains(e.target)) {
                                suggestionsList.classList.add('d-none');
                            }
                        });
                    });
                    
                    carlineButtons.appendChild(button);
                });
                
                if (carlines.length === 0) {
                    const noCarlineMsg = document.createElement('div');
                    noCarlineMsg.className = 'alert alert-warning';
                    noCarlineMsg.textContent = 'No car lines found for this customer.';
                    carlineButtons.appendChild(noCarlineMsg);
                }
            })
            .catch(error => {
                console.error('Error fetching car lines:', error);
                const carlineButtons = document.getElementById('carlineButtons');
                carlineButtons.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error loading car lines. Please try again.
                    </div>
                `;
            });
    }
});
