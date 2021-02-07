import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext.commands import CommandNotFound

clean_id = ['<', '@', '!', '>']

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!')

characters = {}
if os.path.exists('characters.json'):
    with open('characters.json', 'r') as fp:
        characters = json.load(fp)


@bot.event
async def on_ready():
    print("Ready!")
    for guild in bot.guilds:
        try:
            characters[str(guild.id)]
        except KeyError:
            characters[str(guild.id)] = {}
    print('Character Database:')
    print(json.dumps(characters, indent=2))


@bot.command(name='register')
async def register(ctx, user_name, character_name, portrait, color):
    if color.startswith("#"):
        color = color[1:]
    character = {
        "name": character_name,
        "portrait": portrait,
        "color": color,
        "active": True
    }
    try:
        characters[str(ctx.guild.id)][str(ctx.message.channel.id)][user_name.translate({ord(c): '' for c in clean_id})] = character
    except KeyError:
        characters[str(ctx.guild.id)][str(ctx.message.channel.id)] = {}
        characters[str(ctx.guild.id)][str(ctx.message.channel.id)][user_name.translate({ord(c): '' for c in clean_id})] = character
    await ctx.message.delete()

    with open('characters.json', 'w') as fp:
        json.dump(characters, fp)


@bot.command(name='unregister')
async def unregister(ctx, user_name):
    try:
        del characters[str(ctx.guild.id)][str(ctx.message.channel.id)][user_name.translate({ord(c): '' for c in clean_id})]
    except KeyError:
        pass
    await ctx.message.delete()

    with open('characters.json', 'w') as fp:
        json.dump(characters, fp)


@bot.command(name='activate')
async def activate(ctx, user_name):
    try:
        characters[str(ctx.guild.id)][str(ctx.message.channel.id)][user_name.translate({ord(c): '' for c in clean_id})]['active'] = True
    except KeyError:
        pass
    await ctx.message.delete()


@bot.command(name='deactivate')
async def deactivate(ctx, user_name):
    try:
        characters[str(ctx.guild.id)][str(ctx.message.channel.id)][user_name.translate({ord(c): '' for c in clean_id})]['active'] = False
    except KeyError:
        pass
    await ctx.message.delete()


@bot.command(name='ooc')
async def ooc(ctx, arg1):
    pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.listen()
async def on_message(message):
    if not message.author.bot:
        if not message.content.startswith("!"):
            try:
                character = characters[str(message.guild.id)][str(message.channel.id)]['{}'.format(message.author.id)]
                if character['active']:
                    embed = discord.Embed(description=message.content, color=int("0x{}".format(character['color']), 16))

                    embed.set_thumbnail(url=character['portrait'])
                    embed.set_author(name=character['name']) # icon_url=character['portrait']

                    await message.delete()
                    if len(message.content) > 0:
                        await message.channel.send(embed=embed)

                    for attachment in message.attachments:
                        embed = discord.Embed(color=int("0x{}".format(character['color']), 16))
                        embed.set_image(url=attachment.proxy_url)
                        embed.set_author(name=character['name'])
                        await message.channel.send(embed=embed)

                    await bot.process_commands(message)
            except KeyError:
                pass
        if message.content.startswith("!as"):
            msg = message.content.split(" ")
            npc = " ".join(msg[1].split('_'))
            embed = discord.Embed(description=" ".join(msg[2:]))

            # embed.set_thumbnail(url=character['portrait'])
            embed.set_author(name=npc)  # icon_url=character['portrait']

            await message.delete()
            await message.channel.send(embed=embed)
            await bot.process_commands(message)

bot.run(TOKEN)
