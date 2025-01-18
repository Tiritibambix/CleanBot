from flask import Flask, render_template, request, flash, redirect, url_for
import yaml
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.urandom(24)

CONFIG_PATH = Path("/app/config/config.yaml")

def load_config():
    if not CONFIG_PATH.exists():
        return {
            'token': '',
            'channel_ids': [],
            'max_messages': 100,
            'schedule': 'weekly'
        }
    
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f) or {}

def save_config(config):
    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f)

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/save', methods=['POST'])
def save_config_route():
    config = {
        'token': request.form.get('token', '').strip(),
        'channel_ids': [
            int(channel.strip())
            for channel in request.form.get('channels', '').split('\n')
            if channel.strip().isdigit()
        ],
        'max_messages': int(request.form.get('max_messages', 100)),
        'schedule': request.form.get('schedule', 'weekly')
    }
    
    if not config['token']:
        flash('Le token Discord est requis', 'danger')
        return redirect(url_for('index'))
    
    if not config['channel_ids']:
        flash('Au moins un ID de canal est requis', 'danger')
        return redirect(url_for('index'))
    
    try:
        save_config(config)
        flash('Configuration sauvegardée avec succès', 'success')
    except Exception as e:
        flash(f'Erreur lors de la sauvegarde : {str(e)}', 'danger')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
