// HandyConnect Frontend JavaScript
// Basic functionality for the task management interface

document.addEventListener('DOMContentLoaded', function() {
    console.log('HandyConnect frontend loaded');
    
    // Initialize any frontend functionality here
    initializeTaskManagement();
});

function initializeTaskManagement() {
    // Add any task management UI functionality
    console.log('Task management initialized');
}

// API helper functions
async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching tasks:', error);
        return null;
    }
}

async function updateTask(taskId, updates) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updates)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error updating task:', error);
        return null;
    }
}

