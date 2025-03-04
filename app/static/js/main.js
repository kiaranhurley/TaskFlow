// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Task completion toggle
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    if (taskCheckboxes) {
        taskCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                this.closest('form').submit();
            });
        });
    }

    // Confirm delete
    const deleteButtons = document.querySelectorAll('.delete-btn');
    if (deleteButtons) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this task?')) {
                    e.preventDefault();
                }
            });
        });
    }

    // Due date highlighting
    const dueDates = document.querySelectorAll('.due-date');
    if (dueDates) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        dueDates.forEach(dateElement => {
            const dueDate = new Date(dateElement.dataset.date);
            dueDate.setHours(0, 0, 0, 0);
            
            // If due date is today
            if (dueDate.getTime() === today.getTime()) {
                dateElement.classList.add('due-today');
            }
            // If due date is in the past
            else if (dueDate < today) {
                dateElement.classList.add('overdue');
            }
        });
    }
}); 