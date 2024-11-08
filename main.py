import os
import asyncio
import aiohttp
import time
import json
import dotenv
from colorama import Fore, init

init(autoreset=True)

AUTH_HEADER = {"Authorization": dotenv.get_key(".env", "TOKEN")}
offset = 0


with open("settings.json", "r") as file:
    config = json.load(file)

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

async def scrap_messages(guild_id, guild_name):
    global offset
    include_config = config["include"]
    video = include_config["video"]
    image = include_config["image"]
    
    save_guild_by = config["save_guild_by"]
    save_user_by = config["save_user_by"]
    
    nsfw = include_config["nsfw"]
    
    url = f"https://discord.com/api/v9/guilds/{guild_id}/messages/search?"

    if video:
        url += "has=video&"
    if image:
        url += "has=image&"
    if nsfw:
        url += "include_nsfw=true&"
    if offset:
        url += f"offset={offset}"
    
    
    guild_dir = f"./loot/{guild_id}"
    
    if save_guild_by == "name":
        guild_dir = f"./loot/{guild_name}"
    
    os.makedirs(guild_dir, exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=AUTH_HEADER) as response:
            messages = await response.json()
            tasks = []
            messages_obj = messages.get("messages", [])
            
            for message in messages_obj:
                user_dir = ""
                if save_user_by == "id":
                    user_id = message[0]['author']['id']
                    user_dir = os.path.join(guild_dir, user_id)
                else:
                    username = message[0]['author']['username']
                    user_dir = os.path.join(guild_dir, username)
                os.makedirs(user_dir, exist_ok=True)

                for attachment in message[0]["attachments"]:
                    file_path = os.path.join(user_dir, f"{attachment['id']}_{attachment['filename']}")
                    tasks.append(save_file(session, file_path, attachment['url']))
                    
                offset += 1

            await asyncio.gather(*tasks)

async def fetch_guilds():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discordapp.com/api/users/@me/guilds", headers=AUTH_HEADER) as response:
            guilds = await response.json()
            return [(index, guild["id"], guild["name"]) for index, guild in enumerate(guilds)]

async def main():
    global offset, max_offset, equals_max
    if not os.path.exists("loot"):
        os.makedirs("loot")
    
    guilds = await fetch_guilds()
    for index, guild_id, guild_name in guilds:
        status = " - SCRAPPED" if (guild_id in os.listdir("loot") or guild_name in os.listdir("loot")) else "" 
        print(f"{index} - {guild_name}{status}")

    print(Fore.BLUE + "\nType 'all' to scrape all servers")
    print(Fore.BLUE + "Type nothing to exit")
    servers = input("Select one or more servers (comma separated): ")
    
    if servers == "":
        print(Fore.RED + "No servers selected")
        return
    
    if servers == "all":
        servers = ",".join([str(index) for index, _, _ in guilds])
    
    mapped_guilds = map(int, servers.split(","))
    
    for server_index in mapped_guilds:
        target_guild_id = guilds[server_index][1]
        guild_name = guilds[server_index][2]
        print(Fore.CYAN + f"[ + ] - Scraping {guild_name}")
        while True:
            print(Fore.YELLOW + f"Offset: {offset}")
            await scrap_messages(target_guild_id, guild_name)
            if offset % 25 != 0:
                break
        print(Fore.GREEN + f"[ + ] - Finished scraping {guild_name}")
        
        offset = 0

if __name__ == "__main__":
    asyncio.run(main())

