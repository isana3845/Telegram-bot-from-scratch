import requests
from typing import Callable, Optional, Dict, Any

def get_file(id):
    if id:
        file_path = requests.get(f"https://api.telegram.org/bot8516970070:AAFm66YS2sSy4sYT11207msZraQlTLXRkac/getFile?file_id={id}").json()
        if file_path:
            print(file_path)
            file_name = file_path['result']['file_path'].split("/")[-1]
            response = requests.get(f"https://api.telegram.org/file/bot8516970070:AAFm66YS2sSy4sYT11207msZraQlTLXRkac/{file_path['result']['file_path']}")
            with open(file_name, "wb") as f:
                f.write(response.content)
            return response

print("/".join(["", "#21321"]).strip("/"))
#print(get_file("AgACAgIAAxkBAAICKGoFmnSm7s7KAAFOvNFzhLDzI86SYgACZhZrG7wYKUim0T_xQTFylgEAAwIAA3MAAzsE"))