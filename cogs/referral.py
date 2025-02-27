import discord
from discord.ext import commands
import mysql.connector
import os

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
        INSERT INTO referrals (referrer_ign, referrer_id, referred_ign, referred_id, referred_since, logged_at, valid)
        VALUES (%s, %s, %s, %s, NOW(), NULL, FALSE)
        """
        values = (referrer_ign, referrer_id, referred_ign, referred_id)

        try:
            cursor = self.db.cursor()
            cursor.execute(query, values)
            self.db.commit()
            await ctx.send(f"✅ Referral created \n\n {referred_ign} has been referred by {referrer_ign}, but is **not verified yet**.")
        except mysql.connector.Error as e:
            await ctx.send(f"❌ Error adding referral: {e}")

        




# Register cog
async def setup(bot):
    await bot.add_cog(Referral(bot))
