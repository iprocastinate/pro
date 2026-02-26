# Auto Adult Bot

A powerful Telegram bot that automatically fetches, encodes, and uploads anime content using RSS feeds and torrent technology.

## Features

- 🔄 **Automatic RSS Fetching** - Monitor RSS feeds for new titles
- 🎬 **Video Encoding** - Transcodes videos with FFmpeg
- 📤 **One-Click Upload** - Direct upload to Telegram
- 🗄️ **MongoDB Integration** - Persistent data storage
- ⚙️ **Admin Panel** - Control bot behavior via commands
- 🔐 **Security Features** - Admin-only controls, content filtering
- 📊 **Auto-Upload Scheduler** - Schedule uploads by time and limit
- 🌐 **Deployment Ready** - Works on Koyeb, Render, or local

## Quick Start

### Local Deployment

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example config.env
   # Edit config.env with your credentials
   ```

3. **Run the bot:**
   ```bash
   python3 -m bot
   ```

### Cloud Deployment

- **Koyeb**: [See Deployment Guide](DEPLOYMENT.md#deploy-on-koyeb)
- **Render**: [See Deployment Guide](DEPLOYMENT.md#deploy-on-render)
- **Heroku**: Uses `heroku.yml` (legacy)

## Requirements

### Essential

- **Python 3.10+**
- **FFmpeg** (included in Docker)
- **MongoDB** (local or cloud)
- **Telegram Bot Token**

### Create Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create new bot and copy the token
3. Get API ID & Hash from [my.telegram.org](https://my.telegram.org)

### Create MongoDB Database

1. Sign up at [mongodb.com](https://mongodb.com)
2. Create a free cluster
3. Get connection string from "Connect" button

## Configuration

All configuration is done via environment variables in `config.env`:

```env
# Bot Credentials (Required)
API_ID="your_api_id"
API_HASH="your_api_hash"
BOT_TOKEN="your_bot_token"

# Database (Required)
MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net"
MONGO_DB="database_name"

# Channels (Required)
MAIN_CHANNEL="-1002186260966"    # Where content is posted
OWNER="123456789"                # Your Telegram user ID
FILE_STORE="-1002373900011"      # File storage channel

# Optional
LOG_CHANNEL="-1002239258829"
DATABASE_CHANNEL=""
FSUB_CHATS=""
ADMINS=""
```

See [.env.example](.env.example) for all available options.

## Commands

### Admin/Owner Only

- `/settings` - Adjust bot preferences
- `/pause` - Pause RSS fetching
- `/resume` - Resume RSS fetching
- `/addtask <link>` - Add manual upload task
- `/restart` - Restart the bot

### Auto-Upload Control

- Enable/Disable auto-upload
- Set daily upload limit
- Schedule upload time
- View upload statistics

## Architecture

```
bot/
├── __init__.py          # Configuration & initialization
├── __main__.py          # Bot startup & main loop
├── func.py              # Utility functions
├── core/
│   ├── database.py      # MongoDB operations
│   ├── rss_fetcher.py   # RSS parsing & processing
│   ├── text_utils.py    # Text processing & formatting
│   ├── ffencoder.py     # FFmpeg encoding
│   ├── tguploader.py    # Telegram upload handler
│   ├── tordownload.py   # Torrent downloading
│   ├── func_utils.py    # Helper functions
│   └── reporter.py      # Logging & reporting
└── modules/
    ├── cmds.py          # Command handlers
    └── callback.py      # Button/callback handlers
```

## Deployment

### Docker

```bash
docker build -t auto-adult-bot .
docker run -e CONFIG_ENV=config.env auto-adult-bot
```

### Docker Compose

```bash
docker-compose -f docker-compose.yml up -d
```

### Koyeb

See [Deployment Guide](DEPLOYMENT.md#deploy-on-koyeb) for step-by-step instructions.

### Render

See [Deployment Guide](DEPLOYMENT.md#deploy-on-render) for step-by-step instructions.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_ID` | ✅ | Telegram API ID |
| `API_HASH` | ✅ | Telegram API Hash |
| `BOT_TOKEN` | ✅ | Telegram Bot Token |
| `MONGO_URI` | ✅ | MongoDB connection string |
| `MONGO_DB` | ✅ | MongoDB database name |
| `MAIN_CHANNEL` | ✅ | Channel ID for posts |
| `OWNER` | ✅ | Owner user ID |
| `FILE_STORE` | ✅ | File storage channel ID |
| `LOG_CHANNEL` | ❌ | Logging channel ID |
| `RSS_ITEMS` | ❌ | RSS feed URLs (space-separated) |
| `FSUB_CHATS` | ❌ | Force subscribe channels |
| `ADMINS` | ❌ | Admin user IDs (space-separated) |

## Features in Detail

### Auto-Upload Scheduler
- Enable/disable auto-upload
- Set daily upload limit
- Schedule uploads by time
- Tracks upload count per day

### Content Filtering
- Automatic word censoring in captions
- Spoiler effect on posted images
- Admin/owner-only sensitive operations
- Whitelist/ban system for users

### Encoding Support
- Multiple quality options (360p, 480p, 720p, 1080p)
- Batch encoding
- Metadata preservation
- Custom FFmpeg commands

## Security

- ✅ Admin/Owner permission checks on all sensitive operations
- ✅ Content censoring in captions
- ✅ Database authentication required
- ✅ Telegram session tokens encrypted
- ✅ No credentials stored in code

## Support

- **Issues**: Share bugs and suggestions via GitHub Issues
- **Documentation**: [Full Deployment Guide](DEPLOYMENT.md)
- **Telegram**: Join our community channel
- **Updates**: Star this repo to stay updated

## License

This project is licensed under the GNU Affero General Public License v3.0 - see [LICENSE](LICENSE) file for details.

## Disclaimer

This bot is for educational purposes. The operator is responsible for ensuring compliance with local laws and Telegram's Terms of Service.

---

**Made with ❤️ for anime enthusiasts**
