import discord
from discord.commands import Option
from discord import interactions

import os
import json
import random
import typing
import colorsys
from dotenv import load_dotenv
from enum import Enum


clean_id = ['<', '@', '!', '>']

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = discord.Bot()

_character_db = {}
if os.path.exists('characters.json'):
    with open('characters.json', 'r') as fp:
        _character_db = json.load(fp)


@bot.event
async def on_ready():
    print("Ready!\n")
    for guild in bot.guilds:
        try:
            _character_db[str(guild.id)]
        except KeyError:
            _character_db[str(guild.id)] = {}
    print('Character Database:')
    print(json.dumps(_character_db, indent=2))
    print()


class RegisterModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Name"))
        self.add_item(discord.ui.InputText(label="Color", required=False))
        self.add_item(discord.ui.InputText(label="Portrait", required=False))

    async def callback(self, interaction: discord.Interaction):
        name = self.children[0].value
        color = self.children[1].value
        portrait = self.children[2].value
        await register_character(interaction, name, color, portrait)


class UpdateModal(discord.ui.Modal):
    def __init__(self, guild, channel, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.guild = guild
        self.channel = channel
        self.user = user

        current_character = _character_db[guild][channel][user]["characters"][_character_db[guild][channel][user]['as']]

        self.add_item(discord.ui.InputText(label="Name", value=current_character['name']))
        self.add_item(discord.ui.InputText(label="New Name", required=False))
        self.add_item(discord.ui.InputText(label="Color", value=current_character['color'], required=False))
        self.add_item(discord.ui.InputText(label="Portrait", value=current_character['portrait'], required=False))

    async def callback(self, interaction: discord.Interaction):
        name = self.children[0].value
        new_name = self.children[1].value
        color = self.children[2].value
        portrait = self.children[3].value
        await update_character(interaction, name, color, portrait, new_name)


class SelectButton(discord.ui.View):
    def __init__(self, character_name):
        super().__init__(timeout=None)
        self.character_name = character_name

    @discord.ui.button(label="Select Character", custom_id="select", style=discord.ButtonStyle.secondary)
    async def button_callback(self, button, interaction):
        await switch_character(interaction, self.character_name)


@bot.slash_command(name='register', description='Register a new character')
async def register(ctx: discord.ApplicationContext):
    modal = RegisterModal(title="Register New Character")
    await ctx.send_modal(modal)


@bot.slash_command(name='update', description='Register a new character')
async def update(ctx: discord.ApplicationContext):
    guild = str(ctx.guild.id)
    channel = str(ctx.channel.id)
    user = str(ctx.user.id)
    modal = UpdateModal(title="Update Character", guild=guild, channel=channel, user=user)
    await ctx.send_modal(modal)


@bot.slash_command(name='list', description='List your characters registered on the channel')
async def list_characters(ctx: discord.ApplicationContext):
    guild = str(ctx.guild.id)
    channel = str(ctx.channel.id)
    user = str(ctx.user.id)
    character_list = _character_db[guild][channel][user]["characters"]

    for character_name in character_list:
        character = character_list[character_name]

        select = SelectButton(character_name)

        embed = discord.Embed(description="", color=int(f"0x{character['color']}", 16))
        embed.set_thumbnail(url=character['portrait'])
        embed.set_author(name=f"{character['name']}"
                              f"{' is active.' if character_name == _character_db[guild][channel][user]['as'] else ''}")
        await ctx.respond(embed=embed, view=select, ephemeral=True)


@bot.slash_command(name='switch', description='Switch to character!')
async def switch(ctx: discord.ApplicationContext, to_character: Option(str, "Switch to character!", required=False, default='')):
    await switch_character(ctx, to_character)


@bot.slash_command(name='s', description='Say something in-character!')
async def say(ctx: discord.ApplicationContext, message: Option(str, "Say something in-character!", required=False, default='')):
    await send_message(ctx, message=message, message_type="says:", action="", wrapper="", bold=False, italic=False)


@bot.slash_command(name='w', description='Whisper something in-character!')
async def whisper(ctx: discord.ApplicationContext, message: Option(str, "Whisper something in-character!", required=False, default='')):
    await send_message(ctx, message=message, message_type="whispers:", action="", wrapper="~", bold=False, italic=True)


@bot.slash_command(name='a', description='Act in-character!')
async def action(ctx: discord.ApplicationContext,
                 action: Option(str, "Act in-character!", required=False, default=''),
                 message: Option(str, "Say something in-character!", required=False, default='')):
    await send_message(ctx, message=message, message_type="", action=action, wrapper="", bold=False, italic=False)


@bot.slash_command(name='as', description='Act as an NPC!')
async def as_npc(ctx: discord.ApplicationContext,
                 name: Option(str, "NPC name", required=True, default=''),
                 message: Option(str, "Say something as NPC!", required=False, default=''),
                 action: Option(str, "Act as NPC!", required=False, default='')):
    guild = str(ctx.guild.id)
    channel = str(ctx.channel.id)
    user = str(ctx.author.id)

    setup_user(guild, channel, user)

    if name not in _character_db[guild][channel][user]["npcs"]:
        character = {
            "name": name,
            "color": check_color(''),
        }
        _character_db[guild][channel][user]["npcs"][name] = character
        with open('characters.json', 'w') as fp:
            json.dump(_character_db, fp)
    else:
        character = _character_db[guild][channel][user]["npcs"][name]

    await send_message(ctx, message=message, message_type="", action=action, wrapper="", bold=False, italic=False,
                       as_character=character)


@bot.slash_command(name='narrate', description='Add narration!')
async def narrate(ctx: discord.ApplicationContext, message: Option(str, "Add narration!", required=True, default='')):
    message = message.capitalize()
    message = f"{message}." if message[-1] not in [".", "!", "?", ':', '-'] else message

    embed = discord.Embed(description="", color=int(f"0x{'2f3136'}", 16))
    embed.set_author(name=f"{message}")
    await ctx.defer()
    await ctx.delete()
    await ctx.channel.send(embed=embed)


async def send_message(ctx, message="", message_type="", action="", wrapper="", bold=False, italic=False,
                       as_character=None):
    try:
        guild = str(ctx.guild.id)
        channel = str(ctx.channel.id)
        user = _character_db[guild][channel][str(ctx.author.id)]

        if as_character is None:
            character = user["characters"][user['as']]
        else:
            character = as_character

        if len(message) > 0:
            message = message.capitalize()
            message = f"{message}." if message[-1] not in [".", "!", "?", ':', '-'] else message
        if len(action) > 0:
            action = f"{action}." if action[-1] not in [".", "!", "?", ':', '-'] else action

        if action == "" and message_type == "":
            message_type = "says:"

        if italic:
            message = f"*{message}*"
        if bold:
            message = f"**{message}**"

        embed = discord.Embed(description=f"{wrapper}{message}{wrapper}", color=int(f"0x{character['color']}", 16))
        if 'portrait' in character:
            embed.set_thumbnail(url=character['portrait'])
        embed.set_author(name=f"{character['name']} {message_type}{action}")
        await ctx.defer()
        await ctx.delete()
        await ctx.channel.send(embed=embed)
    except KeyError:
        await ctx.respond("Cannot find character! \n"
                          "Please use `/list` to view your current characters. \n"
                          "If you have no characters in the current channel, "
                          "you can create one with the `/register` command", ephemeral=True)


async def register_character(interaction, name, color, portrait):
    guild = str(interaction.guild.id)
    channel = str(interaction.channel.id)
    user = str(interaction.user.id)

    setup_user(guild, channel, user)

    color = check_color(color)

    if portrait == "" or not portrait.startswith('http'):
        portrait = 'https://cdn.discordapp.com/embed/avatars/1.png'

    character = {
        "name": name,
        "portrait": portrait,
        "color": color,
    }

    if name not in _character_db[guild][channel][user]["characters"]:
        _character_db[guild][channel][user]["characters"][name] = character
        _character_db[guild][channel][user]['as'] = name

        embed = discord.Embed(description="", color=int(f"0x{color}", 16))
        embed.set_thumbnail(url=portrait)
        embed.set_author(name=f"{name} enters the scene.")

        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        as_character = _character_db[guild][channel][str(interaction.user.id)]
        character = as_character["characters"][as_character['as']]
        embed = discord.Embed(description="Use `/update` to update the character.",
                              color=int(f"0x{character['color']}", 16))
        embed.set_thumbnail(url=character['portrait'])
        embed.set_author(name=f"{character['name']} already exists in this channel.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    with open('characters.json', 'w') as fp:
        json.dump(_character_db, fp)


async def update_character(interaction, name, color, portrait, new_name):
    guild = str(interaction.guild.id)
    channel = str(interaction.channel.id)
    user = str(interaction.user.id)

    setup_user(guild, channel, user)

    if name in _character_db[guild][channel][user]["characters"]:
        if portrait != "" and portrait.startswith('http'):
            _character_db[guild][channel][user]["characters"][name]['portrait'] = portrait
        if color != "":
            _character_db[guild][channel][user]["characters"][name]['color'] = check_color(color)
        if new_name != "":
            character = _character_db[guild][channel][user]["characters"][name]
            _character_db[guild][channel][user]["characters"][new_name] = character
            _character_db[guild][channel][user]["characters"][new_name]["name"] = new_name
            _character_db[guild][channel][user]['as'] = new_name

            del _character_db[guild][channel][user]["characters"][name]
            name = new_name

        character = _character_db[guild][channel][user]["characters"][name]

        embed = discord.Embed(description="", color=int(f"0x{character['color']}", 16))
        embed.set_thumbnail(url=character['portrait'])
        embed.set_author(name=f"{character['name']} has been updated.")

        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("Cannot find character! \n"
                                                "Please use `/list` to view your current characters. \n"
                                                "If you have no characters in the current channel, "
                                                "you can create one with the `/register` command", ephemeral=True)
    with open('characters.json', 'w') as fp:
        json.dump(_character_db, fp)


async def switch_character(interaction, to_character):
    guild = str(interaction.guild.id)
    channel = str(interaction.channel.id)
    user = str(interaction.user.id)
    _character_db[guild][channel][user]['as'] = to_character

    as_character = _character_db[guild][channel][str(interaction.user.id)]
    character = as_character["characters"][as_character['as']]
    embed = discord.Embed(description="", color=int(f"0x{character['color']}", 16))
    embed.set_thumbnail(url=character['portrait'])
    embed.set_author(name=f"{character['name']} is now active.")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    with open('characters.json', 'w') as fp:
        json.dump(_character_db, fp)


colors = {
    "mint": "00C09A",
    "teal": "008369",
    "green": "00D166",
    "dark green": "008E44",
    "blue": "0099E1",
    "dark blue": "006798",
    "purple": "A652BB",
    "dark purple": "7A2F8F",
    "pink": "FD0061",
    "dark pink": "BC0057",
    "yellow": "F8C300",
    "orange": "E67E22",
    "brown": "a15313",
    "red": "F93A2F",
    "dark red": "A62019",
    "light grey": "91A6A6",
    "grey": "597E8D",
    "dark grey": "4E6F7B",
}


def check_color(color):
    if color in colors:
        color = colors[color]
    else:
        if color.startswith("#"):
            color = color[1:]
        if len(color) != 6 or color.lower() == "2f3136":
            h, s, l = random.random(), random.uniform(0.5, 0.7), random.uniform(0.5, 0.7)
            r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
            color = "{0:02x}{1:02x}{2:02x}".format(r, g, b)
    return color


def setup_user(guild, channel, user):
    if channel not in _character_db[guild]:
        _character_db[guild][channel] = {}

    if user not in _character_db[guild][channel]:
        _character_db[guild][channel][user] = {}
        _character_db[guild][channel][user]['characters'] = {}
        _character_db[guild][channel][user]['npcs'] = {}


bot.run(TOKEN)
