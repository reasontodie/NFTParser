import asyncio

from src.utils import HTTPRequests
from src.utils import os_twitter


class Blur:
    def __init__(self, session: HTTPRequests):
        self.session = session
        self.semaphore = asyncio.Semaphore(20)
        self.checked = []

    async def parse_blur_activity(self):
        url = "https://core-api.prod.blur.io/v1/activity/global"
        querystring = {
            "filters": "{\"count\":100,\"eventTypes\":[\"ORDER_CREATED\",\"SALE\"],\"contractAddresses\":[]}"}
        headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "origin": "https://blur.io",
            "user-agent": "GOTHH"
        }
        return await self.session.get(self.semaphore, url, headers=headers, params=querystring)

    async def proceed_activity(self, data):
        accounts = []
        for event in data["activityItems"]:
            if 'fromTrader' in event and event['fromTrader'] and 'address' in event['fromTrader']:
                if event['fromTrader']['address'] not in self.checked:
                    accounts.append(event['fromTrader']['address'])
                    self.checked.append(event['fromTrader']['address'])
            if 'toTrader' in event and event['toTrader'] and 'address' in event['toTrader']:
                if event['toTrader']['address'] not in self.checked:
                    accounts.append(event['toTrader']['address'])
                    self.checked.append(event['toTrader']['address'])
        return list(set(accounts))

    async def parse_blur(self):
        twitters = []
        final = []
        data = await self.parse_blur_activity()
        if data:
            accounts = await self.proceed_activity(data)
            for account in accounts:
                result = await os_twitter(self.semaphore, account, self.session)
                twitters.append(result)
        for twitter in twitters:
            if 'social' in twitter and 'twitter' in twitter['social']:
                final.append(twitter)
        return final

    async def run(self):
        # a = []
        # for i in range(3):
        #     a += await self.parse_blur()
        # print(a)
        # print(len(a))
        return await self.parse_blur()


if __name__ == '__main__':
    blur = Blur('')
    asyncio.run(blur.run())
