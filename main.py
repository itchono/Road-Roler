import discord
from discord.ext import commands
from discord_slash import SlashCommand
from modules.mongodb import setup

import os
import dotenv

from keep_alive import keep_alive

setup()
dotenv.load_dotenv()  # Load .env file, prior to components loading

bot = commands.Bot(command_prefix="roler ")
slash = SlashCommand(bot, override_type=True,
                     sync_commands=True, sync_on_cog_reload=True,
                     delete_from_unused_guilds=True)

bot.load_extension("modules.roler")

keep_alive()
bot.run(os.environ.get("TOKEN"))
