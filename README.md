# cleanbot
Bot Discord pour purger les canaux d'un serveur


# Guide pour créer un bot Discord qui efface des messages tous les 7 jours

Ce guide vous montre comment créer un bot Discord en utilisant `discord.py` qui effacera des messages dans des canaux spécifiés tous les 7 jours. Nous allons également aborder les permissions nécessaires et les étapes pour configurer et tester le bot.

## Prérequis

Avant de commencer, assurez-vous que :

- Vous avez un bot Discord configuré et fonctionnel.
- Vous avez installé `discord.py` sur votre machine.
- Votre bot a la permission **Gérer les messages** dans les canaux où il doit supprimer les messages.

### 1. Installer `discord.py`

Si vous n'avez pas encore installé `discord.py`, utilisez la commande suivante :

```bash
pip install discord.py
```

Si vous utilisez un environnement virtuel, assurez-vous d'être activé dans ce dernier avant d'installer `discord.py`.

### 2. Créer un bot Discord

Si vous n'avez pas encore créé de bot, suivez ces étapes :

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications).
2. Créez une nouvelle application, puis générez un bot dans la section "Bot".
3. Copiez le **Token** de votre bot, qui sera utilisé dans le script.
4. Donnez les permissions nécessaires au bot, telles que "Gérer les messages".

### 3. Script Python pour le bot

Voici le script complet pour que votre bot efface des messages tous les 7 jours dans les canaux que vous spécifiez.

#### Script Python

```python
import discord
from discord.ext import commands
import asyncio

# Remplacez par votre token
TOKEN = "VOTRE_TOKEN_ICI"
# Liste des ID de canaux où envoyer le message
CHANNEL_IDS = [123456789012345678, 987654321098765432]  # Remplacez avec les IDs de vos canaux
# Nombre maximum de messages a supprimer par execution
AMOUNT_TO_CLEAR = 999

# Initialisation du bot avec les intentions necessaires
intents = discord.Intents.default()
intents.messages = True  # Permet au bot d'interagir avec les messages
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
```

### Explications du script

1. **Initialisation du bot** :
    - Le bot utilise le préfixe `!` pour les commandes et s'assure que les intentions nécessaires (comme la gestion des messages) sont activées.

2. **Liste des canaux** :
    - Les IDs des canaux où le bot effacera les messages sont stockés dans la liste `CHANNEL_IDS`.

3. **La tâche récurrente** :
    - La fonction `clear_messages` est décorée avec `@tasks.loop(hours=168)`, ce qui signifie que cette tâche se déclenchera toutes les 168 heures (soit 7 jours).
    - Le bot purge jusqu'à `AMOUNT_TO_CLEAR` messages dans chaque canal spécifié.

4. **Gestion des erreurs** :
    - Le bot gère les erreurs, telles que les problèmes d'accès ou les erreurs HTTP lors de la tentative de suppression des messages.

5. **Lancer le bot** :
    - Une fois le bot lancé avec `bot.run(TOKEN)`, il commencera à exécuter la tâche récurrente pour effacer les messages dans les canaux spécifiés.

### 4. Vérifier et donner des permissions

Le bot doit avoir la permission **Gérer les messages** dans les canaux où il doit supprimer les messages. Voici comment vérifier cela :

1. Allez dans **Paramètres du serveur** > **Rôles**.
2. Sélectionnez le rôle du bot, puis activez **Gérer les messages**.
3. Assurez-vous également que cette permission est activée dans chaque canal.

### 5. Lancer le script

Une fois que vous avez configuré le bot et le script :

1. Sauvegardez le fichier avec l'extension `.py`, par exemple `bot.py`.
2. Exécutez-le avec la commande suivante :
   ```bash
   nohup python3 /home/scripts/discord/bot.py &
   ```
3. Le bot commencera à exécuter la tâche récurrente pour effacer les messages tous les 7 jours.

### 6. Tester le bot

Si vous voulez tester le bot rapidement, vous pouvez modifier la ligne `@tasks.loop(hours=168)` en `@tasks.loop(seconds=10)` pour effectuer la purge toutes les 10 secondes. Cela vous permettra de voir si tout fonctionne correctement sans attendre une semaine.

### Conclusion

Avec ce script, votre bot effacera automatiquement des messages dans les canaux que vous avez spécifiés tous les 7 jours. Si vous avez des questions ou avez besoin d'ajustements, n'hésitez pas à me contacter !

---
