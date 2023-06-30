
import json
import re
import time
from uuid import uuid1
import datetime
from chatgpt_wrapper import OpenAIAPI

import loguru
import requests

from chatgpt_wrapper import ChatGPT
from insidergpt.config.chatgpt_config import ChatGPTConfig

logger = loguru.logger


class ChatGPTBrowser:
  

    def __init__(self, model=None):
        config = ChatGPTConfig()
        if model is not None:
            config.set("chat.model", model)
        self.bot = ChatGPT(config)

    def get_authorization(self):
       
        return

    def get_latest_message_id(self, conversation_id):
        
        return

    def get_conversation_history(self, limit=20, offset=0):
        
        return self.bot.get_history(limit, offset)

    def send_new_message(self, message):
        
        response = self.bot.ask(message)
        latest_uuid = self.get_conversation_history(limit=1, offset=0).keys()[0]
        return response, latest_uuid

    def send_message(self, message, conversation_id):
       
        return

    def extract_code_fragments(self, text):
        return re.findall(r"```(.*?)```", text, re.DOTALL)

    def delete_conversation(self, conversation_id=None):
        # delete conversation with its uuid
        if conversation_id is not None:
            self.bot.delete_conversation(conversation_id)



