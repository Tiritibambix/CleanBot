from flask import Flask, render_template, request, flash, redirect, url_for
import yaml
import os
from pathlib import Path
import re
import json
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

CONFIG_PATH = Path("/app/config/config.yaml")
BOT_API_URL = "http://bot:8081/purge"  # URL du service bot

def is_valid_cron(expression):
    pattern = r'^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|(\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]))) (\*|([0-9]|1[0-9]|2[0-3])|(\*\/([0-9]|1[0-9]|2[0-3]))) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|(\*\/([1-9]|1[0-9]|2[0-9]|3[0-1]))) (\*|([1-9]|1[0-2])|(\*\/([1-9]|1[0-2]))) (\*|([0-6])|(\*\/([0-6])))$'
    return bool(re.match(pattern, expression))

def load_config():
    if not CONFIG_PATH.exists():
        return {
            'token': '',
            'channel_ids': [],
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
            raise ValueError("Expression cron invalide")
        schedule_config['cron_expression'] = cron_expression
    
    return schedule_config

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/purge-now')
def purge_now():
    try:
        config = load_config()
        
        if not config.get('token') or not config.get('channel_ids'):
            flash('Configuration incomplète. Veuillez d\'abord configurer le bot.', 'danger')
            return redirect(url_for('index'))
        
        # Appeler l'API du bot pour déclencher une purge immédiate
        try:
            response = requests.post(BOT_API_URL, json=config, timeout=30)  # Augmentation du timeout à 30 secondes
            if response.status_code == 200:
                flash('Purge démarrée avec succès', 'success')
            else:
                flash(f'Erreur lors de la purge : {response.text}', 'danger')
        except requests.exceptions.RequestException as e:
            flash(f'Erreur de communication avec le bot : {str(e)}', 'danger')
        
    except Exception as e:
        flash(f'Erreur : {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/save', methods=['POST'])
def save_config_route():
    try:
        # Configuration de base
        config = {
            'token': request.form.get('token', '').strip(),
            'channel_ids': [
                int(channel.strip())
                for channel in request.form.get('channels', '').split('\n')
                if channel.strip()
            ],
            'max_messages': int(request.form.get('max_messages', 100))
        }
        
        # Validation de base
        if not config['token']:
            flash('Le token Discord est requis', 'danger')
            return redirect(url_for('index'))
        
        if not config['channel_ids']:
            flash('Au moins un ID de canal est requis', 'danger')
            return redirect(url_for('index'))
        
        # Ajouter la configuration de planification
        try:
            schedule_config = process_schedule_config(request.form)
            config.update(schedule_config)
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('index'))
        
        save_config(config)
        flash('Configuration sauvegardée avec succès', 'success')
        
    except Exception as e:
        flash(f'Erreur lors de la sauvegarde : {str(e)}', 'danger')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
