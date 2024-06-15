import asyncio

from curl_cffi.requests import AsyncSession

from src.utils import HTTPRequests


class Rarible:
    def __init__(self, session: HTTPRequests):
        self.session = session
        self.checked = []
        self.sema = asyncio.Semaphore(20)
        self.user_agent = 'GOTHH'
        self.rarible_url = 'https://rarible.com/marketplace/api/v4/items/search'
        self.rarible_payload = {
            "size": 100,
            "filter": {
                "verifiedOnly": False,
                "sort": "TRENDING",
                "blockchains": ["ETHEREUM"],
                "hideItemsSupply": "HIDE_LAZY_SUPPLY",
                "nsfw": True,
                "orderSources": [],
                "hasMetaContentOnly": True
            }
        }
        self.rarible_headers = {
            "authority": "rarible.com",
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://rarible.com",
            "referer": "https://rarible.com/explore/all/items",
            "user-agent": self.user_agent,
            "x-fingerprint": "eb530f4a4dfc8801cd46167ff55ea78b"
        }
        self.rarible_twit_headers = {
            "authority": "rarible.com",
            "accept": "*/*",
            "cookie": "_hjSessionUser_2596294=eyJpZCI6ImQzZDgzNDg3LTc5ZDgtNWRlZC1hMGIyLTBmOTgxZTc2OGY1YiIsImNyZWF0ZWQiOjE2OTE3ODMyMTc4NTgsImV4aXN0aW5nIjp0cnVlfQ==; __eventn_id=5643b9e8-ad2e-445a-b607-69dd0e612e2e; _gcl_au=1.1.201652513.1703217075; _ga_QPJ7KC6DS2=GS1.1.1703217075.1.0.1703217075.60.0.0; __eventn_id_usr=%7B%7D; _scid=6d91af3e-a37d-4d14-8440-10bf8a9309ea; _scid_r=6d91af3e-a37d-4d14-8440-10bf8a9309ea; _ga=GA1.2.3309326.1703217076; _gid=GA1.2.1790184840.1703217076; _gat=1; _rdt_uuid=1703217076054.eabf3fad-7404-4dd9-93c5-c576d8e94882; _sc_cspv=https%3A%2F%2Ftr.snapchat.com; _uetsid=5b9190d0a07d11eea20179adc8ae6828; _uetvid=d396a990387f11ee8f9429210a2880ef; _hjIncludedInSessionSample_2596294=0; _hjSession_2596294=eyJpZCI6Ijk0OWRmMDVlLWZkNjEtNDNmYy04MDIxLTc5NGRiMmM4Yzk2MyIsImMiOjE3MDMyMTcwNzc5MDIsInMiOjAsInIiOjAsInNiIjoxfQ==; __kla_id=eyJjaWQiOiJOekl4TW1ZM01tSXRaRGd6WlMwME1EYzBMVGd6TlRFdE0yRXhPRFUwTWpobU9XWTMiLCIkcmVmZXJyZXIiOnsidHMiOjE3MDMyMTcwNzgsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vcmFyaWJsZS5jb20vMHhkNTkvc2Vjb25kYXJ5In0sIiRsYXN0X3JlZmVycmVyIjp7InRzIjoxNzAzMjE3MDc4LCJ2YWx1ZSI6IiIsImZpcnN0X3BhZ2UiOiJodHRwczovL3JhcmlibGUuY29tLzB4ZDU5L3NlY29uZGFyeSJ9fQ==; _ga_HENWSLZ89C=GS1.2.1703217078.1.0.1703217078.60.0.0",
            "referer": "https://rarible.com/0xd59/secondary",
            "user-agent": self.user_agent,
            "x-fingerprint": "8af674ef3158732a27a261e6fb9eb027"
        }

    @staticmethod
    async def _return_rarible_link(eth):
        return f'https://rarible.com/marketplace/api/v4/wallets/{eth}/user'

    async def _fetch_rarible_data(self):
        data = await self.session.post(self.sema, self.rarible_url, json=self.rarible_payload, headers=self.rarible_headers)
        return data

    async def _collect_rarible_data(self):
        eth = []
        data = await self._fetch_rarible_data()
        for et in data:
            if 'creator' in et:
                if et['creator'] not in eth:
                    if et['creator'] not in self.checked:
                        eth.append(et['creator'])
                        self.checked.append(et['creator'])
            if 'ownership' in et and 'creator' in et:
                if et['creator'] != et['ownership']['owner']:
                    if et['ownership']['owner'] not in self.checked:
                        eth.append(et['ownership']['owner'])
                        self.checked.append(et['ownership']['owner'])
        return eth

    async def _parse_rarible_twitters(self, eth, checked):
        url = await self._return_rarible_link(eth)
        r = await self.session.get(self.sema, url, headers=self.rarible_twit_headers)
        if 'twitterUsername' in r and len(r['twitterUsername']) > 1:
            checked.append({'address': eth, 'social': {'twitter': r['twitterUsername']}})

    async def _find_rarible_twitter(self, eth_list):
        checked = []
        for eth in eth_list:
            await self._parse_rarible_twitters(eth, checked)
        return checked

    async def run(self):
        eth_list = await self._collect_rarible_data()
        twitter_eth = await self._find_rarible_twitter(eth_list)
        return twitter_eth


async def main():
    a = []
    async with AsyncSession() as session:
        session = HTTPRequests(session)
        rarible = Rarible(session)
        for i in range(3):
            a += await rarible.run()
    print(a)
    print(len(a))


if __name__ == '__main__':
    asyncio.run(main())