# import aiohttp
# import asyncio
# import socket

# async def test():
#     connector = aiohttp.TCPConnector(family=socket.AF_INET)
#     async with aiohttp.ClientSession(connector=connector) as session:
#         try:
#             async with session.get("https://api.telegram.org") as resp:
#                 print("Подключение работает")
#                 print(await resp.text())
#         except Exception as e:
#             print(f"Ошибка: {e}")

# asyncio.run(test())

# import asyncio
# import aiohttp
# import socket

# async def test():
#     connector = aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)
#     async with aiohttp.ClientSession(connector=connector) as session:
#         try:
#             async with session.get("https://api.telegram.org") as resp:
#                 print("Подключение")
#                 print(await resp.text())
#         except Exception as e:
#             print(f"Ошибка: {e}")

# asyncio.run(test())

import aiohttp
import asyncio

async def test():
    # Попробуй без прокси
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.telegram.org") as resp:
                print("Без прокси")
                return
    except:
        print("Без прокси не работает")
    
    proxies = [
        "http://127.0.0.1:10808",
        "socks5://127.0.0.1:10808", 
        "http://127.0.0.1:10809",
    ]
    
    for proxy in proxies:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.telegram.org", proxy=proxy) as resp:
                    print(f"прокси {proxy} работает!")
                    return
        except:
            print(f"прокси {proxy} не работает")

asyncio.run(test())