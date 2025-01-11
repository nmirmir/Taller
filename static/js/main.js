// Global variables for storing data
let zones = [];
let categories = [];
let statuses = [];

// Cache for API data
let zonesCache = null;
let objectsCache = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Load all necessary data
        const [zonesResponse, categoriesResponse, statusesResponse] = await Promise.all([
            fetch('/api/zones'),
            fetch('/api/categories'),
            fetch('/api/statuses')
        ]);
        
        zones = await zonesResponse.json();
        categories = await categoriesResponse.json();
        statuses = await statusesResponse.json();
        
        // Load objects after loading the supporting data
        await loadObjects();
        
    } catch (error) {
        console.error('Error loading initial data:', error);
        showAlert('Error loading data', 'danger');
    }
});

// API Calls
async function fetchAPI(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    if (data) {
        options.body = JSON.stringify(data);
    }
    const response = await fetch(`/api/${endpoint}`, options);
    return response.json();
}

// Data Loading Functions
async function loadObjects() {
    try {
        const response = await fetch('/api/objects');
        if (!response.ok) throw new Error('Failed to fetch objects');
        const objects = await response.json();
        
        const tableBody = document.querySelector('#objectsTable tbody');
        if (!tableBody) {
            console.error('Table body not found');
            return;
        }
        
        tableBody.innerHTML = '';
        
        if (objects.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="9" class="text-center">No objects found</td></tr>';
            return;
        }
        
        objects.forEach(obj => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${obj.id}</td>
                <td>${obj.name}</td>
                <td>${obj.description || ''}</td>
                <td>${obj.zone_name || ''}</td>
                <td>${obj.category || ''}</td>
                <td>${obj.price || 0}</td>
                <td>${obj.quantity || 0}</td>
                <td>${obj.status || 'Available'}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="editObject(${obj.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteObject(${obj.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading objects:', error);
        showAlert('Error loading objects: ' + error.message, 'danger');
    }
}

async function loadZones() {
    try {
        const response = await fetch('/api/zones');
        if (!response.ok) {
            throw new Error('Failed to fetch zones');
        }
        const zones = await response.json();
        
        const tableBody = document.querySelector('#zonesTable tbody');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        zones.forEach(zone => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${zone.id}</td>
                <td>${zone.name}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteZone(${zone.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading zones:', error);
        showAlert('Error loading zones', 'danger');
    }
}

async function loadCategories() {
    categories = await fetchAPI('categories');
}

async function loadStatuses() {
    statuses = await fetchAPI('statuses');
}

// Display Functions
function displayObjects(objects) {
    const container = document.getElementById('objectsList');
    if (!objects || objects.length === 0) {
        container.innerHTML = '<p class="text-muted">No objects found</p>';
        return;
    }

    let html = '<div class="table-responsive"><table class="table table-striped">';
    html += `
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
    `;

    objects.forEach(obj => {
        html += `
            <tr>
                <td>${obj[0]}</td>
                <td>${obj[1]}</td>
                <td>${obj[2]}</td>
                <td>$${obj[3]}</td>
                <td>${obj[4]}</td>
                <td>${obj[5]}</td>
                <td>
                    <button class="btn btn-sm btn-primary me-1" onclick="showEditObjectModal(${obj[0]})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteObject(${obj[0]})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

function displayZones(zones) {
    const container = document.getElementById('zonesList');
    if (!zones || zones.length === 0) {
        container.innerHTML = '<p class="text-muted">No zones found</p>';
        return;
    }

    let html = '<div class="table-responsive"><table class="table table-striped">';
    html += `
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
    `;

    zones.forEach(zone => {
        html += `
            <tr>
                <td>${zone[0]}</td>
                <td>${zone[1]}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteZone(${zone[0]})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Modal Functions
function showAddObjectModal() {
    loadZoneDropdown();
    const modal = new bootstrap.Modal(document.getElementById('addObjectModal'));
    modal.show();
}

// Function to show edit object modal
async function showEditObjectModal(objectId) {
    console.log('Opening edit modal for object:', objectId);
    
    try {
        // Fetch object details
        const response = await fetch(`/api/objects/${objectId}`);
        const object = await response.json();
        
        // Populate the edit form
        const form = document.getElementById('editObjectForm');
        form.dataset.objectId = objectId;
        form.name.value = object.name;
        form.description.value = object.description;
        form.price.value = object.price;
        form.quantity.value = object.quantity;
        
        // Populate dropdowns
        const zoneSelect = form.querySelector('[name="zone"]');
        const categorySelect = form.querySelector('[name="category"]');
        const statusSelect = form.querySelector('[name="status"]');
        
        // Clear and populate zone dropdown
        zoneSelect.innerHTML = zones.map(zone => 
            `<option value="${zone[0]}" ${zone[0] == object.zone_id ? 'selected' : ''}>
                ${zone[1]}
            </option>`
        ).join('');
        
        // Clear and populate category dropdown
        categorySelect.innerHTML = categories.map(category => 
            `<option value="${category[0]}" ${category[0] == object.category_id ? 'selected' : ''}>
                ${category[1]}
            </option>`
        ).join('');
        
        // Clear and populate status dropdown
        statusSelect.innerHTML = statuses.map(status => 
            `<option value="${status[0]}" ${status[0] == object.status_id ? 'selected' : ''}>
                ${status[1]}
            </option>`
        ).join('');
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('editObjectModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error loading object details', 'danger');
    }
}

function showBulkDeleteModal(type) {
    const modal = new bootstrap.Modal(document.getElementById('bulkDeleteModal'));
    const titleElement = document.getElementById('bulkDeleteTitle');
    const targetSelect = document.getElementById('bulkDeleteTarget');
    
    // Update modal based on type
    switch(type) {
        case 'zone':
            titleElement.textContent = 'Delete All Objects in Zone';
            populateZoneSelect(targetSelect);
            break;
        case 'category':
            titleElement.textContent = 'Delete All Objects in Category';
            populateCategorySelect(targetSelect);
            break;
        case 'all':
            titleElement.textContent = 'Delete All Objects';
            targetSelect.style.display = 'none';
            break;
    }
    
    modal.show();
}

// Action Functions
async function addObject() {
    try {
        const zonesResponse = await fetch('/api/zones');
        if (!zonesResponse.ok) throw new Error('Failed to fetch zones');
        const zones = await zonesResponse.json();
        
        const { value: formValues } = await Swal.fire({
            title: 'Add New Object',
            html: `
                <input id="name" class="swal2-input" placeholder="Name">
                <input id="description" class="swal2-input" placeholder="Description">
                <select id="zone" class="swal2-input">
                    <option value="">Select Zone</option>
                    ${zones.map(zone => `<option value="${zone.id}">${zone.name}</option>`).join('')}
                </select>
                <input id="price" type="number" step="0.01" class="swal2-input" placeholder="Price">
                <input id="quantity" type="number" class="swal2-input" placeholder="Quantity">
                <select id="status" class="swal2-input">
                    <option value="Available">Available</option>
                    <option value="In Use">In Use</option>
                    <option value="Maintenance">Maintenance</option>
                </select>
                <textarea id="comment" class="swal2-textarea" placeholder="Add a comment (optional)"></textarea>
            `,
            focusConfirm: false,
            showCancelButton: true,
            preConfirm: () => {
                const name = document.getElementById('name').value;
                if (!name) {
                    Swal.showValidationMessage('Please enter a name');
                    return false;
                }
                
                return {
                    name: name,
                    description: document.getElementById('description').value,
                    zone_id: document.getElementById('zone').value,
                    price: document.getElementById('price').value || 0,
                    quantity: document.getElementById('quantity').value || 0,
                    status: document.getElementById('status').value || 'Available',
                    comment: document.getElementById('comment').value
                };
            }
        });

        if (formValues) {
            const response = await fetch('/api/objects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formValues)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to add object');
            }

            await loadObjects();
            showAlert('Object added successfully', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error: ' + error.message, 'danger');
    }
}

async function deleteObject(objectId) {
    if (!confirm('Are you sure you want to delete this object?')) {
        return;
    }

    try {
        // First delete the object
        const deleteResponse = await fetch(`/api/objects/${objectId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!deleteResponse.ok) {
            throw new Error(`HTTP error! status: ${deleteResponse.status}`);
        }

        // After successful deletion, ask for comment
        const { isConfirmed: wantsToComment } = await Swal.fire({
            title: 'Add a Comment?',
            text: 'Would you like to add a comment about this deletion?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Yes',
            cancelButtonText: 'No'
        });

        if (wantsToComment) {
            const { value: comment } = await Swal.fire({
                title: 'Enter Comment',
                input: 'textarea',
                inputLabel: 'Your comment',
                inputPlaceholder: 'Type your comment here...',
                showCancelButton: true,
                inputValidator: (value) => {
                    if (!value) {
                        return 'Please enter a comment';
                    }
                }
            });

            if (comment) {
                // Add to history with comment
                await fetch('/api/history', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        object_id: objectId,
                        action_type: 'DELETE',
                        comment: comment
                    })
                });
            }
        }

        clearCache();
        await loadObjects();
        showAlert('Object deleted successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error deleting object: ' + error.message, 'danger');
    }
}

// Function to delete a zone
async function deleteZone(zoneId) {
    try {
        if (!confirm('Are you sure you want to delete this zone?')) {
            return;
        }

        const response = await fetch(`/api/zones/${zoneId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete zone');
        }

        // Ask for action type
        const actionTypeResult = await Swal.fire({
            title: 'Select Action Type',
            html: `
                <div style="text-align: left; margin: 20px;">
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="radio" name="actionType" id="deleteAction" value="DELETE">
                        <label class="form-check-label" for="deleteAction">
                            Delete
                        </label>
                    </div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Continue',
            preConfirm: () => {
                const selected = document.querySelector('input[name="actionType"]:checked');
                if (!selected) {
                    Swal.showValidationMessage('Please select an action type');
                    return false;
                }
                return selected.value;
            }
        });

        if (actionTypeResult.isConfirmed) {
            // Add to history
            await fetch('/api/history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    zone_id: zoneId,
                    action_type: 'DELETE',
                    comment: null
                })
            });
        }

        await loadZones();
        showAlert('Zone deleted successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error deleting zone: ' + error.message, 'danger');
    }
}

// Utility Functions
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
}

function populateDropdowns() {
    console.log('Populating dropdowns');
    console.log('Zones:', zones);
    console.log('Categories:', categories);
    console.log('Statuses:', statuses);
    
    const zoneSelect = document.getElementById('zone');
    const categorySelect = document.getElementById('category');
    const statusSelect = document.getElementById('status');
    
    if (zoneSelect && zones.length) {
        zoneSelect.innerHTML = zones.map(zone => 
            `<option value="${zone[0]}">${zone[1]}</option>`
        ).join('');
    }
    
    if (categorySelect && categories.length) {
        categorySelect.innerHTML = categories.map(category => 
            `<option value="${category[0]}">${category[1]}</option>`
        ).join('');
    }
    
    if (statusSelect && statuses.length) {
        statusSelect.innerHTML = statuses.map(status => 
            `<option value="${status[0]}">${status[1]}</option>`
        ).join('');
    }
}

// Function to show add zone modal
function showAddZoneModal() {
    const modal = new bootstrap.Modal(document.getElementById('addZoneModal'));
    modal.show();
}

// Function to add a new zone
async function addZone(event) {
    event.preventDefault();
    const form = event.target;
    const zoneName = form.zoneName.value.trim();

    try {
        const response = await fetch('/api/zones', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: zoneName })
        });

        if (!response.ok) {
            throw new Error('Failed to add zone');
        }

        const result = await response.json();
        
        // Ask for action type
        const actionTypeResult = await Swal.fire({
            title: 'Select Action Type',
            html: `
                <div style="text-align: left; margin: 20px;">
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="radio" name="actionType" id="createAction" value="CREATE">
                        <label class="form-check-label" for="createAction">
                            Create
                        </label>
                    </div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Continue',
            preConfirm: () => {
                const selected = document.querySelector('input[name="actionType"]:checked');
                if (!selected) {
                    Swal.showValidationMessage('Please select an action type');
                    return false;
                }
                return selected.value;
            }
        });

        if (actionTypeResult.isConfirmed) {
            await addHistoryEntry(result.id, actionTypeResult.value);
        }

        form.reset();
        const modal = bootstrap.Modal.getInstance(document.getElementById('addZoneModal'));
        modal.hide();
        await loadZones();
        showAlert('Zone added successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error adding zone: ' + error.message, 'danger');
    }
}

// Make sure the Add Zone modal is defined in your HTML
function addZoneModalHtml() {
    const modalHtml = `
        <div class="modal fade" id="addZoneModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Zone</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form onsubmit="addZone(event)">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="zoneName" class="form-label">Zone Name</label>
                                <input type="text" class="form-control" id="zoneName" name="zoneName" required>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">Add Zone</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Add the modal to the document if it doesn't exist
    if (!document.getElementById('addZoneModal')) {
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
}

// Function to update object
async function updateObject(event) {
    event.preventDefault();
    const form = event.target;
    const objectId = form.dataset.objectId;
    
    const data = {
        updates: {
            name: form.name.value,
            description: form.description.value,
            price: parseFloat(form.price.value),
            quantity: parseInt(form.quantity.value),
            category_id: parseInt(form.category.value),
            zone_id: parseInt(form.zone.value),
            status_id: parseInt(form.status.value)
        },
        modification_user: 'web_user'
    };
    
    try {
        const response = await fetch(`/api/objects/${objectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        await loadObjects();
        bootstrap.Modal.getInstance(document.getElementById('editObjectModal')).hide();
        showAlert('Object updated successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error updating object: ' + error.message, 'danger');
    }
}

// Tab handling
document.addEventListener('DOMContentLoaded', () => {
    // Show Objects tab by default
    document.querySelector('#objects').style.display = 'block';
    document.querySelector('#objects-tab').classList.add('active');
    
    // Hide other tabs
    document.querySelector('#zones').style.display = 'none';
    document.querySelector('#history').style.display = 'none';

    // Objects tab click
    document.querySelector('#objects-tab').addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.tab-pane').forEach(pane => pane.style.display = 'none');
        document.querySelector('#objects').style.display = 'block';
        document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
        e.target.classList.add('active');
        loadObjects();
    });

    // Zones tab click
    document.querySelector('#zones-tab').addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.tab-pane').forEach(pane => pane.style.display = 'none');
        document.querySelector('#zones').style.display = 'block';
        document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
        e.target.classList.add('active');
        loadZones();
    });

    // History tab click
    document.querySelector('#history-tab').addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.tab-pane').forEach(pane => pane.style.display = 'none');
        document.querySelector('#history').style.display = 'block';
        document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
        e.target.classList.add('active');
        loadHistory();
    });

    // Load initial data
    loadObjects();
    loadZones();
}); 

// Make sure the table exists in your HTML
document.addEventListener('DOMContentLoaded', function() {
    // Create table if it doesn't exist
    if (!document.querySelector('table')) {
        const container = document.querySelector('.container');
        container.innerHTML += `
            <table class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        `;
    }
    
    loadZones();  // Load zones when page loads
}); 

// Load zones when the zones tab is shown
document.querySelector('a[href="#zones"]').addEventListener('click', loadZones);

// Also load zones on initial page load if zones tab is active
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('#zones.active')) {
        loadZones();
    }
}); 

