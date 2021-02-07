# RPbotMINI
A minimalistic Discord bot that let's you speak in character without any prefixes.
You can register your characters per **channel** like this:
`!register @username "character name" https://portrait.png #hexcolor`

If you made a mistake, or want to update your character, you can just run the command again at it will overwrite what you have. You can do this separately for every channel!

Characters are saved in the `characters.json` file which is created first time you register a character so you won't have to set them up every time but keep a copy just in case.

Your messages will automatically be deleted and the bot will push the same message **as** your character. To talk out of character you can use the `!ooc` or just the `!` prefix (for now).

If you want to delete the character you can do so like this (this will only clear your character in the current channel) this will also delete the character from storage:
`!unregister @username`

If you don't want to delete the character just want to turn off the in-character speech, you can deactivate your character like this:
`!deactivate @username`

To activate it again just type:
`!activate @username`


Finally, if you want to speak as an NPC you can use the following syntax:
`!as NPC_name message`
(The `_` will be converted to spaces in the NPC's name.)

Handouts work as well, with normal file uploads! The comment and the file will be separated. The file itself won't have a portrait attached but will still have the name and colour of the character.

The bot cleans up after itself, if a command is successful, you should see it disappear.

## TODO:
More GM tools: support for recurring NPCs with portraits
- refactor the code so the character storage is organised based on users
- let users register multiple characters per channel
- change `!as` to switch between characters
- move `!as` funcionality to `!npc`

- Handle errors with partially filled out character sheets
