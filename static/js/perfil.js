// Funcionalidades del perfil docente
document.addEventListener('DOMContentLoaded', function() {
    // Confirmación antes de eliminar archivos
    const deleteButtons = document.querySelectorAll('.btn-delete-file');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro que desea eliminar este archivo?')) {
                e.preventDefault();
            }
        });
    });
    
    // Mostrar nombre del archivo seleccionado
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'Ningún archivo seleccionado';
            const label = this.previousElementSibling;
            
            if (label && label.tagName === 'LABEL') {
                const fileNameSpan = label.querySelector('.file-name') || document.createElement('span');
                fileNameSpan.className = 'file-name';
                fileNameSpan.textContent = ` - ${fileName}`;
                
                if (!label.querySelector('.file-name')) {
                    label.appendChild(fileNameSpan);
                }
            }
        });
    });
});