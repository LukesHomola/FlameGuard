import discord
from discord.ext import commands
import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Bot setup
intents = discord.Intents.all()
intents.members = True  # Required to fetch members from the Discord server
intents.messages = True  # Required to read messages for commands

bot = commands.Bot(command_prefix="!", intents=intents)

# Replace with your Discord Bot Token
token = os.getenv("BOT_TOKEN")

# Replace with the FlameKnights API URL
FLAMEKNIGHTS_API_URL = "https://api.wynncraft.com/v3/guild/FlameKnights"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot is ready to guard FlameKnights! 👑")

def normalize_name(name):
    """Remove emojis, special characters, and convert to lowercase."""
    # Remove common symbols, including those used for Discord and emojis
    name = re.sub(r'[^\w\s]', '', name)  # Remove everything except word characters and spaces
    name = re.sub(r'\s+', ' ', name).strip()  # Clean up extra spaces and normalize spacing
    return name.lower()

@bot.command()
async def check_members(ctx):
    """Check if all FlameKnights are in the Discord server."""
    await ctx.send("Checking members... 🔍")

    # Fetch guild data from Wynncraft API
    response = requests.get(FLAMEKNIGHTS_API_URL)
    if response.status_code != 200:
        await ctx.send("Failed to fetch guild data. Please try again later. 😢")
        return

    # Parse the guild data
    #guild_data = response.json()

    # Debugging print to inspect the structure of the guild data
    print(guild_data)  # This will show you the data structure

    if "members" not in guild_data:
        await ctx.send("Failed to find members in guild data. 😢")
        return

    # Extract player names from the guild data (case-insensitive)
    flameknights_players = []
    for role, role_members in guild_data["members"].items():
        if role == "total":
            continue  # Skip the "total" key
        if isinstance(role_members, dict):
            for member_name in role_members.keys():
                flameknights_players.append(member_name)
        else:
            await ctx.send(f"Unexpected format for role members: {role_members}")
            return

    # Fetch the list of Discord members (both display name and username)
    discord_members = [normalize_name(member.display_name) for member in ctx.guild.members] + \
                       [normalize_name(member.name) for member in ctx.guild.members]

    # Normalize the in-game player names
    normalized_flameknights_players = [normalize_name(player) for player in flameknights_players]

    # Find missing players
    missing_players = [player for player in normalized_flameknights_players if player not in discord_members]

    if not missing_players:
        await ctx.send("All FlameKnights are in the Discord server! 👑🎉")
    else:
        await ctx.send(f"Missing members: {', '.join(missing_players)} 😢")

        # Get the list of member names or nicknames in the server
        member_names = [member.display_name for member in ctx.guild.members]

        # Join the member names into a single string with line breaks
        member_list = member_names

        # Send a message to the channel with the list of members
        await ctx.send(f"Current members in the guild:\n{member_list}")

# Run the bot
bot.run(token = os.getenv("BOT_TOKEN")
)
