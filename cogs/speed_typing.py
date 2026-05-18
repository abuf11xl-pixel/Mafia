import discord
from discord.ext import commands
import random
import asyncio
import time

class SpeedTyping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
    
    WORDS = [
        "البرمجة", "الكمبيوتر", "المسلسل", "الفيلم", "الموسيقى",
        "الرياضة", "اللعبة", "الدراسة", "المدرسة", "الجامعة",
        "الصديق", "الأسرة", "البيت", "الشارع", "المدينة",
        "الطعام", "الشراب", "التكنولوجيا", "الإنترنت", "الهاتف",
        "السيارة", "الطائرة", "القطار", "الحيوان", "الطبيعة"
    ]
    
    @commands.command(name="سرعة_الكتابة")
    async def speed_typing(self, ctx, rounds: int = 3):
        """لعبة سرعة الكتابة"""
        
        if rounds < 1 or rounds > 10:
            await ctx.send("❌ عدد الجولات يجب أن يكون بين 1 و 10!")
            return
        
        game_id = ctx.guild.id
        
        if game_id in self.games:
            await ctx.send("❌ هناك لعبة جارية بالفعل!")
            return
        
        self.games[game_id] = {
            "rounds": rounds,
            "current_round": 0,
            "scores": {},
            "channel": ctx.channel
        }
        
        embed = discord.Embed(
            title="⌨️ لعبة سرعة الكتابة",
            description=f"تم بدء اللعبة! {rounds} جولات",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📝 التعليمات:",
            value="سيتم إرسال كلمة عشوائية. من يكتبها أولاً يحصل على النقاط!",
            inline=False
        )
        
        await ctx.send(embed=embed)
        await asyncio.sleep(2)
        
        await self.run_typing_game(ctx, game_id)
    
    async def run_typing_game(self, ctx, game_id):
        """تشغيل لعبة السرعة"""
        game = self.games[game_id]
        
        for round_num in range(1, game["rounds"] + 1):
            game["current_round"] = round_num
            
            word = random.choice(self.WORDS)
            
            embed = discord.Embed(
                title=f"⌨️ الجولة {round_num}/{game['rounds']}",
                description=f"**اكتب هذه الكلمة:**\n\n`{word}`",
                color=discord.Color.blue()
            )
            
            msg = await ctx.send(embed=embed)
            
            start_time = time.time()
            winner = None
            
            def check(m):
                return m.channel == ctx.channel and m.content.strip() == word
            
            try:
                result = await self.bot.wait_for("message", check=check, timeout=30)
                elapsed_time = time.time() - start_time
                winner = result.author
                
                # حساب النقاط
                if elapsed_time < 3:
                    points = 100
                elif elapsed_time < 5:
                    points = 90
                elif elapsed_time < 8:
                    points = 80
                else:
                    points = max(50, 100 - int(elapsed_time * 5))
                
                game["scores"][winner] = game["scores"].get(winner, 0) + points
                
                embed = discord.Embed(
                    title="✅ إجابة صحيحة!",
                    description=f"{winner.mention}\n⏱️ **الوقت:** {elapsed_time:.2f} ثانية\n🏆 **النقاط:** {points}",
                    color=discord.Color.green()
                )
                
                await ctx.send(embed=embed)
                
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="⏰ انتهت الجولة!",
                    description=f"لم يتمكن أحد من كتابة الكلمة بالوقت المحدد!",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
            
            await asyncio.sleep(2)
        
        # النتيجة النهائية
        sorted_scores = sorted(game["scores"].items(), key=lambda x: x[1], reverse=True)
        
        leaderboard = "\n".join(
            [f"{i+1}. {player.mention} - {score} 🏆" for i, (player, score) in enumerate(sorted_scores)]
        )
        
        embed = discord.Embed(
            title="🏅 نتائج اللعبة",
            description=leaderboard,
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)
        del self.games[game_id]

async def setup(bot):
    await bot.add_cog(SpeedTyping(bot))
