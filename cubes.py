import random
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
import asyncio
from urllib.parse import unquote
from data import config
import aiohttp
from fake_useragent import UserAgent


class Start:
    def __init__(self, thread: int, account: str):
        self.thread = thread
        self.client = Client(name=account, api_id=config.API_ID, api_hash=config.API_HASH, workdir=config.WORKDIR)

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True)

        self.token = None

    async def main(self):
        while True:
            try:
                await asyncio.sleep(random.uniform(config.ACC_DELAY[0], config.ACC_DELAY[1]))

                tg_web_data = await self.get_tg_web_data()
                balance, energy = await self.login(tg_web_data)

                while True:
                    if energy > 150:
                        balance, energy, boxes, block = await self.mining()

                        logger.success(f"Поток {self.thread} | Сломал блок {block}! Баланс: {balance}; Энергия: {energy}; Боксы: {boxes}")
                        await asyncio.sleep(random.uniform(config.MINING_DELAY[0], config.MINING_DELAY[1]))

                    elif energy <= 150 and balance >= 50:
                        balance, energy, energy_buy = await self.buy_energy(balance)
                        logger.success(f"Поток {self.thread} | Купил {energy_buy} энергии!")

                    else:
                        logger.warning(f"Поток {self.thread} | Кол-во энергии меньше 150, поток спит!")
                        await asyncio.sleep(random.uniform(config.MINING_DELAY[0], config.MINING_DELAY[1]))
                        balance, energy = await self.login(tg_web_data)

            except Exception as e:
                logger.error(f"Поток {self.thread} | Ошибка: {e}")

    async def get_tg_web_data(self):
        await self.client.connect()

        await self.client.send_message(chat_id="cubesonthewater_bot", text="/start NjAwODIzOTE4Mg==")
        await asyncio.sleep(random.uniform(config.MINING_DELAY[0], config.MINING_DELAY[1]))

        web_view = await self.client.invoke(RequestWebView(
            peer=await self.client.resolve_peer('cubesonthewater_bot'),
            bot=await self.client.resolve_peer('cubesonthewater_bot'),
            platform='android',
            from_bot_menu=False,
            url='https://www.thecubes.xyz'
        ))
        auth_url = web_view.url
        await self.client.disconnect()
        return unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))

    async def login(self, tg_web_data):
        json_data = {"initData": tg_web_data}
        resp = await self.session.post("https://server.questioncube.xyz/auth", json=json_data)

        resp_json = await resp.json()
        self.token = resp_json.get("token")

        return int(resp_json.get("drops_amount")), int(resp_json.get("energy"))

    async def mining(self):
        while True:
            resp = await self.session.post("https://server.questioncube.xyz/game/mined", json={"token": self.token})
            try:
                resp_json = await resp.json()
                return int(resp_json.get("drops_amount")), int(resp_json.get("energy")), int(resp_json.get("boxes_amount")), int(resp_json.get("mined_count"))

            except: await asyncio.sleep(random.uniform(config.MINING_DELAY[0]+5, config.MINING_DELAY[1]+5))

    async def buy_energy(self, balance: int):
        if balance >= 250:
            proposal_id = 3
            energy_buy = 500
        elif 250 > balance >= 125:
            proposal_id = 2
            energy_buy = 250
        elif 125 > balance >= 50:
            proposal_id = 1
            energy_buy = 100

        json_data = {"proposal_id": proposal_id, "token": self.token}

        resp = await self.session.post("https://server.questioncube.xyz/game/rest-proposal/buy", json=json_data)
        resp_json = await resp.json()
        return int(resp_json.get("drops_amount")), int(resp_json.get("energy")), energy_buy

