import asyncio

from src.utils import HTTPRequests
from src.utils import os_twitter

from curl_cffi.requests import AsyncSession


class Dappradar:
    def __init__(self, session: HTTPRequests):
        self.session = session
        self.checked = []
        self.sema = asyncio.Semaphore(20)

    async def parse_dappradar_activity(self):
        url = "https://nft-sales-service.dappradar.com/v3.1/sale"
        querystring = {"currency": "usd", "sort": "soldAt", "order": "desc", "resultsPerPage": "50", "page": "1",
                       "range": "day", "chainId\\[\\]": ["27", "1"], "dataType": "mixed"}
        headers = {
            "accept": "application/json, text/plain, */*",
            "origin": "https://dappradar.com",
            "referer": "https://dappradar.com/",
            "user-agent": "GOTHH"
        }
        return await self.session.get(self.sema, url, params=querystring, headers=headers)

    async def proceed_dappradar(self, data):
        accounts = []
        if 'results' in data:
            for account in data['results']:
                if 'seller' in account and account['seller'] is not None:
                    if account['seller'] not in self.checked:
                        accounts.append(account['seller'])
                        self.checked.append(account['seller'])
                if 'buyer' in account and account['buyer'] is not None:
                    if account['buyer'] not in self.checked:
                        accounts.append(account['buyer'])
                        self.checked.append(account['buyer'])
        return list(set(accounts))

    async def run(self):
        result = []
        final = []
        data = await self.parse_dappradar_activity()
        if data:
            accounts = await self.proceed_dappradar(data)
            for account in accounts:
                info = await os_twitter(self.sema, account, self.session)
                result.append(info)
            for res in result:
                if 'social' in res and 'twitter' in res['social']:
                    final.append(res)
        return final


async def main():
    a = []
    async with AsyncSession() as session:
        sess = HTTPRequests(session)
        dapp = Dappradar(sess)
        for i in range(3):
            a += await dapp.run()
    print(a)
    print(len(a))


if __name__ == '__main__':
    asyncio.run(main())
