/**
 * Main JavaScript file for the Synthetic Healthcare Data Viewer
 * Contains common functions and utilities used across the application
 */

// Format currency values
function formatCurrency(value) {
    if (value === undefined || value === null) return 'N/A';
    return '$' + parseFloat(value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// Format dates
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // Return original if invalid
    return date.toLocaleDateString();
}

// Format risk scores with appropriate color coding
function formatRiskScore(score) {
    if (score === undefined || score === null) return 'N/A';
    
    const numericScore = parseFloat(score).toFixed(2);
    let badgeClass = 'bg-success';
    let riskLevel = 'Low';
    
    if (numericScore > 0.7) {
        badgeClass = 'bg-danger';
        riskLevel = 'High';
    } else if (numericScore > 0.4) {
        badgeClass = 'bg-warning';
        riskLevel = 'Medium';
    }
    
    return `<span class="badge ${badgeClass}" title="${riskLevel} Risk">${numericScore}</span>`;
}

// Format medication adherence scores (inverse of risk scores)
function formatAdherenceScore(score) {
    if (score === undefined || score === null) return 'N/A';
    
    const numericScore = parseFloat(score).toFixed(2);
    let badgeClass = 'bg-danger';
    let adherenceLevel = 'Poor';
    
    if (numericScore > 0.7) {
        badgeClass = 'bg-success';
        adherenceLevel = 'Good';
    } else if (numericScore > 0.4) {
        badgeClass = 'bg-warning';
        adherenceLevel = 'Fair';
    }
    
    return `<span class="badge ${badgeClass}" title="${adherenceLevel} Adherence">${numericScore}</span>`;
}

// Format status badges
function formatStatusBadge(status, type) {
    if (!status) return 'N/A';
    
    let badgeClass = 'bg-secondary';
    let statusText = status;
    
    // Normalize status to lowercase for comparison
    const statusLower = status.toLowerCase();
    
    // Claim status badges
    if (type === 'claim') {
        if (statusLower === 'paid') badgeClass = 'bg-success';
        else if (statusLower === 'denied') badgeClass = 'bg-danger';
        else if (statusLower === 'pending') badgeClass = 'bg-warning';
        else if (statusLower === 'in process') badgeClass = 'bg-info';
    }
    // Authorization status badges
    else if (type === 'auth') {
        if (statusLower === 'approved') badgeClass = 'bg-success';
        else if (statusLower === 'denied') badgeClass = 'bg-danger';
        else if (statusLower === 'pending' || statusLower === 'submitted') badgeClass = 'bg-warning';
        else if (statusLower === 'in review') badgeClass = 'bg-info';
        else if (statusLower === 'appealed') badgeClass = 'bg-warning text-dark';
        else if (statusLower === 'additional_info_needed' || statusLower.includes('info')) badgeClass = 'bg-info';
    }
    // Care plan status badges
    else if (type === 'care_plan') {
        if (statusLower === 'active') badgeClass = 'bg-success';
        else if (statusLower === 'completed') badgeClass = 'bg-info';
        else if (statusLower === 'cancelled') badgeClass = 'bg-danger';
        else if (statusLower === 'draft') badgeClass = 'bg-secondary';
    }
    // Default status badges
    else {
        if (statusLower.includes('active') ||
            statusLower.includes('approved') ||
            statusLower.includes('complete')) {
            badgeClass = 'bg-success';
        } else if (statusLower.includes('denied') ||
                  statusLower.includes('cancelled') ||
                  statusLower.includes('rejected')) {
            badgeClass = 'bg-danger';
        } else if (statusLower.includes('pending') ||
                  statusLower.includes('in process') ||
                  statusLower.includes('submitted')) {
            badgeClass = 'bg-warning';
        } else if (statusLower.includes('info') ||
                  statusLower.includes('review')) {
            badgeClass = 'bg-info';
        }
    }
    
    // Format status text for display (capitalize first letter of each word)
    if (statusLower === 'additional_info_needed') {
        statusText = 'Additional Info Needed';
    } else {
        statusText = status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    return `<span class="badge ${badgeClass}">${statusText}</span>`;
}

// Truncate text with ellipsis
function truncateText(text, maxLength = 50) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Get URL parameter by name
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Show loading spinner
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center my-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${message}</p>
            </div>
        `;
    }
}

// Show error message
function showError(elementId, message = 'An error occurred. Please try again.') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger my-3">
                <i class="fas fa-exclamation-circle me-2"></i> ${message}
            </div>
        `;
    }
}

// Initialize DataTables with common settings
function initDataTable(tableId, options = {}) {
    const defaultOptions = {
        pageLength: 25,
        responsive: true,
        autoWidth: false,
        columnDefs: [
            {
                targets: '_all',
                defaultContent: 'N/A'
            }
        ],
        language: {
            search: "Filter:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    };
    
    // Count the number of columns in the table header
    const columnCount = $(`#${tableId} thead th`).length;
    
    // Ensure columns array matches the number of columns in the table
    if (options.columns && options.columns.length !== columnCount) {
        console.warn(`DataTable column count mismatch: Table has ${columnCount} columns, but options specify ${options.columns.length} columns.`);
        
        // Adjust columns array to match table
        if (options.columns.length < columnCount) {
            // Add missing columns
            for (let i = options.columns.length; i < columnCount; i++) {
                options.columns.push({ data: null, defaultContent: 'N/A' });
            }
        } else if (options.columns.length > columnCount) {
            // Remove extra columns
            options.columns = options.columns.slice(0, columnCount);
        }
    }
    
    const mergedOptions = {...defaultOptions, ...options};
    return $('#' + tableId).DataTable(mergedOptions);
}

// Document ready function
$(document).ready(function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});