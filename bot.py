import asyncio
import os
import logging
import discord
from discord.ext import commands
import mux_python
import requests
from config import MUX_TOKEN_ID, MUX_TOKEN_SECRET, DISCORD_BOT_TOKEN

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Set up Mux client
configuration = mux_python.Configuration()
configuration.username = MUX_TOKEN_ID
configuration.password = MUX_TOKEN_SECRET
mux_client = mux_python.ApiClient(configuration)
assets_api = mux_python.AssetsApi(mux_client)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')

@bot.command()
async def ping(ctx):
    logger.info(f'Ping command called by {ctx.author}')
    await ctx.send('Pong!')

@bot.command()
async def convert(ctx, message_link: str, generate_mp4: bool = False):
    logger.info(f'Convert command called by {ctx.author} with link: {message_link}')
    await ctx.send("Fetching video from message, please wait...")

    try:
        video_url = await get_video_url(ctx, message_link)
        if not video_url:
            return

        await ctx.send(f"Creating asset on Mux{'with MP4 support ' if generate_mp4 else ''}...")
        asset = await create_mux_asset(video_url, generate_mp4)

        playback_id = asset.data.playback_ids[0].id
        streaming_url = f"https://stream.mux.com/{playback_id}.m3u8"
        await ctx.send(f"Streaming URL: {streaming_url}")

        if generate_mp4:
            await process_mp4(ctx, asset, playback_id)

    except Exception as e:
        logger.error(f"Error in convert command: {str(e)}", exc_info=True)
        await ctx.send(f"An error occurred: {str(e)}")

async def get_video_url(ctx, message_link):
    # Extract message details from the link
    parts = message_link.split('/')
    if len(parts) < 7:
        await ctx.send("Invalid message link format. Please use a full Discord message link.")
        return None
    
    guild_id, channel_id, message_id = parts[-3:]
    logger.info(f"Extracted guild_id: {guild_id}, channel_id: {channel_id}, message_id: {message_id}")
    
    # Fetch the channel
    channel = bot.get_channel(int(channel_id))
    if not channel:
        logger.info(f"Channel not found in cache, fetching from API")
        try:
            channel = await bot.fetch_channel(int(channel_id))
        except discord.errors.Forbidden:
            await ctx.send("I don't have permission to access that channel.")
            return None
        except discord.errors.NotFound:
            await ctx.send("The specified channel was not found.")
            return None

    # Fetch the message
    try:
        message = await channel.fetch_message(int(message_id))
    except discord.errors.NotFound:
        await ctx.send("The specified message was not found.")
        return None
    except discord.errors.Forbidden:
        await ctx.send("I don't have permission to read messages in that channel.")
        return None

    logger.info(f"Message fetched successfully. Attachments: {len(message.attachments)}")

    # Find the first attachment that's a video
    video_attachment = next((att for att in message.attachments if att.content_type and att.content_type.startswith('video/')), None)

    if not video_attachment:
        await ctx.send("No video found in the linked message.")
        return None

    video_url = video_attachment.url
    logger.info(f"Found video URL: {video_url}")
    return video_url

async def create_mux_asset(video_url, generate_mp4=False):
    input_settings = mux_python.InputSettings(url=video_url)
    create_asset_request = mux_python.CreateAssetRequest(
        input=input_settings,
        playback_policy=['public'],
        mp4_support="capped-1080p" if generate_mp4 else None
    )
    
    asset = assets_api.create_asset(create_asset_request)
    logger.info(f"Asset created with ID: {asset.data.id}")
    
    if not await wait_for_asset_ready(asset.data.id):
        return None
    
    return asset

async def wait_for_asset_ready(asset_id, max_retries=30, retry_delay=10):
    for _ in range(max_retries):
        asset_data = assets_api.get_asset(asset_id)
        if asset_data.data.status == 'ready':
            logger.info("Asset is ready")
            return True
        logger.info(f"Asset not ready. Current status: {asset_data.data.status}")
        await asyncio.sleep(retry_delay)
    
    logger.error("Asset processing timed out")
    return False

async def process_mp4(ctx, asset, playback_id):
    mp4_quality = "capped-1080p"
    if not await wait_for_static_renditions(asset.data.id):
        await ctx.send("MP4 processing timed out. Please try again later.")
        return

    mp4_url = f"https://stream.mux.com/{playback_id}/{mp4_quality}.mp4"
    logger.info(f"Generated MP4 URL: {mp4_url}")
    await ctx.send(f"MP4 download URL: `{mp4_url}`")

async def wait_for_static_renditions(asset_id, max_retries=30, retry_delay=10):
    for _ in range(max_retries):
        asset_data = assets_api.get_asset(asset_id)
        if asset_data.data.status == 'ready':
            if asset_data.data.static_renditions and asset_data.data.static_renditions.status == 'ready':
                logger.info("Static renditions are ready")
                return True
            elif asset_data.data.static_renditions:
                logger.info(f"Waiting for static renditions. Current status: {asset_data.data.static_renditions.status}")
            else:
                logger.info("Static renditions not available yet")
        else:
            logger.info(f"Asset not ready. Current status: {asset_data.data.status}")
        
        await asyncio.sleep(retry_delay)
    
    logger.error("Static renditions processing timed out")
    return False

bot.run(DISCORD_BOT_TOKEN)