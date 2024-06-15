import asyncio

from curl_cffi.requests import AsyncSession

from src.utils import HTTPRequests


class SuperRare:
    def __init__(self, session: HTTPRequests):
        self.session = session
        self.checked = []
        self.last_checked = None
        self.sema = asyncio.Semaphore(30)
        self.was_checked = []

    async def parse_activity(self):
        final = []
        pool = [
            '{"requests":[{"indexName":"prod_artworks","params":"facets=%5B%5D&hitsPerPage=20&tagFilters="},{"indexName":"prod_artworks_activityTimestampUnix_desc","params":"facets=%5B%22metadata.tags%22%2C%22media.mimeType%22%2C%22hasSalePrice%22%2C%22auction.auctionFilterString%22%2C%22hasOpenOffer%22%2C%22isOwnedByCreator%22%2C%22saleType%22%2C%22currentSalePrices.nodes.currency.type%22%2C%22salePriceSzabo%22%2C%22salePriceRare%22%2C%22artists.debutArtworks%22%2C%22artists.hasSales%22%2C%22artists.isNewArtist%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=20&maxValuesPerFacet=27&page=0&tagFilters="},{"indexName":"prod_series","params":"facets=%5B%22category.categoryType%22%2C%22hasLiveAuction%22%2C%22hasNewAddition%22%2C%22hasNewOffer%22%2C%22floorAmountSzabo%22%2C%22floorAmountRare%22%2C%22currency%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=50&maxValuesPerFacet=16&page=0&tagFilters="}]}',
            '{"requests":[{"indexName":"prod_artworks","params":"facets=%5B%5D&hitsPerPage=20&tagFilters="},{"indexName":"prod_artworks_activityTimestampUnix_desc","params":"facets=%5B%22metadata.tags%22%2C%22media.mimeType%22%2C%22hasSalePrice%22%2C%22auction.auctionFilterString%22%2C%22hasOpenOffer%22%2C%22isOwnedByCreator%22%2C%22saleType%22%2C%22currentSalePrices.nodes.currency.type%22%2C%22salePriceSzabo%22%2C%22salePriceRare%22%2C%22artists.debutArtworks%22%2C%22artists.hasSales%22%2C%22artists.isNewArtist%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=20&maxValuesPerFacet=27&page=0&tagFilters="},{"indexName":"prod_series_latestMintAtUnix_desc","params":"facets=%5B%22category.categoryType%22%2C%22hasLiveAuction%22%2C%22hasNewAddition%22%2C%22hasNewOffer%22%2C%22floorAmountSzabo%22%2C%22floorAmountRare%22%2C%22currency%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=50&maxValuesPerFacet=16&page=0&tagFilters="}]}'
        ]
        for i in pool:
            url = 'https://d27t7j41om-2.algolianet.com/1/indexes/*/queries'
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Origin': 'https://superrare.com',
                'Referer': 'https://superrare.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'x-algolia-agent': 'Algolia for JavaScript (4.14.2); Browser (lite); react (17.0.2); react-instantsearch (6.38.0); react-instantsearch-hooks (6.38.0); JS Helper (3.13.3)',
                'x-algolia-api-key': '879cb219411424f5f283980a3945b8fa',
                'x-algolia-application-id': 'D27T7J41OM'
            }
            response = await self.session.post(self.sema, url, headers=headers, data=i)
            final.append(response)
        return final

    async def proceed_activity(self, data):
        accounts = []
        for method in data:
            if 'results' in method:
                for results in method['results']:
                    if 'hits' in results:
                        for activity in results['hits']:
                            if 'creator' in activity and activity['creator'] is not None:
                                if activity['creator']['ethereumAddress'] not in self.checked:
                                    accounts.append((activity['creator']['ethereumAddress'], activity['creator']['username']))
                                    self.checked.append(activity['creator']['ethereumAddress'])
                            if 'owner' in activity and activity['owner'] is not None:
                                if activity['owner']['ethereumAddress'] not in self.checked:
                                    accounts.append((activity['owner']['ethereumAddress'], activity['owner']['username']))
                                    self.checked.append(activity['owner']['ethereumAddress'])
            return accounts

    async def proceed_accounts(self, account, twitters, follows):
        url = "https://superrare.com/api/trpc/profile.getCreations,profile.getByUsername"
        querystring = {"batch": "1",
                       "input": "{\"0\":{\"orderBy\":\"DATE_MINTED_DESC\",\"skip\":0,\"take\":12,\"creatorAddresses\":[\"0x14287e62b859a3a5e19b3c2d59ed1f12ac94ba4c\"],\"contractAddresses\":[],\"cursor\":1},\"1\":{\"username\":\""+account[1]+"\"}}"}
        headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/json",
            "referer": f"https://superrare.com/{account[1]}",
            "user-agent": 'GOTHH'
        }
        info = await self.session.get(self.sema, url, headers=headers, params=querystring)
        if info:
            site_account = info[1]
            if 'result' in site_account and 'data' in site_account['result']:
                data = site_account['result']['data']
                if 'twitterlink' in data and data['twitterlink'] is not None:
                    twitters.append({
                        'social': {
                            'twitter': data['twitterlink'].replace(
                                'http://twitter.com/', '').replace(
                                'https://twitter.com/', '').replace('https://www.Twitter.com/', '').replace(
                                'www.twitter.com/', '').replace('https://www.twitter.com/', '').replace(
                                'http://Twitter.com/', '').replace('https://Twitter.com/', '')
                        },
                        'address': account[0]
                    })
                if 'followers' in data:
                    if data['followers'] is not None:
                        for follower in data['followers']:
                            if follower['user_follower']['ethereum_address'] not in self.checked:
                                follows.append((follower['user_follower']['ethereum_address'],
                                                follower['user_follower']['username']))
                                self.checked.append(follower['user_follower']['ethereum_address'])

                if 'following' in data:
                    if data['following'] is not None:
                        for following in data['following']:
                            if following['user_following']['ethereum_address'] not in self.checked:
                                follows.append((following['user_following']['ethereum_address'],
                                                following['user_following']['username']))
                                self.checked.append(following['user_following']['ethereum_address'])
                if account not in self.was_checked:
                    self.was_checked.append(account)
                    if 'following' in data or 'followers' in data:
                        if data['following'] is not None or data['followers'] is not None:
                            self.last_checked = account
        return twitters, follows

    async def multi_parse_accounts(self, accounts):
        twitters, follows = [], []
        tasks = [self.proceed_accounts(account, twitters, follows) for account in accounts]
        await asyncio.gather(*tasks)
        return twitters, follows

    async def run(self):
        result = []
        final = []
        if self.last_checked is None:
            data = await self.parse_activity()
            if data:
                accounts = await self.proceed_activity(data)
                twitters, follows = await self.multi_parse_accounts(accounts)
                result.extend(twitters)
                twitters2, trash = await self.multi_parse_accounts(follows)
                result.extend(twitters2)
        else:
            twitters, follows = await self.multi_parse_accounts([self.last_checked])
            if len(twitters) < 3 and len(follows) < 3:
                self.last_checked = None
            result.extend(twitters)
            twitters2, trash = await self.multi_parse_accounts(follows)
            result.extend(twitters2)
        for res in result:
            if 'social' in res and 'twitter' in res['social'] and len(res['social']['twitter']) > 1:
                final.append(res)
        return final


async def main():
    a = []
    async with AsyncSession() as session:
        session = HTTPRequests(session)
        super_rare = SuperRare(session)
        for i in range(3):
            a += await super_rare.run()
    print(a)
    print(len(a))


if __name__ == "__main__":
    asyncio.run(main())
