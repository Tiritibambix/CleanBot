import discord
from discord.ext import commands
import asyncio
import yaml
from pathlib import Path
import time

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

def get_sleep_time(schedule):
    if schedule == 'daily':
        return 24 * 60 * 60  # 24 heures
    elif schedule == 'weekly':
        return 7 * 24 * 60 * 60  # 7 jours
    elif schedule == 'monthly':
        return 30 * 24 * 60 * 60  # ~30 jours
    else:
        return 7 * 24 * 60 * 60  # Par défaut: hebdomadaire

async def main():
    while True:
        try:
            config = load_config()
            
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
            
            sleep_time = get_sleep_time(config.get('schedule', 'weekly'))
            print(f"En attente {sleep_time} secondes avant la prochaine exécution...")
            await asyncio.sleep(sleep_time)
            
        except Exception as e:
            print(f"Erreur : {str(e)}")
            print("Nouvelle tentative dans 5 minutes...")
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
