import disnake as discord
from disnake.ext import commands
import dotenv
import os
import aiohttp
import json
import sqlite3

dotenv.load_dotenv()

pxls_auth = os.environ['PXLS_AUTH']

ADMINS = [int(admin) for admin in os.environ['BOT_ADMINS'].split(',')]

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def cog_slash_command_check(self, ctx: discord.ApplicationCommandInteraction):
        return ctx.author.id in ADMINS

    # @commands.Cog.listener()    
    # async def on_slash_command_error(self, ctx, error):
    #     if isinstance(error, commands.errors.CheckFailure):
    #         await ctx.response.send_message('<a:nuhuh:1262041901440303157> You do not have permission to use this command', ephemeral=True)

    # @commands.slash_command(name='admin_echo', description='(Bot Admin Only) Echo a message')
    # async def echo(self, ctx: discord.ApplicationCommandInteraction, message: str):
    #     await ctx.response.send_message(message)

    # @commands.slash_command(name='admin_edit', description='(Bot Admin Only) Edit any message sent by the bot')
    # async def edit(
    #     self,
    #     ctx: discord.ApplicationCommandInteraction, 
    #     message_id: int = commands.Param(name='message_id', description='The message ID to edit'),
    #     message: str = commands.Param(name='message', description='The new message')):
    #     try:
    #         message = await ctx.channel.fetch_message(message_id)
    #         await message.edit(content=message)
    #     except discord.NotFound:
    #         await ctx.response.send_message('Message not found', ephemeral=True)

    # @commands.slash_command(name='admin_delete', description='(Bot Admin Only) Delete any message sent by the bot')
    # async def delete(
    #     self,
    #     ctx: discord.ApplicationCommandInteraction, 
    #     message_id: int = commands.Param(name='message_id', description='The message ID to delete')):
    #     try:
    #         message = await ctx.channel.fetch_message(message_id)
    #         await message.delete()
    #     except discord.NotFound:
    #         await ctx.response.send_message('Message not found', ephemeral=True)

    @commands.slash_command(name='alert_override', description='(Bot Admin Only) (be careful with this command) Manually override alert levels in the grief database')
    async def manual_override(self, ctx: discord.ApplicationCommandInteraction, channel_id: str, alert: str):
        grief_db = sqlite3.connect('grief.db')
        c = grief_db.cursor()
        c.execute('UPDATE grief SET alert = ? WHERE channel_id = ?', (alert, channel_id))
        grief_db.commit()
        grief_db.close()
        await ctx.response.send_message(f'Overriding {channel_id} with alert {alert}')
    
    @commands.slash_command(name='ego_override', description='(Bot Admin Only) (be careful with this command) Manually override ego data in the ego database')
    async def ego_override(self, ctx: discord.ApplicationCommandInteraction, pxls_username: str, ego: str, canvas: bool = commands.Param(name='canvas', description='Whether to override the canvas ego (default: false)', default=False)):
        db = sqlite3.connect('cogs/databases/db.db')
        c = db.cursor()
        if canvas:
            c.execute('UPDATE canvasegos SET ego = ? WHERE pxls_username = ?', (ego, pxls_username))
        else:
            c.execute('UPDATE egos SET ego = ? WHERE pxls_username = ?', (ego, pxls_username))
        db.commit()
        db.close()
        await ctx.response.send_message(f'Overriding {pxls_username} with ego {ego}')

    @commands.slash_command(name='ego_delete', description='(Bot Admin Only) (be careful with this command) Delete ego data from the ego database')
    async def ego_delete(self, ctx: discord.ApplicationCommandInteraction, pxls_username: str, canvas: bool = commands.Param(name='canvas', description='Whether to delete the canvas ego (default: false)', default=False)):
        db = sqlite3.connect('cogs/databases/db.db')
        c = db.cursor()
        if canvas:
            c.execute('DELETE FROM canvasegos WHERE pxls_username = ?', (pxls_username,))
        else:
            c.execute('DELETE FROM egos WHERE pxls_username = ?', (pxls_username,))
        db.commit()
        db.close()
        await ctx.response.send_message(f'Deleted ego data for {pxls_username}')

    @commands.slash_command(name='infodownload', description='(Bot Admin Only) Download the info page from pxls.space')
    async def infodownload(self, ctx: discord.ApplicationCommandInteraction):
        headers = {
            "x-pxls-cfauth": pxls_auth
        }
        timeout = aiohttp.ClientTimeout(sock_connect=10, sock_read=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://pxls.space/info", headers=headers) as response:
                info = await response.json()
                with open('info/info.json', 'w') as f:
                    f.write(json.dumps(info))
        await ctx.response.send_message('Info page downloaded')
    

def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog('Admin')