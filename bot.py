import discord
from discord.ext import commands
import asyncio
import yaml
from pathlib import Path
import time
from datetime import datetime, timedelta
import croniter

CONFIG_PATH = Path("/app/config/config.yaml")

def load_config():
    if not CONFIG_PATH.exists():
        raise ValueError("Le fichier de configuration n'existe pas")
    
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
        
    if not config:
        raise ValueError("Configuration invalide")
        
    return config

async def purge_channels(bot, config):
    for channel_id in config['channel_ids']:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                deleted = await channel.purge(limit=config['max_messages'])
                print(f"{len(deleted)} messages supprimés dans le canal {channel_id}.")
            except discord.errors.Forbidden:
                print(f"Accès refusé pour supprimer les messages dans le canal {channel_id}.")
            except discord.errors.HTTPException as e:
                print(f"Erreur HTTP lors de la tentative de purge dans le canal {channel_id}: {e}")
        else:
            print(f"Canal avec ID {channel_id} introuvable.")

def get_next_run_time(config):
    now = datetime.now()
    
    if config.get('schedule_type') == 'interval':
        interval = config.get('interval', 'daily')
        time_str = config.get('interval_time', '00:00')
        hour, minute = map(int, time_str.split(':'))
        
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            if interval == 'hourly':
                next_run = now.replace(minute=minute, second=0, microsecond=0) + timedelta(hours=1)
            elif interval == 'daily':
                next_run += timedelta(days=1)
            elif interval == 'weekly':
                next_run += timedelta(days=7)
            elif interval == 'biweekly':
                next_run += timedelta(days=14)
            elif interval == 'monthly':
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
        
        return (next_run - now).total_seconds()
    
    elif config.get('schedule_type') == 'specific':
        weekdays = config.get('weekdays', [])
        time_str = config.get('specific_time', '00:00')
        hour, minute = map(int, time_str.split(':'))
        
        if not weekdays:
            return 24 * 60 * 60  # Par défaut: 24h si aucun jour n'est spécifié
            
        # Convertir les noms de jours en numéros (0-6, lundi=0)
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        selected_days = sorted([day_mapping[day] for day in weekdays])
        
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
            
        while next_run.weekday() not in selected_days:
            next_run += timedelta(days=1)
            
        return (next_run - now).total_seconds()
    
    else:  # custom (cron)
        cron_expr = config.get('cron_expression', '0 0 * * *')
        cron = croniter.croniter(cron_expr, now)
        next_run = cron.get_next(datetime)
        return (next_run - now).total_seconds()

async def main():
    while True:
        try:
            config = load_config()
            
            sleep_time = get_next_run_time(config)
            print(f"Prochaine exécution dans {sleep_time/3600:.2f} heures")
            await asyncio.sleep(sleep_time)
            
            intents = discord.Intents.default()
            intents.messages = True
            intents.message_content = True
            bot = commands.Bot(command_prefix="!", intents=intents)
            
            @bot.event
            async def on_ready():
                print(f"Bot connecté comme {bot.user}")
                await purge_channels(bot, config)
                await bot.close()
            
            await bot.start(config['token'])
            
        except Exception as e:
            print(f"Erreur : {str(e)}")
            print("Nouvelle tentative dans 5 minutes...")
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
