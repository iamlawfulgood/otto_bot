# Otto Bot

General purpose moderation bot.

# Features

## Role Management

Otto Bot rolls out roles. :)

Otto bot needs two things for configuration:
1. A guild and message ID to listen for reactions on
2. A mapping from reaction names to role ID

Whenever server members add/remove configured reactions on that message,
Otto will add/remove the corresponding role from their profile.

This can be used to show/hide channels or grant other user-optable functionality.