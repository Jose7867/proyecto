// Funcionalidades del panel de administración
document.addEventListener('DOMContentLoaded', function() {
    // Confirmación antes de eliminar docentes
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro que desea eliminar este docente?')) {
                e.preventDefault();
            }
        });
    });
    
    // Búsqueda en la tabla de docentes
    const searchInput = document.getElementById('searchDocentes');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('.docentes-table tbody tr');
            
            rows.forEach(row => {
                const nombre = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                const email = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
                
                if (nombre.includes(searchTerm) || email.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});