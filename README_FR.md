![Alt text](https://cdn.discordapp.com/app-icons/1310261454959673354/79876aac97de54fdfc9a06fbca4f32ff.png "a title")

# Cleanbot
Bot Discord pour purger les canaux d'un serveur

## Nouvelle Interface Web !

Cleanbot dispose maintenant d'une belle interface web pour une configuration facile ! Vous pouvez désormais gérer les paramètres de votre bot via un tableau de bord convivial.

### Démarrage rapide avec Docker

La façon la plus simple d'utiliser Cleanbot est avec Docker. Voici comment l'installer :

1. D'abord, créez un répertoire pour votre configuration :
```bash
mkdir -p /srv/Files/Cleanbot/config
```

2. Démarrez les services avec docker-compose :
```bash
docker-compose up -d
```

Le fichier docker-compose.yml comprend :
- Une interface web accessible par défaut sur le port 5392 (peut être changé pour n'importe quel port de votre choix)
- Un service bot qui gère les interactions Discord
- Redémarrage automatique en cas d'erreur
- Stockage persistant de la configuration

Configuration :
```yaml
services:
  web:
    image: tiritibambix/cleanbot-web:latest
    ports:
      - "5392:8080"  # Change "5392" to any port you want to use
    volumes:
      - /srv/Files/Cleanbot/config:/app/config
    environment:
      - FLASK_ENV=production
      - TZ=Europe/Paris
    restart: unless-stopped

  bot:
    image: tiritibambix/cleanbot:latest
    volumes:
      - /srv/Files/Cleanbot/config:/app/config
    environment:
      - TZ=Europe/Paris
    expose:
      - "8081"
    restart: unless-stopped

networks:
  cleanbot_network:
    driver: bridge
```

Utilisation :
- Accédez à l'interface web sur http://localhost:5392
- Configurez votre token Discord et les IDs des canaux
- Définissez votre planning de nettoyage
- Utilisez `docker-compose logs` pour voir les logs
- Utilisez `docker-compose down` pour arrêter les services

### Fonctionnalités

- 🌐 Interface web pour une configuration facile
- 🔄 Purge automatique des messages
- ⏰ Planning configurable (quotidien, hebdomadaire, mensuel)
- 🔒 Stockage sécurisé de la configuration
- 🐳 Support Docker
- 🚀 Déploiement facile

### Options de Configuration

Via l'interface web, vous pouvez configurer :
- Token du Bot Discord
- IDs des canaux à purger
- Nombre maximum de messages à supprimer par exécution
- Fréquence de purge (quotidienne, hebdomadaire, mensuelle)

### Installation Manuelle (Alternative)

Si vous préférez exécuter sans Docker, suivez ces étapes :

#### 1. **Créer une application Discord**

1. Rendez-vous sur le portail des développeurs Discord.
2. Cliquez sur **New Application**, donnez-lui un nom, et cliquez sur **Create**.
3. Allez dans l'onglet **Bot** et cliquez sur **Add Bot**. Confirmez.
4. Sous **Token**, cliquez sur **Copy** pour sauvegarder le token du bot (gardez-le privé).

#### 2. **Activer les intentions nécessaires dans le portail Discord :**

1. Allez sur le portail des développeurs Discord.
2. Sélectionnez votre application (le bot).
3. Dans le menu de gauche, cliquez sur **Bot**.
4. Sous **Privileged Gateway Intents**, activez l'option **Message Content Intent**.
5. Cliquez sur **Save Changes**.

#### 3. **Inviter le bot sur votre serveur**

1. Sous l'onglet **OAuth2** > **URL Generator**, cochez : 
    - `bot` dans **Scopes**.
    - Les permissions nécessaires dans **Bot Permissions** (par exemple, `Send Messages`).
2. Copiez l'URL générée et ouvrez-la dans votre navigateur.
3. Invitez le bot sur votre serveur Discord en suivant les instructions.

#### 4. **Installer les dépendances**

```bash
pip install -r requirements.txt
pip install -r web/requirements.txt  # Si vous utilisez l'interface web
```

#### 5. **Lancer l'application**

```bash
# Démarrer l'interface web
python web/app.py

# Dans un autre terminal, démarrer le bot
python bot.py
```

### Points Importants

- **Gardez votre token secret** : Ne partagez jamais votre token. Si vous pensez qu'il est compromis, régénérez-le depuis le portail Discord.
- **Permissions du bot** : Vérifiez que le bot a bien les permissions nécessaires sur chaque canal.
- **Testez localement** : Assurez-vous que tout fonctionne correctement avant le déploiement.

### Images Docker

Nos images Docker sont disponibles sur Docker Hub :
- Bot : `tiritibambix/cleanbot:latest`
- Interface Web : `tiritibambix/cleanbot-web:latest`

### Licence

Ce projet est sous licence Creative Commons Attribution-NonCommercial 4.0 International - voir le fichier [LICENSE](LICENSE) pour plus de détails.
