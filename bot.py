import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import time

# ✅ Load .env file
load_dotenv()

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Import the GuildSync cog
from cogs.guild_sync import GuildSync  # This imports the cog from the cogs folder
from cogs.challenges import Challenges  # This imports the cog from the cogs folder
from cogs.referral import Referral 

# Cooldown dictionary: {channel_id: last_triggered_timestamp}
cooldown_tracker = {}

# Define watched channels for automated role sync
WATCHED_CHANNELS = [1080919063213121636, 1080918159210594467]

# ✅ Startup event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("Bot is ready!")

    # Load all cogs after bot is ready
    await load_cogs()

# ✅ Load all valid cogs asynchronously
async def load_cogs():
    """Load all valid cogs, ignoring __init__.py"""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":  # ✅ Ignore __init__.py
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load cog {filename}: {e}")

# ✅ Add the GuildSync cog here
bot.add_cog(GuildSync(bot))  # Register the cog
bot.add_cog(Challenges(bot))
bot.add_cog(Referral(bot))

# ✅ Help message command
@bot.command()
async def guard_help(ctx):
    """Show the list of available commands"""
    embed = discord.Embed(title="FlameGuard Commands",
                          description="**!guard_help** - Show the list of available commands. " + "\n" +
                          "**!check_discord** - List of guild members missing on our discord. " + "\n" +
                          "**!assign_roles** - Assign discord member role if player is part of the guild. ",
                          color=discord.Color.red())
    await ctx.send(embed=embed)

# ✅ Reload a specific cog command (for bot owner)
@commands.is_owner()
@bot.command()
async def reload_cog(ctx, cog: str):
    """Reload a specific cog"""
    try:
        await bot.unload_extension(f"cogs.{cog}")
        await bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"✅ Reloaded `{cog}` successfully!")
    except Exception as e:
        await ctx.send(f"❌ Failed to reload `{cog}`: {e}")

# ✅ Ping command to check bot's status
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# ✅ on_message event handler to manage auto role assignments with cooldown
@bot.event
async def on_message(message):
    print(f"Message received in {message.channel.name}: {message.content}")  # Debug print
    current_time = time.time()
    channel_id = message.channel.id

    # Check if the channel is in the watched list and enforce a 10s cooldown
    if message.channel.id in WATCHED_CHANNELS:
        last_triggered = cooldown_tracker.get(channel_id, 0)

        if current_time - last_triggered >= 10:  # 10s cooldown
            cooldown_tracker[channel_id] = current_time  # Update cooldown

            print(f"Activated auto assign in {message.channel.name}")  # Debug print
            # Pass the guild for processing
            await assign_roles_silent(message.guild)

        else:
            print(f"Cooldown active for {message.channel.name}, skipping execution.")  # Debug print

    await bot.process_commands(message)  # Ensure commands still work

# ✅ Silent (without chat logging) version of the assign_roles command
async def assign_roles_silent(guild):
    """Assign the correct in-game rank role to matching guild members **without sending messages**."""
    # Your role assignment logic goes here...

# ✅ Main function to start bot
async def main():
    """Main function to start bot"""
    
    # Ensure BOT_TOKEN is not None
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ ERROR: BOT_TOKEN is not set. Check your .env file.")
        return
    
    # Start bot
    await bot.start(token)

# ✅ Fix: Use `asyncio.new_event_loop()` to avoid event loop issues
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
