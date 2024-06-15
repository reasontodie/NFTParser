import asyncio

from curl_cffi.requests import AsyncSession

from src.utils import HTTPRequests


class ExchangeArt:
    def __init__(self, session: HTTPRequests):
        self.session = session
        self.checked = []
        self.sema = asyncio.Semaphore(15)

    async def parse_activity(self):
        url = "https://api.exchange.art/v2/bff/graphql"
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://exchange.art",
            "referer": "https://exchange.art/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        payload = {
            "query": "\n  \n  fragment SellingAgreementsFragment on SellingAgreements {\n    buyNow {\n      createdAt\n      createdBy\n      currency\n      price\n      priceUsd\n      governingProgram\n      stateAccount\n      escrowAccount\n      beginsAt\n      royaltyProtection\n    }\n    offers {\n      createdAt\n      createdBy\n      currency\n      price\n      priceUsd\n      governingProgram\n      stateAccount\n      escrowAccount\n    }\n    auctions {\n      createdAt\n      createdBy\n      currency\n      price\n      priceUsd\n      governingProgram\n      stateAccount\n      escrowAccount\n      endsAt\n      beginsAt\n      endingPhase\n      endingPhasePercentageFlip\n      extensionWindow\n      minimumIncrement\n      reservePrice\n      reservePriceUsd\n      highestBid\n      highestBidUsd\n      highestBidder\n      numberOfBids\n    }\n    editionSales {\n      createdAt\n      createdBy\n      currency\n      price\n      governingProgram\n      stateAccount\n      escrowAccount\n      preSaleWindow\n      pricingType\n      royaltyProtection\n      saleType\n      beginsAt\n      walletMintingCapacity\n      addressLookupTable\n    }\n  }\n\n  \n  \n  fragment SeriesFragment on Series {\n    id\n    description\n    isCertified\n    isCurated\n    isNsfw\n    isOneOfOne\n    name\n    primaryCategory\n    secondaryCategory\n    tags\n    tertiaryCategory\n    website\n    discord\n    twitter\n    thumbnailPath\n    bannerPath\n  }\n\n  fragment NftWithArtistProfileFragmentAndSeries on Nft {\n    id\n    blockchain\n    seriesIds\n    series {\n      ...SeriesFragment\n    }\n    masterEdition {\n      address\n      supply\n      maxSupply\n      permanentlyEnd\n    }\n    edition {\n      address\n      masterEditionId\n      parent\n      num\n    }\n    mintedAt\n    mintedOnExchange\n    artistProfileId\n    artistProfile {\n      md {\n        displayName\n        slug\n      }\n      assets {\n        thumbnail\n      }\n      twitter {\n        handle\n      }\n    }\n    curated\n    certified\n    discounted\n    nsfw\n    aiGenerated\n    royaltyProtected\n    category\n    metadata {\n      accountAddress\n      name\n      symbol\n      updateAuthority\n      primarySaleHappened\n      isMutable\n      creators {\n        address\n        royaltyBps\n      }\n      solanaCollectionKey\n      solanaVerifiedInCollection\n    }\n    json {\n      uri\n      image\n      description\n      attributes {\n        value\n        traitType\n      }\n      files {\n        uri\n        type\n      }\n    }\n  }\n\n  \n  fragment StockReportFragment on StockReport {\n    totalBuyNowSellingAgreements\n    totalAuctionSellingAgreements\n    totalOfferSellingAgreements\n    lowestBuyNowPriceUsd\n    highestBuyNowPriceUsd\n    lowestAuctionPriceUsd\n    highestAuctionPriceUsd\n    lowestOfferPriceUsd\n    highestOfferPriceUsd\n  }\n\n  \n  fragment NftStatsFragment on NftStats {\n    lastSale {\n      currency\n      amount\n      amountUsd\n    }\n  }\n\n  query stockEntry($input: GetStockDto!) {\n    getStockResponse(input: $input) {\n      results {\n        nft {\n          ...NftWithArtistProfileFragmentAndSeries\n        }\n        sellingAgreements {\n          ...SellingAgreementsFragment\n        }\n        report {\n          ...StockReportFragment\n        }\n        nftStats {\n          ...NftStatsFragment\n        }\n      }\n      total\n    }\n  }\n",
            "variables": {
                "input": {
                    "from": 0,
                    "sort": "newest_listed",
                    "filters": {
                        "saleStatus": "on_sale",
                        "blockchains": [
                            "solana",
                            "ethereum"
                        ],
                        "currencies": [],
                        "sellingAgreementTypes": [
                            "auction",
                            "buy_now"
                        ],
                        "nftTypes": [
                            "original_no_supply"
                        ]
                    },
                    "limit": 20
                }
            }
        }
        data = await self.session.post(self.sema, url, headers=headers, json=payload)
        return data

    async def proceed_data(self, data):
        twitters = []
        if 'data' in data and data['data'] and 'getStockResponse' in data['data']:
            for result in data['data']['getStockResponse']['results']:
                if 'nft' in result and 'metadata' in result['nft'] and 'updateAuthority' in result['nft']['metadata']:
                    if result['nft']['metadata']['updateAuthority'] not in self.checked:
                        if result['nft']['artistProfile']['twitter'] is not None:
                            self.checked.append(result['nft']['metadata']['updateAuthority'])
                            twitters.append({'social': {'twitter': result['nft']['artistProfile']['twitter']['handle']},
                                             'address': result['nft']['metadata']['updateAuthority']})
        return twitters

    async def run(self):
        data = await self.parse_activity()
        return await self.proceed_data(data)


async def main():
    a = []
    async with AsyncSession() as session:
        session = HTTPRequests(session)
        excha = ExchangeArt(session, [])
        for i in range(3):
            a += await excha.run()
    print(a)
    print((len(a)))

if __name__ == '__main__':
    asyncio.run(main())
