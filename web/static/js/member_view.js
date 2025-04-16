/**
 * JavaScript for the Member View page
 * Handles loading and displaying member data in the tabbed interface
 */

// Helper functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
}

function formatCurrency(amount) {
    if (amount === undefined || amount === null) return 'N/A';
    return '$' + parseFloat(amount).toFixed(2);
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
        responsive: true
    };
    
    const mergedOptions = {...defaultOptions, ...options};
    return $(`#${tableId}`).DataTable(mergedOptions);
}

$(document).ready(function() {
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
    
    // Load member data
    $.getJSON(`/api/member/${memberId}/related`, function(data) {
        renderMemberProfile(data);
        renderOverviewTab(data);
        renderClaimsTab(data.claims);
        renderAuthorizationsTab(data.authorizations);
        loadAndRenderEOBs(memberId);
        renderClinicalNotesTab(data.clinical_notes);
        renderCarePlansTab(data.care_plans);
        renderCommunicationsTab(data.communications);
        loadAndRenderPatientData(memberId);
        renderCareEpisodesTab(data.care_episodes || []);
        renderSdohTab(data.sdoh_assessments || []);
        renderRiskTab(data.risk_assessments || []);
        renderPharmacyTab(data.pharmacy_claims || []);
        
        // Update tab counts
        $('#claims-tab').text(`Claims (${data.claims.length})`);
        $('#authorizations-tab').text(`Authorizations (${data.authorizations.length})`);
        $('#clinical-notes-tab').text(`Clinical Notes (${data.clinical_notes.length})`);
        $('#care-plans-tab').text(`Care Plans (${data.care_plans.length})`);
        $('#communications-tab').text(`Communications (${data.communications.length})`);
        $('#care-episodes-tab').text(`Care Episodes (${data.care_episodes ? data.care_episodes.length : 0})`);
        $('#sdoh-tab').text(`SDOH (${data.sdoh_assessments ? data.sdoh_assessments.length : 0})`);
        $('#risk-tab').text(`Risk Assessment (${data.risk_assessments ? data.risk_assessments.length : 0})`);
        $('#pharmacy-tab').text(`Pharmacy Claims (${data.pharmacy_claims ? data.pharmacy_claims.length : 0})`);
    }).fail(function() {
        $('#member-profile-container').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i> Failed to load member data. Please try again.
            </div>
        `);
    });
    
    // Function to render member profile
    function renderMemberProfile(data) {
        const member = data.member;
        
        // Format dates
        const dob = new Date(member.date_of_birth);
        const formattedDob = dob.toLocaleDateString();
        
        // Calculate risk level classes
        let clinicalRiskClass = 'success';
        if (member.risk_score !== undefined) {
            const clinicalRisk = parseFloat(member.risk_score);
            if (clinicalRisk > 0.7) clinicalRiskClass = 'danger';
            else if (clinicalRisk > 0.4) clinicalRiskClass = 'warning';
        }
        
        // Build HTML for member profile
        let html = `
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h2 class="mb-0">${member.first_name} ${member.last_name}</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3 text-center mb-3">
                            <div class="avatar-circle bg-light mb-3">
                                <span class="initials">${member.first_name[0]}${member.last_name[0]}</span>
                            </div>
                            <h5>Member ID: ${member.id}</h5>
                            <span class="badge bg-${clinicalRiskClass} mb-2">Risk Score: ${member.risk_score !== undefined ? parseFloat(member.risk_score).toFixed(2) : 'N/A'}</span>
                        </div>
                        <div class="col-md-9">
                            <div class="row">
                                <div class="col-md-6">
                                    <h5>Demographics</h5>
                                    <table class="table table-sm">
                                        <tr>
                                            <th>Age:</th>
                                            <td>${member.age} years (DOB: ${formattedDob})</td>
                                        </tr>
                                        <tr>
                                            <th>Gender:</th>
                                            <td>${member.gender || 'N/A'}</td>
                                        </tr>
                                        <tr>
                                            <th>Address:</th>
                                            <td>${member.address.street}, ${member.address.city}, ${member.address.state} ${member.address.zip}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h5>Insurance</h5>
                                    <table class="table table-sm">
                                        <tr>
                                            <th>Plan:</th>
                                            <td>${member.insurance && member.insurance.plan_name ? member.insurance.plan_name : 'N/A'}</td>
                                        </tr>
                                        <tr>
                                            <th>Member ID:</th>
                                            <td>${member.insurance.member_id}</td>
                                        </tr>
                                        <tr>
                                            <th>Effective Date:</th>
                                            <td>${member.insurance && member.insurance.effective_date ? member.insurance.effective_date : 'N/A'}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-12">
                                    <h5>Contact Information</h5>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <p><i class="fas fa-phone me-2"></i> ${member.phone || 'N/A'}</p>
                                        </div>
                                        <div class="col-md-6">
                                            <p><i class="fas fa-envelope me-2"></i> ${member.email || 'N/A'}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#member-profile-container').html(html);
    }
    
    // Function to render overview tab
    function renderOverviewTab(data) {
        const member = data.member;
        
        let html = `
            <div class="row">
                <!-- Risk Scores -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Risk Scores</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
        `;
        
        // Clinical Risk
        if (member.risk_score !== undefined) {
            const clinicalRisk = parseFloat(member.risk_score).toFixed(2);
            let clinicalRiskClass = 'success';
            if (clinicalRisk > 0.7) clinicalRiskClass = 'danger';
            else if (clinicalRisk > 0.4) clinicalRiskClass = 'warning';
            
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card border-${clinicalRiskClass}">
                        <div class="card-header bg-${clinicalRiskClass} text-white">Clinical Risk</div>
                        <div class="card-body text-center">
                            <h1>${clinicalRisk}</h1>
                            <p>${clinicalRisk < 0.4 ? 'Low' : clinicalRisk < 0.7 ? 'Medium' : 'High'}</p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += `
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Care Gaps -->
                <div class="col-md-6 mb-4">
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
        `;
        
        $('#overview-content').html(html);
    }
    
    // Function to render claims tab
    function renderClaimsTab(claims) {
        if (claims.length === 0) {
            $('#claims-content').html('<div class="alert alert-info">No claims found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-claims-table">
                    <thead>
                        <tr>
                            <th>Claim ID</th>
                            <th>Service Date</th>
                            <th>Provider</th>
                            <th>Service</th>
                            <th>Total Amount</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        claims.forEach(claim => {
            let statusBadge = 'bg-warning';
            if (claim.status === 'Paid') statusBadge = 'bg-success';
            else if (claim.status === 'Denied') statusBadge = 'bg-danger';
            
            html += `
                <tr>
                    <td>${claim.id}</td>
                    <td>${formatDate(claim.service_date)}</td>
                    <td>${claim.provider_name || 'N/A'}</td>
                    <td>${claim.service_description || 'Medical service'}</td>
                    <td>${formatCurrency(claim.total_amount)}</td>
                    <td><span class="badge ${statusBadge}">${claim.status || 'Pending'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-primary view-claim-details" data-id="${claim.id}">
                            <i class="fas fa-eye"></i> View
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#claims-content').html(html);
        
        // Initialize DataTable using the enhanced initDataTable function
        initDataTable('member-claims-table', {
            order: [[1, 'desc']], // Sort by service date (descending)
            pageLength: 10
        });
        
        // Add event handler for view claim details button
        $('#member-claims-table').on('click', '.view-claim-details', function() {
            const claimId = $(this).data('id');
            
            // Show the modal
            $('#claimDetailModal').modal('show');
            
            // Find the claim in the claims array
            const claim = claims.find(c => c.id === claimId);
            
            if (claim) {
                renderClaimDetails(claim);
            } else {
                // If claim not found in the array, fetch it from the API
                $.getJSON(`/api/claims/${claimId}`, function(claimData) {
                    renderClaimDetails(claimData);
                }).fail(function() {
                    $('#claim-detail-content').html(`
                        <div class="alert alert-danger">
                            Failed to load claim details. Please try again.
                        </div>
                    `);
                });
            }
        });
        
        // Function to render claim details in the modal
        function renderClaimDetails(claim) {
            let html = `
                <div class="card mb-3">
                    <div class="card-header">
                        <h5 class="card-title mb-0">Claim Summary</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <table class="table table-sm">
                                    <tr>
                                        <th>Claim ID:</th>
                                        <td>${claim.id}</td>
                                    </tr>
                                    <tr>
                                        <th>Member ID:</th>
                                        <td>${claim.member_id}</td>
                                    </tr>
                                    <tr>
                                        <th>Service Date:</th>
                                        <td>${formatDate(claim.service_date)}</td>
                                    </tr>
                                    <tr>
                                        <th>Provider:</th>
                                        <td>${claim.provider_name || 'N/A'}</td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <table class="table table-sm">
                                    <tr>
                                        <th>Service:</th>
                                        <td>${claim.service_description || 'N/A'}</td>
                                    </tr>
                                    <tr>
                                        <th>Total Amount:</th>
                                        <td>${formatCurrency(claim.total_amount)}</td>
                                    </tr>
                                    <tr>
                                        <th>Status:</th>
                                        <td>${claim.status || 'Pending'}</td>
                                    </tr>
                                    <tr>
                                        <th>Submission Date:</th>
                                        <td>${formatDate(claim.date_received)}</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Line Items (if available)
            if (claim.service_lines && claim.service_lines.length > 0) {
                html += `
                    <div class="card mb-3">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Line Items</h5>
                        </div>
                        <div class="card-body">
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
                `;
                
                claim.service_lines.forEach(item => {
                    html += `
                        <tr>
                            <td>${item.service_code || 'N/A'}</td>
                            <td>${item.description || 'N/A'}</td>
                            <td>${item.quantity || 1}</td>
                            <td>${formatCurrency(item.unit_price)}</td>
                            <td>${formatCurrency(item.total_price || (item.unit_price * item.quantity))}</td>
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
            
            // Diagnosis Codes (if available)
            if (claim.diagnosis_codes && claim.diagnosis_codes.length > 0) {
                html += `
                    <div class="card mb-3">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Diagnosis Codes</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                `;
                
                claim.diagnosis_codes.forEach(code => {
                    html += `
                        <div class="col-md-4 mb-2">
                            <div class="card">
                                <div class="card-body py-2">
                                    <strong>${code}</strong>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                html += `
                            </div>
                        </div>
                    </div>
                `;
            }
            
            $('#claim-detail-content').html(html);
            $('#claimDetailModalLabel').text(`Claim Details: ${claim.id}`);
        }
    }
    
    // Function to render authorizations tab
    function renderAuthorizationsTab(authorizations) {
        if (authorizations.length === 0) {
            $('#authorizations-content').html('<div class="alert alert-info">No authorizations found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-authorizations-table">
                    <thead>
                        <tr>
                            <th>Auth ID</th>
                            <th>Request Date</th>
                            <th>Service</th>
                            <th>Provider</th>
                            <th>Status</th>
                            <th>Decision Date</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        authorizations.forEach(auth => {
            let statusBadge = 'bg-warning';
            if (auth.status === 'Approved') statusBadge = 'bg-success';
            else if (auth.status === 'Denied') statusBadge = 'bg-danger';
            
            html += `
                <tr>
                    <td>${auth.id}</td>
                    <td>${formatDate(auth.request_date)}</td>
                    <td>${auth.service_description || 'N/A'}</td>
                    <td>${auth.provider_name || 'N/A'}</td>
                    <td><span class="badge ${statusBadge}">${auth.status || 'Pending'}</span></td>
                    <td>${formatDate(auth.decision_date) || 'Pending'}</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#authorizations-content').html(html);
        
        // Initialize DataTable using the enhanced initDataTable function
        initDataTable('member-authorizations-table', {
            order: [[1, 'desc']], // Sort by request date (descending)
            pageLength: 10
        });
    }
    
    // Function to load and render EOBs
    function loadAndRenderEOBs(memberId) {
        $.getJSON('/api/eobs', function(allEobs) {
            // Filter EOBs for this member
            const memberEobs = allEobs.filter(eob => eob.member_id === memberId);
            
            if (memberEobs.length === 0) {
                $('#eobs-content').html('<div class="alert alert-info">No explanation of benefits found for this member.</div>');
                $('#eobs-tab').text('EOBs (0)');
                return;
            }
            
            let html = `
                <div class="table-responsive">
                    <table class="table table-striped table-hover" id="member-eobs-table">
                        <thead>
                            <tr>
                                <th>EOB ID</th>
                                <th>Claim ID</th>
                                <th>Service Date</th>
                                <th>Provider</th>
                                <th>Billed Amount</th>
                                <th>Patient Responsibility</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            memberEobs.forEach(eob => {
                html += `
                    <tr>
                        <td>${eob.id}</td>
                        <td>${eob.claim_id || 'N/A'}</td>
                        <td>${formatDate(eob.service_date)}</td>
                        <td>${eob.provider_name || 'N/A'}</td>
                        <td>${formatCurrency(eob.billed_amount)}</td>
                        <td>${formatCurrency(eob.patient_responsibility)}</td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
            
            $('#eobs-content').html(html);
            $('#eobs-tab').text(`EOBs (${memberEobs.length})`);
            
            // Initialize DataTable using the enhanced initDataTable function
            initDataTable('member-eobs-table', {
                order: [[2, 'desc']], // Sort by service date (descending)
                pageLength: 10
            });
        }).fail(function() {
            $('#eobs-content').html('<div class="alert alert-danger">Failed to load EOB data.</div>');
            $('#eobs-tab').text('EOBs (!)');
        });
    }
    
    // Function to render clinical notes tab
    function renderClinicalNotesTab(notes) {
        if (notes.length === 0) {
            $('#clinical-notes-content').html('<div class="alert alert-info">No clinical notes found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-clinical-notes-table">
                    <thead>
                        <tr>
                            <th>Note ID</th>
                            <th>Date</th>
                            <th>Provider</th>
                            <th>Type</th>
                            <th>Chief Complaint</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        notes.forEach(note => {
            html += `
                <tr>
                    <td>${note.id}</td>
                    <td>${formatDate(note.date)}</td>
                    <td>${note.provider_name || 'N/A'}</td>
                    <td>${note.note_type || 'N/A'}</td>
                    <td>${note.chief_complaint || 'N/A'}</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#clinical-notes-content').html(html);
        
        // Initialize DataTable using the enhanced initDataTable function
        initDataTable('member-clinical-notes-table', {
            order: [[1, 'desc']], // Sort by date (descending)
            pageLength: 10
        });
    }
    
    // Function to render care plans tab
    function renderCarePlansTab(plans) {
        if (plans.length === 0) {
            $('#care-plans-content').html('<div class="alert alert-info">No care plans found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-care-plans-table">
                    <thead>
                        <tr>
                            <th>Plan ID</th>
                            <th>Created Date</th>
                            <th>Condition</th>
                            <th>Goals</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        plans.forEach(plan => {
            let statusBadge = 'bg-warning';
            if (plan.status === 'Active') statusBadge = 'bg-success';
            else if (plan.status === 'Completed') statusBadge = 'bg-info';
            
            html += `
                <tr>
                    <td>${plan.id}</td>
                    <td>${formatDate(plan.created_date)}</td>
                    <td>${plan.condition || 'N/A'}</td>
                    <td>${plan.goals ? plan.goals.length : 0}</td>
                    <td><span class="badge ${statusBadge}">${plan.status || 'Unknown'}</span></td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#care-plans-content').html(html);
        
        // Initialize DataTable using the enhanced initDataTable function
        initDataTable('member-care-plans-table', {
            order: [[1, 'desc']], // Sort by created date (descending)
            pageLength: 10
        });
    }
    
    // Function to render communications tab
    function renderCommunicationsTab(communications) {
        if (communications.length === 0) {
            $('#communications-content').html('<div class="alert alert-info">No communications found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-communications-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Date</th>
                            <th>Type</th>
                            <th>Sender</th>
                            <th>Recipient</th>
                            <th>Subject</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        communications.forEach(comm => {
            html += `
                <tr>
                    <td>${comm.id}</td>
                    <td>${formatDate(comm.date)}</td>
                    <td>${comm.communication_type || 'N/A'}</td>
                    <td>${comm.sender || 'N/A'}</td>
                    <td>${comm.recipient || 'N/A'}</td>
                    <td>${comm.subject || 'N/A'}</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#communications-content').html(html);
        
        // Initialize DataTable using the enhanced initDataTable function
        initDataTable('member-communications-table', {
            order: [[1, 'desc']], // Sort by date (descending)
            pageLength: 10
        });
    }
    
    // Function to load and render patient-generated data
    function loadAndRenderPatientData(memberId) {
        $.getJSON('/api/patient-generated-data', function(allData) {
            // Filter data for this member
            const memberData = allData.filter(data => data.member_id === memberId);
            
            if (memberData.length === 0) {
                $('#patient-data-content').html('<div class="alert alert-info">No patient-generated data found for this member.</div>');
                $('#patient-data-tab').text('Patient Data (0)');
                return;
            }
            
            let html = `
                <div class="table-responsive">
                    <table class="table table-striped table-hover" id="member-patient-data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Value</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            memberData.forEach(data => {
                html += `
                    <tr>
                        <td>${data.id}</td>
                        <td>${formatDate(data.date)}</td>
                        <td>${data.data_type || 'N/A'}</td>
                        <td>${data.value || 'N/A'}</td>
                        <td>${data.notes || 'N/A'}</td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
            
            $('#patient-data-content').html(html);
            $('#patient-data-tab').text(`Patient Data (${memberData.length})`);
            
            // Initialize DataTable using the enhanced initDataTable function
            initDataTable('member-patient-data-table', {
                order: [[1, 'desc']], // Sort by date (descending)
                pageLength: 10
            });
        }).fail(function() {
            $('#patient-data-content').html('<div class="alert alert-danger">Failed to load patient-generated data.</div>');
            $('#patient-data-tab').text('Patient Data (!)');
        });
    }
    
    // Function to render care episodes tab
    function renderCareEpisodesTab(episodes) {
        if (episodes.length === 0) {
            $('#care-episodes-content').html('<div class="alert alert-info">No care episodes found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-care-episodes-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Episode Type</th>
                            <th>Start Date</th>
                            <th>Status</th>
                            <th>Primary Condition</th>
                            <th>Events</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        episodes.forEach(episode => {
            let statusBadge = 'bg-secondary';
            if (episode.status === 'active') statusBadge = 'bg-success';
            else if (episode.status === 'completed') statusBadge = 'bg-primary';
            else if (episode.status === 'cancelled') statusBadge = 'bg-danger';
            
            html += `
                <tr>
                    <td>${episode.id}</td>
                    <td>${episode.episode_type || 'N/A'}</td>
                    <td>${formatDate(episode.start_date)}</td>
                    <td><span class="badge ${statusBadge}">${episode.status || 'N/A'}</span></td>
                    <td>${episode.primary_condition ? episode.primary_condition.name : 'N/A'}</td>
                    <td>${episode.events ? episode.events.length : 0}</td>
                    <td>
                        <a href="/care-episodes?id=${episode.id}" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> View
                        </a>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#care-episodes-content').html(html);
        
        // Initialize DataTable
        initDataTable('member-care-episodes-table', {
            order: [[2, 'desc']], // Sort by start date (descending)
            pageLength: 10
        });
    }
    
    // Function to render SDOH assessments tab
    function renderSdohTab(assessments) {
        if (assessments.length === 0) {
            $('#sdoh-content').html('<div class="alert alert-info">No SDOH assessments found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-sdoh-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Assessment Date</th>
                            <th>Provider</th>
                            <th>Overall Risk Level</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        assessments.forEach(assessment => {
            let riskBadge = 'bg-secondary';
            if (assessment.overall_risk_level === 'low') riskBadge = 'bg-success';
            else if (assessment.overall_risk_level === 'moderate') riskBadge = 'bg-warning';
            else if (assessment.overall_risk_level === 'high') riskBadge = 'bg-danger';
            
            html += `
                <tr>
                    <td>${assessment.id}</td>
                    <td>${formatDate(assessment.assessment_date)}</td>
                    <td>${assessment.provider_id || 'N/A'}</td>
                    <td><span class="badge ${riskBadge}">${assessment.overall_risk_level || 'N/A'}</span></td>
                    <td>
                        <a href="/sdoh-assessments?id=${assessment.id}" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> View
                        </a>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#sdoh-content').html(html);
        
        // Initialize DataTable
        initDataTable('member-sdoh-table', {
            order: [[1, 'desc']], // Sort by assessment date (descending)
            pageLength: 10
        });
    }
    
    // Function to render risk assessments tab
    function renderRiskTab(assessments) {
        if (assessments.length === 0) {
            $('#risk-content').html('<div class="alert alert-info">No risk assessments found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-risk-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Assessment Date</th>
                            <th>Overall Score</th>
                            <th>Risk Level</th>
                            <th>Stratification</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        assessments.forEach(assessment => {
            let riskBadge = 'bg-secondary';
            if (assessment.overall_risk && assessment.overall_risk.level) {
                if (assessment.overall_risk.level === 'low') riskBadge = 'bg-success';
                else if (assessment.overall_risk.level === 'moderate') riskBadge = 'bg-warning';
                else if (assessment.overall_risk.level === 'high') riskBadge = 'bg-danger';
            }
            
            html += `
                <tr>
                    <td>${assessment.id}</td>
                    <td>${formatDate(assessment.assessment_date)}</td>
                    <td>${assessment.overall_risk && assessment.overall_risk.score ? assessment.overall_risk.score.toFixed(1) : 'N/A'}</td>
                    <td><span class="badge ${riskBadge}">${assessment.overall_risk && assessment.overall_risk.level ? assessment.overall_risk.level : 'N/A'}</span></td>
                    <td>${assessment.overall_risk && assessment.overall_risk.stratification ? assessment.overall_risk.stratification : 'N/A'}</td>
                    <td>
                        <a href="/risk-assessments?id=${assessment.id}" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> View
                        </a>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#risk-content').html(html);
        
        // Initialize DataTable
        initDataTable('member-risk-table', {
            order: [[1, 'desc']], // Sort by assessment date (descending)
            pageLength: 10
        });
    }
    
    // Function to render pharmacy claims tab
    function renderPharmacyTab(claims) {
        if (!claims || claims.length === 0) {
            $('#pharmacy-content').html('<div class="alert alert-info">No pharmacy claims found for this member.</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover" id="member-pharmacy-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Drug Name</th>
                            <th>Fill Date</th>
                            <th>Days Supply</th>
                            <th>Quantity</th>
                            <th>Total Cost</th>
                            <th>Member Cost</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        claims.forEach(claim => {
            let statusBadge = 'bg-secondary';
            if (claim.status === 'paid') statusBadge = 'bg-success';
            else if (claim.status === 'rejected') statusBadge = 'bg-danger';
            else if (claim.status === 'pending') statusBadge = 'bg-warning';
            
            html += `
                <tr>
                    <td>${claim.id}</td>
                    <td>${claim.drug_name || 'N/A'}</td>
                    <td>${formatDate(claim.fill_date)}</td>
                    <td>${claim.days_supply || 'N/A'}</td>
                    <td>${claim.quantity || 'N/A'}</td>
                    <td>${formatCurrency(claim.total_cost)}</td>
                    <td>${formatCurrency(claim.member_cost)}</td>
                    <td><span class="badge ${statusBadge}">${claim.status || 'Unknown'}</span></td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        $('#pharmacy-content').html(html);
        
        // Initialize DataTable
        initDataTable('member-pharmacy-table', {
            order: [[2, 'desc']], // Sort by fill date (descending)
            pageLength: 10
        });
    }
});
