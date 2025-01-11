// Global variables for storing data
let zones = [];
let categories = [];
let statuses = [];

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
        console.log('Loading objects...'); // Debug log
        const response = await fetch('/api/objects');
        console.log('Response received:', response); // Debug log
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const objects = await response.json();
        console.log('Objects loaded:', objects); // Debug log
        
        const tableBody = document.querySelector('#objectsTable tbody');
        if (!tableBody) {
            console.error('Objects table body not found');
            return;
        }
        
        tableBody.innerHTML = '';
        
        if (objects.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="7" class="text-center">No objects found</td>';
            tableBody.appendChild(row);
            return;
        }
        
        objects.forEach(obj => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${obj.id}</td>
                <td>${obj.name}</td>
                <td>${obj.description || ''}</td>
                <td>${obj.price}</td>
                <td>${obj.quantity}</td>
                <td>${obj.status}</td>
                <td>
                    <button class="btn btn-danger" onclick="deleteObject(${obj.id})">
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
        console.log('Loading zones...'); // Debug log
        const response = await fetch('/api/zones');
        console.log('Zones response:', response); // Debug log
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const zones = await response.json();
        console.log('Zones loaded:', zones); // Debug log
        
        const tableBody = document.querySelector('#zonesTable tbody');
        if (!tableBody) {
            console.error('Zones table body not found');
            return;
        }
        
        tableBody.innerHTML = '';
        
        if (zones.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="3" class="text-center">No zones found</td>';
            tableBody.appendChild(row);
            return;
        }
        
        zones.forEach(zone => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${zone.id}</td>
                <td>${zone.name}</td>
                <td>
                    <button class="btn btn-danger" onclick="deleteZone(${zone.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading zones:', error);
        showAlert('Error loading zones: ' + error.message, 'danger');
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
async function addObject(event) {
    event.preventDefault();
    const form = event.target;
    
    const formData = {
        name: form.name.value.trim(),
        description: form.description.value.trim(),
        zone_id: parseInt(form.zone_id.value),
        category_id: parseInt(form.category_id.value),
        price: parseFloat(form.price.value),
        quantity: parseInt(form.quantity.value),
        status: form.status.value
    };

    try {
        const response = await fetch('/api/objects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.error || 'Failed to add object');
        }

        await loadObjects();
        const modal = bootstrap.Modal.getInstance(document.getElementById('addObjectModal'));
        modal.hide();
        form.reset();
        showAlert('Object added successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error adding object: ' + error.message, 'danger');
    }
}

async function deleteObject(objectId) {
    if (!confirm('Are you sure you want to delete this object?')) {
        return;
    }

    try {
        const response = await fetch(`/api/objects/${objectId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ deletion_user: 'web_user' })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        await loadObjects();
        showAlert('Object deleted successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error deleting object: ' + error.message, 'danger');
    }
}

// Function to delete a zone
async function deleteZone(zoneId) {
    if (!confirm('Are you sure you want to delete this zone? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/zones/${zoneId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
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
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.nav-tabs'));
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
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
    
    const zoneName = document.querySelector('#addZoneModal input[name="zoneName"]').value.trim();
    
    if (!zoneName) {
        showAlert('Zone name cannot be empty', 'danger');
        return;
    }

    try {
        const response = await fetch('/api/zones', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: zoneName
            })
        });

        // First check if the response is ok
        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage;
            try {
                const errorJson = JSON.parse(errorText);
                errorMessage = errorJson.error;
            } catch (e) {
                errorMessage = errorText;
            }
            throw new Error(errorMessage || 'Failed to add zone');
        }

        // Only try to parse JSON if response was ok
        const result = await response.json();
        
        // Refresh zones list
        await loadZones();
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('addZoneModal'));
        modal.hide();
        document.querySelector('#addZoneModal form').reset();
        
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

// Add event listener for tab changes
document.addEventListener('DOMContentLoaded', function() {
    addZoneModalHtml();  // Add the modal HTML
    loadObjects();
    loadZones();
    
    // Load initial data
    loadObjects();
    loadZones();
    
    // Add tab change listeners
    const tabs = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target');
            if (targetId === '#objects') {
                loadObjects();
            } else if (targetId === '#zones') {
                loadZones();
            }
        });
    });
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