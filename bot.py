import discord
from discord.ext import commands
import asyncio
from aiohttp import web
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def purge_channels(token, channel_ids, max_messages=999):
    # Initialisation du bot
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    results = []
    
    @bot.event
    async def on_ready():
        logger.info(f"Bot connecté comme {bot.user}")
        
        for channel_id in channel_ids:
            try:
                channel_id = int(channel_id)
                channel = bot.get_channel(channel_id)
                if channel:
                    try:
                        deleted = await channel.purge(limit=max_messages)
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
            except ValueError:
                msg = f"ID de canal invalide : {channel_id}"
                logger.error(msg)
                results.append({"channel": channel_id, "status": "error", "message": msg})
        
        # Fermer le bot après la purge
        await bot.close()
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Erreur lors de la connexion du bot : {e}")
        results.append({"status": "error", "message": str(e)})
    
    return results

async def handle_purge(request):
    try:
        config = await request.json()
        
        if not config.get('token') or not config.get('channel_ids'):
            return web.Response(text="Configuration invalide", status=400)
        
        # Créer une nouvelle tâche pour la purge
        results = await purge_channels(
            config['token'],
            config['channel_ids'],
            config.get('max_messages', 999)
        )
        
        return web.Response(
            text=json.dumps({"status": "success", "results": results}),
            content_type='application/json'
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la purge : {e}")
        return web.Response(
            text=json.dumps({"status": "error", "message": str(e)}),
            content_type='application/json',
            status=500
        )

async def handle_health(request):
    return web.Response(text="OK")

async def run_api():
    app = web.Application()
    app.router.add_post('/purge', handle_purge)
    app.router.add_get('/health', handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=8081)
    await site.start()
    logger.info("API démarrée sur 0.0.0.0:8081")
    
    # Garder l'API en vie
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(run_api())
