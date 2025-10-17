━━━━━━━━━━━━━━━━━━━━

<h2 align="center">
    ──「 ғɪʟᴇ sᴛᴏʀᴇ ᴘʀᴏ - ʙʏ ʀɪᴍᴜʀᴜ 」──
</h2>

<p align="center">
  <img src="https://camo.githubusercontent.com/6cfe41b279bbe53061fc4591d115038dc36acc593bb6062d0692b8a0810d1bde/68747470733a2f2f74652e6c656772612e70682f66696c652f3066373538333231613932613934323861366334382e6a7067">
</p>

<p align="center">
<a href="https://github.com/soloflix-bots/filestore/stargazers"><img src="https://img.shields.io/github/stars/soloflix-bots/filestore?color=black&logo=github&logoColor=black&style=for-the-badge" alt="Stars" /></a>
<a href="https://github.com/soloflix-bots/filestore/network/members"> <img src="https://img.shields.io/github/forks/soloflix-bots/filestore?color=black&logo=github&logoColor=black&style=for-the-badge" /></a>
<a href="https://github.com/soloflix-bots/filestore/blob/main/LICENSE"> <img src="https://img.shields.io/badge/License-MIT-blueviolet?style=for-the-badge" alt="License" /> </a>
<a href="https://www.python.org/"> <img src="https://img.shields.io/badge/Written%20in-Python-orange?style=for-the-badge&logo=python" alt="Python" /> </a>
<a href="https://github.com/soloflix-bots/filestore/commits/main"> <img src="https://img.shields.io/github/last-commit/soloflix-bots/filestore?color=blue&logo=github&logoColor=green&style=for-the-badge" /></a>
</p>

<p align="center">
<b>𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧 𝗠𝗘𝗧𝗛𝗢𝗗𝗦</b>
</p>

<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ 」─
</h3>

<p align="center"><a href="https://dashboard.heroku.com/new?template=https://github.com/soloflix-bots/filestore"> <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-black?style=for-the-badge&logo=heroku" width="220" height="38.45"/></a></p>

<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ᴠᴘs/ʟᴏᴄᴀʟ 」─
</h3>

<details><summary><b> - ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:</b></summary>

## ғᴇᴀᴛᴜʀᴇs
### ›› ʀᴇǫᴜᴇsᴛ ғᴏʀᴄᴇ sᴜʙ: 
<i>Request-based Force-Sub with private channel link and join request for flexible management.</i>

### ›› ᴄᴜsᴛᴏᴍ ғᴏʀᴄᴇ sᴜʙ: 
<i>Add unlimited Force-Sub channels; manage freely.</i>

### ›› ᴀᴅᴅ ᴍᴜʟᴛɪ ᴀᴅᴍɪɴs: 
<i>Add or remove multiple admins.</i>

### ›› ʙᴀɴ-ᴜɴʙᴀɴ: 
<i>Ban spammers or annoying users instantly.</i>

### ›› ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ: 
<i>Auto-delete shared files after a timer; re-generate link message sent afterward.</i>

### ›› ᴄᴏɴᴛᴇɴᴛ ʙᴜᴛᴛᴏɴ & sᴇᴛ ʙᴜᴛᴛᴏɴ: 
<i>Add custom buttons and links to shared files.</i>

### ›› ʜɪᴅᴇ/ᴘʀᴏᴛᴇᴄᴛ ᴄᴀᴘᴛɪᴏɴ: 
<i>Hide or protect captions from being forwarded.</i>

### ›› sᴛᴀʀᴛ & ғsᴜʙ ᴍᴇᴅɪᴀ:
<i>Set custom media for Start & Force-Sub messages.</i>

### ›› ꜰᴜʟʟʏ ᴇᴅɪᴛᴀʙʟᴇ ᴍᴇssᴀɢᴇs:
<i>Customize Start, About, Reply, FSUB texts with placeholders.</i>

</details>

<details><summary><b> - ᴀᴅᴍɪɴ ᴀɴᴅ ᴜsᴇʀs ᴄᴏᴍᴍᴀɴᴅs :</b></summary>

## ᴀᴅᴍɪɴ ᴀɴᴅ ᴜsᴇʀs ᴄᴏᴍᴍᴀɴᴅs
- **start** - Start the bot    
- **users** - View user list  
- **broadcast** - Send message to all  
- **batch** - Send in batches  
- **genlink** - Generate a link  
- **usage** - Check link usage  
- **pbroadcast** - Premium broadcast  
- **ban / unban** - Manage banned users 

</details>

<details><summary><b> - ᴠᴀʀɪᴀʙʟᴇs :</b></summary>

```python
# Bot Instance Configuration
SESSION = "your_session_name"
TOKEN = "your_bot_token"
API_ID = your_api_id
API_HASH = "your_api_hash"
WORKERS = 5

# Database Configuration
DB_URI = "your_mongodb_uri"
DB_NAME = "your_database_name"

# Force Subscription Channels [channel_id, request_enabled, timer_in_minutes]
FSUBS = [[-1001234567890, True, 10]]

# Database Channel
DB_CHANNEL = -1001234567890

# Auto Delete Timer (seconds)
AUTO_DEL = 300

# Admin IDs
ADMINS = [123456789, 987654321]

# Bot Settings
DISABLE_BTN = True
PROTECT = True

# Messages Configuration
MESSAGES = {
    "START": "Your start message here with {first}",
    "FSUB": "Your force subscription message",
    "ABOUT": "About message",
}

