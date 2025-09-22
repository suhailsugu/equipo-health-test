// Main JavaScript functionality for Consultation Report Generator

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form functionality
    initializeFormHandlers();
    initializeCharacterCounters();
    initializeLogoPreview();
    initializeFormValidation();
    initializeFormattingTools();
});

function initializeFormHandlers() {
    const form = document.getElementById('consultationForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (form && submitBtn) {
        form.addEventListener('submit', function(e) {
            // Add loading state to button
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            
            // Re-enable after 10 seconds (fallback)
            setTimeout(() => {
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
            }, 10000);
        });
    }
}

function initializeCharacterCounters() {
    // Character counters for textareas
    const textareas = [
        { element: 'id_chief_complaint', counter: 'complaintCount', limit: 5000 },
        { element: 'id_consultation_note', counter: 'noteCount', limit: 5000 }
    ];
    
    textareas.forEach(config => {
        const textarea = document.getElementById(config.element);
        const counter = document.getElementById(config.counter);
        
        if (textarea && counter) {
            // Initial count
            updateCharCount(textarea, counter, config.limit);
            
            // Update on input
            textarea.addEventListener('input', () => 
                updateCharCount(textarea, counter, config.limit)
            );
            
            // Update on paste
            textarea.addEventListener('paste', () => 
                setTimeout(() => updateCharCount(textarea, counter, config.limit), 0)
            );
        }
    });
}

function updateCharCount(textarea, counter, limit) {
    const count = textarea.value.length;
    counter.textContent = count.toLocaleString();
    
    // Update styling based on character count
    const parent = counter.parentElement;
    parent.classList.remove('warning', 'danger');
    
    if (count > limit * 0.9) {
        parent.classList.add('danger');
    } else if (count > limit * 0.8) {
        parent.classList.add('warning');
    }
    
    // Prevent exceeding limit
    if (count > limit) {
        textarea.value = textarea.value.substring(0, limit);
        counter.textContent = limit.toLocaleString();
        parent.classList.add('danger');
        
        // Show warning
        showTemporaryMessage('Character limit reached!', 'warning');
    }
}

function initializeLogoPreview() {
    const logoInput = document.getElementById('id_clinic_logo');
    const logoPreview = document.getElementById('logoPreview');
    const logoImage = document.getElementById('logoImage');
    
    if (logoInput && logoPreview && logoImage) {
        logoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Validate file type
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    showTemporaryMessage('Please select a valid image file (JPEG, PNG, GIF, or WebP)', 'error');
                    logoInput.value = '';
                    logoPreview.style.display = 'none';
                    return;
                }
                
                // Validate file size (5MB limit)
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    showTemporaryMessage('File size cannot exceed 5MB', 'error');
                    logoInput.value = '';
                    logoPreview.style.display = 'none';
                    return;
                }
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    logoImage.src = e.target.result;
                    logoPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                logoPreview.style.display = 'none';
            }
        });
    }
}

function initializeFormValidation() {
    const form = document.getElementById('consultationForm');
    
    if (form) {
        // Real-time validation for contact fields
        const contactFields = ['id_physician_contact', 'id_patient_contact'];
        
        contactFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', () => validateContactField(field));
                field.addEventListener('input', () => clearFieldErrors(field));
            }
        });
        
        // Date validation
        const dobField = document.getElementById('id_patient_dob');
        if (dobField) {
            dobField.addEventListener('change', () => validateDateField(dobField));
        }
        
        // Required field validation
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', () => validateRequiredField(field));
            field.addEventListener('input', () => clearFieldErrors(field));
        });
    }
}

function validateContactField(field) {
    const value = field.value.trim();
    if (value && !isValidContact(value)) {
        showFieldError(field, 'Please enter a valid email address or phone number');
        return false;
    }
    clearFieldErrors(field);
    return true;
}

function validateDateField(field) {
    const value = field.value;
    if (value) {
        const selectedDate = new Date(value);
        const today = new Date();
        
        if (selectedDate > today) {
            showFieldError(field, 'Date of birth cannot be in the future');
            return false;
        }
        
        // Check if date is reasonable (not too old)
        const hundredYearsAgo = new Date();
        hundredYearsAgo.setFullYear(today.getFullYear() - 120);
        
        if (selectedDate < hundredYearsAgo) {
            showFieldError(field, 'Please enter a valid date of birth');
            return false;
        }
    }
    clearFieldErrors(field);
    return true;
}

function validateRequiredField(field) {
    const value = field.value.trim();
    if (!value) {
        showFieldError(field, `${getFieldLabel(field)} is required`);
        return false;
    }
    clearFieldErrors(field);
    return true;
}

function isValidContact(contact) {
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailRegex.test(contact)) {
        return true;
    }
    
    // Phone validation (flexible pattern)
    const phoneRegex = /^[\+]?[1-9][\d\s\-\(\)]{9,}$/;
    const cleanPhone = contact.replace(/[\s\-\(\)]/g, '');
    return phoneRegex.test(cleanPhone);
}

function showFieldError(field, message) {
    clearFieldErrors(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i>${message}`;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldErrors(field) {
    field.classList.remove('is-invalid');
    
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
}

function getFieldLabel(field) {
    const label = field.parentNode.querySelector('label');
    return label ? label.textContent.replace('*', '').trim() : 'This field';
}

function initializeFormattingTools() {
    const formatButtons = document.querySelectorAll('.format-btn');
    
    formatButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const format = this.dataset.format;
            const targetId = this.dataset.target;
            const textarea = document.getElementById(`id_${targetId}`);
            
            if (textarea) {
                applyFormatting(textarea, format);
            }
        });
    });
}

function applyFormatting(textarea, format) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    if (selectedText.length === 0) {
        showTemporaryMessage('Please select text to format', 'info');
        return;
    }
    
    let formattedText = selectedText;
    
    switch (format) {
        case 'bold':
            formattedText = `**${selectedText}**`;
            break;
        case 'italic':
            formattedText = `*${selectedText}*`;
            break;
        default:
            return;
    }
    
    // Replace selected text with formatted text
    const newText = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
    textarea.value = newText;
    
    // Update character count if applicable
    textarea.dispatchEvent(new Event('input'));
    
    // Restore focus and selection
    setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start, start + formattedText.length);
    }, 0);
    
    showTemporaryMessage(`Applied ${format} formatting`, 'success');
}

function showTemporaryMessage(message, type = 'info') {
    // Remove existing temporary messages
    const existingMessages = document.querySelectorAll('.temp-message');
    existingMessages.forEach(msg => msg.remove());
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} temp-message`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
    `;
    
    // Insert at top of form
    const form = document.getElementById('consultationForm');
    if (form) {
        form.insertBefore(alertDiv, form.firstChild);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}

function getIconForType(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'warning': return 'exclamation-triangle';
        case 'error': 
        case 'danger': return 'exclamation-circle';
        default: return 'info-circle';
    }
}

// Utility functions
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

// Export functions for potential use in other scripts
window.ConsultationReportApp = {
    validateContactField,
    validateDateField,
    validateRequiredField,
    showTemporaryMessage,
    applyFormatting
};