document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.componente-checkbox');
    const maxMsg = document.getElementById('maxMsg');
    const form = document.getElementById('componentesForm');
    const btnAceptar = document.getElementById('btnAceptar');
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
    const btnConfirmar = document.getElementById('confirmarSeleccion');

    function validarSeleccion() {
        const seleccionados = document.querySelectorAll('.componente-checkbox:checked');
        if (seleccionados.length > 2) {
            maxMsg.style.display = 'block';
            btnAceptar.disabled = true;
        } else {
            maxMsg.style.display = 'none';
            btnAceptar.disabled = false;
        }
    }

    checkboxes.forEach(cb => {
        cb.addEventListener('change', function() {
            const seleccionados = document.querySelectorAll('.componente-checkbox:checked');
            if (seleccionados.length > 2) {
                this.checked = false;
            }
            validarSeleccion();
        });
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        if (document.querySelectorAll('.componente-checkbox:checked').length === 0) {
            maxMsg.textContent = 'Debes seleccionar al menos un componente.';
            maxMsg.style.display = 'block';
            return;
        }
        confirmModal.show();
    });

    btnConfirmar.addEventListener('click', function() {
        form.submit();
    });
}); 