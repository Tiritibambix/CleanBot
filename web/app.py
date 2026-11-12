from flask import Flask, render_template, request, flash, redirect, url_for, make_response
import yaml
import os
from pathlib import Path
import re
import json
import requests
from translations import TRANSLATIONS, SUPPORTED_LANGS, DEFAULT_LANG

app = Flask(__name__)
app.secret_key = os.urandom(24)

CONFIG_PATH = Path("/app/config/config.yaml")
BOT_API_URL = "http://bot:8081/purge"  # URL du service bot
CHANNEL_COMMENT_DELIMITER = '#'  # tout ce qui suit ce caractère sur une ligne est une description, pas l'ID
LANG_COOKIE_NAME = 'lang'
LANG_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 an

def get_lang():
    """Langue courante, choisie par l'utilisateur via le sélecteur FR/EN (cookie).

    Un simple cookie (plutôt que la session Flask signée) est utilisé ici :
    c'est une préférence d'affichage sans enjeu de sécurité, et ça évite tout
    souci si app.secret_key change au redémarrage du conteneur.
    """
    lang = request.cookies.get(LANG_COOKIE_NAME, DEFAULT_LANG)
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG

def t(key, **kwargs):
    """Traduit `key` dans la langue courante, avec interpolation `{...}` optionnelle."""
    strings = TRANSLATIONS.get(get_lang(), TRANSLATIONS[DEFAULT_LANG])
    template = strings.get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))
    return template.format(**kwargs) if kwargs else template

# Rend t() et la langue courante disponibles dans tous les templates Jinja
app.jinja_env.globals['t'] = t

@app.context_processor
def inject_lang():
    return {'current_lang': get_lang(), 'supported_langs': SUPPORTED_LANGS}

@app.route('/lang/<lang_code>')
def set_lang(lang_code):
    target = lang_code if lang_code in SUPPORTED_LANGS else DEFAULT_LANG
    resp = make_response(redirect(request.referrer or url_for('index')))
    resp.set_cookie(LANG_COOKIE_NAME, target, max_age=LANG_COOKIE_MAX_AGE)
    return resp

def parse_channel_lines(raw_text):
    """Transforme le contenu du textarea 'channels' en liste d'IDs.

    Chaque ligne peut être :
      - vide                                      -> ignorée
      - un commentaire pur : "# Annonces"         -> ignorée (pas d'ID)
      - un ID seul : "123456789012345678"         -> ID ajouté
      - un ID + description : "123456789012345678 # Général"
                                                    -> seul l'ID est gardé, la description
                                                       sert uniquement d'aide-mémoire visuel
    Retourne (channel_ids, erreurs) où erreurs liste les lignes dont la partie
    avant le délimiteur n'est pas un entier valide.
    """
    channel_ids = []
    errors = []

    for line in raw_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        id_part = line.split(CHANNEL_COMMENT_DELIMITER, 1)[0].strip()
        if not id_part:
            # Ligne entièrement commentée (ex: "# --- Canaux publics ---"), on l'ignore
            continue

        try:
            channel_ids.append(int(id_part))
        except ValueError:
            errors.append(line)

    return channel_ids, errors

def is_valid_cron(expression):
    pattern = r'^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|(\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]))) (\*|([0-9]|1[0-9]|2[0-3])|(\*\/([0-9]|1[0-9]|2[0-3]))) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|(\*\/([1-9]|1[0-9]|2[0-9]|3[0-1]))) (\*|([1-9]|1[0-2])|(\*\/([1-9]|1[0-2]))) (\*|([0-6])|(\*\/([0-6])))$'
    return bool(re.match(pattern, expression))

def load_config():
    if not CONFIG_PATH.exists():
        return {
            'token': '',
            'channel_ids': [],
            'channels_raw': '',
            'max_messages': 100,
            'schedule_type': 'interval',
            'interval': 'daily',
            'interval_time': '00:00',
            'weekdays': [],
            'specific_time': '00:00',
            'cron_expression': '0 0 * * *'
        }
    
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f) or {}
        # Assurer la compatibilité avec les anciennes configurations
        if 'schedule' in config:
            config['schedule_type'] = 'interval'
            config['interval'] = config.pop('schedule')
        # Anciennes configs : pas de texte brut sauvegardé (donc pas de descriptions),
        # on reconstitue l'affichage à partir des IDs seuls
        if 'channels_raw' not in config:
            config['channels_raw'] = '\n'.join(str(c) for c in config.get('channel_ids', []))
        return config

