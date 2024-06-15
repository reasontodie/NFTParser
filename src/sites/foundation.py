import random
import asyncio

from src.utils import HTTPRequests


class Foundation:
    def __init__(self, session: HTTPRequests):
        self.checked = []
        self.last_on_foundation = None
        self.was_last = []
        self.sema = asyncio.Semaphore(20)
        self.session = session

    async def get_user_foundation(self, user):
        url = "https://hasura2.foundation.app/v1/graphql"
        headers = {"accept": "*/*", "content-type": "application/json", "user-agent": "GOTHH"}
        payload = {
            "query": "\n    query UserProfileByPublicKey($publicKey: String!) {\n  user: user_by_pk(publicKey: $publicKey) {\n    ownedArtworks: artworks(\n      limit: 12\n      where: {isIndexed: {_eq: true}, deletedAt: {_is_null: true}, ownerPublicKey: {_neq: $publicKey}}\n      distinct_on: ownerPublicKey\n    ) {\n      owner {\n        publicKey\n        username\n        profileImageUrl\n        coverImageUrl\n        name\n        bio\n        moderationStatus\n        createdAt\n        isAdmin\n        links\n      }\n    }\n    collectorsCount: artworks_aggregate(\n      where: {isIndexed: {_eq: true}, deletedAt: {_is_null: true}, ownerPublicKey: {_neq: $publicKey}}\n      distinct_on: ownerPublicKey\n    ) {\n      aggregate {\n        count\n      }\n    }\n    ...UserProfileFragment\n  }\n}\n    \n    fragment UserProfileFragment on user {\n  ...UserFragment\n  twitSocialVerifs: socialVerifications(\n    where: {isValid: {_eq: true}, service: {_eq: \"TWITTER\"}}\n    limit: 1\n  ) {\n    ...SocialVerificationFragment\n  }\n  instaSocialVerifs: socialVerifications(\n    where: {isValid: {_eq: true}, service: {_eq: \"INSTAGRAM\"}}\n    limit: 1\n  ) {\n    ...SocialVerificationFragment\n  }\n  followerCount: follows_aggregate(where: {isFollowing: {_eq: true}}) {\n    aggregate {\n      count\n    }\n  }\n  followingCount: following_aggregate(where: {isFollowing: {_eq: true}}) {\n    aggregate {\n      count\n    }\n  }\n}\n    \n    fragment UserFragment on user {\n  bio\n  coverImageUrl\n  createdAt\n  isAdmin\n  links\n  moderationStatus\n  name\n  profileImageUrl\n  publicKey\n  username\n}\n    \n\n    fragment SocialVerificationFragment on social_verification {\n  id\n  user\n  createdAt\n  updatedAt\n  expiresAt\n  lastCheckedAt\n  socialVerificationURL\n  verificationText\n  userId\n  username\n  isValid\n  service\n  failedReason\n  status\n}\n    ",
            "variables": {
                "publicKey": f"{user['address']}"
            }
        }
        user = {'social': {}, 'address': user['address']}
        response = await self.session.post(self.sema, url, headers=headers, json=payload)
        if response:
            if 'data' in response and 'user' in response['data']:
                if response['data']['user']['twitSocialVerifs'] is not None:
                    for link in response['data']['user']['twitSocialVerifs']:
                        user['social']['twitter'] = f"https://twitter.com/{link['username']}"
        return user

    async def get_subs(self, users):
        accounts = []
        if users is not None:
            random.shuffle(users)
            for n in users:
                url = 'https://hasura2.foundation.app/v1/graphql'
                payload = {
                    "query": "\n    query UserFollowing($publicKey: String!, $currentUserPublicKey: String!, $offset: Int!, $limit: Int!) {\n  user: user_by_pk(publicKey: $publicKey) {\n    items: following(\n      where: {isFollowing: {_eq: true}}\n      offset: $offset\n      limit: $limit\n    ) {\n      user: userByFollowedUser {\n        name\n        username\n        profileImageUrl\n        publicKey\n        isFollowingUser: follows_aggregate(\n          where: {user: {_eq: $currentUserPublicKey}, isFollowing: {_eq: true}}\n        ) {\n          aggregate {\n            count\n          }\n        }\n      }\n    }\n  }\n}\n    ",
                    "variables": {
                        "publicKey": n['address'],
                        "currentUserPublicKey": "",
                        "offset": 0,
                        "limit": 40
                    }
                }
                headers = {"Accept": "*/*", "Content-Type": "application/json", "User-Agent": "GOTHH"}
                response = await self.session.post(self.sema, url, headers=headers, json=payload)
                if response:
                    if 'data' in response:
                        for item in response['data']['user']['items']:
                            if item['user']['publicKey'] not in self.checked:
                                self.checked.append(item['user']['publicKey'])
                                if item['user']['publicKey'] not in self.was_last:
                                    self.last_on_foundation = item['user']['publicKey']
                                    self.was_last.append(item['user']['publicKey'])
                                accounts.append({'social': {}, 'address': item['user']['publicKey']})
        return accounts

    async def get_browse_foundation(self):
        url = "https://api-v2.foundation.app/graphql"
        payload = {
            "query": "\n    query Nfts($accountAddress: ID, $collectionAddresses: [ID], $marketAvailability: NftMarketAvailability, $distinctAssetKey: String, $sort: NftSortOption, $page: Int, $perPage: Int, $distinct: Boolean) {\n  nftsSearch(\n    accountAddress: $accountAddress\n    collectionAddresses: $collectionAddresses\n    marketAvailability: $marketAvailability\n    distinctAssetKey: $distinctAssetKey\n    sort: $sort\n    page: $page\n    perPage: $perPage\n    distinct: $distinct\n  ) {\n    items: nfts\n    counts {\n      collectionCounts\n      marketAvailabilityCounts\n      distinctCounts\n    }\n    page\n    perPage\n    totalPages\n  }\n}\n    ",
            "variables": {
                "marketAvailability": None,
                "sort": "MINT_DATE_DESC",
                "distinct": True,
                "page": 0
            }
        }
        headers = {"Accept": "*/*", "Content-Type": "application/json", "User-Agent": "GOTHH"}
        response = await self.session.post(self.sema, url, json=payload, headers=headers)
        addresses = []
        if response is not None:
            for item in response['data']['nftsSearch']['items']:
                if 'creator' in item and item['creator']['publicKey'] is not None:
                    if item['creator']['publicKey'] not in self.checked:
                        account = {'social': {}, 'address': item['creator']['publicKey']}
                        self.checked.append(item['creator']['publicKey'])
                        addresses.append(account)
            return addresses

    async def foundation_parse(self):
        clear = []
        if self.last_on_foundation is not None:
            browse = []
            subs = await self.get_subs([{'address': self.last_on_foundation}])
            if len(subs) < 3:
                self.last_on_foundation = None
        else:
            browse = await self.get_browse_foundation()
            subs = await self.get_subs(browse)
        if browse is None:
            browse = []
        if subs is None:
            subs = []
        for account in browse+subs:
            if account['address'] not in clear:
                clear.append(account)
        tasks = [self.get_user_foundation(u) for u in clear]
        result = await asyncio.gather(*tasks)
        clear = []
        for res in result:
            if 'twitter' in res['social']:
                clear.append(res)
        return clear

    async def run(self):
        # a = []
        # for i in range(3):
        #     a += await self.foundation_parse()
        # print(a)
        # print(len(a))
        return await self.foundation_parse()


if __name__ == '__main__':
    found = Foundation('')  # session
    asyncio.run(found.run())
