import asyncio

from curl_cffi.requests import AsyncSession

from src.utils import HTTPRequests
from src.utils import os_twitter


class OKX:
    def __init__(self, session: HTTPRequests):
        self.session = session
        self.checked = []
        self.sema = asyncio.Semaphore(20)

    async def parse_okx_activity(self):
        url = "https://www.okx.com/priapi/v1/nft/trading/collectionHistory"
        querystring = {"showCollOrder": "true", "chain": "1,501", "type": "SALE,MINT,OFFER", "project": "",
                       "address": "", "direction": "1", "limit": "100", "t": ""}
        headers = {
            "accept": "application/json",
            "app-type": "web",
            "nft_token": "undefined",
            "referer": "https://www.okx.com/ru/web3/marketplace/nft/stats/activity"
        }
        response = await self.session.get(self.sema, url, headers=headers, params=querystring)
        return response

    async def proceed_data(self, data):
        accounts = []
        if 'data' in data and data['data'] is not None and data['data']['data']:
            for res in data['data']['data']:
                if len(res['from']) > 0:
                    if res['from'] not in self.checked:
                        self.checked.append(res['from'])
                        accounts.append(res['from'])
                if len(res['to']) > 0:
                    if res['to'] not in self.checked:
                        self.checked.append(res['to'])
                        accounts.append(res['to'])
        return accounts

    async def run(self):
        twitter = []
        final = []
        data = await self.parse_okx_activity()
        if data:
            accounts = await self.proceed_data(data)
            for account in accounts:
                result = await os_twitter(self.sema, account, self.session)
                twitter.append(result)
            for tw in twitter:
                if 'social' in tw and 'twitter' in tw['social']:
                    final.append(tw)
        return final


async def main():
    a = []
    async with AsyncSession() as session:
        session = HTTPRequests(session)
        okx = OKX(session)
        for i in range(3):
            a += await okx.run()
        print(a)
        print(len(a))


if __name__ == '__main__':
    asyncio.run(main())
