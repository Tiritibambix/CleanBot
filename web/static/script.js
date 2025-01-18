document.addEventListener('DOMContentLoaded', function() {
    // Initialisation de l'affichage des options de planification
    toggleScheduleOptions();

    // Animation des messages flash
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            alert.classList.add('alert-dismissible', 'fade', 'show');
            const closeButton = document.createElement('button');
            closeButton.className = 'btn-close';
            closeButton.setAttribute('data-bs-dismiss', 'alert');
            closeButton.setAttribute('aria-label', 'Close');
            alert.appendChild(closeButton);
        }
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Force 24-hour format for time input
    const timeInput = document.getElementById('interval_time');
    if (timeInput) {
        timeInput.addEventListener('change', function() {
            const time = this.value;
            if (time) {
                const [hours, minutes] = time.split(':');
                const formattedTime = `${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}`;
                this.value = formattedTime;
            }
        });
    }
});
