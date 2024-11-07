import os
import asyncio
import aiohttp
import time
from colorama import Fore, Style, init

init(autoreset=True)

AUTH_HEADER = {"Authorization": "put your token here"}

async def save_file(session, filename, url):
    start_time = time.time()
    async with session.get(url) as response:
        if response.status == 200:
            content = await response.read()
            with open(filename, "wb") as file:
                file.write(content)
            elapsed_time = time.time() - start_time
            print(Fore.GREEN + f"[+] - Saved: {filename} (Time: {elapsed_time:.2f}s)")
        else:
            print(Fore.RED + f"[-] - Failed to save {filename} (Status: {response.status})")

async def scrap_messages(offset, guild_id):
    guild_dir = f"./loot/{guild_id}"
    os.makedirs(guild_dir, exist_ok=True)

    url = (
        f"https://discord.com/api/v9/guilds/{guild_id}/messages/search"
        f"?has=image&has=video&include_nsfw=true"
        + (f"&offset={offset}" if offset else "")
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=AUTH_HEADER) as response:
            messages = await response.json()
            tasks = []

            for message in messages.get("messages", []):
                username = message[0]['author']['username']
                user_dir = os.path.join(guild_dir, username)
                os.makedirs(user_dir, exist_ok=True)

                for attachment in message[0]["attachments"]:
                    file_path = os.path.join(user_dir, f"{attachment['id']}_{attachment['filename']}")
                    tasks.append(save_file(session, file_path, attachment['url']))

            await asyncio.gather(*tasks)

async def fetch_guilds():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discordapp.com/api/users/@me/guilds", headers=AUTH_HEADER) as response:
            guilds = await response.json()
            return [(index, guild["id"], guild["name"]) for index, guild in enumerate(guilds)]

async def main():
    guilds = await fetch_guilds()
    for index, guild_id, guild_name in guilds:
        status = " - SCRAPPED" if guild_id in os.listdir("loot") else ""
        print(f"{index} - {guild_name}{status}")

    server_index = int(input("Select one: "))
    target_guild_id = guilds[server_index][1]

    print(Fore.CYAN + f"[ + ] - Scraping {guilds[server_index][2]}")
    offset = 0

    while True:
        print(Fore.YELLOW + f"Offset: {offset}")
        await scrap_messages(offset, target_guild_id)
        offset += 25

if __name__ == "__main__":
    asyncio.run(main())

