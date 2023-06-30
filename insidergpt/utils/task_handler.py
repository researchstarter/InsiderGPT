from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import CompleteStyle, prompt


class localTaskCompleter(Completer):
    tasks = [
        "muhokama",
	"yechim",
	"yordam",
	"google",
	"davomi",
    ]

    task_meta = {
        "muhokama": HTML("Ushbu mahalliy vazifa haqida <b>InsiderGPT</b> bilan muhokama qiling."),
        "yechim": HTML(
            "<b>InsiderGPT</b>ga barcha mumkin bo'lgan yechimlar uchun mahalliy vazifa bo'yicha aqliy hujumga ruxsat bering."
        ),
        "yordam": HTML("Ushbu mahalliy vazifa uchun yordam sahifasini ko'rsating."),
        "google": HTML("Googleda qidiring."),
        "davomi": HTML("Mahalliy vazifadan chiqing va oldingi testni davom ettiring."),
    }

    task_details = """
Quyida mavjud vazifalar mavjud:
     - muhokama: InsiderGPT bilan ushbu mahalliy vazifani muhokama qilish.
     - yechim: InsiderGPT-ga barcha mumkin bo'lgan yechimlar uchun mahalliy vazifa bo'yicha miya hujumiga ruxsat berish.
     - yordam: Ushbu mahalliy vazifa uchun yordam sahifasini ko'rsatish.
     - google: Googleda qidirish.
     - chiqish: Mahalliy vazifadan chiqing va testni davom ettirish."""

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for task in self.tasks:
            if task.startswith(word):
                yield Completion(
                    task,
                    start_position=-len(word),
                    display=task,
                    display_meta=self.task_meta.get(task),
                )


class mainTaskCompleter(Completer):
    tasks = [
        "keyingisi",
        "ko'proq",
        "topshiriq",
        "muhokama",
        "google",
        "yordam",
        "chiqish",
    ]

    task_meta = {
        "keyingisi": HTML("Keyingi bosqichga o'tish."),
        "ko'proq": HTML("Vazifani batafsilroq tushuntirish."),
        "topshiriq": HTML("Vazifalar uchun <b>InsiderGPT</b>dan so'rash."),
        "muhokama": HTML("<b>InsiderGPT</b> bilan muhokama qilish."),
        "google": HTML("Googleda qidirish."),
        "yordam": HTML("Yordam sahifasini ko'rsatish."),
        "chiqish": HTML("Jarayonni tugatish."),
    }

    task_details = """
Quyida mavjud vazifalar mavjud:
  - keyingi: Test natijalarini kiritish orqali keyingi bosqichga o'tish.
  - ko'proq: Oldingi topshiriqni batafsilroq tushuntirish.
  - topshiriq: InsiderGPT-dan vazifalar ro'yxati va keyin nima qilish kerakligini so'rash.
  - muhokama qiling: InsiderGPT bilan muhokama qilish. Siz yordam so'rashingiz, vazifani muhokama qilishingiz yoki har qanday fikr-mulohazalarni bildirishingiz mumkin.
  - google: Savolingizni Google orqali qidirish. Natijalar Google tomonidan avtomatik ravishda tahlil qilinadi.
  - yordam: Ushbu yordam sahifasini ko'rsatish.
  - chiqish: joriy seansni tugatish."""

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for task in self.tasks:
            if task.startswith(word):
                yield Completion(
                    task,
                    start_position=-len(word),
                    display=task,
                    display_meta=self.task_meta.get(task),
                )


def main_task_entry(text="> "):
 
    task_completer = mainTaskCompleter()
    while True:
        result = prompt(text, completer=task_completer)
        if result not in task_completer.tasks:
            print("Vazifa noto‘g‘ri, qayta urinib ko‘ring.")
        else:
            return result


def local_task_entry(text="> "):
  
    task_completer = localTaskCompleter()
    while True:
        result = prompt(text, completer=task_completer)
        if result not in task_completer.tasks:
            print("Vazifa noto‘g‘ri, qayta urinib ko‘ring.")
        else:
            return result


if __name__ == "__main__":
    main_task_entry()
