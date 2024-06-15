import asyncio

from curl_cffi.requests import AsyncSession

from src.utils import HTTPRequests


class KnownOrigin:
    def __init__(self, session: HTTPRequests):
        self.session = session
        self.checked = []
        self.sema = asyncio.Semaphore(20)

    async def parse_known_activity(self):
        url = "https://api.thegraph.com/subgraphs/name/knownorigin/known-origin"
        headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/json",
            "origin": "https://knownorigin.io",
            "user-agent": "GOTHH"
        }
        payload = {
            "operationName": "activityEvents",
            "variables": {
                "first": 50,
                "skip": 0,
                "eventTypes": [
                    "EditionCreated",
                    "Purchase",
                    "BidPlaced",
                    "BidAccepted",
                    "BidIncreased",
                    "TokenListed",
                    "PriceChanged",
                    "ReserveBidPlaced",
                    "ReserveBidWithdrawn",
                    "ReserveCountdownStarted",
                    "ReserveExtended",
                    "ReservePriceChanged"
                ]
            },
            "query": "query activityEvents($first: Int!, $skip: Int!, $eventTypes: [String!]) {\n  activityEvents(first: $first, skip: $skip, orderBy: timestamp, orderDirection: desc, subgraphError: allow, where: {eventType_in: $eventTypes}) {\n    id\n    type\n    eventType\n    edition {\n      id\n      version\n      salesType\n      editionNmber\n      priceInWei\n      totalSupply\n      totalAvailable\n      totalSold\n      totalBurnt\n      tokenURI\n      collective {\n        recipients\n        __typename\n      }\n      tokenIds\n      createdTimestamp\n      creatorContract {\n        id\n        blockNumber\n        timestamp\n        implementation\n        deployer\n        creator\n        paused\n        owner\n        secondaryRoyaltyPercentage\n        minter\n        defaultFundsHandler\n        defaultFundsRecipients\n        defaultFundsShares\n        ERC165InterfaceID\n        isBatchBuyItNow\n        isHidden\n        totalNumOfEditions\n        totalNumOfTokensSold\n        totalEthValueOfSales\n        totalNumOfTransfers\n        __typename\n      }\n      artistAccount\n      artistCommission\n      optionalCommissionAccount\n      optionalCommissionRate\n      auctionEnabled\n      collaborators\n      totalEthSpentOnEdition\n      offersOnly\n      isGenesisEdition\n      isEnhancedEdition\n      isOpenEdition\n      remainingSupply\n      startDate\n      endDate\n      currentStep\n      active\n      metadataPrice\n      activeBid {\n        id\n        ethValue\n        bidder\n        __typename\n      }\n      sales {\n        transferCount\n        primaryValueInEth\n        birthTimestamp\n        lastTransferTimestamp\n        __typename\n      }\n      transfers {\n        id\n        tokenId\n        __typename\n      }\n      allOwners {\n        id\n        address\n        __typename\n      }\n      metadata {\n        id\n        name\n        description\n        image\n        image_type\n        artist\n        cover_image\n        cover_image_type\n        image_sphere\n        animation_url\n        scarcity\n        tags\n        format\n        theme\n        __typename\n      }\n      reserveAuctionSeller\n      reserveAuctionBidder\n      reservePrice\n      reserveAuctionBid\n      reserveAuctionStartDate\n      previousReserveAuctionEndTimestamp\n      reserveAuctionEndTimestamp\n      reserveAuctionNumTimesExtended\n      isReserveAuctionInSuddenDeath\n      reserveAuctionTotalExtensionLengthInSeconds\n      isReserveAuctionResulted\n      isReserveAuctionResultedDateTime\n      reserveAuctionResulter\n      reserveAuctionCanEmergencyExit\n      stepSaleBasePrice\n      stepSaleStepPrice\n      gatedSale {\n        id\n        paused\n        phases {\n          id\n          saleId\n          phaseId\n          startTime\n          endTime\n          priceInWei\n          walletMintLimit\n          mintCount\n          mintCap\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    token {\n      id\n      version\n      primaryValueInEth\n      birthTimestamp\n      editionNumber\n      tokenURI\n      artistAccount\n      edition {\n        id\n        collaborators\n        totalSupply\n        totalAvailable\n        collective {\n          recipients\n          __typename\n        }\n        __typename\n      }\n      currentOwner {\n        id\n        address\n        __typename\n      }\n      metadata {\n        id\n        name\n        description\n        image\n        image_type\n        artist\n        cover_image\n        cover_image_type\n        image_sphere\n        animation_url\n        scarcity\n        tags\n        format\n        theme\n        __typename\n      }\n      listing {\n        id\n        reserveAuctionSeller\n        reserveAuctionBidder\n        reservePrice\n        reserveAuctionBid\n        reserveAuctionStartDate\n        previousReserveAuctionEndTimestamp\n        reserveAuctionEndTimestamp\n        reserveAuctionNumTimesExtended\n        isReserveAuctionInSuddenDeath\n        reserveAuctionTotalExtensionLengthInSeconds\n        isReserveAuctionResulted\n        isReserveAuctionResultedDateTime\n        reserveAuctionResulter\n        reserveAuctionCanEmergencyExit\n        __typename\n      }\n      __typename\n    }\n    timestamp\n    eventValueInWei\n    creator\n    creatorCommission\n    collaborator\n    collaboratorCommission\n    transactionHash\n    triggeredBy\n    buyer\n    seller\n    __typename\n  }\n}\n"
        }
        data = await self.session.post(self.sema, url, json=payload, headers=headers)
        return data

    async def proceed_data(self, data):
        accounts = []
        if 'data' in data and data and 'activityEvents' in data['data']:
            for event in data['data']['activityEvents']:
                if event['buyer'] is not None:
                    if event['buyer'] not in self.checked:
                        self.checked.append(event['buyer'])
                        accounts.append(event['buyer'])
                if event['seller'] is not None:
                    if event['seller'] not in self.checked:
                        self.checked.append(event['seller'])
                        accounts.append(event['seller'])
                if 'edition' in event:
                    if 'collaborators' in event['edition']:
                        for collaborator in event['edition']['collaborators']:
                            if collaborator not in self.checked:
                                self.checked.append(collaborator)
                                accounts.append(collaborator)
        return accounts

    async def get_twitter_known(self, eth):
        url = f"https://us-central1-known-origin-io.cloudfunctions.net/main/api/verification/user/{eth}"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "origin": "https://knownorigin.io",
            "referrer-policy": "origin",
            "user-agent": "GOTHH"
        }
        data = await self.session.get(self.sema, url, headers=headers)
        if data:
            if 'twitter' in data and 'handle' in data['twitter']:
                return {'social': {'twitter': data['twitter']['handle']}, 'address': eth}
            else:
                return {'social': {}, 'address': eth}

    async def run(self):
        final = []
        data = await self.parse_known_activity()
        if data:
            accounts = await self.proceed_data(data)
            accounts = list(set(accounts))
            for account in accounts:
                info = await self.get_twitter_known(account)
                final.append(info)
        return final


async def main():
    a = []
    async with AsyncSession() as session:
        session = HTTPRequests(session)
        known = KnownOrigin(session)
        for i in range(3):
            a += await known.run()
    print(a)
    print(len(a))

if __name__ == '__main__':
    asyncio.run(main())
