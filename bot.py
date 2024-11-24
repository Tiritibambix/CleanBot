import discord
from discord.ext import commands
import asyncio

# Remplacez par votre propre token
TOKEN = "VOTRE_TOKEN_ICI"
# Remplacez par les IDs des canaux ou vous souhaitez effacer des messages
CHANNEL_IDS = [123456789012345678, 987654321098765432]  # Exemple d'IDs de canaux
# Nombre maximum de messages a supprimer par execution
AMOUNT_TO_CLEAR = 100

# Initialisation du bot avec les intentions necessaires
intents = discord.Intents.default()
intents.messages = True  # Permet au bot d'interagir avec les messages
intents.message_content = True  # Necessaire pour acceder au contenu des messages
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connected comme {bot.user}")

    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                # Purge des messages dans le canal
                deleted = await channel.purge(limit=AMOUNT_TO_CLEAR)
                print(f"{len(deleted)} messages supprimes dans le canal {channel_id}.")
            except discord.errors.Forbidden:
                print(f"Acces refuse pour supprimer les messages dans le canal {channel_id}.")
            except discord.errors.HTTPException as e:
                print(f"Erreur HTTP lors de la tentative de purge dans le canal {channel_id}: {e}")
        else:
            print(f"Canal avec ID {channel_id} introuvable.")

    # Arreter le bot apres l'execution de la purge
    await bot.close()

# Lancer le bot
bot.run(TOKEN)
