from insidergpt.config.chatgpt_config import ChatGPTConfig
from rich.spinner import Spinner
from insidergpt.utils.chatgpt import ChatGPT
from insidergpt.utils.chatgpt_api import ChatGPTAPI
from rich.console import Console
from insidergpt.prompts.prompt_class import InsiderGPTPrompt
from insidergpt.utils.prompt_select import prompt_select, prompt_ask
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import confirm
from insidergpt.utils.task_handler import (
    main_task_entry,
    mainTaskCompleter,
    local_task_entry,
    localTaskCompleter,
)
from insidergpt.utils.web_parser import google_search, parse_web
import time
import datetime as dt

import loguru
import time, os, textwrap, json, sys, traceback

logger = loguru.logger
logger.add(sink="logs/insider_gpt.log")


def prompt_continuation(width, line_number, wrap_count):

    if wrap_count > 0:
        return " " * (width - 3) + "-> "
    text = ("- %i - " % (line_number + 1)).rjust(width)
    return HTML("<strong>%s</strong>") % text


class insiderGPT:
    postfix_options = {
        "tool": "Kirish mazmuni xavfsizlikni tekshirish vositasidan olingan. Sizni qiziqtirgan barcha fikrlarni sanab o'tishingiz kerak; Qo‘shimcha yo‘l-yo‘riq olish uchun yuqori darajali penetratsion testerga hisobot berayotgandek xulosa qilishingiz kerak.\n",
        "user-comments": "Kiritilgan kontent foydalanuvchi izohlaridan olingan.\n",
        "web": "Kiritilgan tarkib veb-sahifalardan olingan. Siz oʻqilishi mumkin boʻlgan tarkibni umumlashtirishingiz va kirish testi uchun qiziqarli boʻlishi mumkin boʻlgan barcha fikrlarni sanab oʻtishingiz kerak.\n",
        "default": "Foydalanuvchi kirish manbasini aniqlamadi. Tarkibga asoslanib xulosa qilishingiz kerak.\n",
    }

    def __init__(
        self, reasoning_model="gpt-4", useAPI=True, baseUrl="https://api.openai.com/v1"
    ):
        self.log_dir = "logs"
        self.save_dir = "test_history"
        self.task_log = (
            {}
        )  
        self.useAPI = useAPI
        self.baseUrl = baseUrl
        if useAPI is False:
            self.chatGPTAgent = ChatGPT(ChatGPTConfig())
            self.chatGPT4Agent = ChatGPT(ChatGPTConfig(model=reasoning_model))
        else:
            self.chatGPTAgent = ChatGPTAPI(ChatGPTConfig())
            self.chatGPT4Agent = ChatGPTAPI(
                ChatGPTConfig(model=reasoning_model, api_base=baseUrl)
            )
        self.prompts = InsiderGPTPrompt
        self.console = Console()
        self.spinner = Spinner("line", "Tahlil")
        self.test_generation_session_id = None
        self.test_reasoning_session_id = None
        self.input_parsing_session_id = None
        self.chat_count = 0
        self.step_reasoning = (
            None  
        )
        self.history = {
            "user": [],
            "insiderGPT": [],
            "reasoning": [],
            "input_parsing": [],
            "generation": [],
            "exception": [],
        }  

    def log_conversation(self, source, text):
       
        timestamp = time.time()
        if source not in self.history.keys():
            # an exception
            source = "exception"
        self.history[source].append((timestamp, text))

    def refresh_session(self):
        if self.useAPI:
            self.console.print(
                "Siz API rejimidan foydalanmoqdasiz, shuning uchun sessiyani yangilash shart emas."
            )
            self.log_conversation(
                "insiderGPT",
                "Siz API rejimidan foydalanmoqdasiz, shuning uchun sessiyani yangilash shart emas.",
            )
        else:
            self.console.print(
                "Curl buyrug'ini `config/chatgpt_config_curl.txt' ichiga qo'yganingizga ishonch hosil qiling.",
                style="bold green",
            )
            self.log_conversation(
                "insiderGPT",
                "Iltimos, curl buyrug'ini `config/chatgpt_config_curl.txt' ichiga qo'yganingizga ishonch hosil qiling.",
            )
            input("Davom etish uchun Enter tugmasini bosing...")
            self.chatGPTAgent.refresh()
            self.chatGPT4Agent.refresh()
            self.console.print(
                "Jarayon yangilandi. Agar bir xil jarayonni yangilash soʻrovini olsangiz, iltimos, ChatGPT sahifasini yangilang va yangi curl soʻrovini qayta joylashtiring.",
                style="bold green",
            )
            self.log_conversation("insiderGPT", "Jarayon yangilandi")
            return "Jarayon yangilandi"

    def _feed_init_prompts(self):

        init_description = prompt_ask(
            "Iltimos, kirish testi topshirigʻini bir qatorda tasvirlab bering, jumladan maqsadli IP, vazifa turi va hokazo.\n>",
            multiline=False,
        )
        self.log_conversation("user", init_description)
        self.task_log["task description"] = init_description
       
        prefixed_init_description = self.prompts.task_description + init_description
        with self.console.status(
            "[bold green] Vazifa maʼlumotlari yaratilmoqda..."
        ) as status:
            _response = self.reasoning_handler(prefixed_init_description)
            print("debug: ", _response)
        self.console.print("- Vazifa ma'lumotlari yaratildi. \n", style="bold green")
       
        with self.console.status("[bold green]Qayta ishlash...") as status:
            first_generation_response = self.test_generation_handler(
                self.prompts.first_todo + _response
            )

        self.console.print(
            "InsiderGPT sizga quyidagilarni qilishni taklif qiladi:", style="bold green"
        )
        self.console.print(_response)
        self.log_conversation(
            "InsiderGPT", "InsiderGPT sizga quyidagilarni qilishni taklif qiladi:" + _response
        )
        self.console.print("Topshiriq ketma-ketligi:", style="bold green")
        self.console.print(first_generation_response)
        self.log_conversation(
            "InsiderGPT", "Topshiriq ketma-ketligi:" + first_generation_response
        )

    def initialize(self, previous_session_ids=None):
        if (
            previous_session_ids is not None and self.useAPI is False
        ): 
            self.test_generation_session_id = previous_session_ids.get(
                "test_generation", None
            )
            self.test_reasoning_session_id = previous_session_ids.get("reasoning", None)
            self.input_parsing_session_id = previous_session_ids.get("parsing", None)
           
           
            self.task_log = previous_session_ids.get("task_log", {})
            self.console.print(f"Task log: {str(self.task_log)}", style="bold green")
            print("Vazifani eslatish uchun munozara funksiyasidan foydalanishingiz mumkin.")

            
            if (
                self.test_generation_session_id is None
                or self.test_reasoning_session_id is None
                or self.input_parsing_session_id is None
            ):
                self.console.print(
                    "[bold red] Xato: oldingi seans identifikatorlari yaroqsiz. Yangi seanslar yuklanmoqda"
                )
                self.initialize()

        else:
            with self.console.status(
                "[bold green] ChatGPT seanslarini ishga tushirish..."
            ) as status:
                try:
                    (
                        text_0,
                        self.test_generation_session_id,
                    ) = self.chatGPTAgent.send_new_message(
                        self.prompts.generation_session_init,
                    )
                    (
                        text_1,
                        self.test_reasoning_session_id,
                    ) = self.chatGPT4Agent.send_new_message(
                        self.prompts.reasoning_session_init
                    )
                    (
                        text_2,
                        self.input_parsing_session_id,
                    ) = self.chatGPTAgent.send_new_message(
                        self.prompts.input_parsing_init
                    )
                except Exception as e:
                    logger.error(e)
            self.console.print("- ChatGPT Sessions Initialized.", style="bold green")
            self._feed_init_prompts()

    def reasoning_handler(self, text) -> str:
        
        if len(text) > 8000:
            text = self.input_parsing_handler(text)
        
        response = self.chatGPT4Agent.send_message(
            self.prompts.process_results + text, self.test_reasoning_session_id
        )
        
        self.log_conversation("reasoning", response)
        return response

    def input_parsing_handler(self, text, source=None) -> str:
        prefix = "Iltimos, quyidagi kiritishni umumlashtiring. "

        if source is not None and source in self.postfix_options.keys():
            prefix += self.postfix_options[source]
        text = text.replace("\r", " ").replace("\n", " ")

        wrapped_text = textwrap.fill(text, 8000)
        wrapped_inputs = wrapped_text.split("\n")
        
        summarized_content = ""
        for wrapped_input in wrapped_inputs:
            word_limit = f"Kirish {8000/len(wrapped_inputs)} soʻzdan kam boʻlishiga ishonch hosil qiling.\n"
            summarized_content += self.chatGPTAgent.send_message(
                prefix + word_limit + wrapped_input, self.input_parsing_session_id
            )
        
        self.log_conversation("input_parsing", summarized_content)
        return summarized_content

    def test_generation_handler(self, text):
        
        response = self.chatGPTAgent.send_message(text, self.test_generation_session_id)
        
        self.log_conversation("generation", response)
        return response

    def local_input_handler(self) -> str:
       
        local_task_response = ""
        self.chat_count += 1
        local_request_option = local_task_entry()
        self.log_conversation("user", local_request_option)

        if local_request_option == "help":
            print(localTaskCompleter().task_details)

        elif local_request_option == "discuss":
            
            self.console.print(
                "Iltimos, topilmalar va savollaringizni InsiderGPT bilan baham ko'ring."
            )
            self.log_conversation(
                "insiderGPT",
                "Iltimos, topilmalar va savollaringizni InsiderGPT bilan baham ko'ring. (<shift + o'ngga strelka> bilan tugating)",
            )
            user_input = prompt_ask("Sizning kiritishingiz: ", multiline=True)
            self.log_conversation("user", user_input)

            with self.console.status("[bold green] InsiderGPT o'ylayapti...") as status:
                local_task_response = self.test_generation_handler(
                    self.prompts.local_task_prefix + user_input
                )

            self.console.print("InsiderGPT:\n", style="bold green")
            self.console.print(local_task_response + "\n", style="yellow")
            self.log_conversation("insiderGPT", local_task_response)

        elif local_request_option == "brainstorm":

            self.console.print(
                "Iltimos, savollaringizni InsiderGPT bilan baham ko'ring."
            )
            self.log_conversation(
                "insiderGPT",
                "Iltimos, tashvish va savollaringizni InsiderGPT bilan baham ko'ring. <shift + o'ngga strelka> bilan tugating)",
            )
            user_input = prompt_ask("Sizning kiritishingiz: ", multiline=True)
            self.log_conversation("user", user_input)
            
            with self.console.status("[bold green] InsiderGPT o'ylayapti...") as status:
                local_task_response = self.test_generation_handler(
                    self.prompts.local_task_brainstorm + user_input
                )
         
            self.console.print("InsiderGPT:\n", style="bold green")
            self.console.print(local_task_response + "\n", style="yellow")
            self.log_conversation("insiderGPT", local_task_response)

        elif local_request_option == "google":
            
            self.console.print(
                "Iltimos, qidiruv so'rovingizni kiriting. InsiderGPT Google ma'lumotlarini umumlashtiradi. (<shift + o'ngga strelka> bilan tugating)",
                style="bold green",
            )
            self.log_conversation(
                "insiderGPT",
                "Iltimos, qidiruv so'rovingizni kiriting. InsiderGPT Google ma'lumotlarini umumlashtiradi.",
            )
            user_input = prompt_ask("Sizning kiritishingiz: ", multiline=False)
            self.log_conversation("user", user_input)
            with self.console.status("[bold green] InsiderGPT o'ylayapti...") as status:
                
                result: dict = google_search(user_input, 5)  # 5 results by default
               
                local_task_response = (
                    "Google qidiruv natijalari:\n" + "hali ishlab chiqilmoqda."
                )
            self.console.print(local_task_response + "\n", style="yellow")
            self.log_conversation("insiderGPT", local_task_response)
            return local_task_response

        elif local_request_option == "continue":
            self.console.print("Mahalliy vazifadan chiqing va asosiy vazifani davom ettiring.")
            self.log_conversation(
                "insiderGPT", "Mahalliy vazifadan chiqing va asosiy vazifani davom ettiring."
            )
            local_task_response = "continue"

        return local_task_response

    def input_handler(self) -> str:
      
        self.chat_count += 1

        request_option = main_task_entry()
        self.log_conversation("user", request_option)
       
        if not self.useAPI:
            conversation_history = self.chatGPTAgent.get_conversation_history()
            while conversation_history is None:
                self.refresh_session()
                conversation_history = self.chatGPTAgent.get_conversation_history()

        if request_option == "help":
            print(mainTaskCompleter().task_details)

        if request_option == "next":
          
            options = list(self.postfix_options.keys())
            value_list = [
                (i, HTML(f'<style fg="cyan">{options[i]}</style>'))
                for i in range(len(options))
            ]
            source = prompt_select(
                title="Iltimos, ma'lumot manbasini tanlang.", values=value_list
            )
            self.console.print(
                "Sizning kiritishingiz: (<shift + right-arrow>) bilan tugating", style="bold green"
            )
            user_input = prompt_ask("> ", multiline=True)
            self.log_conversation(
                "user", f"Manba: {options[int(source)]}" + "\n" + user_input
            )
            with self.console.status("[bold green] InsiderGPT o'yalayapti...") as status:
                parsed_input = self.input_parsing_handler(
                    user_input, source=options[int(source)]
                )
                
                reasoning_response = self.reasoning_handler(parsed_input)
                self.step_reasoning_response = reasoning_response

            
            self.console.print(
                "Tahlil asosida quyidagi vazifalar tavsiya etiladi:",
                style="bold green",
            )
            self.console.print(reasoning_response + "\n")
            self.log_conversation(
                "insiderGPT",
                "Tahlil asosida quyidagi vazifalar tavsiya etiladi:"
                + reasoning_response,
            )
            response = reasoning_response

        elif request_option == "more":
            self.log_conversation("user", "more")
            
            if not hasattr(self, "step_reasoning_response"):
                self.console.print(
                    "Siz hali vazifani ishga tushirmadingiz. Iltimos, “keyingi” opsiyadan keyin asosiy testni bajaring.",
                    style="bold red",
                )
                response = "Siz hali vazifani ishga tushirmadingiz. Iltimos, “keyingi” opsiyadan keyin asosiy testni bajaring."
                self.log_conversation("insiderGPT", response)
                return response
           
            self.console.print(
                "InsiderGPT will generate more test details, and enter the sub-task generation mode. (Pressing Enter to continue)",
                style="bold green",
            )
            self.log_conversation(
                "insiderGPT",
                "InsiderGPT qo'shimcha test ma'lumotlarini ishlab chiqaradi va pastki vazifalarni yaratish rejimiga kiradi.",
            )
            input()

            
            with self.console.status("[bold green] InsiderGPT o'ylayapti...") as status:
                generation_response = self.test_generation_handler(
                    self.step_reasoning_response
                )
                _local_init_response = self.test_generation_handler(
                    self.prompts.local_task_init
                )

            self.console.print(
                "Quyida batafsil ma'lumotlar keltirilgan.",
                style="bold green",
            )
            self.console.print(generation_response + "\n")
            response = generation_response
            self.log_conversation("insiderGPT", response)

     
            while True:
                local_task_response = self.local_input_handler()
                if local_task_response == "continue":
           
                    break

        elif request_option == "todo":
            
            self.log_conversation("user", "todo")
            
            with self.console.status("[bold green] InsiderGPT o'ylayapti...") as status:
                reasoning_response = self.reasoning_handler(self.prompts.ask_todo)
               
                message = self.prompts.todo_to_command + "\n" + reasoning_response
                generation_response = self.test_generation_handler(message)
                
            self.console.print(
                "Tahlil asosida quyidagi vazifalar tavsiya etiladi:",
                style="bold green",
            )
            self.console.print(reasoning_response + "\n")
            self.console.print(
                "Vazifalarni bajarish uchun quyidagi ko'rsatmalarga amal qilishingiz mumkin.",
                style="bold green",
            )
            self.console.print(generation_response + "\n")
            response = reasoning_response
            self.log_conversation(
                "insiderGPT",
                (
                    (
                        (
                            (
                                "Vazifalarni bajarish uchun quyidagi ko'rsatmalarga amal qilishingiz mumkin:"
                                + response
                            )
                            + "\n"
                        )
                        + "Vazifalarni bajarish uchun quyidagi ko'rsatmalarga amal qilishingiz mumkin."
                    )
                    + generation_response
                ),
            )
        elif request_option == "discuss":
            
            self.console.print(
                "Iltimos, InsiderGPT bilan o'z fikrlaringiz/savollaringiz bilan o'rtoqlashing. (<shift + o'ngga strelka> bilan tugating)"
            )
            self.log_conversation(
                "insiderGPT", "Iltimos, InsiderGPT bilan o'z fikrlaringiz/savollaringiz bilan o'rtoqlashing."
            )
            user_input = prompt_ask("Sizning kiritishingiz: ", multiline=True)
            self.log_conversation("user", user_input)

            with self.console.status("[bold green] InsiderGPT o'ylayapti...") as status:
                response = self.reasoning_handler(self.prompts.discussion + user_input)
           
           
            self.console.print("InsiderGPT:\n", style="bold green")
            self.console.print(response + "\n", style="yellow")
            self.log_conversation("insiderGPT", response)

        elif request_option == "google":

            self.console.print(
                "Iltimos, qidiruv so'rovingizni kiriting. InsiderGPT Google ma'lumotlarini umumlashtiradi. (<shift + o'ngga strelka> bilan tugating)",
                style="bold green",
            )
            self.log_conversation(
                "insiderGPT",
                "Iltimos, qidiruv so'rovingizni kiriting. InsiderGPT Google ma'lumotlarini umumlashtiradi.",
            )
            user_input = prompt_ask("Sizning kiritishingiz: ", multiline=False)
            self.log_conversation("user", user_input)
            with self.console.status("[bold green] InsiderGPT o'ylayapti...") as status:
            
                result: dict = google_search(user_input, 5)  
              
                response = "Google search natijalari:\n" + "still under development."
            self.console.print(response + "\n", style="yellow")
            self.log_conversation("insiderGPT", response)
            return response

        elif request_option == "quit":
            response = False
            self.console.print("InsiderGPT dan foydalanganingiz uchun tashakkur!", style="bold green")
            self.log_conversation("insiderGPT", "InsiderGPT dan foydalanganingiz uchun tashakkur!")

        else:
            self.console.print("Iltimos, to'g'ri variantlarni kiriting.", style="bold red")
            self.log_conversation("insiderGPT", "Iltimos, to'g'ri variantlarni kiriting.")
            response = "Iltimos, to'g'ri variantlarni kiriting."
        return response

    def save_session(self):
     
        self.console.print(
            "Chiqishdan oldin jarayonni saqlashingiz mumkin.",
            style="bold green",
        )
        
        save_name = prompt_ask(
            "Iltimos, joriy seans nomini kiriting. (Joriy vaqt tamg‘asi bilan birlamchi)\n>",
            multiline=False,
        )
        if save_name == "":
            save_name = str(time.time())
       
        with open(os.path.join(self.save_dir, save_name), "w") as f:
          
            session_ids = {
                "reasoning": self.test_reasoning_session_id,
                "test_generation": self.test_generation_session_id,
                "parsing": self.input_parsing_session_id,
                "task_log": self.task_log,
            }
            json.dump(session_ids, f)
        self.console.print(
            f"Joriy seans {save_name} sifatida saqlangan", style="bold green"
        )
        return

    def _preload_session(self) -> dict:
        
        if continue_from_previous := confirm(
            "Oldingi jarayonni davom ettirmoqchimisiz?"
        ):
            
            filenames = os.listdir(self.save_dir)
            if len(filenames) == 0:
                print("Avvalgi jarayon topilmadi. Iltimos, yangi seansni boshlang.")
                return None
            else:
                print("Iltimos, avvalgi jarayonni indeks (butun son) bo'yicha tanlang:")
                for i, filename in enumerate(filenames):
                    print(f"{str(i)}. {filename}")
             
                try:
                    previous_testing_name = filenames[
                        int(input("Iltimos, variantingizni kiriting (butun son): "))
                    ]
                    print(f"Siz tanladingiz: {previous_testing_name}")
                except ValueError as e:
                    print("Siz yaroqsiz variantni kiritdingiz. Yangi sessiya boshlanadi.")
                    return None

        elif continue_from_previous is False:
            return None
        else:
            print("Siz yaroqsiz variantni kiritdingiz. Yangi jarayon boshlanadi.")
            return None
        
        if previous_testing_name is not None:
            try:
                with open(os.path.join(self.save_dir, previous_testing_name), "r") as f:
                    return json.load(f)
            except Exception as e:
                print(
                    "Oldingi seansni yuklashda xatolik yuz berdi. Fayl nomi noto'g'ri"
                )
                print(e)
                previous_testing_name = None
                return None

    def main(self):
       
      
        loaded_ids = self._preload_session()
        self.initialize(previous_session_ids=loaded_ids)

        
        while True:
            try:
                result = self.input_handler()
                self.console.print(
                    "-----------------------------------------", style="bold white"
                )
                if not result:  
                    break
            except Exception as e:  
               
                self.log_conversation("exception", str(e))
              
                self.console.print(f"Exception: {str(e)}", style="bold red")
              
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.console.print(
                    "Istisno tafsilotlari quyida keltirilgan. Siz github-da muammoni yuborishingiz va xato izini joylashtirishingiz mumkin",
                    style="bold green",
                )
                
                print(traceback.format_exc())
               
                break
   
        timestamp = time.time()
        log_name = f"insiderGPT_log_{str(timestamp)}.txt"
        # save it in the logs folder
        log_path = os.path.join(self.log_dir, log_name)
        with open(log_path, "w") as f:
            json.dump(self.history, f)

        
        self.save_session()
