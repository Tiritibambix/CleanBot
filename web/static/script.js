document.addEventListener('DOMContentLoaded', function() {
    // Initialisation de l'affichage des options de planification
    toggleScheduleOptions();

    // Animation des messages flash
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    });
});
