# -*- coding: utf-8 -*-
"""Chaînes de l'interface web, en français et en anglais.

Toutes les clés doivent exister dans les deux langues. Les valeurs peuvent
contenir des emplacements `{nom}` remplis via `str.format(**kwargs)` (voir
`app.t()`), et peuvent contenir du HTML simple (elles sont marquées `|safe`
dans les templates, donc n'y mettez jamais de texte venant de l'utilisateur).
"""

SUPPORTED_LANGS = ('fr', 'en')
DEFAULT_LANG = 'fr'

TRANSLATIONS = {
    'fr': {
        # Page
        'page_title': 'Configuration CleanBot',
        'card_title': 'Configuration CleanBot',

        # Formulaire principal
        'label_token': 'Token Discord',
        'label_channels': 'IDs des canaux (un par ligne)',
        'help_channels': (
            "Entrez un ID de canal Discord par ligne. Ajoutez une description après "
            "<code>#</code> pour vous souvenir de quel canal il s'agit (elle est "
            "ignorée lors de la purge), par ex. :<br>"
            "<code>123456789012345678 # Annonces générales</code>"
        ),
        'label_max_messages': 'Nombre maximum de messages à supprimer',

        'label_schedule_type': 'Type de planification',
        'option_schedule_interval': 'Intervalle régulier',
        'option_schedule_specific': 'Jours spécifiques',
        'option_schedule_custom': 'Personnalisé',

        'label_interval': 'Intervalle',
        'option_interval_hourly': 'Toutes les heures',
        'option_interval_daily': 'Tous les jours',
        'option_interval_weekly': 'Toutes les semaines',
        'option_interval_biweekly': 'Toutes les deux semaines',
        'option_interval_monthly': 'Tous les mois',
        'label_exec_time': "Heure d'exécution",

        'label_weekdays': 'Jours de la semaine',
        'day_monday': 'Lundi',
        'day_tuesday': 'Mardi',
        'day_wednesday': 'Mercredi',
        'day_thursday': 'Jeudi',
        'day_friday': 'Vendredi',
        'day_saturday': 'Samedi',
        'day_sunday': 'Dimanche',

        'label_cron': 'Expression Cron',
        'help_cron': 'Format: minute heure jour mois jour_semaine (ex: */30 * * * * pour toutes les 30 minutes)',

        'btn_save': 'Sauvegarder la configuration',
        'btn_purge_now': 'Purger maintenant',
        'confirm_purge': 'Êtes-vous sûr de vouloir purger tous les canaux maintenant ?',

        # Validation / sauvegarde (web/app.py)
        'flash_token_required': 'Le token Discord est requis',
        'flash_invalid_channel_lines': (
            'Ligne(s) invalide(s) dans les IDs de canaux (avant le premier « # », '
            'il doit y avoir uniquement des chiffres) : {lines}'
        ),
        'flash_channel_required': 'Au moins un ID de canal est requis',
        'error_invalid_cron': 'Expression cron invalide',
        'flash_save_success': 'Configuration sauvegardée avec succès',
        'flash_save_error': 'Erreur lors de la sauvegarde : {error}',

        # Purge (web/app.py)
        'flash_incomplete_config': "Configuration incomplète. Veuillez d'abord configurer le bot.",
        'flash_purge_success': 'Purge réussie : {count} messages supprimés au total',
        'flash_purge_partial': 'Purge partielle : {count} messages supprimés. Erreurs : {errors}',
        'flash_purge_error': 'Erreur lors de la purge : {error}',
        'flash_purge_unknown_error': 'Erreur inconnue',
        'flash_purge_comm_error': 'Erreur de communication avec le bot : {error}',
        'flash_purge_response_error': 'Erreur lors du traitement de la réponse : {error}',
        'flash_generic_error': 'Erreur : {error}',

        # Raisons d'échec renvoyées par le bot pour un canal donné
        'purge_error_forbidden': 'Accès refusé pour le canal {channel}',
        'purge_error_http_error': 'Erreur HTTP pour le canal {channel} : {detail}',
        'purge_error_not_found': 'Canal {channel} introuvable',
        'purge_error_invalid_id': 'ID de canal invalide : {channel}',
        'purge_error_auth': 'Erreur de connexion du bot : {detail}',
        'purge_error_unknown': 'Canal {channel} : {detail}',
    },
    'en': {
        # Page
        'page_title': 'CleanBot Configuration',
        'card_title': 'CleanBot Configuration',

        # Main form
        'label_token': 'Discord Token',
        'label_channels': 'Channel IDs (one per line)',
        'help_channels': (
            "Enter one Discord channel ID per line. Add a description after "
            "<code>#</code> to remember which channel it is (it is ignored "
            "when purging), e.g.:<br>"
            "<code>123456789012345678 # General announcements</code>"
        ),
        'label_max_messages': 'Maximum number of messages to delete',

        'label_schedule_type': 'Schedule type',
        'option_schedule_interval': 'Regular interval',
        'option_schedule_specific': 'Specific days',
        'option_schedule_custom': 'Custom',

        'label_interval': 'Interval',
        'option_interval_hourly': 'Every hour',
        'option_interval_daily': 'Every day',
        'option_interval_weekly': 'Every week',
        'option_interval_biweekly': 'Every two weeks',
        'option_interval_monthly': 'Every month',
        'label_exec_time': 'Execution time',

        'label_weekdays': 'Days of the week',
        'day_monday': 'Monday',
        'day_tuesday': 'Tuesday',
        'day_wednesday': 'Wednesday',
        'day_thursday': 'Thursday',
        'day_friday': 'Friday',
        'day_saturday': 'Saturday',
        'day_sunday': 'Sunday',

        'label_cron': 'Cron expression',
        'help_cron': 'Format: minute hour day month weekday (e.g. */30 * * * * for every 30 minutes)',

        'btn_save': 'Save configuration',
        'btn_purge_now': 'Purge now',
        'confirm_purge': 'Are you sure you want to purge all channels now?',

        # Validation / saving (web/app.py)
        'flash_token_required': 'The Discord token is required',
        'flash_invalid_channel_lines': (
            'Invalid line(s) in channel IDs (before the first "#", there must '
            'be only digits): {lines}'
        ),
        'flash_channel_required': 'At least one channel ID is required',
        'error_invalid_cron': 'Invalid cron expression',
        'flash_save_success': 'Configuration saved successfully',
        'flash_save_error': 'Error while saving: {error}',

        # Purge (web/app.py)
        'flash_incomplete_config': 'Incomplete configuration. Please configure the bot first.',
        'flash_purge_success': 'Purge successful: {count} messages deleted in total',
        'flash_purge_partial': 'Partial purge: {count} messages deleted. Errors: {errors}',
        'flash_purge_error': 'Error during purge: {error}',
        'flash_purge_unknown_error': 'Unknown error',
        'flash_purge_comm_error': 'Error communicating with the bot: {error}',
        'flash_purge_response_error': 'Error while processing the response: {error}',
        'flash_generic_error': 'Error: {error}',

        # Failure reasons returned by the bot for a given channel
        'purge_error_forbidden': 'Access denied for channel {channel}',
        'purge_error_http_error': 'HTTP error for channel {channel}: {detail}',
        'purge_error_not_found': 'Channel {channel} not found',
        'purge_error_invalid_id': 'Invalid channel ID: {channel}',
        'purge_error_auth': 'Bot connection error: {detail}',
        'purge_error_unknown': 'Channel {channel}: {detail}',
    },
}
