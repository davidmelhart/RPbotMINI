import os
import json
import discord
import random
import typing
import colorsys
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
    print("Ready!\n")
    for guild in bot.guilds:
        try:
            characters[str(guild.id)]
        except KeyError:
            characters[str(guild.id)] = {}
    print('Character Database:')
    print(json.dumps(characters, indent=2))
    print()


@bot.command(name='register')
async def register(ctx, character_name, portrait: typing.Optional[str], color: typing.Optional[str]):
    if not color:
        h, s, l = random.random(), random.uniform(0.5, 0.7), random.uniform(0.5, 0.7)
        r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
        color = "{0:02x}{1:02x}{2:02x}".format(r, g, b)
    elif color.startswith("#"):
        color = color[1:]

    if not portrait:
        portrait = 'https://cdn.discordapp.com/embed/avatars/1.png'
    elif not portrait.startswith('http'):
        portrait = 'https://cdn.discordapp.com/embed/avatars/1.png'

    guild = str(ctx.guild.id)
    channel = str(ctx.message.channel.id)
    user = '{}'.format(ctx.message.author.id)

    character = {
        "name": character_name,
        "portrait": portrait,
        "color": color,
    }

    if channel not in characters[guild]:
        characters[guild][channel] = {}

    if user not in characters[guild][channel]:
        characters[guild][channel][user] = {}
        characters[guild][channel][user]['characters'] = {}

    characters[guild][channel][user]['active'] = True
    characters[guild][channel][user]["characters"][character_name] = character
    characters[guild][channel][user]['as'] = character_name
    await ctx.message.delete()

    with open('characters.json', 'w') as fp:
        json.dump(characters, fp)
    print('Character Database Updated!')
    print(json.dumps(characters, indent=2))
    print()


@bot.command(name='list')
async def character_list(ctx, user_name: typing.Optional[discord.Member]):
    guild = str(ctx.guild.id)
    channel = str(ctx.message.channel.id)
    if not user_name:
        user = '{}'.format(ctx.message.author.id)
    else:
        user = '{}'.format(user_name.id)

    try:
        c_list = characters[guild][channel][user]['characters']
        if len(c_list) > 0:
            if not user_name:
                await ctx.message.author.send("Your characters registered on {}:"
                                              .format(ctx.message.channel.name), delete_after=60)
            else:
                await ctx.message.author.send("Characters of {} registered on {}:"
                                              .format(user_name.display_name, ctx.message.channel.name), delete_after=60)
            for c in c_list:
                character = c_list[c]
                embed = discord.Embed(color=int("0x{}".format(character['color']), 16))
                embed.set_thumbnail(url=character['portrait'])
                embed.set_author(name=character['name'])  # icon_url=character['portrait']

                await ctx.message.author.send(embed=embed, delete_after=60)
        else:
            if not user_name:
                await ctx.message.author.send("You have no characters registered on {}."
                                              .format(ctx.message.channel.name), delete_after=60)
            else:
                await ctx.message.author.send("{} has no characters registered on {}."
                                              .format(user_name.display_name, ctx.message.channel.name), delete_after=60)
    except KeyError:
        if not user_name:
            await ctx.message.author.send("You have no characters registered on {}."
                                          .format(ctx.message.channel.name), delete_after=60)
        else:
            await ctx.message.author.send("{} has no characters registered on {}."
                                          .format(user_name.display_name, ctx.message.channel.name), delete_after=60)
    await ctx.message.delete()


@bot.command(name='clear')
async def clear_channel(ctx):
    guild = str(ctx.guild.id)
    channel = str(ctx.message.channel.id)
    user = '{}'.format(ctx.message.author.id)
    try:
        del characters[guild][channel][user]
    except KeyError:
        await ctx.message.author.send("You have no characters registered on {}."
                                      .format(ctx.message.channel.name), delete_after=60)
    await ctx.message.delete()

    with open('characters.json', 'w') as fp:
        json.dump(characters, fp)
    print('Character Database Updated!')
    print(json.dumps(characters, indent=2))
    print()


@bot.command(name='delete')
async def delete_user(ctx):
    guild = str(ctx.guild.id)
    user = '{}'.format(ctx.message.author.id)

    for channel in characters[guild].keys():
        try:
            del characters[guild][channel][user]
        except KeyError:
            pass
    await ctx.message.delete()

    with open('characters.json', 'w') as fp:
        json.dump(characters, fp)
    print('Character Database Updated!')
    print(json.dumps(characters, indent=2))
    print()