// Load objects when the objects tab is shown
document.querySelector('a[href="#objects"]').addEventListener('click', loadObjects);

// Also load objects on initial page load since objects tab is active by default
document.addEventListener('DOMContentLoaded', function() {
    loadObjects();
}); 

// Make sure objects are loaded when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, loading objects...'); // Debug log
    loadObjects();
}); 

// Add event listener for tab switching
document.addEventListener('DOMContentLoaded', function() {
    // Load initial content based on active tab
    if (document.querySelector('#zones.active')) {
        loadZones();
    } else if (document.querySelector('#objects.active')) {
        loadObjects();
    }
    
    // Add click handlers for tab switching
    document.querySelectorAll('a[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            if (event.target.getAttribute('href') === '#zones') {
                loadZones();
            } else if (event.target.getAttribute('href') === '#objects') {
                loadObjects();
            }
        });
    });
}); 

// Add this function to load zones into the dropdown
async function loadZoneDropdown() {
    try {
        const response = await fetch('/api/zones');
        const zones = await response.json();
        
        const zoneSelect = document.querySelector('#objectZone');
        zoneSelect.innerHTML = '<option value="">Select a zone</option>';
        
        zones.forEach(zone => {
            const option = document.createElement('option');
            option.value = zone.id;
            option.textContent = zone.name;
            zoneSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading zones for dropdown:', error);
        showAlert('Error loading zones', 'danger');
    }
} 

// Clear cache when adding/updating/deleting
function clearCache() {
    zonesCache = null;
    objectsCache = null;
} 

// Function to add history entry
async function addHistoryEntry(objectId, actionType, comment) {
    try {
        const response = await fetch('/api/history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                object_id: objectId,
                action_type: actionType,
                comment: comment
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save history');
        }

        return await response.json();
    } catch (error) {
        console.error('Error saving history:', error);
        throw error;
    }
} 

// Call loadZones when the page loads
document.addEventListener('DOMContentLoaded', loadZones); 

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) throw new Error('Failed to fetch history');
        const history = await response.json();
        
        const tableBody = document.querySelector('#historyTable tbody');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        history.forEach(entry => {
            const row = document.createElement('tr');
            const date = new Date(entry.modification_date).toLocaleString();
            row.innerHTML = `
                <td>${date}</td>
                <td>${entry.zone_name || 'N/A'}</td>
                <td>${entry.action_type}</td>
                <td>${entry.comment || ''}</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error loading history', 'danger');
    }
}

// Add this to your existing tab handling code
document.querySelector('#history-tab').addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelectorAll('.tab-pane').forEach(pane => pane.style.display = 'none');
    document.querySelector('#history').style.display = 'block';
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    e.target.classList.add('active');
    loadHistory();
}); 

// Add these bulk operation functions
async function deleteZoneObjects() {
    try {
        const zones = await fetch('/api/zones').then(r => r.json());
        
        const { value: formValues } = await Swal.fire({
            title: 'Delete Zone Objects',
            html: `
                <select id="zoneSelect" class="form-control mb-3">
                    <option value="">Select a zone</option>
                    ${zones.map(z => `<option value="${z.id}">${z.name}</option>`).join('')}
                </select>
                <input id="comment" class="form-control mb-3" placeholder="Add a comment (optional)">
                <input id="password" type="password" class="form-control" placeholder="Enter admin password">
            `,
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: 'Delete',
            preConfirm: () => {
                const zoneId = document.getElementById('zoneSelect').value;
                const comment = document.getElementById('comment').value;
                const password = document.getElementById('password').value;
                
                if (!zoneId) {
                    Swal.showValidationMessage('Please select a zone');
                    return false;
                }
                if (!password) {
                    Swal.showValidationMessage('Please enter the password');
                    return false;
                }
                return { zoneId, comment, password };
            }
        });

        if (formValues) {
            console.log('Sending data:', {  // Debug log
                password: formValues.password,
                comment: formValues.comment
            });
            
            const response = await fetch(`/api/zones/${formValues.zoneId}/objects`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    password: formValues.password,
                    comment: formValues.comment
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to delete zone objects');
            }

            await loadObjects();
            showAlert('Zone objects deleted successfully', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error: ' + error.message, 'danger');
    }
}

async function deleteAllObjects() {
    try {
        const result = await Swal.fire({
            title: 'Are you sure?',
            text: "This will delete ALL objects! This action cannot be undone!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            confirmButtonText: 'Yes, delete all!'
        });

        if (result.isConfirmed) {
            const { value: password } = await Swal.fire({
                title: 'Enter Admin Password',
                input: 'password',
                inputPlaceholder: 'Enter password',
                showCancelButton: true,
                inputValidator: (value) => {
                    if (!value) {
                        return 'You need to enter the password!';
                    }
                }
            });

            if (password) {
                const response = await fetch('/api/objects/all', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password })
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to delete all objects');
                }

                showAlert('All objects deleted successfully', 'success');
                loadObjects();
            }
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error: ' + error.message, 'danger');
    }
}

// Similar implementations for deleteCategoryObjects and deleteStatusObjects
async function deleteCategoryObjects() {
    // Implementation similar to deleteZoneObjects but with categories
}

async function deleteStatusObjects() {
    // Implementation similar to deleteZoneObjects but with statuses
}

// Update tab handling to include bulk operations
document.querySelector('#bulk-operations-tab').addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelectorAll('.tab-pane').forEach(pane => pane.style.display = 'none');
    document.querySelector('#bulk-operations').style.display = 'block';
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    e.target.classList.add('active');
}); 

// Add event listeners for the buttons
document.getElementById('addZoneBtn').addEventListener('click', () => {
    const modal = new bootstrap.Modal(document.getElementById('addZoneModal'));
    modal.show();
});

document.getElementById('addObjectBtn').addEventListener('click', () => {
    const modal = new bootstrap.Modal(document.getElementById('addObjectModal'));
    modal.show();
});

// Add form submit handlers
document.querySelector('#addZoneModal form').addEventListener('submit', addZone);
document.querySelector('#addObjectModal form').addEventListener('submit', addObject); 

// Function to populate zone dropdown
async function populateZoneDropdown() {
    try {
        const response = await fetch('/api/zones');
        if (!response.ok) {
            throw new Error('Failed to fetch zones');
        }
        const zones = await response.json();
        
        const zoneSelect = document.getElementById('objectZone');
        zoneSelect.innerHTML = '<option value="">Select a zone</option>';
        
        zones.forEach(zone => {
            const option = document.createElement('option');
            option.value = zone.id;
            option.textContent = zone.name;
            zoneSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading zones:', error);
        showAlert('Error loading zones for dropdown', 'danger');
    }
}

// Add event listener for the Add Object button
document.getElementById('addObjectBtn').addEventListener('click', () => {
    populateZoneDropdown(); // Populate zones when modal opens
    const modal = new bootstrap.Modal(document.getElementById('addObjectModal'));
    modal.show();
});

// Make sure the object form has the correct select element
document.addEventListener('DOMContentLoaded', () => {
    // Existing DOMContentLoaded code...
    
    // Add this to handle zone loading when switching to Objects tab
    document.querySelector('#objects-tab').addEventListener('click', () => {
        loadObjects();
        populateZoneDropdown();
    });
}); 

// Add edit object function
async function editObject(objectId) {
    try {
        // Get the object data from the table row
        const row = document.querySelector(`tr[data-object-id="${objectId}"]`);
        const object = {
            id: objectId,
            name: row.cells[1].textContent,
            description: row.cells[2].textContent,
            zone_name: row.cells[3].textContent,
            price: row.cells[5].textContent,
            quantity: row.cells[6].textContent,
            status: row.cells[7].textContent
        };

        // Populate zones dropdown
        await populateZoneDropdown();

        const { value: formValues } = await Swal.fire({
            title: 'Edit Object',
            html: `
                <form id="editForm" class="text-start">
                    <div class="mb-3">
                        <label class="form-label">Name</label>
                        <input type="text" class="form-control" id="editName" value="${object.name}" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea class="form-control" id="editDescription">${object.description}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Zone</label>
                        <select class="form-control" id="editZone" required>
                            ${document.getElementById('objectZone').innerHTML}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Price</label>
                        <input type="number" class="form-control" id="editPrice" value="${object.price}" step="0.01" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Quantity</label>
                        <input type="number" class="form-control" id="editQuantity" value="${object.quantity}" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Status</label>
                        <select class="form-control" id="editStatus" required>
                            <option value="Available" ${object.status === 'Available' ? 'selected' : ''}>Available</option>
                            <option value="In Use" ${object.status === 'In Use' ? 'selected' : ''}>In Use</option>
                            <option value="Maintenance" ${object.status === 'Maintenance' ? 'selected' : ''}>Maintenance</option>
                        </select>
                    </div>
                </form>
            `,
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: 'Save',
            preConfirm: () => {
                return {
                    name: document.getElementById('editName').value,
                    description: document.getElementById('editDescription').value,
                    zone_id: parseInt(document.getElementById('editZone').value),
                    price: parseFloat(document.getElementById('editPrice').value),
                    quantity: parseInt(document.getElementById('editQuantity').value),
                    status: document.getElementById('editStatus').value
                };
            }
        });

        if (formValues) {
            console.log('Sending update:', formValues); // Debug log
            const updateResponse = await fetch(`/api/objects/${objectId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formValues)
            });

            if (!updateResponse.ok) {
                const errorData = await updateResponse.json();
                throw new Error(errorData.error || 'Failed to update object');
            }

            await loadObjects();
            showAlert('Object updated successfully', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error updating object: ' + error.message, 'danger');
    }
} 

// Make sure objects load when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, loading objects...'); // Debug log
    loadObjects();
});

// Also add this to ensure the table exists
document.addEventListener('DOMContentLoaded', () => {
    if (!document.querySelector('#objectsTable')) {
        const container = document.querySelector('.container');
        container.innerHTML += `
            <table id="objectsTable" class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Zone</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Quantity</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        `;
    }
    loadObjects();
}); 