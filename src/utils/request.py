import curl_cffi.requests.errors
from loguru import logger
from curl_cffi.requests import AsyncSession
from httpx import AsyncClient


class HTTPRequests:
    def __init__(self, session: [AsyncSession|AsyncClient]):
        self.session = session

    async def post(self, semaphore, url, json=None, headers=None, data=None):
        while True:
            try:
                async with semaphore:
                    response = await self.session.post(url, json=json, headers=headers, data=data)
                    logger.debug(f'Request to ({url}) | Status: {response.status_code}')
                    if response.status_code == 200:
                        return response.json()
            except Exception as e:
                logger.error(f'Error while request to ({url}) | Error: {e} ')

    async def get(self, semaphore, url, headers=None, params=None):
        while True:
            try:
                async with semaphore:
                    response = await self.session.get(url, headers=headers, params=params)
                    logger.debug(f'Request to ({url}) | Status: {response.status_code} | {response.headers}')
                    if response.status_code in [200, 207]:
                        return response.json()
            except Exception as e:
                logger.error(f'Error while request to ({url}) | Error: {e} ')