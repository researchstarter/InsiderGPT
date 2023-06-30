import dataclasses
import re
import time
from typing import Any, Dict, List, Tuple
from uuid import uuid1
from insidergpt.config.chatgpt_config import ChatGPTConfig
import inspect

import loguru
import openai, tiktoken


logger = loguru.logger
logger.remove()
logger.add(level="WARNING", sink="logs/chatgpt.log")


@dataclasses.dataclass
class Message:
    ask_id: str = None
    ask: dict = None
    answer: dict = None
    answer_id: str = None
    request_start_timestamp: float = None
    request_end_timestamp: float = None
    time_escaped: float = None


@dataclasses.dataclass
class Conversation:
    conversation_id: str = None
    message_list: List[Message] = dataclasses.field(default_factory=list)

    def __hash__(self):
        return hash(self.conversation_id)

    def __eq__(self, other):
        if not isinstance(other, Conversation):
            return False
        return self.conversation_id == other.conversation_id


class ChatGPTAPI:
    def __init__(self, config: ChatGPTConfig):
        self.config = config
        openai.api_key = config.openai_key
        openai.proxy = config.proxies
        openai.api_base = config.api_base
        self.history_length = 5  
        self.conversation_dict: Dict[str, Conversation] = {}

    def count_token(self, messages) -> int:
       
        model = "gpt-3.5-turbo-0301"
        tokens_per_message = (
            4 
        )
        tokens_per_name = -1  
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3 
        return num_tokens

    def token_compression(self, complete_messages) -> str:
       
        if self.config.model == "gpt-4":
            token_limit = 8000
        else:
            token_limit = 4000
        if self.count_token(complete_messages) > token_limit:
            
            chat_message = [
                {
                    "role": "system",
                    "content": "Siz xabarlarni umumlashtirishga yordam beradigan yordamchisiz.",
                },
                {
                    "role": "user",
                    "content": "Tokenlarni saqlash uchun berilgan xabarning soʻz sonini kamaytiring. Katta til modeli tomonidan tushunilishi uchun uning asl ma'nosini saqlang.",
                },
            ]
            compressed_message = self.chatgpt_completion(chat_message)
            return compressed_message

        
        raw_message = complete_messages[-1]["content"]
        return raw_message

    def chatgpt_completion(
        self, history: List, model="gpt-3.5-turbo", temperature=0.5
    ) -> str:
        if self.config.model == "gpt-4":
            model = "gpt-4"
           
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=history,
                temperature=temperature,
            )
        except openai.error.APIConnectionError as e:  
            logger.warning(
                "API ulanish xatosi. {} soniya kutilmoqda".format(
                    self.config.error_wait_time
                )
            )
            logger.log("Connection Error: ", e)
            time.sleep(self.config.error_wait_time)
            response = openai.ChatCompletion.create(
                model=model,
                messages=history,
                temperature=temperature,
            )
        except openai.error.RateLimitError as e: 
            logger.warning(
                "Tarif limitiga yetdi. {} soniya kutilmoqda".format(
                    self.config.error_wait_time
                )
            )
            logger.error("Rate Limit Error: ", e)
            time.sleep(self.config.error_wait_time)
            response = openai.ChatCompletion.create(
                model=model,
                messages=history,
                temperature=temperature,
            )
        except openai.error.InvalidRequestError as e:  
            logger.warning("Token hajmi chegarasiga yetdi. Oxirgi xabar siqilgan")
            logger.error("Token hajmi xatosi; siqilgan xabar bilan qayta urinib ko'radi ", e)
           
            history[-1]["content"] = self.token_compression(history)
            
            if self.history_length > 2:
                self.history_length -= 1
           
            history = history[-self.history_length :]
            response = openai.ChatCompletion.create(
                model=model,
                messages=history,
                temperature=temperature,
            )

      
        if isinstance(response, tuple):
            logger.warning("Javob noto'g'ri. 5 soniya kuting")
            try:
                time.sleep(5)
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=history,
                    temperature=temperature,
                )
                if isinstance(response, tuple):
                    logger.error("Javob noto'g'ri. ")
                    raise Exception("Javob noto'g'ri. ")
            except Exception as e:
                logger.error("Javob noto'g'ri. ", e)
                raise Exception(
                    "Javob noto'g'ri. Eng mumkin bo'lgan sabab - OpenAI-ga ulanish barqaror emas. "
                    "Iltimos, “insidergpt-connection” bilan ikki marta tekshiring"
                )
        return response["choices"][0]["message"]["content"]

    def send_new_message(self, message):
      
        start_time = time.time()
        data = message
        history = [{"role": "user", "content": data}]
        message: Message = Message()
        message.ask_id = str(uuid1())
        message.ask = data
        message.request_start_timestamp = start_time
        response = self.chatgpt_completion(history)
        message.answer = response
        message.request_end_timestamp = time.time()
        message.time_escaped = (
            message.request_end_timestamp - message.request_start_timestamp
        )

      
        conversation_id = str(uuid1())
        conversation: Conversation = Conversation()
        conversation.conversation_id = conversation_id
        conversation.message_list.append(message)

        self.conversation_dict[conversation_id] = conversation
        print("Yangi suhbat." + conversation_id + " is created." + "\n")
        return response, conversation_id

    def send_message(self, message, conversation_id, debug_mode=False):
       
        chat_message = [
            {
                "role": "system",
                "content": "Siz inson sinovchilariga yuqori sifatli penetratsiya testini o'tkazishda yordam beruvchi foydali penetratsion tester yordamchisisiz.",
            },
        ]
        data = message
        conversation = self.conversation_dict[conversation_id]
        for message in conversation.message_list[-self.history_length :]:
            chat_message.extend(
                (
                    {"role": "user", "content": message.ask},
                    {"role": "assistant", "content": message.answer},
                )
            )
        
        chat_message.append({"role": "user", "content": data})
       
        message: Message = Message()
        message.ask_id = str(uuid1())
        message.ask = data
        message.request_start_timestamp = time.time()
       
        num_tokens = self.count_token(chat_message)
       
        response = self.chatgpt_completion(chat_message)

       
        message.answer = response
        message.request_end_timestamp = time.time()
        message.time_escaped = (
            message.request_end_timestamp - message.request_start_timestamp
        )
        conversation.message_list.append(message)
        self.conversation_dict[conversation_id] = conversation
        
        if debug_mode:
            print("Caller: ", inspect.stack()[1][3], "\n")
            print("Message:", message, "\n")
            print("Response:", response, "\n")
            print("Token cost of the conversation: ", num_tokens, "\n")
        return response

    def extract_code_fragments(self, text):
        return re.findall(r"```(.*?)```", text, re.DOTALL)

    def get_conversation_history(self):
       
        return

