import loguru
import sys

from insidergpt.utils.chatgpt import ChatGPT
from insidergpt.utils.chatgpt_api import ChatGPTAPI
from insidergpt.config.chatgpt_config import ChatGPTConfig
import openai
import argparse

from rich.console import Console

logger = loguru.logger
logger.add(level="ERROR", sink="logs/chatgpt_connection_test.log")


def main():
    parser = argparse.ArgumentParser(description="InsiderGPTTestConnection")
    parser.add_argument(
        "--baseUrl",
        type=str,
        default="https://api.openai.com/v1",
        help="OpenAI API uchun asosiy URL: https://api.openai.com/v1",
    )

    args = parser.parse_args()

    chatgpt_config = ChatGPTConfig(api_base=args.baseUrl)
    console = Console()

    
    print("#### Chatgpt cookie fayli uchun ulanishni sinab ko'ring")
    try:
        chatgpt = ChatGPT(chatgpt_config)
        conversations = chatgpt.get_conversation_history()
        if conversations is not None:
            console.print(
                "1. Siz ChatGPT Plus cookie-fayliga ulangansiz. \nInsiderGPT-ni ishga tushirish uchun <insidergpt --reaning_model=gpt-4> dan foydalaning.",
                style="bold green",
            )
        else:
            console.print(
                "Cookie ChatGPT Cookie bilan to'g'ri sozlanmagan. “CHATGPT_COOKIE”ni eksport qilish=<cookie-faylingiz>` orqali cookie-faylni yangilash uchun README-ga rioya qiling",
                style="bold red",
            )
    except Exception as e: 
        logger.error(e)
        print(
            "Cookie to'g'ri sozlanmagan. Config/chatgpt_config.py sahifasida cookie-faylni yangilash uchun README-ga rioya qiling"
        )

    
    print("#### OpenAI api (GPT-4) uchun sinov ulanishi")
    try:
        chatgpt_config.model = "gpt-4"
        chatgpt = ChatGPTAPI(chatgpt_config)
        openai.api_key = chatgpt_config.openai_key
        result, conversation_id = chatgpt.send_new_message("Salom, qalaysiz?")
        console.print(
            "2. Siz OpenAI API bilan ulangansiz. Sizda GPT-4 ruxsati bor. InsiderGPT-ni ishga tushirish uchun <insidergpt --reaning_model=gpt-4 --useAPI> dan foydalaning.",
            style="bold green",
        )
    except Exception as e:  
        console.print(
            "OpenAI API kaliti toʻgʻri sozlanmagan. OpenAI API kalitini `export OPENAI_KEY=<>` orqali yangilash uchun README-ga amal qiling.",
            style="bold red",
        )
        print("Xato quyida:", e)

   
    print("#### OpenAI api (GPT-3.5) uchun sinov ulanishi")
    try:
        chatgpt_config.model = "gpt-3.5-turbo"
        chatgpt = ChatGPTAPI(chatgpt_config)
        openai.api_key = chatgpt_config.openai_key
        result, conversation_id = chatgpt.send_new_message("Salom, qalaysiz?")
        console.print(
            "3. Siz OpenAI API bilan ulangansiz. Sizda GPT-3.5 kirish huquqi bor. InsiderGPT-ni ishga tushirish uchun <insidergpt --reaning_model=gpt-3.5-turbo --useAPI> dan foydalaning.",
            style="bold green",
        )
    except Exception as e:  
        logger.error(e)
        console.print(
            "OpenAI API kaliti toʻgʻri sozlanmagan. OpenAI API kalitini `export OPENAI_KEY=<>` orqali yangilash uchun README-ga amal qiling.",
            style="bold red",
        )
        print("Xato quyida:", e)


if __name__ == "__main__":
    main()
