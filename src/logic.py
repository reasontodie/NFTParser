import asyncio

from loguru import logger
from httpx import AsyncClient
from curl_cffi.requests import AsyncSession

from src.sites import Blur, Dappradar
from src.sites import Deca, ExchangeArt
from src.sites import Foundation, KnownOrigin
from src.sites import OKX, Rarible, SuperRare

from src.utils import HTTPRequests
from src.utils import save_string
from src.utils import load_config
from src.utils import load_cache

from src.balance import get_balance


class MainLogic:
    def __init__(self, value):
        self.value = value
        self.checked = []

    @staticmethod
    async def make_one_list(data):
        flat_list = []
        for item in data:
            flat_list.extend(item)
        return flat_list

    async def filter(self, data):
        filtered = []
        for item in data:
            if item['address'] not in self.checked:
                filtered.append(item)
                self.checked.append(item)
        return filtered

    async def check_balances(self, accounts):
        group_size = 50
        wallets = [x['address'] for x in accounts]
        x = [wallets[i:i + group_size] for i in range(0, len(wallets), group_size)]
        async with AsyncClient() as client:
            session = HTTPRequests(client)
            for wallets in x:
                info = await get_balance(wallets, session)
                for address, balance in info.items():
                    for account in accounts:
                        if account['address'] == address:
                            account['balance'] = balance
                            if account['balance'] > self.value and account['address'] not in self.checked:
                                if 'social' in account and 'twitter' in account['social']:
                                    if not ('https://twitter.com/' in account['social']['twitter']):
                                        account['social']['twitter'] = f"https://twitter.com/{account['social']['twitter']}"
                                prestring = (
                                    f'{"|" + account["social"]["twitter"] if "twitter" in account["social"] else ""}'
                                    f'{"|" + account["social"]["discord"] if "discord" in account["social"] else ""}')
                                string = f"{account['address']}|${account['balance']}" + prestring
                                logger.success(string)
                                self.checked.append(account['address'])
                                await save_string(load_config()['save_results'], string + '\n')
                await asyncio.sleep(1)

    async def x_load_cache(self):
        self.checked = await load_cache(load_config()['save_results'])
        return self.checked

    async def run(self):
        await self.x_load_cache()
        async with AsyncSession() as session:
            session = HTTPRequests(session)
            deca_art = Deca(session)
            foundation = Foundation(session)
            blur = Blur(session)
            dapp_radar = Dappradar(session)
            exchange_art = ExchangeArt(session)
            known = KnownOrigin(session)
            okx = OKX(session)
            rarible = Rarible(session)
            super_rare = SuperRare(session)
            pool = [deca_art, foundation, blur,
                    dapp_radar, exchange_art, known,
                    okx, rarible, super_rare]
            while True:
                tasks = [i.run() for i in pool]
                data = await asyncio.gather(*tasks)
                data = await self.make_one_list(data)
                accounts = await self.filter(data)
                logger.info(f'Total accounts: {len(accounts)}')
                if accounts:
                    await self.check_balances(accounts)


if __name__ == '__main__':
    asyncio.run(MainLogic(100).run())
