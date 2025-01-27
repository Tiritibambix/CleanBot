import yaml
from datetime import datetime
import logging
from pathlib import Path
from bot import purge_channels
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import pytz
import os

# Configuration du logging avec timezone
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z'
)
logger = logging.getLogger(__name__)

# Configurer le timezone du logger
tz = pytz.timezone(os.getenv('TZ', 'Europe/Paris'))
logging.Formatter.converter = lambda *args: datetime.now(tz=tz).timetuple()

CONFIG_PATH = Path("/app/config/config.yaml")

def load_config():
    if not CONFIG_PATH.exists():
        return None
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def get_cron_expression(config):
    if config.get('schedule_type') == 'specific':
        time = config.get('specific_time', '00:00')
        hour, minute = time.split(':')
        weekdays = config.get('weekdays', [])
        
        if weekdays:
            # Convertir les noms de jours en nombres (0-6, où 0 est lundi)
            day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
                      'friday': 4, 'saturday': 5, 'sunday': 6}
            day_numbers = [str(day_map[day.lower()]) for day in weekdays]
            return f'{minute} {hour} * * {",".join(day_numbers)}'
        
        return f'{minute} {hour} * * *'
    
    return None

async def execute_purge():
    try:
        config = load_config()
        if config:
            current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
            logger.info(f"Exécution de la purge planifiée à {current_time}")
            await purge_channels(
                config['token'],
                config['channel_ids'],
                config.get('max_messages', 999)
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la purge : {e}")

async def setup_scheduler():
    scheduler = AsyncIOScheduler(timezone=tz)
    
    async def update_schedule():
        scheduler.remove_all_jobs()
        config = load_config()
        if config:
            cron_expr = get_cron_expression(config)
            if cron_expr:
                scheduler.add_job(
                    execute_purge,
                    CronTrigger.from_crontab(cron_expr),
                    id='purge_job',
                    name='Purge Discord channels'
                )
                current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
                logger.info(f"Tâche planifiée avec l'expression cron : {cron_expr} (heure actuelle : {current_time})")
    
    # Configuration initiale
    await update_schedule()
    
    # Vérifier les changements de configuration toutes les 5 minutes
    scheduler.add_job(
        update_schedule,
        'interval',
        minutes=5,
        id='config_check',
        name='Check configuration changes'
    )
    
    scheduler.start()
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    logger.info(f"Scheduler démarré à {current_time}")
    
    try:
        # Garder le processus en vie
        while True:
            await asyncio.sleep(3600)  # Attendre 1 heure
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    logger.info(f"Timezone configurée : {tz.zone}")
    asyncio.run(setup_scheduler())
