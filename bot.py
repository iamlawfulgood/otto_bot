import asyncio
import configparser
from typing import List
import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned
import os
import random
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

sizeray_message = re.compile(
    r"<:(?:shrinkray:795068808002928642|sizeray:789563482906689627)>\s*<@\!?840458895670378517>\s*"
)

tiny_responses = [
    "How did someone so small even manage to pick up the gun? I'll fix that...",
    "I barely even saw you down there. I'd rather not see you at all...",
    "A tiny should know better than to try something like that. Time for a lesson why...",
]
switch_responses = [
    "Oh? Let's see how you like it...",
    "Ha! You thought you could shrink _me_? My turn...",
    "I don't need a gun to reduce you to nothing. Have fun down there...",
]
giant_responses = [
    "Oh? Even a giant is intimidated by me? Good. You should be. Enjoy your new size...",
    "You think being bigger makes you stronger? In that case...",
    "You need attention, big guy? Careful what you wish for...",
]
shield_responses = [
    "That shield protects you from the gun, not me.",
    "You thought a flimsy role could stop me from shrinking you?",
    "Omnipotence beats your sizeray shield. Nice try, though.",
]
already_shrunken = [
    "🥱",
    "🙄",
    "😑",
]


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    mentioned_ids = message.raw_mentions
    if len(mentioned_ids) == 0:
        return
    if bot.user.id not in mentioned_ids:
        return
    if not message.content.startswith("<:s"):
        return
    if sizeray_message.match(message.content) is None:
        return

    # Wait a sec to see what role the sizeray assigned
    await asyncio.sleep(2)

    # If Otto didn't shrink, he's fine with it
    if not _otto_shrank():
        return

    await _remove_shrunken_role()
    await _respond(message)


def _otto_shrank() -> bool:
    guild = bot.get_guild(int(config["Guild"]["ID"]))
    otto = guild.get_member(bot.user.id)
    return _is_shrunken(otto)


async def _respond(original_message: discord.Message) -> None:
    if _is_shrunken(original_message.author):
        await original_message.reply(random.choice(already_shrunken))
        return

    await _send_response(original_message)
    await asyncio.gather(
        _shrink(original_message.author), _send_shield_response(original_message)
    )


def _is_shrunken(member: discord.Member) -> bool:
    role_ids = _get_role_ids(member)
    return (
        int(config["Sizes"]["ShrunkSpeckish"]) in role_ids
        or int(config["Sizes"]["ShrunkTiny"]) in role_ids
    )


async def _remove_shrunken_role() -> None:
    guild = bot.get_guild(int(config["Guild"]["ID"]))
    otto = guild.get_member(bot.user.id)
    shrunken_speckish_role = guild.get_role(int(config["Sizes"]["ShrunkSpeckish"]))
    shrunken_tiny_role = guild.get_role(int(config["Sizes"]["ShrunkTiny"]))
    await otto.remove_roles(shrunken_speckish_role, shrunken_tiny_role)


async def _send_response(original_message: discord.Message) -> None:
    author_role_ids = _get_role_ids(original_message.author)

    if int(config["Sizes"]["Tiny"]) in author_role_ids:
        response_message = random.choice(tiny_responses)
    elif int(config["Sizes"]["Giant"]) in author_role_ids:
        response_message = random.choice(giant_responses)
    else:
        response_message = random.choice(switch_responses)

    await original_message.reply(response_message)


async def _shrink(author: discord.Member) -> None:
    guild = bot.get_guild(int(config["Guild"]["ID"]))
    shrunken_role = guild.get_role(int(config["Sizes"]["ShrunkSpeckish"]))
    await author.add_roles(shrunken_role)
    await asyncio.sleep(300)
    await author.remove_roles(shrunken_role)


async def _send_shield_response(original_message: discord.Message) -> None:
    author_role_ids = _get_role_ids(original_message.author)
    if int(config["Sizes"]["Shield"]) not in author_role_ids:
        return
    await asyncio.sleep(1)
    await original_message.channel.send(random.choice(shield_responses))


def _get_role_ids(author: discord.Member) -> List[int]:
    return list(map(lambda role: role.id, author.roles))


@bot.event
async def on_raw_reaction_add(payload):
    await _handle_reaction_action(payload, True)


@bot.event
async def on_raw_reaction_remove(payload):
    await _handle_reaction_action(payload, False)


async def _handle_reaction_action(payload, should_add) -> None:
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


def _valid_reaction_payload(payload) -> bool:
    # Don't listen to private messages
    if not payload.guild_id:
        return False

    # Don't listen to other channels
    if int(payload.channel_id) != int(config["Guild"]["Channel"]):
        return False

    # Only listen to the designated role message
    if int(payload.message_id) != int(config["Guild"]["Message"]):
        return False

    emoji_name = payload.emoji.name
    if emoji_name not in config["Roles"]:
        return False

    return True


bot.run(config["Discord"]["Token"])
