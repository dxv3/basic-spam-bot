# Discord Multi-Spam Bot

A versatile Discord bot for spamming messages using user tokens and webhooks. Features include creating and managing webhooks, sending messages to channels, and spamming with multiple webhooks and user tokens simultaneously. Supports looping for continuous message sending.

## Key Features
- **Webhook Management**: Create, delete, and rename webhooks.
- **Message Sending**: Send messages to specified channels using user tokens and webhooks.
- **Spamming**: Spam messages using multiple webhooks and tokens simultaneously.
- **Looping Support**: Enable continuous message sending with the `-loop` option.
- **Stop Command**: Halt all active tasks with the `stop` command.

## Commands

use `|` to separate commands.

dxv3send [channel_id] [cmds] [-loop]  
dxv3stop  
dxv3webhook [channel_id] [webhook_name] [amount]  
dxv3hookspam [webhook_id] [messages] [-loop]  
dxv3spamall [channel_id] [messages] [-loop]  
dxv3h  

replace BOT_TOKEN on line 8 
put tokens in tokens.txt