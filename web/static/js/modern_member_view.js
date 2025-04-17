/**
 * JavaScript for the Modern Member View page
 * Handles loading and displaying member data in the tabbed interface
 * with enhanced visualizations and UI improvements
 */

// Helper functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
}

function formatCurrency(amount) {
    if (amount === undefined || amount === null) return 'N/A';
    return '$' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

function initDataTable(tableId, options = {}) {
    const defaultOptions = {
        pageLength: 10,
        lengthMenu: [5, 10, 25, 50],
        responsive: true,
        language: {
            search: "Filter:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    };
    
    const mergedOptions = {...defaultOptions, ...options};
    return $(`#${tableId}`).DataTable(mergedOptions);
}

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

// Global variables to store data for each tab
let globalMemberData = {};
let globalSdohAssessments = [];
let globalRiskAssessments = [];
let globalPharmacyClaims = [];

$(document).ready(function() {
    // Check if there's an error passed from the server
    const serverError = document.getElementById('server-error');
    if (serverError && serverError.value) {
        $('#member-profile-container').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i> ${serverError.value}
            </div>
        `);
        return;
    }

    // Get member ID from URL path
    let memberId = window.location.pathname.split('/').pop();
    
    // If not found in path, try query parameter
    if (!memberId || memberId === 'member') {
        memberId = getUrlParameter('id');
    }
    
    if (!memberId) {
        $('#member-profile-container').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i> No member ID specified.
            </div>
        `);
        return;
    }
    
    // Update URL if needed for consistency
    if (window.location.pathname.indexOf(memberId) === -1) {
        history.replaceState(null, null, `/member/${memberId}`);
    }
    
    // Show loading indicator
    const loadingIndicator = `
        <div class="text-center my-5">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading member data...</p>
        </div>
    `;
    $('#member-profile-container').html(loadingIndicator);
    
    // Load member data with timeout
    const dataRequest = $.ajax({
        url: `/api/member/${memberId}/related`,
        type: 'GET',
        dataType: 'json',
        timeout: 30000 // 30 second timeout
    });
    
    dataRequest.done(function(data) {
        if (data.error) {
            $('#member-profile-container').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i> ${data.error}: ${data.message}
                </div>
            `);
            return;
        }
        
        // Store data in global variables
        globalMemberData = data;
        globalSdohAssessments = data.sdoh_assessments || [];
        globalRiskAssessments = data.risk_assessments || [];
        globalPharmacyClaims = data.pharmacy_claims || [];
        
        console.log("Data loaded:", data);
        console.log("SDOH Assessments:", globalSdohAssessments);
        console.log("Risk Assessments:", globalRiskAssessments);
        console.log("Pharmacy Claims:", globalPharmacyClaims);
        
        renderMemberProfile(data);
        renderOverviewTab(data);
        renderClaimsTab(data.claims || []);
        renderAuthorizationsTab(data.authorizations || []);
        loadAndRenderEOBs(memberId);
        renderClinicalNotesTab(data.clinical_notes || []);
        renderClinicalEncountersTab(data.clinical_encounters || []);
        renderCarePlansTab(data.care_plans || []);
        renderCommunicationsTab(data.communications || []);
        loadAndRenderPatientData(memberId);
        renderCareEpisodesTab(data.care_episodes || []);
        renderSdohTab(globalSdohAssessments);
        renderRiskTab(globalRiskAssessments);
        renderPharmacyTab(globalPharmacyClaims);
        
        // Update tab counts - use a more direct approach
        console.log("Updating tab counts...");
        
        // Add some debugging to see what's happening
        console.log("Claims count:", data.claims ? data.claims.length : 0);
        
        // Try a different approach - directly set the text with parentheses
        $('#claims-tab').text(`Claims (${data.claims ? data.claims.length : 0})`);
        $('#authorizations-tab').text(`Authorizations (${data.authorizations ? data.authorizations.length : 0})`);
        $('#clinical-notes-tab').text(`Clinical Notes (${data.clinical_notes ? data.clinical_notes.length : 0})`);
        $('#clinical-encounters-tab').text(`Clinical Encounters (${data.clinical_encounters ? data.clinical_encounters.length : 0})`);
        $('#care-plans-tab').text(`Care Plans (${data.care_plans ? data.care_plans.length : 0})`);
        $('#communications-tab').text(`Communications (${data.communications ? data.communications.length : 0})`);
        $('#care-episodes-tab').text(`Care Episodes (${data.care_episodes ? data.care_episodes.length : 0})`);
        $('#sdoh-tab').text(`SDOH (${data.sdoh_assessments ? data.sdoh_assessments.length : 0})`);
        $('#risk-tab').text(`Risk Assessment (${data.risk_assessments ? data.risk_assessments.length : 0})`);
        $('#pharmacy-tab').text(`Pharmacy Claims (${data.pharmacy_claims ? data.pharmacy_claims.length : 0})`);
        $('#eobs-tab').text(`EOBs (${data.eobs ? data.eobs.length : 0})`);
        $('#patient-data-tab').text(`Patient Data (${data.patient_generated_data ? data.patient_generated_data.length : 0})`);
        
        // Log after update to confirm
        console.log("Tab counts updated. Claims tab text is now:", $('#claims-tab').text());
    }).fail(function(jqXHR, textStatus, errorThrown) {
        let errorMessage = 'Failed to load member data.';
        if (textStatus === 'timeout') {
            errorMessage = 'Request timed out. The server took too long to respond.';
        } else if (jqXHR.status === 404) {
            errorMessage = 'Member not found.';
        } else if (jqXHR.status === 500) {
            errorMessage = 'Server error. Please try again later.';
        }
        
        $('#member-profile-container').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i> ${errorMessage}
                <hr>
                <p class="mb-0">Error details: ${textStatus} - ${errorThrown}</p>
            </div>
        `);
    });
    
    // Function to render member profile with improved design
    function renderMemberProfile(data) {
        const member = data.member;
        
        // Format dates
        const dob = new Date(member.date_of_birth);
        const formattedDob = dob.toLocaleDateString();
        
        // Calculate risk level classes
        let clinicalRiskClass = 'success';
        let riskLevel = 'Low';
        if (member.risk_score !== undefined) {
            const clinicalRisk = parseFloat(member.risk_score);
            if (clinicalRisk > 0.7) {
                clinicalRiskClass = 'danger';
                riskLevel = 'High';
            } else if (clinicalRisk > 0.4) {
                clinicalRiskClass = 'warning';
                riskLevel = 'Medium';
            }
        }
        
        // Build HTML for member profile
        let html = `
            <div class="member-profile-header mb-4">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h1 class="display-5 fw-bold mb-0">${member.first_name} ${member.last_name}</h1>
                        <p class="text-muted mb-2">Member ID: ${member.id}</p>
                        <div class="d-flex align-items-center">
                            <span class="badge bg-${clinicalRiskClass} me-2">Risk: ${member.risk_score !== undefined ? parseFloat(member.risk_score).toFixed(2) : 'N/A'}</span>
                            <span class="text-${clinicalRiskClass}">${riskLevel} Risk</span>
                        </div>
                    </div>
                    <div class="col-md-4 text-md-end">
                        <div class="btn-group">
                            <button class="btn btn-outline-primary">
                                <i class="fas fa-print me-2"></i> Print Profile
                            </button>
                            <button class="btn btn-outline-primary">
                                <i class="fas fa-file-export me-2"></i> Export Data
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <div class="text-center mb-4">
                                <div class="avatar-circle bg-light mb-3">
                                    <span class="initials">${member.first_name[0]}${member.last_name[0]}</span>
                                </div>
                                <h4 class="mb-1">${member.first_name} ${member.last_name}</h4>
                                <p class="text-muted mb-0">${member.age} years old</p>
                            </div>
                            
                            <div class="member-info">
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Date of Birth</span>
                                    <span class="fw-medium">${formattedDob}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Gender</span>
                                    <span class="fw-medium">${member.gender || 'N/A'}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Phone</span>
                                    <span class="fw-medium">${member.phone || 'N/A'}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Email</span>
                                    <span class="fw-medium">${member.email || 'N/A'}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2">
                                    <span class="text-muted">Address</span>
                                    <span class="fw-medium text-end">${member.address.street}<br>${member.address.city}, ${member.address.state} ${member.address.zip}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Insurance Information</h5>
                        </div>
                        <div class="card-body">
                            <div class="member-info">
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Plan</span>
                                    <span class="fw-medium">${member.insurance && member.insurance.plan_name ? member.insurance.plan_name : 'N/A'}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Member ID</span>
                                    <span class="fw-medium">${member.insurance.member_id}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Effective Date</span>
                                    <span class="fw-medium">${member.insurance && member.insurance.effective_date ? formatDate(member.insurance.effective_date) : 'N/A'}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Group Number</span>
                                    <span class="fw-medium">${member.insurance && member.insurance.group_number ? member.insurance.group_number : 'N/A'}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2">
                                    <span class="text-muted">Type</span>
                                    <span class="fw-medium">${member.insurance && member.insurance.type ? member.insurance.type : 'N/A'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Risk Assessment</h5>
                        </div>
                        <div class="card-body">
                            <div class="text-center mb-4">
                                <div class="risk-gauge">
                                    <div class="risk-gauge-value bg-${clinicalRiskClass}">
                                        <span>${member.risk_score !== undefined ? parseFloat(member.risk_score).toFixed(2) : 'N/A'}</span>
                                    </div>
                                    <div class="risk-gauge-label">${riskLevel} Risk</div>
                                </div>
                            </div>
                            
                            <div class="member-info">
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Care Gaps</span>
                                    <span class="fw-medium">${member.care_gaps ? member.care_gaps.length : 0}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                    <span class="text-muted">Recent Claims</span>
                                    <span class="fw-medium">${data.claims ? data.claims.length : 0}</span>
                                </div>
                                <div class="info-item d-flex justify-content-between py-2">
                                    <span class="text-muted">Active Care Plans</span>
                                    <span class="fw-medium">${data.care_plans ? data.care_plans.filter(plan => plan.status === 'Active').length : 0}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#member-profile-container').html(html);
        
        // Add CSS for risk gauge
        if (!document.getElementById('risk-gauge-style')) {
            const style = document.createElement('style');
            style.id = 'risk-gauge-style';
            style.innerHTML = `
                .risk-gauge {
                    position: relative;
                    width: 150px;
                    height: 150px;
                    margin: 0 auto;
                    border-radius: 50%;
                    background: #f0f0f0;
                    overflow: hidden;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                .risk-gauge-value {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: white;
                }
                .risk-gauge-label {
                    position: absolute;
                    bottom: 20px;
                    left: 0;
                    width: 100%;
                    text-align: center;
                    font-size: 1rem;
                    font-weight: 500;
                    color: white;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Function to render overview tab with enhanced visualizations
    function renderOverviewTab(data) {
        const member = data.member;
        
        let html = `
            <div class="row">
                <!-- Recent Activity Timeline -->
                <div class="col-md-8 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Recent Activity</h5>
                        </div>
                        <div class="card-body">
                            <div class="timeline">
        `;
        
        // Collect all activities
        const activities = [];
        
        // Add claims
        data.claims.forEach(claim => {
            activities.push({
                type: 'claim',
                date: new Date(claim.date_received || claim.submission_date),
                data: claim,
                icon: 'file-invoice-dollar',
                iconBg: 'bg-primary'
            });
        });
        
        // Add clinical notes
        data.clinical_notes.forEach(note => {
            activities.push({
                type: 'note',
                date: new Date(note.date),
                data: note,
                icon: 'notes-medical',
                iconBg: 'bg-info'
            });
        });
        
        // Add authorizations
        data.authorizations.forEach(auth => {
            activities.push({
                type: 'auth',
                date: new Date(auth.submission_date),
                data: auth,
                icon: 'clipboard-check',
                iconBg: 'bg-warning'
            });
        });
        
        // Sort by date (newest first)
        activities.sort((a, b) => b.date - a.date);
        
        // Take the 5 most recent activities
        const recentActivities = activities.slice(0, 5);
        
        if (recentActivities.length > 0) {
            recentActivities.forEach(activity => {
                let content = '';
                
                if (activity.type === 'claim') {
                    const claim = activity.data;
                    content = `
                        <h6 class="mb-1">Claim Submitted</h6>
                        <p class="mb-1">Claim ID: ${claim.id}</p>
                        <p class="mb-1">Provider: ${claim.provider_name || 'N/A'}</p>
                        <p class="mb-1">Amount: ${formatCurrency(claim.total_amount || claim.total_charge)}</p>
                        <p class="mb-0">Status: ${formatStatusBadge(claim.status, 'claim')}</p>
                    `;
                } else if (activity.type === 'note') {
                    const note = activity.data;
                    content = `
                        <h6 class="mb-1">Clinical Note Added</h6>
                        <p class="mb-1">Provider: ${note.provider_name || 'N/A'}</p>
                        <p class="mb-1">Type: ${note.note_type || 'N/A'}</p>
                        <p class="mb-0">${note.content ? note.content.substring(0, 100) + '...' : 'N/A'}</p>
                    `;
                } else if (activity.type === 'auth') {
                    const auth = activity.data;
                    content = `
                        <h6 class="mb-1">Authorization ${auth.status}</h6>
                        <p class="mb-1">Auth ID: ${auth.id}</p>
                        <p class="mb-1">Service: ${auth.service_description || 'N/A'}</p>
                        <p class="mb-0">Status: ${formatStatusBadge(auth.status, 'auth')}</p>
                    `;
                }
                
                html += `
                    <div class="timeline-item">
                        <div class="timeline-icon ${activity.iconBg}">
                            <i class="fas fa-${activity.icon}"></i>
                        </div>
                        <div class="timeline-content">
                            <div class="timeline-date">${activity.date.toLocaleDateString()} ${activity.date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
                            ${content}
                        </div>
                    </div>
                `;
            });
        } else {
            html += `<div class="alert alert-info">No recent activity found for this member.</div>`;
        }
        
        html += `
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Care Gaps -->
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Care Gaps</h5>
                        </div>
                        <div class="card-body">
        `;
        
        if (member.care_gaps && member.care_gaps.length > 0) {
            html += `
                <div class="table-responsive">
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Description</th>
                                <th>Type</th>
                                <th>Priority</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            member.care_gaps.forEach(gap => {
                let priorityBadge = 'bg-success';
                if (gap.priority === 'High') priorityBadge = 'bg-danger';
                else if (gap.priority === 'Medium') priorityBadge = 'bg-warning';
                
                html += `
                    <tr>
                        <td>${gap.description}</td>
                        <td>${gap.type}</td>
                        <td><span class="badge ${priorityBadge}">${gap.priority}</span></td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            html += `<div class="alert alert-info">No care gaps identified for this member.</div>`;
        }
        
        html += `
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <!-- Claims Summary -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Claims Summary</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="claimsChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Pharmacy Claims -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Pharmacy Claims</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="pharmacyChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#overview-content').html(html);
        
        // Initialize charts if data is available
        if (data.claims && data.claims.length > 0) {
            initClaimsChart(data.claims);
        }
        
        if (data.pharmacy_claims && data.pharmacy_claims.length > 0) {
            initPharmacyChart(data.pharmacy_claims);
        }
    }
    
    // Function to initialize claims chart
    function initClaimsChart(claims) {
        // Group claims by month
        const claimsByMonth = {};
        const statusCounts = {
            'Paid': 0,
            'Denied': 0,
            'Pending': 0,
            'In Process': 0
        };
        
        claims.forEach(claim => {
            // Count by status
            const status = claim.status || 'Pending';
            statusCounts[status] = (statusCounts[status] || 0) + 1;
            
            // Group by month
            const dateStr = claim.date_received || claim.submission_date;
            if (!dateStr) return;
            
            const date = new Date(dateStr);
            const monthYear = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
            
            if (!claimsByMonth[monthYear]) {
                claimsByMonth[monthYear] = {
                    total: 0,
                    amount: 0
                };
            }
            
            claimsByMonth[monthYear].total += 1;
            claimsByMonth[monthYear].amount += parseFloat(claim.total_amount || claim.total_charge || 0);
        });
        
        // Convert to arrays for chart
        const months = Object.keys(claimsByMonth).sort((a, b) => {
            return new Date(a) - new Date(b);
        });
        
        const claimCounts = months.map(month => claimsByMonth[month].total);
        const claimAmounts = months.map(month => claimsByMonth[month].amount);
        
        // Create chart
        const ctx = document.getElementById('claimsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Claim Count',
                        data: claimCounts,
                        backgroundColor: 'rgba(52, 152, 219, 0.7)',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Claim Amount ($)',
                        data: claimAmounts,
                        type: 'line',
                        fill: false,
                        backgroundColor: 'rgba(46, 204, 113, 0.7)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 2,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Claim Count'
                        }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Claim Amount ($)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }
    
    // Function to initialize pharmacy chart
    function initPharmacyChart(pharmacyClaims) {
        // Group by drug tier
        const tierCounts = {};
        
        pharmacyClaims.forEach(claim => {
            const tier = claim.drug_tier || 'Unknown';
            tierCounts[tier] = (tierCounts[tier] || 0) + 1;
        });
        
        // Convert to arrays for chart
        const tiers = Object.keys(tierCounts);
        const counts = tiers.map(tier => tierCounts[tier]);
        
        // Destroy existing chart if it exists
        const chartElement = document.getElementById('pharmacyChart');
        if (chartElement) {
            const chartInstance = Chart.getChart(chartElement);
            if (chartInstance) {
                console.log("Destroying existing pharmacy chart");
                chartInstance.destroy();
            }
        }
        
        // Create chart
        const ctx = document.getElementById('pharmacyChart').getContext('2d');
        const pharmacyChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: tiers,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.7)',
                        'rgba(46, 204, 113, 0.7)',
                        'rgba(155, 89, 182, 0.7)',
                        'rgba(241, 196, 15, 0.7)',
                        'rgba(230, 126, 34, 0.7)'
                    ],
                    borderColor: [
                        'rgba(52, 152, 219, 1)',
                        'rgba(46, 204, 113, 1)',
                        'rgba(155, 89, 182, 1)',
                        'rgba(241, 196, 15, 1)',
                        'rgba(230, 126, 34, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Pharmacy Claims by Drug Tier'
                    }
                }
            }
        });
    }
    // Implement the remaining functions
    
    // Function to render authorizations tab
    function renderAuthorizationsTab(authorizations) {
        if (authorizations.length === 0) {
            $('#authorizations-content').html('<div class="alert alert-info">No authorizations found for this member.</div>');
            return;
        }
        
        $('#authorizations-content').html(`
            <div class="table-responsive">
                <table class="table table-striped" id="authorizations-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Provider</th>
                            <th>Date Requested</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${authorizations.map(auth => `
                            <tr>
                                <td>${auth.id}</td>
                                <td>${auth.provider_id || 'N/A'}</td>
                                <td>${formatDate(auth.date_requested)}</td>
                                <td>${formatStatusBadge(auth.status, 'auth')}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-auth" data-auth-id="${auth.id}">
                                        View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `);
        
        // Initialize DataTable
        initDataTable('authorizations-table');
        
        // Add event listener for view authorization button
        $('.view-auth').on('click', function() {
            const authId = $(this).data('auth-id');
            // Find the authorization in the data
            const auth = authorizations.find(a => a.id === authId);
            if (auth) {
                renderAuthDetails(auth);
                $('#authDetailModal').modal('show');
            }
        });
    }
    
    // Function to render authorization details in modal
    function renderAuthDetails(auth) {
        let serviceLines = '';
        if (auth.service_lines && auth.service_lines.length > 0) {
            serviceLines = `
                <h5 class="mt-4">Service Lines</h5>
                <div class="table-responsive">
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Description</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${auth.service_lines.map(line => `
                                <tr>
                                    <td>${line.service_code || 'N/A'}</td>
                                    <td>${line.description || 'N/A'}</td>
                                    <td>${line.quantity || 'N/A'}</td>
                                    <td>${formatCurrency(line.unit_price)}</td>
                                    <td>${formatCurrency(line.total_price)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
        
        let diagnosisCodes = '';
        if (auth.diagnosis_codes && auth.diagnosis_codes.length > 0) {
            diagnosisCodes = `
                <h5 class="mt-4">Diagnosis Codes</h5>
                <div class="diagnosis-codes">
                    ${auth.diagnosis_codes.map(code => `
                        <span class="badge bg-info me-2 mb-2">${code}</span>
                    `).join('')}
                </div>
            `;
        }
        
        $('#auth-detail-content').html(`
            <div class="auth-detail">
                <div class="row">
                    <div class="col-md-6">
                        <h4>Authorization Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Authorization ID</span>
                            <span class="fw-medium">${auth.id}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Provider</span>
                            <span class="fw-medium">${auth.provider_id || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Date Requested</span>
                            <span class="fw-medium">${formatDate(auth.date_requested)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Status</span>
                            <span class="fw-medium">${formatStatusBadge(auth.status, 'auth')}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>Clinical Information</h4>
                        <div class="info-item py-2 border-bottom">
                            <div class="text-muted mb-1">Clinical Justification</div>
                            <div class="fw-medium">${auth.clinical_justification || 'N/A'}</div>
                        </div>
                    </div>
                </div>
                
                ${diagnosisCodes}
                ${serviceLines}
            </div>
        `);
    }
    
    // Function to load and render EOBs
    function loadAndRenderEOBs(memberId) {
        // Show loading indicator
        $('#eobs-content').html(`
            <div class="text-center my-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading EOB data...</p>
            </div>
        `);
        
        // Fetch EOB data from API
        $.getJSON(`/api/eobs`, function(allEobs) {
            console.log("Loaded all EOBs:", allEobs);
            
            // Filter EOBs for this member
            const eobs = allEobs.filter(eob => eob.member_id === memberId);
            console.log("Filtered EOBs for member:", eobs);
            
            if (!eobs || eobs.length === 0) {
                $('#eobs-content').html('<div class="alert alert-info">No EOBs found for this member.</div>');
                return;
            }
            
            let html = `
                <div class="table-responsive">
                    <table class="table table-striped" id="eobs-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Date Issued</th>
                                <th>Service Date</th>
                                <th>Provider</th>
                                <th>Total Billed</th>
                                <th>Total Plan Paid</th>
                                <th>Member Responsibility</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${eobs.map(eob => `
                                <tr>
                                    <td>${eob.id}</td>
                                    <td>${formatDate(eob.date_issued)}</td>
                                    <td>${formatDate(eob.service_date_start)}</td>
                                    <td>${eob.provider_name || 'N/A'}</td>
                                    <td>${formatCurrency(eob.total_billed)}</td>
                                    <td>${formatCurrency(eob.total_plan_paid)}</td>
                                    <td>${formatCurrency(eob.total_member_responsibility)}</td>
                                    <td>
                                        <button class="btn btn-sm btn-primary view-eob" data-eob-id="${eob.id}">
                                            View Details
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            $('#eobs-content').html(html);
            
            // Initialize DataTable
            initDataTable('eobs-table');
            
            // Add event listener for view button - use delegated event handling
            $(document).off('click', '.view-eob').on('click', '.view-eob', function() {
                console.log("EOB View button clicked");
                const eobId = $(this).data('eob-id');
                console.log("EOB ID:", eobId);
                
                // Fetch EOB details from API
                $.getJSON(`/api/eobs/${eobId}`, function(eob) {
                    console.log("Fetched EOB:", eob);
                    renderEobDetails(eob);
                    $('#eobDetailModal').modal('show');
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    console.error("Error fetching EOB:", textStatus, errorThrown);
                    alert("Error loading EOB details. Please try again.");
                });
            });
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.error("Error loading EOBs:", textStatus, errorThrown);
            $('#eobs-content').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i> Error loading EOB data: ${textStatus}
                </div>
            `);
        });
    }
    
    // Function to render EOB details
    function renderEobDetails(eob) {
        let detailsHtml = `
            <div class="eob-detail">
                <div class="row">
                    <div class="col-md-6">
                        <h4>EOB Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">ID</span>
                            <span class="fw-medium">${eob.id}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Date Issued</span>
                            <span class="fw-medium">${formatDate(eob.date_issued)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Service Date</span>
                            <span class="fw-medium">${formatDate(eob.service_date_start)}${eob.service_date_end && eob.service_date_end !== eob.service_date_start ? ' to ' + formatDate(eob.service_date_end) : ''}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Provider</span>
                            <span class="fw-medium">${eob.provider_name || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Claim ID</span>
                            <span class="fw-medium">${eob.claim_id || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>Financial Summary</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Total Billed</span>
                            <span class="fw-medium">${formatCurrency(eob.total_billed)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Total Allowed</span>
                            <span class="fw-medium">${formatCurrency(eob.total_allowed)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Total Not Covered</span>
                            <span class="fw-medium">${formatCurrency(eob.total_not_covered)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Total Plan Paid</span>
                            <span class="fw-medium">${formatCurrency(eob.total_plan_paid)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Member Responsibility</span>
                            <span class="fw-medium">${formatCurrency(eob.total_member_responsibility)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <h4>Service Lines</h4>
                        ${eob.service_lines && eob.service_lines.length > 0 ? `
                            <div class="table-responsive">
                                <table class="table table-sm table-striped">
                                    <thead>
                                        <tr>
                                            <th>Service</th>
                                            <th>Code</th>
                                            <th>Billed</th>
                                            <th>Allowed</th>
                                            <th>Not Covered</th>
                                            <th>Deductible</th>
                                            <th>Copay</th>
                                            <th>Coinsurance</th>
                                            <th>Plan Paid</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${eob.service_lines.map(line => `
                                            <tr>
                                                <td>${line.service_description || 'N/A'}</td>
                                                <td>${line.service_code || 'N/A'}</td>
                                                <td>${formatCurrency(line.billed_amount)}</td>
                                                <td>${formatCurrency(line.allowed_amount)}</td>
                                                <td>${formatCurrency(line.not_covered_amount)}</td>
                                                <td>${formatCurrency(line.deductible_amount)}</td>
                                                <td>${formatCurrency(line.copay_amount)}</td>
                                                <td>${formatCurrency(line.coinsurance_amount)}</td>
                                                <td>${formatCurrency(line.plan_paid_amount)}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        ` : '<div class="alert alert-info">No service lines available</div>'}
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <h4>Year-to-Date Summary</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Deductible Used</span>
                            <span class="fw-medium">${formatCurrency(eob.year_to_date_deductible)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Out-of-Pocket Used</span>
                            <span class="fw-medium">${formatCurrency(eob.year_to_date_out_of_pocket)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <h4>Appeal Rights</h4>
                        <div class="alert alert-info">
                            ${eob.appeal_rights || 'No appeal rights information available.'}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Create modal if it doesn't exist
        if ($('#eobDetailModal').length === 0) {
            $('body').append(`
                <div class="modal fade" id="eobDetailModal" tabindex="-1" aria-labelledby="eobDetailModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="eobDetailModalLabel">EOB Details</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div id="eob-detail-content">
                                    <!-- Will be populated by JavaScript -->
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        }
        
        $('#eob-detail-content').html(detailsHtml);
    }
    
    // Function to render clinical notes tab
    function renderClinicalNotesTab(notes) {
        if (notes.length === 0) {
            $('#clinical-notes-content').html('<div class="alert alert-info">No clinical notes found for this member.</div>');
            return;
        }
        
        $('#clinical-notes-content').html(`
            <div class="table-responsive">
                <table class="table table-striped" id="clinical-notes-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Provider</th>
                            <th>Type</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${notes.map(note => `
                            <tr>
                                <td>${formatDate(note.date)}</td>
                                <td>${note.provider_name || 'N/A'}</td>
                                <td>${note.note_type || 'N/A'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-note" data-note-id="${note.id}">
                                        View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `);
        
        // Initialize DataTable
        initDataTable('clinical-notes-table');
        
        // Add event listener for view note button - use delegated event handling
        $(document).off('click', '.view-note').on('click', '.view-note', function() {
            console.log("Clinical Note View button clicked");
            const noteId = $(this).data('note-id');
            console.log("Note ID:", noteId);
            
            // Try to find the note in the data
            let note = notes.find(n => String(n.id) === String(noteId));
            
            if (note) {
                console.log("Found note in data:", note);
                renderNoteDetails(note);
                $('#noteDetailModal').modal('show');
            } else {
                console.log("Note not found in data, fetching from API...");
                // If not found in data, fetch it directly from the API
                $.getJSON(`/api/clinical-notes/${noteId}`, function(data) {
                    console.log("Fetched note from API:", data);
                    renderNoteDetails(data);
                    $('#noteDetailModal').modal('show');
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    console.error("Error fetching note:", textStatus, errorThrown);
                    alert("Error loading clinical note details. Please try again.");
                });
            }
        });
    }
    
    // Function to render note details in modal
    function renderClinicalEncountersTab(encounters) {
        if (encounters.length === 0) {
            $('#clinical-encounters-content').html('<div class="alert alert-info">No clinical encounters found for this member.</div>');
            return;
        }
        
        $('#clinical-encounters-content').html(`
            <div class="table-responsive">
                <table class="table table-striped" id="clinical-encounters-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${encounters.map(encounter => `
                            <tr>
                                <td>${encounter.id}</td>
                                <td>${formatDate(encounter.start_datetime)}</td>
                                <td>${encounter.end_datetime ? formatDate(encounter.end_datetime) : 'Ongoing'}</td>
                                <td>${encounter.type || 'N/A'}</td>
                                <td>${formatStatusBadge(encounter.status, 'encounter')}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-encounter" data-encounter-id="${encounter.id}">
                                        View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `);
        
        // Initialize DataTable
        initDataTable('clinical-encounters-table');
        
        // Add event listener for view encounter button - use delegated event handling
        $(document).off('click', '.view-encounter').on('click', '.view-encounter', function() {
            console.log("Clinical Encounter View button clicked");
            const encounterId = $(this).data('encounter-id');
            console.log("Encounter ID:", encounterId);
            
            // Try to find the encounter in the data
            let encounter = encounters.find(e => String(e.id) === String(encounterId));
            
            if (encounter) {
                console.log("Found encounter in data:", encounter);
                renderEncounterDetails(encounter);
                $('#encounterDetailModal').modal('show');
            } else {
                console.log("Encounter not found in data, fetching from API...");
                // If not found in data, fetch it directly from the API
                $.getJSON(`/api/clinical-encounters/${encounterId}`, function(data) {
                    console.log("Fetched encounter from API:", data);
                    renderEncounterDetails(data);
                    $('#encounterDetailModal').modal('show');
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    console.error("Error fetching encounter:", textStatus, errorThrown);
                    alert("Error loading clinical encounter details. Please try again.");
                });
            }
        });
    }
    
    function renderEncounterDetails(encounter) {
        let html = `
            <div class="card mb-3">
                <div class="card-header">
                    <h5 class="card-title mb-0">Encounter Information</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <table class="table table-sm">
                                <tr>
                                    <th>Encounter ID:</th>
                                    <td>${encounter.id}</td>
                                </tr>
                                <tr>
                                    <th>Start Date:</th>
                                    <td>${formatDate(encounter.start_datetime)}</td>
                                </tr>
                                <tr>
                                    <th>End Date:</th>
                                    <td>${encounter.end_datetime ? formatDate(encounter.end_datetime) : 'Ongoing'}</td>
                                </tr>
                                <tr>
                                    <th>Length of Stay:</th>
                                    <td>${encounter.length_of_stay ? encounter.length_of_stay + ' days' : 'N/A'}</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <table class="table table-sm">
                                <tr>
                                    <th>Type:</th>
                                    <td>${encounter.type || 'N/A'}</td>
                                </tr>
                                <tr>
                                    <th>Status:</th>
                                    <td>${formatStatusBadge(encounter.status, 'encounter')}</td>
                                </tr>
                                <tr>
                                    <th>Class:</th>
                                    <td>${encounter.class_type || 'N/A'}</td>
                                </tr>
                                <tr>
                                    <th>Chief Complaint:</th>
                                    <td>${encounter.chief_complaint || 'N/A'}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Participants
        if (encounter.participants && encounter.participants.length > 0) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h5 class="card-title mb-0">Participants</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm table-striped">
                                <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>ID</th>
                                        <th>Role</th>
                                        <th>Start</th>
                                        <th>End</th>
                                        <th>Primary</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;
            
            encounter.participants.forEach(participant => {
                html += `
                    <tr>
                        <td>${participant.participant_type}</td>
                        <td>${participant.participant_id}</td>
                        <td>${participant.role || 'N/A'}</td>
                        <td>${formatDate(participant.start_datetime)}</td>
                        <td>${participant.end_datetime ? formatDate(participant.end_datetime) : 'Ongoing'}</td>
                        <td>${participant.primary ? 'Yes' : 'No'}</td>
                    </tr>
                `;
            });
            
            html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Diagnoses
        if (encounter.diagnoses && encounter.diagnoses.length > 0) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h5 class="card-title mb-0">Diagnoses</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm table-striped">
                                <thead>
                                    <tr>
                                        <th>Code</th>
                                        <th>Description</th>
                                        <th>Type</th>
                                        <th>Present on Admission</th>
                                        <th>Rank</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;
            
            encounter.diagnoses.forEach(diagnosis => {
                html += `
                    <tr>
                        <td>${diagnosis.diagnosis_code}</td>
                        <td>${diagnosis.diagnosis_description}</td>
                        <td>${diagnosis.diagnosis_type || 'N/A'}</td>
                        <td>${diagnosis.present_on_admission ? 'Yes' : 'No'}</td>
                        <td>${diagnosis.rank || 'N/A'}</td>
                    </tr>
                `;
            });
            
            html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Procedures
        if (encounter.procedures && encounter.procedures.length > 0) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h5 class="card-title mb-0">Procedures</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm table-striped">
                                <thead>
                                    <tr>
                                        <th>Code</th>
                                        <th>Description</th>
                                        <th>Date</th>
                                        <th>Duration</th>
                                        <th>Provider</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;
            
            encounter.procedures.forEach(procedure => {
                html += `
                    <tr>
                        <td>${procedure.procedure_code}</td>
                        <td>${procedure.procedure_description}</td>
                        <td>${formatDate(procedure.datetime)}</td>
                        <td>${procedure.duration_minutes ? procedure.duration_minutes + ' min' : 'N/A'}</td>
                        <td>${procedure.provider_id || 'N/A'}</td>
                        <td>${formatStatusBadge(procedure.status, 'procedure')}</td>
                    </tr>
                `;
            });
            
            html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }
        
        $('#encounter-detail-content').html(html);
        $('#encounterDetailModalLabel').text(`Clinical Encounter: ${encounter.id}`);
    }

    function renderNoteDetails(note) {
        console.log("Rendering note details:", note);
        
        $('#note-detail-content').html(`
            <div class="note-detail">
                <div class="row">
                    <div class="col-md-6">
                        <h4>Clinical Note Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Note ID</span>
                            <span class="fw-medium">${note.id}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Provider</span>
                            <span class="fw-medium">${note.provider_id || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Date</span>
                            <span class="fw-medium">${formatDate(note.date)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Type</span>
                            <span class="fw-medium">${note.note_type || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Encounter ID</span>
                            <span class="fw-medium">${note.encounter_id || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>Follow-up Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Follow-up</span>
                            <span class="fw-medium">${note.follow_up || 'N/A'}</span>
                        </div>
                        ${note.medications_prescribed && note.medications_prescribed.length > 0 ? `
                            <h5 class="mt-3">Medications Prescribed</h5>
                            <ul class="list-group">
                                ${note.medications_prescribed.map(med => `
                                    <li class="list-group-item">
                                        <strong>${med.name}</strong> ${med.dosage}, ${med.frequency}
                                        ${med.duration ? `<div class="text-muted">Duration: ${med.duration}</div>` : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        ` : ''}
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-12">
                        <h4>Chief Complaint</h4>
                        <div class="p-3 bg-light rounded mb-3">
                            ${note.chief_complaint || 'No chief complaint recorded.'}
                        </div>
                        
                        <h4>History of Present Illness</h4>
                        <div class="p-3 bg-light rounded mb-3">
                            ${note.history_of_present_illness || 'No history of present illness recorded.'}
                        </div>
                        
                        <h4>Review of Systems</h4>
                        <div class="p-3 bg-light rounded mb-3">
                            ${note.review_of_systems || 'No review of systems recorded.'}
                        </div>
                        
                        <h4>Physical Exam</h4>
                        <div class="p-3 bg-light rounded mb-3">
                            ${note.physical_exam || 'No physical exam recorded.'}
                        </div>
                        
                        <h4>Assessment</h4>
                        <div class="p-3 bg-light rounded mb-3">
                            ${note.assessment || 'No assessment recorded.'}
                        </div>
                        
                        <h4>Plan</h4>
                        <div class="p-3 bg-light rounded mb-3">
                            ${note.plan || 'No plan recorded.'}
                        </div>
                    </div>
                </div>
            </div>
        `);
    }
    
    // Function to render care plans tab
    function renderCarePlansTab(plans) {
        if (plans.length === 0) {
            $('#care-plans-content').html('<div class="alert alert-info">No care plans found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped" id="care-plans-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Created</th>
                            <th>Status</th>
                            <th>Provider</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${plans.map(plan => `
                            <tr>
                                <td>${plan.id}</td>
                                <td>${plan.title || 'N/A'}</td>
                                <td>${formatDate(plan.created_date)}</td>
                                <td>${formatStatusBadge(plan.status, 'care_plan')}</td>
                                <td>${plan.provider_name || 'N/A'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-plan" data-plan-id="${plan.id}">
                                        View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        $('#care-plans-content').html(html);
        
        // Initialize DataTable
        initDataTable('care-plans-table');
    }
    
    // Function to render communications tab
    function renderCommunicationsTab(communications) {
        if (communications.length === 0) {
            $('#communications-content').html('<div class="alert alert-info">No communications found for this member.</div>');
            return;
        }
        
        $('#communications-content').html(`
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i> Communications data will be displayed here.
            </div>
        `);
    }
    
    // Function to load and render patient data
    function loadAndRenderPatientData(memberId) {
        // Show loading indicator
        $('#patient-data-content').html(`
            <div class="text-center my-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading patient data...</p>
            </div>
        `);
        
        // Load patient data via AJAX
        $.ajax({
            url: `/api/patient-generated-data?member_id=${memberId}`,
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                renderPatientData(data);
            },
            error: function() {
                $('#patient-data-content').html(`
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i> Failed to load patient data.
                    </div>
                `);
            }
        });
    }
    
    // Function to render patient data
    function renderPatientData(patientData) {
        if (!patientData || patientData.length === 0) {
            $('#patient-data-content').html('<div class="alert alert-info">No patient-generated data found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped" id="patient-data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Date</th>
                            <th>Type</th>
                            <th>Source</th>
                            <th>Value</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${patientData.map(item => `
                            <tr>
                                <td>${item.id}</td>
                                <td>${formatDate(item.date)}</td>
                                <td>${item.data_type || 'N/A'}</td>
                                <td>${item.source || 'N/A'}</td>
                                <td>${item.value !== undefined ? item.value : 'N/A'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-patient-data" data-item-id="${item.id}">
                                        View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        $('#patient-data-content').html(html);
        
        // Initialize DataTable
        initDataTable('patient-data-table');
        
        // Add event listener for view button
        $('.view-patient-data').on('click', function() {
            const itemId = $(this).data('item-id');
            // Find the item in the data
            const item = patientData.find(i => i.id === itemId);
            if (item) {
                renderPatientDataDetails(item);
                $('#patientDataDetailModal').modal('show');
            }
        });
    }
    
    // Function to render patient data details
    function renderPatientDataDetails(item) {
        let detailsHtml = `
            <div class="patient-data-detail">
                <div class="row">
                    <div class="col-md-6">
                        <h4>Patient Data Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">ID</span>
                            <span class="fw-medium">${item.id}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Date</span>
                            <span class="fw-medium">${formatDate(item.date)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Type</span>
                            <span class="fw-medium">${item.data_type || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Source</span>
                            <span class="fw-medium">${item.source || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Value</span>
                            <span class="fw-medium">${item.value !== undefined ? item.value : 'N/A'}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>Additional Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Device</span>
                            <span class="fw-medium">${item.device || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Units</span>
                            <span class="fw-medium">${item.units || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2">
                            <span class="text-muted">Notes</span>
                            <span class="fw-medium">${item.notes || 'N/A'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#patient-data-detail-content').html(detailsHtml);
    }
    
    // Function to render care episodes tab
    function renderCareEpisodesTab(episodes) {
        if (episodes.length === 0) {
            $('#care-episodes-content').html('<div class="alert alert-info">No care episodes found for this member.</div>');
            return;
        }
        
        $('#care-episodes-content').html(`
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i> Care episodes data will be displayed here.
            </div>
        `);
    }
    
    // Function to render SDOH tab
    function renderSdohTab(assessments) {
        if (assessments.length === 0) {
            $('#sdoh-content').html('<div class="alert alert-info">No SDOH assessments found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped" id="sdoh-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Assessment Date</th>
                            <th>Type</th>
                            <th>Score</th>
                            <th>Risk Level</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${assessments.map(assessment => {
                            // Determine risk level based on score
                            let riskLevel = 'Low';
                            let riskClass = 'success';
                            if (assessment.score > 7) {
                                riskLevel = 'High';
                                riskClass = 'danger';
                            } else if (assessment.score > 4) {
                                riskLevel = 'Medium';
                                riskClass = 'warning';
                            }
                            
                            return `
                                <tr>
                                    <td>${assessment.id}</td>
                                    <td>${formatDate(assessment.assessment_date)}</td>
                                    <td>${assessment.assessment_type || 'N/A'}</td>
                                    <td>${assessment.score !== undefined ? assessment.score : 'N/A'}</td>
                                    <td><span class="badge bg-${riskClass}">${riskLevel}</span></td>
                                    <td>
                                        <button class="btn btn-sm btn-primary view-sdoh" data-assessment-id="${assessment.id}">
                                            View Details
                                        </button>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        $('#sdoh-content').html(html);
        
        // Initialize DataTable
        initDataTable('sdoh-table');
        
        // Add event listener for view button - use delegated event handling
        $(document).off('click', '.view-sdoh').on('click', '.view-sdoh', function() {
            console.log("SDOH View button clicked");
            const assessmentId = $(this).data('assessment-id');
            console.log("Assessment ID:", assessmentId);
            console.log("Global SDOH Assessments:", globalSdohAssessments);
            
            // Try to find the assessment in the global data
            let assessment = globalSdohAssessments.find(a => String(a.id) === String(assessmentId));
            
            if (assessment) {
                console.log("Found assessment in global data:", assessment);
                renderSdohDetails(assessment);
                $('#sdohDetailModal').modal('show');
            } else {
                console.log("Assessment not found in global data, fetching from API...");
                // If not found in global data, fetch it directly from the API
                $.getJSON(`/api/sdoh-assessments/${assessmentId}`, function(data) {
                    console.log("Fetched assessment from API:", data);
                    renderSdohDetails(data);
                    $('#sdohDetailModal').modal('show');
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    console.error("Error fetching assessment:", textStatus, errorThrown);
                    alert("Error loading SDOH assessment details. Please try again.");
                });
            }
        });
    }
    
    // Function to render SDOH assessment details
    function renderSdohDetails(assessment) {
        console.log("Rendering SDOH details for assessment:", assessment);
        
        let detailsHtml = `
            <div class="sdoh-detail">
                <div class="row">
                    <div class="col-md-6">
                        <h4>Assessment Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">ID</span>
                            <span class="fw-medium">${assessment.id}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Assessment Date</span>
                            <span class="fw-medium">${formatDate(assessment.assessment_date)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Provider ID</span>
                            <span class="fw-medium">${assessment.provider_id || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Overall Risk Level</span>
                            <span class="fw-medium">${assessment.overall_risk_level || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>Domain Scores</h4>
                        ${assessment.domains ? Object.entries(assessment.domains).map(([domain, data]) => `
                            <div class="info-item d-flex justify-content-between py-2 border-bottom">
                                <span class="text-muted">${domain.replace(/_/g, ' ')}</span>
                                <span class="fw-medium">${data.score}</span>
                            </div>
                        `).join('') : '<div class="alert alert-info">No domain scores available</div>'}
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <h4>Risk Factors</h4>
                        ${assessment.risk_factors && assessment.risk_factors.length > 0 ? `
                            <ul class="list-group">
                                ${assessment.risk_factors.map(factor => `
                                    <li class="list-group-item">
                                        <strong>${factor.category}:</strong> ${factor.description}
                                        <span class="badge bg-${factor.severity === 'high' ? 'danger' : factor.severity === 'moderate' ? 'warning' : 'success'} float-end">
                                            ${factor.severity}
                                        </span>
                                    </li>
                                `).join('')}
                            </ul>
                        ` : '<div class="alert alert-info">No risk factors available</div>'}
                    </div>
                    <div class="col-md-6">
                        <h4>Interventions</h4>
                        ${assessment.interventions && assessment.interventions.length > 0 ? `
                            <ul class="list-group">
                                ${assessment.interventions.map(intervention => `
                                    <li class="list-group-item">
                                        <strong>${intervention.type}:</strong> ${intervention.description}
                                        <span class="badge bg-${intervention.status === 'completed' ? 'success' : intervention.status === 'in_progress' ? 'primary' : 'secondary'} float-end">
                                            ${intervention.status}
                                        </span>
                                    </li>
                                `).join('')}
                            </ul>
                        ` : '<div class="alert alert-info">No interventions available</div>'}
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <h4>Referrals</h4>
                        ${assessment.referrals && assessment.referrals.length > 0 ? `
                            <ul class="list-group">
                                ${assessment.referrals.map(referral => `
                                    <li class="list-group-item">
                                        <strong>${referral.service_type}:</strong> ${referral.organization}
                                        <span class="badge bg-${referral.status === 'completed' ? 'success' : referral.status === 'pending' ? 'warning' : 'secondary'} float-end">
                                            ${referral.status}
                                        </span>
                                    </li>
                                `).join('')}
                            </ul>
                        ` : '<div class="alert alert-info">No referrals available</div>'}
                    </div>
                </div>
            </div>
        `;
        
        $('#sdoh-detail-content').html(detailsHtml);
    }
    
    // Function to render risk tab
    function renderRiskTab(assessments) {
        if (assessments.length === 0) {
            $('#risk-content').html('<div class="alert alert-info">No risk assessments found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped" id="risk-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Assessment Date</th>
                            <th>Type</th>
                            <th>Risk Score</th>
                            <th>Risk Level</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${assessments.map(assessment => {
                            // Determine risk level based on score
                            let riskLevel = 'Low';
                            let riskClass = 'success';
                            if (assessment.risk_score > 0.7) {
                                riskLevel = 'High';
                                riskClass = 'danger';
                            } else if (assessment.risk_score > 0.4) {
                                riskLevel = 'Medium';
                                riskClass = 'warning';
                            }
                            
                            return `
                                <tr>
                                    <td>${assessment.id}</td>
                                    <td>${formatDate(assessment.assessment_date)}</td>
                                    <td>${assessment.assessment_type || 'N/A'}</td>
                                    <td>${assessment.risk_score !== undefined ? assessment.risk_score.toFixed(2) : 'N/A'}</td>
                                    <td><span class="badge bg-${riskClass}">${riskLevel}</span></td>
                                    <td>
                                        <button class="btn btn-sm btn-primary view-risk" data-assessment-id="${assessment.id}">
                                            View Details
                                        </button>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        $('#risk-content').html(html);
        
        // Initialize DataTable
        initDataTable('risk-table');
        
        // Add event listener for view button - use delegated event handling
        $(document).off('click', '.view-risk').on('click', '.view-risk', function() {
            console.log("Risk View button clicked");
            const assessmentId = $(this).data('assessment-id');
            console.log("Assessment ID:", assessmentId);
            console.log("Global Risk Assessments:", globalRiskAssessments);
            
            // Try to find the assessment in the global data
            let assessment = globalRiskAssessments.find(a => String(a.id) === String(assessmentId));
            
            if (assessment) {
                console.log("Found assessment in global data:", assessment);
                renderRiskDetails(assessment);
                $('#riskDetailModal').modal('show');
            } else {
                console.log("Assessment not found in global data, fetching from API...");
                // If not found in global data, fetch it directly from the API
                $.getJSON(`/api/risk-assessments/${assessmentId}`, function(data) {
                    console.log("Fetched assessment from API:", data);
                    renderRiskDetails(data);
                    $('#riskDetailModal').modal('show');
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    console.error("Error fetching assessment:", textStatus, errorThrown);
                    alert("Error loading risk assessment details. Please try again.");
                });
            }
        });
    }
    
    // Function to render risk assessment details
    function renderRiskDetails(assessment) {
        console.log("Rendering risk details for assessment:", assessment);
        
        let detailsHtml = `
            <div class="risk-detail">
                <div class="row">
                    <div class="col-md-6">
                        <h4>Assessment Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">ID</span>
                            <span class="fw-medium">${assessment.id}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Assessment Date</span>
                            <span class="fw-medium">${formatDate(assessment.assessment_date)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Overall Risk Score</span>
                            <span class="fw-medium">${assessment.overall_risk ? assessment.overall_risk.score.toFixed(1) : 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Overall Risk Level</span>
                            <span class="fw-medium">
                                <span class="badge bg-${assessment.overall_risk && assessment.overall_risk.level === 'high' ? 'danger' :
                                                      assessment.overall_risk && assessment.overall_risk.level === 'moderate' ? 'warning' : 'success'}">
                                    ${assessment.overall_risk ? assessment.overall_risk.level : 'N/A'}
                                </span>
                            </span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Stratification</span>
                            <span class="fw-medium">${assessment.overall_risk ? assessment.overall_risk.stratification : 'N/A'}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>Risk Categories</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Clinical Risk</span>
                            <span class="fw-medium">
                                <span class="badge bg-${assessment.clinical_risk && assessment.clinical_risk.level === 'high' ? 'danger' :
                                                      assessment.clinical_risk && assessment.clinical_risk.level === 'moderate' ? 'warning' : 'success'}">
                                    ${assessment.clinical_risk ? `${assessment.clinical_risk.score.toFixed(1)} (${assessment.clinical_risk.level})` : 'N/A'}
                                </span>
                            </span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Financial Risk</span>
                            <span class="fw-medium">
                                <span class="badge bg-${assessment.financial_risk && assessment.financial_risk.level === 'high' ? 'danger' :
                                                      assessment.financial_risk && assessment.financial_risk.level === 'moderate' ? 'warning' : 'success'}">
                                    ${assessment.financial_risk ? `${assessment.financial_risk.score.toFixed(1)} (${assessment.financial_risk.level})` : 'N/A'}
                                </span>
                            </span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Care Management Risk</span>
                            <span class="fw-medium">
                                <span class="badge bg-${assessment.care_management_risk && assessment.care_management_risk.level === 'high' ? 'danger' :
                                                      assessment.care_management_risk && assessment.care_management_risk.level === 'moderate' ? 'warning' : 'success'}">
                                    ${assessment.care_management_risk ? `${assessment.care_management_risk.score.toFixed(1)} (${assessment.care_management_risk.level})` : 'N/A'}
                                </span>
                            </span>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-12">
                        <h4>Clinical Risk Factors</h4>
                        ${assessment.clinical_risk && assessment.clinical_risk.factors && assessment.clinical_risk.factors.length > 0 ? `
                            <ul class="list-group">
                                ${assessment.clinical_risk.factors.map(factor => `
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>${factor.type}:</strong> ${factor.description}
                                            <span class="badge bg-${factor.impact === 'high' ? 'danger' :
                                                                  factor.impact === 'moderate' ? 'warning' : 'success'} ms-2">
                                                ${factor.impact}
                                            </span>
                                        </div>
                                        <span class="badge bg-${factor.modifiable ? 'success' : 'secondary'}">
                                            ${factor.modifiable ? 'Modifiable' : 'Not Modifiable'}
                                        </span>
                                    </li>
                                `).join('')}
                            </ul>
                        ` : '<div class="alert alert-info">No clinical risk factors available</div>'}
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-12">
                        <h4>Care Management Risk Factors</h4>
                        ${assessment.care_management_risk && assessment.care_management_risk.factors && assessment.care_management_risk.factors.length > 0 ? `
                            <ul class="list-group">
                                ${assessment.care_management_risk.factors.map(factor => `
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>${factor.type}:</strong> ${factor.description}
                                            <span class="badge bg-${factor.impact === 'high' ? 'danger' :
                                                                  factor.impact === 'moderate' ? 'warning' : 'success'} ms-2">
                                                ${factor.impact}
                                            </span>
                                        </div>
                                        <span class="badge bg-${factor.modifiable ? 'success' : 'secondary'}">
                                            ${factor.modifiable ? 'Modifiable' : 'Not Modifiable'}
                                        </span>
                                    </li>
                                `).join('')}
                            </ul>
                        ` : '<div class="alert alert-info">No care management risk factors available</div>'}
                    </div>
                </div>
            </div>
        `;
        
        $('#risk-detail-content').html(detailsHtml);
    }
    
    // Function to render pharmacy tab
    function renderPharmacyTab(claims) {
        if (claims.length === 0) {
            $('#pharmacy-content').html('<div class="alert alert-info">No pharmacy claims found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped" id="pharmacy-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Fill Date</th>
                            <th>Medication</th>
                            <th>Pharmacy</th>
                            <th>Days Supply</th>
                            <th>Cost</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${claims.map(claim => `
                            <tr>
                                <td>${claim.id}</td>
                                <td>${formatDate(claim.fill_date)}</td>
                                <td>${claim.medication_name || 'N/A'}</td>
                                <td>${claim.pharmacy_name || 'N/A'}</td>
                                <td>${claim.days_supply || 'N/A'}</td>
                                <td>${formatCurrency(claim.total_cost)}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-pharmacy" data-claim-id="${claim.id}">
                                        View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        $('#pharmacy-content').html(html);
        
        // Initialize DataTable
        initDataTable('pharmacy-table');
        
        // Add chart visualization
        if (claims.length > 0) {
            html += `
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title mb-0">Medication Distribution</h5>
                            </div>
                            <div class="card-body">
                                <canvas id="pharmacyChart" height="250"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            $('#pharmacy-content').html(html);
            
            // Initialize DataTable again after updating the HTML
            initDataTable('pharmacy-table');
            
            // Initialize pharmacy chart
            initPharmacyChart(claims);
        }
        
        // Add event listener for view button - use delegated event handling
        $(document).off('click', '.view-pharmacy').on('click', '.view-pharmacy', function() {
            console.log("Pharmacy View button clicked");
            const claimId = $(this).data('claim-id');
            console.log("Claim ID:", claimId);
            console.log("Global Pharmacy Claims:", globalPharmacyClaims);
            
            // Try to find the claim in the global data
            let claim = globalPharmacyClaims.find(c => String(c.id) === String(claimId));
            
            if (claim) {
                console.log("Found claim in global data:", claim);
                renderPharmacyDetails(claim);
                $('#pharmacyDetailModal').modal('show');
            } else {
                console.log("Claim not found in global data, fetching from API...");
                // If not found in global data, fetch it directly from the API
                $.getJSON(`/api/pharmacy-benefit/claims/${claimId}`, function(data) {
                    console.log("Fetched claim from API:", data);
                    renderPharmacyDetails(data);
                    $('#pharmacyDetailModal').modal('show');
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    console.error("Error fetching claim:", textStatus, errorThrown);
                    alert("Error loading pharmacy claim details. Please try again.");
                });
            }
        });
    }
    
    // Function to render pharmacy claim details
    function renderPharmacyDetails(claim) {
        let detailsHtml = `
            <div class="pharmacy-detail">
                <div class="row">
                    <div class="col-md-6">
                        <h4>Claim Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Claim ID</span>
                            <span class="fw-medium">${claim.id}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Fill Date</span>
                            <span class="fw-medium">${formatDate(claim.fill_date)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Pharmacy</span>
                            <span class="fw-medium">${claim.pharmacy_name || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Pharmacy NPI</span>
                            <span class="fw-medium">${claim.pharmacy_npi || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Prescriber</span>
                            <span class="fw-medium">${claim.prescriber_name || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>Medication Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Medication</span>
                            <span class="fw-medium">${claim.medication_name || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">NDC</span>
                            <span class="fw-medium">${claim.ndc || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Drug Tier</span>
                            <span class="fw-medium">${claim.drug_tier || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Days Supply</span>
                            <span class="fw-medium">${claim.days_supply || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Quantity</span>
                            <span class="fw-medium">${claim.quantity || 'N/A'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <h4>Financial Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Total Cost</span>
                            <span class="fw-medium">${formatCurrency(claim.total_cost)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Plan Paid</span>
                            <span class="fw-medium">${formatCurrency(claim.plan_paid)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Member Paid</span>
                            <span class="fw-medium">${formatCurrency(claim.member_paid)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#pharmacy-detail-content').html(detailsHtml);
    }
    
    // but with enhanced styling and visualizations. For brevity, I'm not including them all here.
    // Function to render claims tab
    function renderClaimsTab(claims) {
        if (claims.length === 0) {
            $('#claims-content').html('<div class="alert alert-info">No claims found for this member.</div>');
            return;
        }
        
        // Claims tab implementation would go here
        $('#claims-content').html(`
            <div class="table-responsive">
                <table class="table table-striped" id="claims-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Provider</th>
                            <th>Date</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${claims.map(claim => `
                            <tr>
                                <td>${claim.id}</td>
                                <td>${claim.provider_name || 'N/A'}</td>
                                <td>${formatDate(claim.date_of_service || claim.service_date)}</td>
                                <td>${formatCurrency(claim.total_charge || claim.total_amount)}</td>
                                <td>${formatStatusBadge(claim.status, 'claim')}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-claim" data-claim-id="${claim.id}">
                                        View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `);
        
        // Initialize DataTable
        initDataTable('claims-table');
        
        // Add event listener for view claim button
        $('.view-claim').on('click', function() {
            const claimId = $(this).data('claim-id');
            // Find the claim in the data
            const claim = claims.find(c => c.id === claimId);
            if (claim) {
                renderClaimDetails(claim);
                $('#claimDetailModal').modal('show');
            }
        });
    }
    
    // Function to render claim details in modal
    function renderClaimDetails(claim) {
        let serviceLines = '';
        if (claim.service_lines && claim.service_lines.length > 0) {
            serviceLines = `
                <h5 class="mt-4">Service Lines</h5>
                <div class="table-responsive">
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Description</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${claim.service_lines.map(line => `
                                <tr>
                                    <td>${line.service_code || 'N/A'}</td>
                                    <td>${line.description || 'N/A'}</td>
                                    <td>${line.quantity || 'N/A'}</td>
                                    <td>${formatCurrency(line.unit_price)}</td>
                                    <td>${formatCurrency(line.total_price)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
        
        let diagnosisCodes = '';
        if (claim.diagnosis_codes && claim.diagnosis_codes.length > 0) {
            diagnosisCodes = `
                <h5 class="mt-4">Diagnosis Codes</h5>
                <div class="diagnosis-codes">
                    ${claim.diagnosis_codes.map(code => `
                        <span class="badge bg-info me-2 mb-2">${code}</span>
                    `).join('')}
                </div>
            `;
        }
        
        $('#claim-detail-content').html(`
            <div class="claim-detail">
                <div class="row">
                    <div class="col-md-6">
                        <h4>Claim Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Claim ID</span>
                            <span class="fw-medium">${claim.id}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Provider</span>
                            <span class="fw-medium">${claim.provider_name || 'N/A'}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Date of Service</span>
                            <span class="fw-medium">${formatDate(claim.date_of_service || claim.service_date)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Date Received</span>
                            <span class="fw-medium">${formatDate(claim.date_received || claim.submission_date)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Status</span>
                            <span class="fw-medium">${formatStatusBadge(claim.status, 'claim')}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>Financial Information</h4>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Total Charge</span>
                            <span class="fw-medium">${formatCurrency(claim.total_charge || claim.total_amount)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Allowed Amount</span>
                            <span class="fw-medium">${formatCurrency(claim.allowed_amount)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Member Responsibility</span>
                            <span class="fw-medium">${formatCurrency(claim.member_responsibility)}</span>
                        </div>
                        <div class="info-item d-flex justify-content-between py-2 border-bottom">
                            <span class="text-muted">Plan Paid</span>
                            <span class="fw-medium">${formatCurrency(claim.plan_paid)}</span>
                        </div>
                    </div>
                </div>
                
                ${diagnosisCodes}
                ${serviceLines}
            </div>
        `);
    }
});
