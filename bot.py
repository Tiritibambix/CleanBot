import discord
from discord.ext import commands
import asyncio
import yaml
from pathlib import Path
import time
from datetime import datetime, timedelta
import croniter
from aiohttp import web
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path("/app/config/config.yaml")

class CleanBot:
    def __init__(self):
        self.bot = None
        self.config = None
        self.last_token = None

    async def ensure_bot_connected(self, token):
        if self.bot is None or self.last_token != token:
            if self.bot:
                try:
                    await self.bot.close()
                except:
                    pass

            intents = discord.Intents.default()
            intents.messages = True
            intents.message_content = True
            self.bot = commands.Bot(command_prefix="!", intents=intents)
            
            try:
                logger.info("Tentative de connexion du bot...")
                await self.bot.login(token)
                logger.info("Login réussi, tentative de connexion...")
                await self.bot.connect()
                self.last_token = token
                logger.info("Bot connecté avec succès")
                return True
            except Exception as e:
                logger.error(f"Erreur lors de la connexion du bot : {e}")
                self.bot = None
                self.last_token = None
                return False
        return True

    async def purge_channels(self, config):
        if not await self.ensure_bot_connected(config['token']):
            raise Exception("Impossible de connecter le bot")

        results = []
        for channel_id in config['channel_ids']:
            channel = self.bot.get_channel(channel_id)
            if channel:
                try:
                    deleted = await channel.purge(limit=config['max_messages'])
                    msg = f"{len(deleted)} messages supprimés dans le canal {channel_id}"
                    logger.info(msg)
                    results.append({"channel": channel_id, "status": "success", "deleted": len(deleted)})
                except discord.errors.Forbidden:
                    msg = f"Accès refusé pour le canal {channel_id}"
                    logger.error(msg)
                    results.append({"channel": channel_id, "status": "error", "message": msg})
                except discord.errors.HTTPException as e:
                    msg = f"Erreur HTTP pour le canal {channel_id}: {e}"
                    logger.error(msg)
                    results.append({"channel": channel_id, "status": "error", "message": msg})
            else:
                msg = f"Canal {channel_id} introuvable"
                logger.error(msg)
                results.append({"channel": channel_id, "status": "error", "message": msg})
        
        return results

# Instance globale du bot
clean_bot = CleanBot()

def load_config():
    if not CONFIG_PATH.exists():
        raise ValueError("Le fichier de configuration n'existe pas")
    
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
        
    if not config:
        raise ValueError("Configuration invalide")
        
    return config

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

async def handle_purge(request):
    try:
        logger.info("Réception d'une requête de purge")
        config = await request.json()
        
        if not config.get('token') or not config.get('channel_ids'):
            logger.error("Configuration invalide reçue")
            return web.Response(text="Configuration invalide", status=400)
        
        results = await clean_bot.purge_channels(config)
        return web.Response(text=json.dumps({"status": "success", "results": results}),
                          content_type='application/json')
        
    except Exception as e:
        logger.error(f"Erreur lors de la purge : {e}")
        return web.Response(text=json.dumps({"status": "error", "message": str(e)}),
                          content_type='application/json',
                          status=500)

async def run_api():
    app = web.Application()
    app.router.add_post('/purge', handle_purge)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    logger.info("API démarrée sur le port 8081")

async def main():
    try:
        logger.info("Démarrage de l'API...")
        await run_api()
        logger.info("API démarrée, début de la boucle principale")
        
        while True:
            try:
                config = load_config()
                
                sleep_time = get_next_run_time(config)
                logger.info(f"Prochaine exécution dans {sleep_time/3600:.2f} heures")
                await asyncio.sleep(sleep_time)
                
                if await clean_bot.ensure_bot_connected(config['token']):
                    await clean_bot.purge_channels(config)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale : {e}")
                logger.info("Nouvelle tentative dans 5 minutes...")
                await asyncio.sleep(300)
    except Exception as e:
        logger.error(f"Erreur fatale : {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
