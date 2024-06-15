import json

from javascript import require

generate_debank_headers = require("./headers_generator.js").generate_debank_headers


def get_headers(payload, path) -> dict[str, str]:
    while True:
        js_headers = json.loads(str(generate_debank_headers(payload, path)))
        if "\x00" in js_headers["signature"]:
            continue
        break

    headers = {
        'authority': 'api.debank.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
        # 'account': json.dumps({
        #     "random_at": int(time.time()),
        #     "random_id": uuid.uuid4().hex,
        #     # "user_addr": "0x3c7d6e2a5b2ab6ba29e9b49f1dd69cd2019d9686",
        #     # "wallet_type": "metamask",
        #     # "session_id": session_id,
        #     # "is_verified": True
        # }).replace(" ", ""),
        'cache-control': 'no-cache',
        'origin': 'https://debank.com',
        'pragma': 'no-cache',
        'referer': 'https://debank.com/',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'source': 'web',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'x-api-nonce': js_headers["nonce"],
        'x-api-sign': js_headers["signature"],
        'x-api-ts': str(js_headers["ts"]),
        'x-api-ver': js_headers["version"],
    }
    return headers