@bot.command(name='unregister')
async def unregister(ctx, character_name):
    guild = str(ctx.guild.id)
    channel = str(ctx.message.channel.id)
    user = '{}'.format(ctx.message.author.id)

    try:
        del characters[guild][channel][user]["characters"][character_name]
        character_list = characters[guild][channel][user]["characters"]
        if characters[guild][channel][user]["as"] == character_name and len(character_list) > 0:
            random_character = character_list[random.choice(list(character_list.keys()))]
            characters[guild][channel][user]["as"] = random_character['name']

            embed = discord.Embed(description="{} unregistered, now speaking as {}.\n"
                                              "To get a list of available characters in the channel call:\n"
                                              "`!list @username`"
                                  .format(character_name, random_character['name']),
                                  color=int("0x{}".format(random_character['color']), 16))
            embed.set_thumbnail(url=random_character['portrait'])
            embed.set_author(name=random_character['name'])  # icon_url=character['portrait']

            await ctx.message.author.send(embed=embed, delete_after=60)
    except KeyError:
        await ctx.message.author.send("This character is not registered on {}.\n"
                                      "To get a list of available characters in the channel call: `!list`"
                                      .format(ctx.message.channel.name), delete_after=60)
    await ctx.message.delete()

    with open('characters.json', 'w') as fp:
        json.dump(characters, fp)
    print('Character Database Updated!')
    print(json.dumps(characters, indent=2))
    print()


@bot.command(name='as')
async def speak_as(ctx, character_name):
    guild = str(ctx.guild.id)
    channel = str(ctx.message.channel.id)
    user = '{}'.format(ctx.message.author.id)
    try:
        characters[guild][channel][user]['as'] = characters[guild][channel][user]['characters'][character_name]['name']
    except KeyError:
        await ctx.message.author.send("This character is not registered on {}.\n"
                                      "To get a list of available characters in the channel call: `!list`"
                                      .format(ctx.message.channel.name), delete_after=60)
    await ctx.message.delete()

    with open('characters.json', 'w') as fp:
        json.dump(characters, fp)


@bot.command(name='activate')
async def activate(ctx):
    guild = str(ctx.guild.id)
    channel = str(ctx.message.channel.id)
    user = '{}'.format(ctx.message.author.id)
    try:
        characters[guild][channel][user]['active'] = True
    except KeyError:
        await ctx.message.author.send("This user has no characters registered on {}."
                                      .format(ctx.message.channel.name), delete_after=60)
    await ctx.message.delete()


@bot.command(name='deactivate')
async def deactivate(ctx):
    guild = str(ctx.guild.id)
    channel = str(ctx.message.channel.id)
    user = '{}'.format(ctx.message.author.id)
    try:
        characters[guild][channel][user]['active'] = False
    except KeyError:
        await ctx.message.author.send("This user has no characters registered on {}."
                                      .format(ctx.message.channel.name), delete_after=60)
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
            guild = str(message.guild.id)
            channel = str(message.channel.id)
            user = '{}'.format(message.author.id)

            try:
                user_data = characters[guild][channel][user]
                speak_as = user_data['as']
                character = user_data['characters'][speak_as]

                if user_data['active']:
                    embed = discord.Embed(description=message.content, color=int("0x{}".format(character['color']), 16))

                    embed.set_thumbnail(url=character['portrait'])
                    embed.set_author(name=character['name'])  # icon_url=character['portrait']

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

        if message.content.startswith("!npc"):
            msg = message.content.split(" ")
            npc = " ".join(msg[1].split('_'))
            embed = discord.Embed(description=" ".join(msg[2:]))

            # embed.set_thumbnail(url=character['portrait'])
            embed.set_author(name=npc)  # icon_url=character['portrait']

            await message.delete()
            await message.channel.send(embed=embed)
            await bot.process_commands(message)


@bot.command(name='purge')
async def purge(ctx):
    if ctx.guild is None:
        async for message in ctx.message.channel.history(limit=100):
            if message.author.id == bot.user.id:
                await message.delete()

bot.run(TOKEN)
