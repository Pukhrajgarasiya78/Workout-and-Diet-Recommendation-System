$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add fade-in animation to cards
    $('.card').addClass('fade-in');

    // Format numbers with commas
    $('.format-number').each(function() {
        var num = $(this).text();
        $(this).text(Number(num).toLocaleString());
    });

    // Auto-resize textareas
    $('textarea').on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Confirm dangerous actions
    $('[data-confirm]').on('click', function(e) {
        if (!confirm($(this).data('confirm'))) {
            e.preventDefault();
        }
    });

    // Handle form validation
    $('form').on('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });

    // Show loading spinner on form submit
    $('form').on('submit', function() {
        if (this.checkValidity()) {
            $(this).find('[type="submit"]').html(`
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Loading...
            `).prop('disabled', true);
        }
    });

    // Handle AJAX errors
    $(document).ajaxError(function(event, jqXHR, settings, error) {
        var message = 'An error occurred. Please try again.';
        if (jqXHR.responseJSON && jqXHR.responseJSON.message) {
            message = jqXHR.responseJSON.message;
        }
        showAlert('error', message);
    });

    // Show alert message
    window.showAlert = function(type, message) {
        var alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('#alerts-container').append(alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            $('.alert').alert('close');
        }, 5000);
    };

    // Handle mobile menu
    $('.navbar-toggler').on('click', function() {
        $('.navbar-collapse').toggleClass('show');
    });

    // Smooth scroll to top
    $('.scroll-to-top').on('click', function(e) {
        e.preventDefault();
        $('html, body').animate({scrollTop: 0}, 'smooth');
    });

    // Handle modal forms
    $('.modal form').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var modal = form.closest('.modal');
        var submitBtn = form.find('[type="submit"]');
        var originalBtnText = submitBtn.html();

        submitBtn.html(`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Saving...
        `).prop('disabled', true);

        $.ajax({
            url: form.attr('action'),
            type: form.attr('method') || 'POST',
            data: form.serialize(),
            success: function(response) {
                if (response.status === 'success') {
                    modal.modal('hide');
                    showAlert('success', response.message || 'Changes saved successfully!');
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    } else {
                        location.reload();
                    }
                } else {
                    showAlert('error', response.message || 'An error occurred. Please try again.');
                }
            },
            error: function() {
                showAlert('error', 'An error occurred. Please try again.');
            },
            complete: function() {
                submitBtn.html(originalBtnText).prop('disabled', false);
            }
        });
    });

    // Handle file inputs
    $('.custom-file-input').on('change', function() {
        var fileName = $(this).val().split('\\').pop();
        $(this).next('.custom-file-label').html(fileName);
    });

    // Handle dynamic form fields
    $('.add-field').on('click', function() {
        var template = $($(this).data('template')).html();
        var container = $($(this).data('container'));
        container.append(template);
    });

    $('.remove-field').on('click', function() {
        $(this).closest('.field-group').remove();
    });

    // Handle tabs with AJAX content
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        var target = $(e.target).attr('href');
        var url = $(e.target).data('url');
        
        if (url && !$(target).data('loaded')) {
            $(target).load(url, function() {
                $(target).data('loaded', true);
            });
        }
    });
}); 