import dataclasses
from rich.console import Console
import os
import sys


@dataclasses.dataclass
class ChatGPTConfig:
    
    model: str = "gpt-4-browsing"

    api_base: str = "https://api.openai.com/v1"

 
    openai_key = os.getenv("OPENAI_KEY", None)

    userAgent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
  
    cookie: str = os.getenv("CHATGPT_COOKIE", None)

    if openai_key is None:
        print("OPENAI_KEY sozlanmagan. Iltimos, uni muhit o'zgaruvchisiga o'rnating.")
    if cookie is None:
        print(
            "Sizning CHATGPT_COOKIE sozlanmagan. Iltimos, uni muhit o'zgaruvchisiga o'rnating."
        )

    error_wait_time: float = 20
    is_debugging: bool = False
    proxies: dict = dataclasses.field(
        default_factory=lambda: {
            "http": "",
            "https": "",
        }
    )
