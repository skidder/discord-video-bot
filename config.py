import os
from dotenv import load_dotenv

load_dotenv()

MUX_TOKEN_ID = os.getenv('MUX_TOKEN_ID')
MUX_TOKEN_SECRET = os.getenv('MUX_TOKEN_SECRET')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')