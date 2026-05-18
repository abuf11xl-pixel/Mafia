import discord
from discord.ext import commands
import random
import asyncio
from enum import Enum

class Role(Enum):
    MAFIA = "مافيا"
    VILLAGER = "مدني"
    DETECTIVE = "محقق"
    DOCTOR = "طبيب"

class MafiaGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
    
    @commands.command(name="ماfia")
    async def mafia(self, ctx, num_players: int = 5):
        """بدء لعبة المافيا"""
        
        if num_players < 4 or num_players > 20:
            await ctx.send("❌ عدد اللاعبين يجب أن يكون بين 4 و 20!")
            return
        
        game_id = ctx.guild.id
        
        if game_id in self.games:
            await ctx.send("❌ هناك لعبة جارية بالفعل!")
            return
        
        self.games[game_id] = {
            "players": [],
            "max_players": num_players,
            "channel": ctx.channel,
            "state": "waiting",
            "roles": {}
        }
        
        embed = discord.Embed(
            title="🎭 لعبة المافيا",
            description=f"انضم للعبة! ({len(self.games[game_id]['players'])}/{num_players})",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="📝 التعليمات:",
            value="اكتب `!انضم` للانضمام للعبة\nعندما يكتمل العدد اكتب `!ابدأ`",
            inline=False
        )
        
        game_msg = await ctx.send(embed=embed)
        self.games[game_id]["message"] = game_msg
    
    @commands.command(name="انضم")
    async def join_game(self, ctx):
        """الانضمام للعبة"""
        
        game_id = ctx.guild.id
        
        if game_id not in self.games:
            await ctx.send("❌ لا توجد لعبة جارية!")
            return
        
        game = self.games[game_id]
        
        if ctx.author in game["players"]:
            await ctx.send("❌ أنت بالفعل في اللعبة!")
            return
        
        if len(game["players"]) >= game["max_players"]:
            await ctx.send("❌ اللعبة امتلأت!")
            return
        
        game["players"].append(ctx.author)
        
        embed = discord.Embed(
            title="🎭 لعبة المافيا",
            description=f"✅ {ctx.author.mention} انضم للعبة!\n\n({len(game['players'])}/{game['max_players']})",
            color=discord.Color.green()
        )
        embed.add_field(
            name="اللاعبون:",
            value="\n".join([p.mention for p in game["players"]]),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ابدأ")
    async def start_game(self, ctx):
        """بدء اللعبة"""
        
        game_id = ctx.guild.id
        
        if game_id not in self.games:
            await ctx.send("❌ لا توجد لعبة جارية!")
            return
        
        game = self.games[game_id]
        
        if len(game["players"]) < 4:
            await ctx.send("❌ يجب أن يكون هناك 4 لاعبين على الأقل!")
            return
        
        game["state"] = "started"
        
        # توزيع الأدوار
        players = game["players"].copy()
        random.shuffle(players)
        
        num_mafia = max(1, len(players) // 3)
        
        roles = []
        for i, player in enumerate(players):
            if i < num_mafia:
                role = Role.MAFIA
            elif i == num_mafia:
                role = Role.DETECTIVE
            elif i == num_mafia + 1:
                role = Role.DOCTOR
            else:
                role = Role.VILLAGER
            
            game["roles"][player] = role
            roles.append((player, role))
        
        # إرسال الأدوار للاعبين بشكل خاص
        for player, role in roles:
            try:
                embed = discord.Embed(
                    title="🎭 دورك في لعبة المافيا",
                    description=f"أنت: **{role.value}**",
                    color=discord.Color.red() if role == Role.MAFIA else discord.Color.green()
                )
                embed.add_field(
                    name="معلومات الدور:",
                    value=self.get_role_info(role),
                    inline=False
                )
                
                await player.send(embed=embed)
            except:
                pass
        
        embed = discord.Embed(
            title="🎭 لعبة المافيا - بدأت!",
            description=f"تم توزيع الأدوار على {len(players)} لاعبين",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="📊 إحصائيات:",
            value=f"🔴 المافيا: {num_mafia}\n👮 المحقق: 1\n🏥 الطبيب: 1\n🏘️ المدنيون: {len(players) - num_mafia - 2}",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # بدء مراحل اللعبة
        await self.play_game(ctx, game_id)
    
    def get_role_info(self, role):
        """الحصول على معلومات الدور"""
        info = {
            Role.MAFIA: "🔴 **المافيا**: تقتل لاعب واحد كل ليل. فوزك عندما تساوي عدد المافيا عدد المدنيين.",
            Role.VILLAGER: "🏘️ **المدني**: لاعب عادي. ابحث عن المافيا عن طريق التصويت.",
            Role.DETECTIVE: "👮 **المحقق**: تستطيع التحقق من دور لاعب واحد كل ليل.",
            Role.DOCTOR: "🏥 **الطبيب**: تستطيع حماية لاعب واحد من القتل كل ليل."
        }
        return info.get(role, "دور غير معروف")
    
    async def play_game(self, ctx, game_id):
        """تشغيل مراحل اللعبة"""
        game = self.games[game_id]
        day_number = 1
        
        while True:
            # فحص شروط الفوز
            mafia_count = sum(1 for p in game["players"] if game["roles"].get(p) == Role.MAFIA and p.name != "")
            villager_count = sum(1 for p in game["players"] if game["roles"].get(p) != Role.MAFIA and p.name != "")
            
            if mafia_count == 0:
                await ctx.send("✅ **انتصر المدنيون!** تم القضاء على جميع أفراد المافيا!")
                break
            
            if mafia_count >= villager_count:
                await ctx.send("❌ **انتصرت المافيا!** أصبحوا أكثرية!")
                break
            
            # مرحلة النهار
            embed = discord.Embed(
                title=f"☀️ اليوم {day_number}",
                description="حان وقت التصويت! من تريد أن تزيل?",
                color=discord.Color.gold()
            )
            
            await ctx.send(embed=embed)
            await asyncio.sleep(3)
            
            # مرحلة الليل
            embed = discord.Embed(
                title="🌙 الليل",
                description="المافيا تختار الهدف... الطبيب يحمي... المحقق يتحقق...",
                color=discord.Color.blue()
            )
            
            await ctx.send(embed=embed)
            await asyncio.sleep(3)
            
            day_number += 1
            
            if day_number > 10:
                await ctx.send("⏰ انتهت اللعبة بسبب انقضاء الوقت!")
                break
        
        del self.games[game_id]

async def setup(bot):
    await bot.add_cog(MafiaGame(bot))
