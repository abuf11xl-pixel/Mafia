import discord
from discord.ext import commands
import os

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول: {bot.user}")
    print("🎮 الألعاب جاهزة!")

# تحميل الملحقات (Cogs)
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ تم تحميل: {filename}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start("YOUR_BOT_TOKEN_HERE")  # ضع توكن البوت هنا

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