def save_config(config):
    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f)

def process_schedule_config(form_data):
    schedule_config = {
        'schedule_type': form_data.get('schedule_type', 'interval')
    }
    
    if schedule_config['schedule_type'] == 'interval':
        schedule_config.update({
            'interval': form_data.get('interval', 'daily'),
            'interval_time': form_data.get('interval_time', '00:00')
        })
    elif schedule_config['schedule_type'] == 'specific':
        schedule_config.update({
            'weekdays': request.form.getlist('weekdays[]'),
            'specific_time': form_data.get('specific_time', '00:00')
        })
    else:  # custom
        cron_expression = form_data.get('cron_expression', '0 0 * * *')
        if not is_valid_cron(cron_expression):
            raise ValueError(t('error_invalid_cron'))
        schedule_config['cron_expression'] = cron_expression
    
    return schedule_config

def format_purge_error(result):
    """Construit, dans la langue courante, le message d'erreur pour un canal
    à partir du `reason` structuré renvoyé par bot.py (voir bot.py)."""
    channel = result.get('channel', '?')
    reason = result.get('reason', 'unknown')
    detail = result.get('detail', '')

    if reason == 'forbidden':
        return t('purge_error_forbidden', channel=channel)
    if reason == 'http_error':
        return t('purge_error_http_error', channel=channel, detail=detail)
    if reason == 'not_found':
        return t('purge_error_not_found', channel=channel)
    if reason == 'invalid_id':
        return t('purge_error_invalid_id', channel=channel)
    if reason == 'auth':
        return t('purge_error_auth', detail=detail)
    return t('purge_error_unknown', channel=channel, detail=detail)

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/purge-now')
def purge_now():
    try:
        config = load_config()
        
        if not config.get('token') or not config.get('channel_ids'):
            flash(t('flash_incomplete_config'), 'danger')
            return redirect(url_for('index'))
        
        try:
            response = requests.post(BOT_API_URL, json=config, timeout=30)
            response_data = response.json()
            
            if response.status_code == 200:
                # Créer un résumé des résultats
                success_count = sum(1 for r in response_data['results'] if r['status'] == 'success')
                total_deleted = sum(r.get('deleted', 0) for r in response_data['results'] if r['status'] == 'success')
                
                if success_count == len(config['channel_ids']):
                    flash(t('flash_purge_success', count=total_deleted), 'success')
                else:
                    error_channels = [r for r in response_data['results'] if r['status'] == 'error']
                    error_msgs = [format_purge_error(r) for r in error_channels]
                    flash(t('flash_purge_partial', count=total_deleted, errors=", ".join(error_msgs)), 'warning')
            else:
                flash(t('flash_purge_error', error=response_data.get('message', t('flash_purge_unknown_error'))), 'danger')
                
        except requests.exceptions.RequestException as e:
            flash(t('flash_purge_comm_error', error=str(e)), 'danger')
        except ValueError as e:
            flash(t('flash_purge_response_error', error=str(e)), 'danger')
        
    except Exception as e:
        flash(t('flash_generic_error', error=str(e)), 'danger')
    
    return redirect(url_for('index'))

@app.route('/save', methods=['POST'])
def save_config_route():
    try:
        # Configuration de base
        channels_raw = request.form.get('channels', '')
        channel_ids, invalid_lines = parse_channel_lines(channels_raw)

        config = {
            'token': request.form.get('token', '').strip(),
            'channel_ids': channel_ids,
            'channels_raw': channels_raw,
            'max_messages': int(request.form.get('max_messages', 100))
        }
        
        # Validation de base
        if not config['token']:
            flash(t('flash_token_required'), 'danger')
            return redirect(url_for('index'))

        if invalid_lines:
            flash(t('flash_invalid_channel_lines', lines=", ".join(invalid_lines)), 'danger')
            return redirect(url_for('index'))

        if not config['channel_ids']:
            flash(t('flash_channel_required'), 'danger')
            return redirect(url_for('index'))
        
        # Ajouter la configuration de planification
        try:
            schedule_config = process_schedule_config(request.form)
            config.update(schedule_config)
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('index'))
        
        save_config(config)
        flash(t('flash_save_success'), 'success')
        
    except Exception as e:
        flash(t('flash_save_error', error=str(e)), 'danger')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
