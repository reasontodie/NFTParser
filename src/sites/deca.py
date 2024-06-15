import asyncio
import random

from loguru import logger

from src.utils import HTTPRequests


class Deca:
    def __init__(self, session: HTTPRequests):
        self.last_on_deca = None
        self.checked = []
        self.latests_on_deca = []
        self.sema = asyncio.Semaphore(20)
        self.session = session

    @staticmethod
    async def proceed_user_deka(user):
        pr_user = {"social": {}}
        js = user['result']['data']['json']
        if 'links' in js:
            for link in js['links']:
                l_type = link['type']
                pr_user["social"][l_type.lower()] = link['url']
        if 'wallets' in js:
            for wallet in js['wallets']:
                if wallet['blockchain'] == 'ethereum':
                    pr_user['address'] = wallet['address']

        return pr_user

    @staticmethod
    async def procceed_deka_following(following):
        ids = []
        conn = following['result']['data']['json']['connections']
        for co in conn:
            ids.append({co['user']['username']: co['user']['id']})
        return ids

    async def get_user_from_deca(self, username, user_id):
        url = "https://deca.art/api/trpc/user.profile,social.connectionCounts,gallery.previews,user.me,social.connections,social.connections,social.connections,uploads.getUploadCollectionsForUser,artist.leaderboard,user.activity,comments.countForEntity,comments.forEntity"
        querystring = {"batch": "1",
                       "input": "{\"0\":{\"json\":{\"usernameOrAddress\":\"" + username + "\"}},\"1\":{\"json\":{\"userId\":\"" + user_id + "\"}},\"2\":{\"json\":{\"usernameOrAddress\":\"" + username + "\"}},\"3\":{\"json\":null,\"meta\":{\"values\":[\"undefined\"]}},\"4\":{\"json\":{\"userId\":\"" + user_id + "\",\"direction\":\"TO_ME\",\"type\":\"FOLLOWERS\",\"cursor\":null},\"meta\":{\"values\":{\"cursor\":[\"undefined\"]}}},\"5\":{\"json\":{\"userId\":\"" + user_id + "\",\"direction\":\"FROM_ME\",\"type\":\"FOLLOWERS\",\"cursor\":null},\"meta\":{\"values\":{\"cursor\":[\"undefined\"]}}},\"6\":{\"json\":{\"userId\":\"" + user_id + "\",\"direction\":\"FROM_ME\",\"type\":\"SUBSCRIBERS\",\"cursor\":null},\"meta\":{\"values\":{\"cursor\":[\"undefined\"]}}},\"7\":{\"json\":{\"userId\":\"" + user_id + "\",\"showHidden\":false}},\"8\":{\"json\":{\"userId\":\"" + user_id + "\"}},\"9\":{\"json\":{\"userId\":\"" + user_id + "\",\"cursor\":null},\"meta\":{\"values\":{\"cursor\":[\"undefined\"]}}},\"10\":{\"json\":{\"entityType\":\"ASSET\",\"entityId\":\"a784c48f-c77f-43f8-b0ba-e4d9130cb9d6\"}},\"11\":{\"json\":{\"entityType\":\"ASSET\",\"entityId\":\"a784c48f-c77f-43f8-b0ba-e4d9130cb9d6\",\"cursor\":null},\"meta\":{\"values\":{\"cursor\":[\"undefined\"]}}}}"}
        headers = {"accept": "*/*", "content-type": "application/json", "user-agent": "GOTHH"}
        response = await self.session.get(self.sema, url, headers=headers, params=querystring)
        return response

    async def process_unique(self, unique):
        username, user_id = tuple(unique.items())[0]
        user = await self.get_user_from_deca(username, user_id)
        if user:
            follows = user[1]['result']['data']['json']['follows']
            followers = user[1]['result']['data']['json']['followers']
            total = follows + followers
            great_result = await self.proceed_user_deka(user[0])
            if total > 3 and {username: user_id} not in self.latests_on_deca:
                self.last_on_deca = {username: user_id}
            return great_result

    async def bridge_to_unique(self, unique_list):
        tasks = [self.process_unique(unique) for unique in unique_list]
        return await asyncio.gather(*tasks)

    async def get_data_from_deca(self, username=None, user_id=None):
        great = []
        if self.last_on_deca is not None:
            user = await self.get_user_from_deca(username, user_id)
        elif username is not None and user_id is not None:
            user = await self.get_user_from_deca(username, user_id)
        if user:
            great.append(await self.proceed_user_deka(user[0]))
            for_check = []
            for i in [user[5], user[6]]:
                followings = await self.procceed_deka_following(i)
                for_check.extend(followings)
            random.shuffle(for_check)
            unique_set = {tuple(sorted(d.items())) for d in for_check}
            unique_list = [dict(t) for t in unique_set]
            result = await self.bridge_to_unique(unique_list)
            great += result
            ne = []
            if great:
                for gray in great:
                    if ('twitter' in gray['social'] or 'discord' in gray['social']) and 'address' in gray:
                        if gray['address'] not in self.checked:
                            self.checked.append(gray['address'])
                            ne.append(gray)
            return ne

    async def get_random_deca(self):
        url = "https://deca.art/api/trpc/features.enabled,mintOnDemand.browse"
        querystring = {"batch": "1",
                       "input": "{\"0\":{\"json\":null,\"meta\":{\"values\":[\"undefined\"]}},\"1\":{\"json\":{\"limit\":20,\"onlyFeatured\":true}}}"}
        headers = {
            "accept": "*/*", "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "content-type": "application/json"}
        response = await self.session.get(self.sema, url, headers=headers, params=querystring)
        if response is not None:
            data = response[1]
            if data is not None:
                assets = data['result']['data']['json']['assets']
                asset = random.choice(assets)
                return asset['assetCreator']['username'], asset['assetCreator']['id']

    async def deca_parse(self):
        accounts = []
        if self.last_on_deca is not None:
            username, user_id = tuple(self.last_on_deca.items())[0]
            self.latests_on_deca.append({username, user_id})
            data_deca = await self.get_data_from_deca(username, user_id)
            if len(data_deca) < 3:
                self.last_on_deca = None
            accounts.extend(data_deca)
        else:
            try:
                username, user_id = await self.get_random_deca()
                data_deca = await self.get_data_from_deca(username, user_id)
                accounts += data_deca
            except Exception as e:
                logger.error(f'Error Deca | Error: {e}')
        return accounts

    async def run(self):
        return await self.deca_parse()
        # a = []
        # for i in range(4):
        #     a += await self.deca_parse()
        # print(a)
        # print(len(a))


if __name__ == '__main__':
    deca = Deca('')  # session
    asyncio.run(deca.run())
