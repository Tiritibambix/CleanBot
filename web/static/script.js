document.addEventListener('DOMContentLoaded', function() {
    // Validation des IDs de canaux
    const channelsTextarea = document.getElementById('channels');
    channelsTextarea.addEventListener('input', function() {
        const lines = this.value.split('\n');
        const validLines = lines.filter(line => {
            const trimmed = line.trim();
            return trimmed === '' || /^\d+$/.test(trimmed);
        });
        this.value = validLines.join('\n');
    });

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
