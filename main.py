import discord
from discord.ext import commands
import asyncio
import aiohttp
import requests
import time

BOT_TOKEN = ""

def read_tokens(file_path):
    with open(file_path, 'r') as file:
        tokens = [line.strip() for line in file.readlines() if line.strip()]
    return tokens

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='dxv3', intents=intents)

tokens_file = 'tokens.txt'
tokens = read_tokens(tokens_file)

looping = False
loop_tasks = []

class DiscordWebhookManager:
    def __init__(self):
        self.webhooks = []

    def create_webhook(self, token, channel_id, webhook_name):
        url = f"https://discord.com/api/v9/channels/{channel_id}/webhooks"
        headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "name": webhook_name
        }
        
        try:
            response = requests.post(url, headers=headers, json=json_data)
            response.raise_for_status()
            webhook_data = response.json()
            webhook = {
                "id": webhook_data["id"],
                "token": webhook_data["token"],
                "url": f"https://discord.com/api/webhooks/{webhook_data['id']}/{webhook_data['token']}",
                "name": webhook_name
            }
            self.webhooks.append(webhook)
            print(f"[+] webhook '{webhook_name}' created successfully.")
        except requests.exceptions.HTTPError as errh:
            print(f"[!] failed to create webhook: {errh}")
        except requests.exceptions.RequestException as err:
            print(f"[!] request exception: {err}")

    def send_message(self, webhook_url, message):
        try:
            response = requests.post(webhook_url, json={"content": message})
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(f"[!] HTTP Error: {errh}")
        except requests.exceptions.RequestException as err:
            print(f"[!] Request Exception: {err}")

    def delete_webhook(self, webhook_url):
        try:
            response = requests.delete(webhook_url)
            response.raise_for_status()
            print("[+] webhook deleted successfully")
        except requests.exceptions.HTTPError as errh:
            print(f"[!] HTTP error: {errh}")
        except requests.exceptions.RequestException as err:
            print(f"[!] request exception: {err}")

    def rename_webhook(self, webhook_url, new_name):
        url = f"{webhook_url}"
        headers = {
            "Content-Type": "application/json"
        }
        json_data = {
            "name": new_name
        }
        
        try:
            response = requests.patch(url, headers=headers, json=json_data)
            response.raise_for_status()
            print(f"[+] webhook renamed to '{new_name}' successfully.")
        except requests.exceptions.HTTPError as errh:
            print(f"[!] HTTP error: {errh}")
        except requests.exceptions.RequestException as err:
            print(f"[!] request exception: {errh}")

    def spam_webhooks(self, webhook_ids, messages, loop=False):
        if not self.webhooks:
            print("[!] no webhooks available! make a webhook first lmao")
            return
        
        try:
            print("[!] spam has started. ctrl+c or dxv3stop in discord to stop")
            while True:
                for webhook_id in webhook_ids:
                    webhook = next((wh for wh in self.webhooks if wh["id"] == webhook_id), None)
                    if webhook:
                        response = requests.post(webhook["url"], json={"content": messages})
                        response.raise_for_status()
                        print(f"[+] sent message to '{webhook['name']}'")
                        if not loop:
                            break
                    else:
                        print(f"[!] webhook with ID {webhook_id} not found.")
                if not loop:
                    break
                time.sleep(0.5)  # <---- DELAY BETWEEN MSGS
        except KeyboardInterrupt:
            print("\n[!] spam stopped.")
        except requests.exceptions.HTTPError as errh:
            print(f"[!] HTTP error: {errh}")
        except requests.exceptions.RequestException as err:
            print(f"[!] request exception: {errh}")

webhook_manager = DiscordWebhookManager()

@bot.command(name='send')
async def dxv3send(ctx, channel_id: int, *, cmd_and_loop: str):
    global looping, loop_tasks

    parts = cmd_and_loop.rsplit(' -loop', 1)
    cmds = parts[0].strip()
    loop_flag = len(parts) > 1

    command_list = cmds.split('|')
    channel = bot.get_channel(channel_id)

    if channel is None:
        await ctx.send(f"Channel ID {channel_id} not found.")
        return

    async def send_with_token(token, cmd):
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": token.strip(),
                "Content-Type": "application/json"
            }
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
            json_data = {"content": f"{cmd.strip()}"}
            async with session.post(url, headers=headers, json=json_data) as response:
                if response.status != 200:
                    print(f"failed to send message using user token: {response.status} {await response.text()}")

    async def send_messages():
        tasks = []
        for cmd in command_list:
            tasks.append(channel.send(f"{cmd.strip()}"))
            for token in tokens:
                tasks.append(send_with_token(token, cmd))
        await asyncio.gather(*tasks)

    async def loop_messages():
        while looping:
            await send_messages()
            await asyncio.sleep(1)

    if loop_flag:
        if looping:
            return
        looping = True
        task = asyncio.create_task(loop_messages())
        loop_tasks.append(task)
    else:
        if looping:
            looping = False
            for task in loop_tasks:
                task.cancel()
            loop_tasks = []
        await send_messages()

