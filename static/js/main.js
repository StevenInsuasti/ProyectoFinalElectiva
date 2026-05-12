/**
 * Sistema de Reservas de Espacios - JavaScript global
 * Integrante 1 - Módulo de Autenticación
 */

// Auto-cerrar alertas después de 5 segundos
document.addEventListener('DOMContentLoaded', function () {
    const alertas = document.querySelectorAll('.alert.alert-dismissible');
    alertas.forEach(function (alerta) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alerta);
            bsAlert.close();
        }, 5000);
    });
});

// Confirmación antes de enviar formularios de eliminación/toggle
document.addEventListener('DOMContentLoaded', function () {
    const formsConfirm = document.querySelectorAll('[data-confirm]');
    formsConfirm.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const mensaje = form.getAttribute('data-confirm');
            if (!confirm(mensaje)) {
                e.preventDefault();
            }
        });
    });
});
