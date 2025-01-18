![Cleanbot](https://cdn.discordapp.com/app-icons/1310261454959673354/79876aac97de54fdfc9a06fbca4f32ff.png "Cleanbot")

# Cleanbot
Bot Discord pour purger les canaux d'un serveur

## Fonctionnalités

- 🌐 Interface web pour une configuration facile
- 🔄 Purge automatique des messages
- 🔲 Saisie simple des IDs de canaux
- 🚀 Bouton de purge immédiate
- 🔒 Stockage sécurisé de la configuration
- 🐳 Support Docker
- 📝 Retour détaillé des opérations

## Option 1 : Déploiement Docker (Recommandé)

### Prérequis

1. **Créer une Application Discord**
   1. Rendez-vous sur le portail des développeurs Discord
   2. Cliquez sur **New Application**, donnez-lui un nom, et cliquez sur **Create**
   3. Allez dans l'onglet **Bot** et cliquez sur **Add Bot**. Confirmez
   4. Sous **Token**, cliquez sur **Copy** pour sauvegarder le token du bot (gardez-le privé)

2. **Activer les Intents Nécessaires**
   1. Dans le portail des développeurs Discord, sélectionnez votre application
   2. Sous l'onglet **Bot**, activez les Intents Privilégiés suivants :
      - Message Content Intent
      - Server Members Intent

3. **Configurer les Permissions du Bot**
   1. Sous **OAuth2** > **URL Generator** :
      - Dans **Scopes**, sélectionnez `bot`
      - Dans **Bot Permissions**, sélectionnez :
        - Lire les messages/Voir les salons
        - Gérer les messages
        - Lire l'historique des messages
   2. Copiez l'URL générée et ouvrez-la dans votre navigateur
   3. Suivez les instructions pour inviter le bot sur votre serveur

### Démarrage Rapide

1. Créez le répertoire de configuration :
```bash
mkdir -p /srv/Files/Cleanbot/config
```

2. Démarrez les services :
```bash
docker-compose up -d
```

3. Accédez à l'interface web sur `http://localhost:5392`

4. Entrez votre token de bot et les IDs des canaux dans l'interface web

### Dépannage Docker

- Vérifiez les logs des conteneurs :
```bash
docker-compose logs -f
```
- Assurez-vous que le répertoire config a les bonnes permissions
- Vérifiez la connectivité réseau entre les conteneurs

## Option 2 : Développement Local

### Étapes pour Créer et Exécuter le Bot

#### 1. **Créer une application Discord**

1. Rendez-vous sur le portail des développeurs Discord.
2. Cliquez sur **New Application**, donnez-lui un nom, et cliquez sur **Create**.
3. Allez dans l’onglet **Bot** et cliquez sur **Add Bot**. Confirmez.
4. Sous **Token**, cliquez sur **Copy** pour sauvegarder le token du bot (gardez-le privé).

#### 2. **Activer les intentions nécessaires dans le portail Discord :**

1. Allez sur le portail des développeurs Discord.
2. Sélectionnez votre application (le bot).
3. Dans le menu de gauche, cliquez sur **Bot**.
4. Sous **Privileged Gateway Intents**, activez l'option **Message Content Intent**.
5. Cliquez sur **Save Changes**.

#### 3. **Inviter le bot sur votre serveur**

1. Sous l’onglet **OAuth2** &gt; **URL Generator**, cochez : 
    - `bot` dans **Scopes**.
    - Les permissions nécessaires dans **Bot Permissions** (par exemple, `Send Messages`).
2. Copiez l’URL générée et ouvrez-la dans votre navigateur.
3. Invitez le bot sur votre serveur Discord en suivant les instructions.

#### 4. **Obtenir les IDs des canaux**

Activez le **Mode Développeur** dans Discord (Paramètres &gt; Avancés &gt; Mode Développeur). Faites un clic droit sur le canal concerné et sélectionnez **Copier l’identifiant**.

#### 5. **Installer les dépendances**

Sur votre Debian, installez Python et les bibliothèques nécessaires :

```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install discord.py
```

#### 6. **Écrire le script Python**

Créez un fichier `bot.py` avec le contenu suivant :

```python
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
```

#### 7. Lancer le bot en arrière-plan avec `nohup`

Pour faire tourner le bot en arrière-plan, vous pouvez utiliser `nohup` pour qu'il continue à fonctionner même si vous fermez le terminal. Voici la commande à exécuter pour démarrer le bot et enregistrer les logs dans un fichier :

```bash
nohup python3 /path/to/bot.py > /path/to/bot_output.log 2>&1 &
```

Cette commande exécute le script en arrière-plan et redirige les sorties (logs et erreurs) vers le fichier `bot_output.log`.

#### 8. Configurer une tâche cron pour redémarrer le bot chaque lundi à 5:00AM

Pour redémarrer automatiquement le bot chaque lundi à 5:00AM, vous devez configurer une tâche cron. Pour cela, éditez votre crontab :

```bash
crontab -e
```

Ajoutez la ligne suivante pour exécuter le bot chaque lundi à 5:00AM :

```bash
0 5 * * 1 nohup python3 /path/to/bot.py > path/to/bot_output.log 2>&1 &
```

`nohup` est optionnel puisqu'on n'execute pas le script depuis le terminal.

Cela fera en sorte que votre bot soit exécuté automatiquement chaque lundi à 5:00AM.

## Considérations de Sécurité

- Ne commitez jamais et ne partagez jamais votre token de bot
- Utilisez des variables d'environnement pour les données sensibles
- Gardez vos dépendances à jour
- Vérifiez régulièrement le portail des développeurs Discord pour les mises à jour de sécurité

## Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.