@bot.command(name='stop')
async def dxv3stop(ctx):
    global looping, loop_tasks

    if looping:
        looping = False
        for task in loop_tasks:
            task.cancel()
        loop_tasks = []



@bot.command(name='webhook')
async def dxv3webhook(ctx, channel_id: int, webhook_name: str, amount: int):
    global webhook_manager

    try:
        for _ in range(amount):
            webhook_manager.create_webhook(bot.http.token, channel_id, webhook_name)
    except ValueError:
        await ctx.send("invalid channel ID or amount")

@bot.command(name='hookspam')
async def dxv3hookspam(ctx, webhook_id: int, *, messages_and_loop: str):
    global looping, loop_tasks

    parts = messages_and_loop.rsplit(' -loop', 1)
    messages = parts[0].strip()
    loop_flag = len(parts) > 1

    message_list = messages.split('|')

    if loop_flag:
        if looping:
            return
        looping = True
        webhook_ids = [webhook_id]
        task = asyncio.create_task(webhook_manager.spam_webhooks(webhook_ids, messages, loop=True))
        loop_tasks.append(task)
    else:
        webhook_ids = [webhook_id]
        await webhook_manager.spam_webhooks(webhook_ids, messages, loop=False)

@bot.command(name='spamall')
async def dxv3spamall(ctx, channel_id: int, *, cmds_and_loop: str):
    global looping

    parts = cmds_and_loop.rsplit(' -loop', 1)
    cmds = parts[0].strip()
    loop_flag = len(parts) > 1

    channel = bot.get_channel(channel_id)

    if channel is None:
        await ctx.send(f"Channel ID {channel_id} not found.")
        return

    async def send_with_token(token, cmd):
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": token.strip(),
                "Content-Type": "application/json"
            }
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
            json_data = {"content": f"{cmd.strip()}"}
            async with session.post(url, headers=headers, json=json_data) as response:
                if response.status != 200:
                    await ctx.send(f"failed to send message using user token: {response.status} {await response.text()}")

    async def send_with_webhook(webhook_url, cmd):
        try:
            webhook_manager.send_message(webhook_url, cmd)
        except requests.exceptions.HTTPError as errh:
            print(f"[!] HTTP error: {errh}")
        except requests.exceptions.RequestException as err:
            print(f"[!] request exception: {err}")

    async def send_messages():
        tasks = []
        for cmd in cmds.split('|'):
            for token in tokens:
                tasks.append(send_with_token(token, cmd.strip()))
            for webhook in webhook_manager.webhooks:
                tasks.append(send_with_webhook(webhook['url'], cmd.strip()))
            tasks.append(channel.send(cmd.strip()))
        await asyncio.gather(*tasks)

    async def loop_messages():
        while looping:
            await send_messages()
            await asyncio.sleep(1)  # adjust delay as needed

    if loop_flag:
        if looping:
            return
        looping = True
        task = asyncio.create_task(loop_messages())
    else:
        await send_messages()


@bot.command(name='h')
async def dxv3h(ctx):
    embed = discord.Embed(
        title="dxv3 cmd help",
        description="here are the available commands and their usage:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="send [channel_id] [cmds]  [-loop]",
        value="send msgs to a channel. Use '|' to separate commands. e.g.: `send 1234567 hello | how are you`"
    )
    embed.add_field(
        name="stop",
        value="stops current task"
    )
    embed.add_field(
        name="webhook [channel_id] [webhook_name] [amount]",
        value="e.g. `webhook 1234567 mywebhook 5`"
    )
    embed.add_field(
        name="hookspam [webhook_id] [messages] [-loop]",
        value="spam w specific webhook id. use '|' to separate messages. e.g.: `hookspam 1234567 hello | how are you -loop`"
    )
    embed.add_field(
        name="spamall [channel_id] [messages] [-loop]",
        value="spam msgs using all created webhooks. use '|' to separate msgs. e.g.: `spamall 1234567 hello | how are you -loop`"
    )

    await ctx.send(embed=embed)

bot.run('BOT_TOKEN')
