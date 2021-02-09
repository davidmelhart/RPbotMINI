# RPbotMINI
A minimalistic Discord bot that let's you speak in character without any prefixes. The bot catches your messages, deletes them, and post their content as your active "speak as" character in the given channel.

The characters are saved in a JSON database. The database saves characters for each guild>channel>user, so you have to have characters with unique names on the same **channel** but not necessarily on the same guild.

You can register a character with the `!register "character name" https://portrait.png #hexcolor` command. **Name** and **portrait** are mandatory fields, **hexcolor** is optional. If you don't put in a colour, the bot will assign one randomly. 

The characters are indexed by their name. If you made a mistake or want to update the **portrait or colour** of your character, you can just run the command again and it will overwrite the existing one.

If you want to delete the character (to for example give it another name) you can do so with the `!unregister "character name"` command.

If you want to clear all your characters on the current channel you can use the `!clear` command. If you want to delete all your characters from the whole **guild**, you can use the `!delete` command. 

**PLEASE BE AWARE THAT DELETING CHARACTERS IS FINAL! RUNNING `!unregister`, `!clear`, AND `!delete` ALSO REMOVES THE CHARACTERS FROM THE DATABASE!**

You can register multiple characters on one channel (useful for recurring NPCs). You can switch between characters with the `!as "character name"` command.

You can get a list of your characters on the channel with `!list`. You can also request a list of another person's characters with `!list @user`.

You can talk **out of character** with the `!ooc` or just the `!` prefix (for now). Alternatively, you can turn off the in-character speech with `!deactivate`. You can turn it back on with the `!activate` command.

Finally you can speak as a random NPC with this syntax: `!npc NPC_name message` (The `_` characters will be converted to spaces in the NPC's name.)

You can use uploads as well to create handouts. Comments and the file will be sent as separate messages. The file itself won't have a portrait attached but will still have the name and colour of the character.

The bot cleans up after itself, if a command is successful, you should see it disappear. There is some minimal error handling through DMs. DM messages are kept for **one minute** after which they are automatically deleted. If for some reason the messages stick, you can use the `!purge` command in the bot DMs to clear the last 100 messages sent by the bot.