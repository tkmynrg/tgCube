from utils.core import create_sessions
from utils.telegram import Accounts
from utils.cubes import Start
import asyncio
import argparse


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')
    action = parser.parse_args().action


    if action == 2:
        await create_sessions()

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []
        for thread, account in enumerate(accounts):
            tasks.append(asyncio.create_task(Start(account=account, thread=thread).main()))

        await asyncio.gather(*tasks)



if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
