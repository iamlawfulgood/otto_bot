import asyncio
import configparser
import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned
import os
import re

description = "Omnipotent moderator of Kwakwa's Taco Truck"
intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.guild_messages = True
intents.guild_reactions = True

bot = commands.Bot(
    command_prefix=when_mentioned, description=description, intents=intents
)

config = configparser.ConfigParser()
config.read(os.environ.get("CONFIG_PATH"))

otto_user_id = 840458895670378517
shrink_message = re.compile(
    r"<:shrinkray:795068808002928642>\s*<@\!840458895670378517>\s*"
)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    mentioned_ids = message.raw_mentions
    if len(mentioned_ids) == 0:
        return
    if otto_user_id not in mentioned_ids:
        return
    if not message.content.startswith("<:shrinkray"):
        return

    if shrink_message.match(message.content) is not None:
        await message.reply("😏")
        await asyncio.sleep(1)
        await message.channel.send(
            f"<:shrinkray:795068808002928642> {message.author.mention}"
        )


@bot.event
async def on_raw_reaction_add(payload):
    await _handle_reaction_action(payload, True)


@bot.event
async def on_raw_reaction_remove(payload):
    await _handle_reaction_action(payload, False)


async def _handle_reaction_action(payload, should_add):
    if not _valid_reaction_payload(payload):
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    emoji_name = payload.emoji.name
    role_id = int(config["Roles"][emoji_name])
    role = guild.get_role(role_id)
    if role is None:
        return

    member = guild.get_member(payload.user_id)
    if should_add:
        if role not in member.roles:
            await member.add_roles(role)
    else:
        if role in member.roles:
            await member.remove_roles(role)


def _valid_reaction_payload(payload):
    # Don't listen to private messages
    if not payload.guild_id:
        return False

    # Don't listen to channels other than #welcome
    if int(payload.channel_id) != int(config["Guild"]["Channel"]):
        return False

    # Only listen to the designated role message in #welcome
    if int(payload.message_id) != int(config["Guild"]["Message"]):
        return False

    emoji_name = payload.emoji.name
    if emoji_name not in config["Roles"]:
        return False

    return True


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.channel.send(str(error), delete_after=5)
    await ctx.message.delete(delay=5)


bot.run(config["Discord"]["Token"])
