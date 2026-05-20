# import aiohttp
# import asyncio
# import socket

# async def test():
#     connector = aiohttp.TCPConnector(family=socket.AF_INET)
#     async with aiohttp.ClientSession(connector=connector) as session:
#         try:
#             async with session.get("https://api.telegram.org") as resp:
#                 print("✅ Подключение работает!")
#                 print(await resp.text())
#         except Exception as e:
#             print(f"❌ Ошибка: {e}")

# asyncio.run(test())

import asyncio
import aiohttp
import socket

async def test():
    connector = aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get("https://api.telegram.org") as resp:
                print("✅ Подключение работает!")
                print(await resp.text())
        except Exception as e:
            print(f"❌ Ошибка: {e}")

asyncio.run(test())