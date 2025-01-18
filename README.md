![Cleanbot](https://cdn.discordapp.com/app-icons/1310261454959673354/79876aac97de54fdfc9a06fbca4f32ff.png "Cleanbot")

# Cleanbot

Discord Bot to Purge Server Channels

## Features

- 🌐 Web interface for easy configuration
- 🔄 Automatic message purging
- 🔲 Simple channel ID input
- 🚀 Immediate purge button
- 🔒 Secure configuration storage
- 🐳 Docker support
- 📝 Detailed operation feedback

## Option 1: Docker Deployment (Recommended)

### Prerequisites

1. **Create a Discord Application**
   1. Go to the Discord Developer Portal
   2. Click on **New Application**, give it a name, and click on **Create**
   3. Go to the **Bot** tab and click on **Add Bot**. Confirm
   4. Under **Token**, click on **Copy** to save the bot token (keep it private)

2. **Enable Necessary Intents**
   1. In the Discord Developer Portal, select your application
   2. Under **Bot** tab, enable the following Privileged Gateway Intents:
      - Message Content Intent
      - Server Members Intent

3. **Configure Bot Permissions**
   1. Under **OAuth2** > **URL Generator**:
      - In **Scopes**, select `bot`
      - In **Bot Permissions**, select:
        - Read Messages/View Channels
        - Manage Messages
        - Read Message History
   2. Copy the generated URL and open it in your browser
   3. Follow the instructions to invite the bot to your server

### Quick Start

1. Create the configuration directory:
```bash
mkdir -p /srv/Files/Cleanbot/config
```

2. Start the services:
```bash
docker-compose up -d
```

3. Access the web interface at `http://localhost:5392`

4. Enter your bot token and channel IDs in the web interface

### Docker Troubleshooting

- Check container logs:
```bash
docker-compose logs -f
```
- Ensure the config directory has correct permissions
- Verify network connectivity between containers

## Option 2: Local Development

### Steps to Create and Run the Bot

#### 1. **Create a Discord Application**

#### 1. **Create a Discord Application**

1. Go to the Discord Developer Portal.
2. Click on **New Application**, give it a name, and click on **Create**.
3. Go to the **Bot** tab and click on **Add Bot**. Confirm.
4. Under **Token**, click on **Copy** to save the bot token (keep it private).

#### 2. **Enable Necessary Intents in the Discord Portal:**

1. Go to the Discord Developer Portal.
2. Select your application (the bot).
3. In the left menu, click on **Bot**.
4. Under **Privileged Gateway Intents**, enable the **Message Content Intent** option.
5. Click on **Save Changes**.

#### 3. **Invite the Bot to Your Server**

1. Under the **OAuth2** > **URL Generator** tab, check:
    - `bot` in **Scopes**.
    - The necessary permissions in **Bot Permissions** (e.g., `Send Messages`).
2. Copy the generated URL and open it in your browser.
3. Invite the bot to your Discord server by following the instructions.

#### 4. **Obtain Channel IDs**

Enable **Developer Mode** in Discord (Settings > Advanced > Developer Mode). Right-click on the relevant channel and select **Copy ID**.

#### 5. **Install Dependencies**

On your Debian, install Python and the necessary libraries:

```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install discord.py
```

#### 6. **Write the Python Script**

Create a file `bot.py` with the following content:

```python
import discord
from discord.ext import commands
import asyncio

# Replace with your own token
TOKEN = "YOUR_TOKEN_HERE"
# Replace with the IDs of the channels where you want to delete messages
CHANNEL_IDS = [123456789012345678, 987654321098765432]  # Example channel IDs
# Maximum number of messages to delete per execution
AMOUNT_TO_CLEAR = 100

# Initialize the bot with the necessary intents
intents = discord.Intents.default()
intents.messages = True  # Allows the bot to interact with messages
intents.message_content = True  # Necessary to access message content
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                # Purge messages in the channel
                deleted = await channel.purge(limit=AMOUNT_TO_CLEAR)
                print(f"{len(deleted)} messages deleted in channel {channel_id}.")
            except discord.errors.Forbidden:
                print(f"Access denied to delete messages in channel {channel_id}.")
            except discord.errors.HTTPException as e:
                print(f"HTTP error while attempting to purge in channel {channel_id}: {e}")
        else:
            print(f"Channel with ID {channel_id} not found.")

    # Stop the bot after executing the purge
    await bot.close()

# Run the bot
bot.run(TOKEN)
```

#### 7. Run the Bot in the Background with `nohup`

To run the bot in the background, you can use `nohup` so it continues to run even if you close the terminal. Here is the command to execute to start the bot and log the output to a file:

```bash
nohup python3 /path/to/bot.py > /path/to/bot_output.log 2>&1 &
```

This command runs the script in the background and redirects the output (logs and errors) to the `bot_output.log` file.

#### 8. Set Up a Cron Job to Restart the Bot Every Monday at 5:00 AM

To automatically restart the bot every Monday at 5:00 AM, you need to set up a cron job. To do this, edit your crontab:

```bash
crontab -e
```

Add the following line to run the bot every Monday at 5:00 AM:

```bash
0 5 * * 1 nohup python3 /path/to/bot.py > path/to/bot_output.log 2>&1 &
```

`nohup` is optional since the script is not being run from the terminal.

This will ensure that your bot is automatically executed every Monday at 5:00 AM.

## Security Considerations

- Never commit or share your bot token
- Use environment variables for sensitive data
- Keep your dependencies up to date
- Regularly check Discord Developer Portal for security updates

## License

This project is licensed under the MIT License - see the LICENSE file for details.
