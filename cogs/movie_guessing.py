import discord
from discord.ext import commands
import random
import asyncio

class MovieGuessing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
    
    MOVIES = [
        {
            "name": "Inception",
            "hints": [
                "🎬 فيلم حول الأحلام والواقع",
                "🎬 بطولة ليوناردو دي كابريو",
                "🎬 من إخراج كريستوفر نولان",
                "🎬 الفيلم يتعامل مع مستويات متعددة من الأحلام"
            ]
        },
        {
            "name": "Breaking Bad",
            "hints": [
                "🎬 مسلسل درامي أمريكي",
                "🎬 بطولة برايان كرانستون",
                "🎬 عن معلم كيمياء يصبح مجرماً",
                "🎬 يدور حول تصنيع الميثامفيتامين"
            ]
        },
        {
            "name": "Titanic",
            "hints": [
                "🎬 فيلم رومانسي درامي",
                "🎬 عن غرق سفينة",
                "🎬 بطولة ليوناردو دي كابريو وكيت وينسلت",
                "🎬 تدور أحداثه على السفينة تايتانك"
            ]
        },
        {
            "name": "The Matrix",
            "hints": [
                "🎬 فيلم خيال علمي",
                "🎬 يتعلق بالواقع الافتراضي",
                "🎬 بطولة كيانو ريفز",
                "🎬 يحتوي على مشاهد حركة مشهورة"
            ]
        },
        {
            "name": "Game of Thrones",
            "hints": [
                "🎬 مسلسل خيالي ملحمي",
                "🎬 يتعلق بالعروش والقوة",
                "🎬 عدد من الممثلين المشهورين",
                "🎬 يدور في عوالم خيالية مع تنانين"
            ]
        },
        {
            "name": "Avengers",
            "hints": [
                "🎬 فيلم كوميكس سوبر هيرو",
                "🎬 فريق من الأبطال الخارقين",
                "🎬 تجمع شخصيات متعددة",
                "🎬 عن محاربة الشرور"
            ]
        },
        {
            "name": "Pulp Fiction",
            "hints": [
                "🎬 فيلم جريمة وعنف",
                "🎬 من إخراج كوينتين تارانتينو",
                "🎬 أحداث متشابكة ومتداخلة",
                "🎬 بطولة جون ترافولتا وأوما ثورمان"
            ]
        },
        {
            "name": "The Shawshank Redemption",
            "hints": [
                "🎬 فيلم درامي سجن",
                "🎬 عن الخروج من السجن",
                "🎬 صداقة قوية بين شخصين",
                "🎬 فيلم كلاسيكي مشهور جداً"
            ]
        },
        {
            "name": "Interstellar",
            "hints": [
                "🎬 فيلم خيال علمي ملحمي",
                "🎬 عن السفر عبر الثقوب السوداء",
                "🎬 بطولة ماثيو ماكونهي",
                "🎬 من إخراج كريستوفر نولان"
            ]
        },
        {
            "name": "The Dark Knight",
            "hints": [
                "🎬 فيلم سوبر هيرو",
                "🎬 البطل خفافيش",
                "🎬 في مدينة ملحة",
                "🎬 يحارب الجريمة"
            ]
        }
    ]
    
    @commands.command(name="تخمين_الفيلم")
    async def movie_guessing(self, ctx, rounds: int = 3):
        """لعبة تخمين الفيلم"""
        
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
            title="🎬 لعبة تخمين الفيلم/المسلسل",
            description=f"تم بدء اللعبة! {rounds} جولات",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="📝 التعليمات:",
            value="سيتم إعطاؤك تلميحات عن فيلم أو مسلسل. خمن الاسم! من يتخمن أولاً يحصل على النقاط!",
            inline=False
        )
        
        await ctx.send(embed=embed)
        await asyncio.sleep(2)
        
        await self.run_movie_game(ctx, game_id)
    
    async def run_movie_game(self, ctx, game_id):
        """تشغيل لعبة تخمين الفيلم"""
        game = self.games[game_id]
        
        for round_num in range(1, game["rounds"] + 1):
            game["current_round"] = round_num
            
            movie = random.choice(self.MOVIES)
            movie_name = movie["name"]
            hints = movie["hints"]
            
            embed = discord.Embed(
                title=f"🎬 الجولة {round_num}/{game['rounds']}",
                description=f"**التلميح الأول:**\n{hints[0]}",
                color=discord.Color.purple()
            )
            
            hint_msg = await ctx.send(embed=embed)
            
            hint_index = 1
            
            def check(m):
                return (m.channel == ctx.channel and 
                       m.content.strip().lower() == movie_name.lower() and
                       m.author != self.bot.user)
            
            start_time = None
            winner = None
            correct = False
            
            while hint_index < len(hints):
                try:
                    result = await self.bot.wait_for("message", check=check, timeout=20)
                    if start_time is None:
                        start_time = 0
                    
                    elapsed_time = 20 * (hint_index - 1)
                    winner = result.author
                    correct = True
                    
                    # حساب النقاط
                    if hint_index == 1:
                        points = 100
                    elif hint_index == 2:
                        points = 80
                    elif hint_index == 3:
                        points = 60
                    else:
                        points = 40
                    
                    game["scores"][winner] = game["scores"].get(winner, 0) + points
                    
                    embed = discord.Embed(
                        title="✅ إجابة صحيحة!",
                        description=f"{winner.mention}\n🎬 **الفيلم:** {movie_name}\n🏆 **النقاط:** {points}",
                        color=discord.Color.green()
                    )
                    
                    await ctx.send(embed=embed)
                    break
                    
                except asyncio.TimeoutError:
                    if hint_index < len(hints) - 1:
                        hint_index += 1
                        embed = discord.Embed(
                            title=f"🎬 الجولة {round_num}/{game['rounds']}",
                            description=f"**التلميح {hint_index}:**\n{hints[hint_index - 1]}",
                            color=discord.Color.purple()
                        )
                        hint_msg = await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title="⏰ انتهت الجولة!",
                            description=f"لم يتمكن أحد من التخمين!\n🎬 **الإجابة:** {movie_name}",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                        break
            
            await asyncio.sleep(2)
        
        # النتيجة النهائية
        if game["scores"]:
            sorted_scores = sorted(game["scores"].items(), key=lambda x: x[1], reverse=True)
            
            leaderboard = "\n".join(
                [f"{i+1}. {player.mention} - {score} 🏆" for i, (player, score) in enumerate(sorted_scores)]
            )
            
            embed = discord.Embed(
                title="🏅 نتائج اللعبة",
                description=leaderboard,
                color=discord.Color.gold()
            )
        else:
            embed = discord.Embed(
                title="🏅 نتائج اللعبة",
                description="لم يحصل أحد على نقاط!",
                color=discord.Color.gold()
            )
        
        await ctx.send(embed=embed)
        del self.games[game_id]

async def setup(bot):
    await bot.add_cog(MovieGuessing(bot))
