// static/js/main.js

$(document).ready(function() {
    // Select essential DOM elements
    const modalContainer = $('#modal-container'); // The background overlay
    const modalContent = $('#modal-content'); // The inner box
    const modalBody = $('#modal-body');       // Where the form HTML is inserted
    const closeModalBtn = $('#close-modal-btn'); // The close button (X)

    // --- A. Handle Opening the Modal (Intercepts Click) ---
    // Listens for clicks on any element with the class 'modal-trigger'
    $(document).on('click', '.modal-trigger', function() {
        const url = $(this).data('modal-url'); // Get the URL from the button's data attribute

        // 1. Prepare and show the container
        modalBody.html('<p style="text-align: center;">Loading...</p>');
        modalContainer.show(); 
        
        // Optional: Fade in the inner content slightly delayed for smoother look
        modalContent.hide().fadeIn(150); 

        // 2. Send AJAX GET request to fetch the form HTML
        $.get(url, function(data) {
            // Success: Insert the fetched HTML into the modal body
            modalBody.html(data); 
        })
        .fail(function(jqXHR) {
            // Error: Handle cases where the Flask route returns 404/500
            let errorMsg = 'Error loading form. Please check the URL and server logs.';
            if (jqXHR.responseJSON && jqXHR.responseJSON.error) {
                errorMsg = jqXHR.responseJSON.error;
            }
            modalBody.html('<p style="color: red;">' + errorMsg + '</p>');
        });
    });

    // --- B. Handle Closing the Modal ---
    
    // 1. Close when the 'X' button is clicked
    closeModalBtn.on('click', function() {
        modalContainer.hide();
        modalBody.empty(); // Clear content to reset the form state
    });

    // 2. Close when the user clicks anywhere on the dark background (outside the content box)
    modalContainer.on('click', function(e) {
        // If the click target is the container itself, not a child element
        if (e.target.id === 'modal-container') {
            modalContainer.hide();
            modalBody.empty();
        }
    });


    // --- C. Handle Form Submission (Intercepts POST) ---
    // Listens for submission on the form with id="ajax-form", which is dynamically added to modalBody
    $(document).on('submit', '#ajax-form', function(e) {
        e.preventDefault(); // STOP the browser from submitting the form normally (prevent page reload)

        const form = $(this);
        const url = form.attr('action'); // Get the POST endpoint URL
        const formErrorsDiv = $('#form-errors');
        formErrorsDiv.empty(); // Clear previous errors

        // 1. Send AJAX POST request with form data
        $.ajax({
            type: form.attr('method'), 
            url: url,
            data: form.serialize(), // Includes all form data, including the CSRF token
            
            success: function(response) {
                // SUCCESS: Flask route returned 200 OK
                if (response.success) {
                    modalContainer.hide();
                    
                    // Simple way to show a success message:
                    //alert('Action successful! Reloading page to show updates.'); 
                    
                    // Reload the page to display the updated data and clear flash messages
                    window.location.reload(); 
                }
            },
            
            error: function(jqXHR) {
                // FAILURE: Flask route returned HTTP 400 (Validation Error) or 500 (DB Error)
                
                if (jqXHR.status === 400 && jqXHR.responseJSON && jqXHR.responseJSON.errors) {
                    // Validation Errors (from Flask-WTF)
                    let errorHtml = '<ul>';
                    // Loop through the dictionary of errors (e.g., {'name': ['This field is required.']})
                    for (let field in jqXHR.responseJSON.errors) {
                        jqXHR.responseJSON.errors[field].forEach(error => {
                            // Capitalize the field name for display
                            const fieldName = field.charAt(0).toUpperCase() + field.slice(1);
                            errorHtml += `<li><strong>${fieldName}</strong>: ${error}</li>`;
                        });
                    }
                    errorHtml += '</ul>';
                    formErrorsDiv.html(errorHtml); // Display errors inside the form
                } 
                else if (jqXHR.status === 500 && jqXHR.responseJSON && jqXHR.responseJSON.error) {
                    // Database or Server Error (500)
                     formErrorsDiv.html(`<ul><li>Server Error: ${jqXHR.responseJSON.error}</li></ul>`);
                }
                else {
                    // General AJAX or unexpected error
                    alert('An unknown error occurred. Please try again.');
                }
            }
        });
    });
});