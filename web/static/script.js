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

    // Gestion des sélecteurs d'heure
    function updateTimeInput(hourId, minuteId, targetInput) {
        const hour = document.getElementById(hourId).value;
        const minute = document.getElementById(minuteId).value;
        document.getElementById(targetInput).value = `${hour}:${minute}`;
    }

    // Pour interval_time
    document.getElementById('interval_time_hour').addEventListener('change', () => {
        updateTimeInput('interval_time_hour', 'interval_time_minute', 'interval_time');
    });
    document.getElementById('interval_time_minute').addEventListener('change', () => {
        updateTimeInput('interval_time_hour', 'interval_time_minute', 'interval_time');
    });

    // Pour specific_time
    document.getElementById('specific_time_hour').addEventListener('change', () => {
        updateTimeInput('specific_time_hour', 'specific_time_minute', 'specific_time');
    });
    document.getElementById('specific_time_minute').addEventListener('change', () => {
        updateTimeInput('specific_time_hour', 'specific_time_minute', 'specific_time');
    });
});
