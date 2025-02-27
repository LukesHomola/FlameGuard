import discord
from discord.ext import commands
import mysql.connector
import os
import requests


class Referral(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.connect_db()

    # Connecting to database
    def connect_db(self):
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password=os.getenv("DB_PASS"),
                database=os.getenv("DB_NAME")  
            )
            print("✅ Connected to MySQL")
            return conn
        except mysql.connector.Error as e:
            print(f"❌ Failed to connect to MySQL: {e}")
            return None


    @commands.command(name="refer")
    async def refer(self, ctx, referred_ign: str = None):
        """Command to add a referral (only IGN is needed)"""
        # Permissions required to use
        required_role = "FlameKnight"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            print(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        if not referred_ign:
            await ctx.send("❌ Incorrect usage \n\n **Usage:** `!refer <IGN>`\n Example: `!refer Steve`")
            return
        
        referred_member = None

        # Fetching guild players to get playtime at join
        response = requests.get("https://api.wynncraft.com/v3/player/" + referred_ign)
        referred = response.json() 
        playtime = referred.get("playtime", 0) 

        # Print raw response (before converting to JSON)
        print(f"Response Status Code: {response.status_code}")
        print(f"Raw Response Text: {response.text}")
        print(f"Player Playtime: {playtime} hours")
        

        if response.status_code != 200:
            return await print(f"❌ Failed to fetch player data for `{referred_ign}`. Try again later.")
        else:
            guild_data = response.json()
            print(guild_data)  # Print the full JSON response for debugging


        # If mention is used (ex: !refer @Steve), extract user ID
        if referred_ign.startswith("<@") and referred_ign.endswith(">"):
            mentioned_id = referred_ign.strip("<@!>")  # Remove <@ and > and also handle <@!ID> format
            referred_member = ctx.guild.get_member(int(mentioned_id))
        else:
            # Normalize the input (convert to lowercase and remove leading emoji/symbol)
            normalized_ign = referred_ign.lower().lstrip("🔱🛡️⚜️⭐🌟📃👑")  # Add more symbols if needed

            # Try matching by exact Discord username
            referred_member = discord.utils.find(lambda m: m.name.lower() == normalized_ign, ctx.guild.members)

            # If not found, try matching by Discord server nickname (display_name)
            if not referred_member:
                referred_member = discord.utils.find(lambda m: m.display_name.lower().lstrip("🔥⭐🌟💀") == normalized_ign, ctx.guild.members)

        if not referred_member:
            return await ctx.send(f"❌ Member not found \n\n Could not find the user `{referred_ign}` in the server.")

        bot_role = discord.utils.get(ctx.guild.roles, name="🤖BOT")

        if referred_member.bot or (bot_role and bot_role in referred_member.roles):
            return await ctx.send(f"❌ `{referred_member.display_name}` cannot referr a bot.")

        referred_ign = referred_member.display_name  # Store clean username in the database
        referred_id = referred_member.id  

        referrer_ign = ctx.author.name
        referrer_id = ctx.author.id

        if not self.db:
            await ctx.send("❌ Database connection is unavailable.")
            return

        query = """
        INSERT INTO referrals (referrer_ign, referrer_id, referred_ign, referred_id, logged_at, referred_since, last_activity, valid, hours)
        VALUES (%s, %s, %s, %s, NOW(), NUll, NULL, FALSE, %s)
        """
        values = (referrer_ign, referrer_id, referred_ign, referred_id, playtime)

        try:
            cursor = self.db.cursor()
            cursor.execute(query, values)
            self.db.commit()
            await ctx.send(f"✅ Referral created \n\n {referred_ign} has been referred by {referrer_ign}, but is **not verified yet**.")
        except mysql.connector.Error as e:
            await ctx.send(f"❌ Error adding referral: {e}")

    @commands.command(name="referal_list")
    async def referal_list(self, ctx):
        required_role = "FlameKnight"
        member = ctx.author

        if not discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"❌ {member.display_name} does not have the `{required_role}` role!")
            return

        if not self.db:
            return await ctx.send("❌ Database connection is unavailable.")

        query = "SELECT id, referrer_ign, referred_ign, logged_at, valid FROM referrals"

        try:
            cursor = self.db.cursor()
            cursor.execute(query)
            referrals = cursor.fetchall()
            cursor.close()

            if not referrals:
                await ctx.send("📜 No referrals found.")
                return

            # 📜 Simple Test Embed
            embed = discord.Embed(
                title="📜 Referral List",
                description="List of all referrals in the database. \n",
                color=discord.Color.blue()
            )
            referral_text = ""

            for row in referrals[:10]:  # Limit to avoid issues
                ref_id, referrer, referred, logged_at, valid = row
                logged_at = logged_at.strftime("%Y-%m-%d %H:%M") if logged_at else "N/A"
                verified = "✅" if valid else "❌"

                # Append each referral with clear spacing
                referral_text += (
                    f"⠀⠀⠀⠀⠀⠀⠀\n" 
                    f"**#️⃣ Referral #{ref_id}**\n"
                    f"👤 Recruiter: **{referrer}**\n"
                    f"👥 New Member: **{referred}**\n"
                    f"🕒 Logged: **{logged_at}**\n"
                    f"📝 Verified: **{verified}**\n"
                    f"⠀⠀⠀⠀⠀⠀⠀\n" 
                )

            # Add final text as a single field
            embed.add_field(name="", value=referral_text, inline=False)

            await ctx.send(embed=embed)  # ✅ Test if Embed Sends
        except mysql.connector.Error as e:
            await ctx.send(f"❌ Database error: {e}")

# Register cog
async def setup(bot):
    await bot.add_cog(Referral(bot))
