import discord
from discord.ext import commands
import requests
import re
import os
from dotenv import load_dotenv
import time


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
GUILD_ROLE_NAME = "FlameKnight"
# Mapping Wynncraft ranks to Discord roles
RANK_ROLE_MAPPING = {
    "owner": "👑Emperor",
    "chief": "🌟High King",
    "strategist": "⭐ArchDuke",
    "captain": "⚜️Baron",
    "recruiter": "🛡️Duke",
    "recruit": "🔱Knight"
}

# Define watched channels for automated role sync
WATCHED_CHANNELS = [1080919063213121636,
                    1080918159210594467]

# Cooldown dictionary: {channel_id: last_triggered_timestamp}
cooldown_tracker = {}

#
# Startup event
#


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot is ready to guard FlameKnights! 👑")

#
# Silent (without chat logging) version of the assign_roles command
#


async def assign_roles_silent(guild):
    """Assign the correct in-game rank role to matching guild members **without sending messages**."""

    # Fetch guild data from Wynncraft API
    response = requests.get(FLAMEKNIGHTS_API_URL)
    if response.status_code != 200:
        print("Failed to fetch guild data. Please try again later. 😢")
        return

    guild_data = response.json()
    if "members" not in guild_data:
        print("Failed to find members in guild data. 😢")
        return

    # Extract player names from the guild
    flameknights_players = []
    for role, role_members in guild_data["members"].items():
        if isinstance(role_members, dict):
            flameknights_players.extend(role_members.keys())

    # Normalize names
    normalized_guild_players = [normalize_name(
        player) for player in flameknights_players]

    # Normalize both Discord usernames and display names
    normalized_discord_users = {
        normalize_name(member.name): member for member in guild.members
    }
    normalized_discord_display_names = {
        normalize_name(member.display_name): member for member in guild.members
    }

    assigned_count = 0

    # Go through each in-game rank and assign the corresponding role
    for in_game_rank, discord_role_name in RANK_ROLE_MAPPING.items():
        if in_game_rank in guild_data["members"]:
            discord_role = discord.utils.get(guild.roles, name=discord_role_name)
            if discord_role:
                for player_name in guild_data["members"][in_game_rank].keys():
                    normalized_player_name = normalize_name(player_name)
                    member = normalized_discord_users.get(normalized_player_name) or normalized_discord_display_names.get(
                        normalized_player_name)

                    if member:
                        # Assign the correct in-game rank role (one role only)
                        if discord_role not in member.roles:
                            try:
                                await member.add_roles(discord_role)
                                assigned_count += 1
                                print(f"Assigned {discord_role.name} role to {member.display_name}")
                            except discord.Forbidden:
                                print(f"❌ No permission to assign the {discord_role_name} role to {member.display_name}.")
                            except discord.HTTPException:
                                print(f"⚠️ Failed to assign the {discord_role_name} role to {member.display_name}.")
    
    print(f"Assigned roles silently to {assigned_count} members.")

#
# Automated guild members sync without messages
#


@bot.event
async def on_message(message):
    current_time = time.time()
    channel_id = message.channel.id

    # Check if the channel is in the watched list and enforce a 10s cooldown
    if message.channel.id in WATCHED_CHANNELS:
        last_triggered = cooldown_tracker.get(channel_id, 0)

        if current_time - last_triggered >= 10:  # 10s cooldown
            cooldown_tracker[channel_id] = current_time  # Update cooldown

            print(f"Activated auto assign in {message.channel.name}")
            # Pass the guild for processing
            await assign_roles_silent(message.guild)

        else:
            print(f"Cooldown active for {message.channel.name}, skipping execution.")

    await bot.process_commands(message)  # Ensure commands still work

#
# Normalize the player name by removing emojis, special characters, and converting to lowercase.
#


def normalize_name(name):
    """Remove emojis, special characters, and convert to lowercase."""
    # Remove common symbols, including those used for Discord and emojis
    # Remove everything except word characters and spaces
    name = re.sub(r'[^\w\s]', '', name)
    # Clean up extra spaces and normalize spacing
    name = re.sub(r'\s+', ' ', name).strip()
    return name.lower()

# Run the bot
bot.run(token=os.getenv("BOT_TOKEN"))
