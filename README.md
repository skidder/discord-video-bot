# Discord Video Converter Bot

This Discord bot allows users to convert videos shared in Discord messages to streaming formats and optionally to MP4 files using [Mux's](https://www.mux.com/) video processing services.

## Features

- Convert videos from Discord message links to streaming URLs
- Optionally generate downloadable MP4 files
- Simple command interface within Discord

## Prerequisites

- Python 3.7+
- Discord Bot Token
- Mux API credentials

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/skidder/discord-video-bot.git
   cd discord-video-bot
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:
   ```
   MUX_TOKEN_ID=your_mux_token_id
   MUX_TOKEN_SECRET=your_mux_token_secret
   DISCORD_BOT_TOKEN=your_discord_bot_token
   ```

## Usage

1. Start the bot:
   ```
   python bot.py
   ```

2. In Discord, use the following commands:
   - To convert a video to streaming format:
     ```
     !convert <message_link>
     ```
   - To convert a video to streaming format and generate an MP4:
     ```
     !convert <message_link> True
     ```

## Configuration

You can adjust the following settings in `bot.py`:
- `mp4_quality`: Change the quality of the generated MP4 (default: "capped-1080p")
- `max_retries` and `retry_delay`: Adjust the waiting time for video processing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This bot is for educational purposes only. Ensure you have the right to convert and distribute any videos processed by this bot.

