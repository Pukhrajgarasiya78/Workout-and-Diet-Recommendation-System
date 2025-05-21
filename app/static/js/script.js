// Common JavaScript functions for the application

// Flash message handling
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
        form.reportValidity();
        return false;
    }
    return true;
}

// Number input validation
function validateNumberInput(input, min = 0, max = null) {
    let value = parseInt(input.value);
    if (isNaN(value) || value < min || (max !== null && value > max)) {
        input.value = min;
    }
}

// Format numbers with commas
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Update progress bars
function updateProgressBar(elementId, current, total) {
    const progressBar = document.getElementById(elementId);
    if (progressBar) {
        const percentage = Math.min((current / total) * 100, 100);
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
    }
}

// Serialize form data to JSON
function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};
    
    // Handle arrays (for food items)
    const arrays = {};
    
    for (let [key, value] of formData.entries()) {
        if (key.endsWith('[]')) {
            const arrayName = key.slice(0, -2);
            if (!arrays[arrayName]) {
                arrays[arrayName] = [];
            }
            arrays[arrayName].push(value);
        } else {
            data[key] = value;
        }
    }
    
    // Add arrays to data
    Object.assign(data, arrays);
    return data;
}

// Initialize meal logging
document.addEventListener('DOMContentLoaded', function() {
    const logMealForm = document.getElementById('logMealForm');
    if (logMealForm) {
        logMealForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!validateForm('logMealForm')) return;
            
            const data = serializeForm(this);
            
            fetch('/log-meal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert('Meal logged successfully!');
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('logMealModal'));
                    modal.hide();
                    // Refresh page to update stats
                    location.reload();
                } else {
                    showAlert(data.message || 'Error logging meal', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred while logging the meal', 'danger');
            });
        });
    }
    
    // Add more food items button
    const addMoreFoodBtn = document.getElementById('addMoreFood');
    if (addMoreFoodBtn) {
        addMoreFoodBtn.addEventListener('click', function() {
            const template = document.querySelector('.food-entry').cloneNode(true);
            template.querySelectorAll('input').forEach(input => input.value = '');
            document.getElementById('foodEntries').appendChild(template);
        });
    }
});

// Initialize workout logging
document.addEventListener('DOMContentLoaded', function() {
    const logWorkoutForm = document.getElementById('logWorkoutForm');
    if (logWorkoutForm) {
        logWorkoutForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!validateForm('logWorkoutForm')) return;
            
            const data = serializeForm(this);
            
            fetch('/log-workout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert('Workout logged successfully!');
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('logWorkoutModal'));
                    modal.hide();
                    // Refresh page to update stats
                    location.reload();
                } else {
                    showAlert(data.message || 'Error logging workout', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred while logging the workout', 'danger');
            });
        });
    }
}); 