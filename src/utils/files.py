import json
import os

import aiofiles


def load_config(path: str = 'settings.json'):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


async def save_string(path: str, string: str):
    writen = False
    async with aiofiles.open(path, 'a+', encoding='utf-8') as file:
        while writen is False:
            try:
                await file.write(string)
                writen = True
            except PermissionError:
                pass

async def load_cache(path: str):
    if os.path.exists(path):
        async with aiofiles.open(path, 'r', encoding='utf-8') as file:
            lines = await file.readlines()
            return [line.split('|')[0] for line in lines]
    else:
        return []
