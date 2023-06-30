<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/GreyDGL/InsiderGPT">
  </a>

<h3 align="center">InsiderGPT</h3>

  <p align="center">
    GPT asosidagi xavfsizlikni tekshirish vositasi. 
    <br />
    ·
    <a href="https://www.youtube.com/watch?v=lAjLIj1JT3c">View Demo</a>
    
    </p>
</div>




<!-- Umumiy savollar -->
## Umumiy savollar
- **Q**: InsiderGPT nima?
  - **A**: InsiderGPT - bu ChatGPT modeliga assoslangan xavfsizlikni tekshirish vositasi. U penetratsion test jarayonini avtomatlashtirish uchun mo'ljallangan. U ChatGPT asosida qurilgan, maxsus operatsiyalarda ham penetratsiya testerlarini boshqarish uchun interaktiv rejimda ishlaydi.
- **Q**: InsiderGPT-dan foydalanish uchun ChatGPT plus a'zosi bo'lishim kerakmi?
  - **A**: ChatGPT plus yoki GPT-4 API dan foydalanish tavsiya etiladi. InsiderGPT yuqori sifatli fikr yuritish uchun GPT-4 modeliga tayanadi. Agar sizda ruxsat bo'lsa, GPT-4 API to'g'ridan-to'g'ri foydalanishingiz mumkin.
- **Q**: Nima uchun GPT-4?
  - **A**: GPT-4 ning penetratsion testlarni o'ylash nuqtai nazaridan GPT-3.5 dan yaxshiroq ishlashini aniqladik. 
- **Q**: Nega faqat GPT-4 dan to'g'ridan-to'g'ri foydalanmaslik kerak?
  - **A**: Biz GPT-4 kontekstni yo'qotishdan aziyat chekishini aniqladik, chunki test chuqurroq bo'ladi. Ushbu jarayonda "sinov holati haqida xabardorlikni" saqlab qolish juda muhimdir.

    
<!-- Kirish -->
## Kirish
- **InsiderGPT** bu **ChatGPT** tomonidan quvvatlangan xavfsizlikni tekshirish vositasi. 
- U penetratsion test jarayonini avtomatlashtirish uchun mo'ljallangan. U ChatGPT-ning tepasida qurilgan va umumiy rivojlanishda ham, maxsus operatsiyalarda ham penetratsiya testerlarini boshqarish uchun interaktiv rejimda ishlaydi.



### O'rnatish
**InsiderGPT** joriy versiyasi **ChatGPT** va **OpenAI API** ning backendini qo‘llab-quvvatlaydi. Siz ulardan birini ishlatishingiz mumkin. 
Barqarorlik va ishlash uchun OpenAI API dan foydalanish tavsiya etiladi. 

1. `pip3 install .` bilan so'nggi versiyani o'rnating
2. Agar siz **ChatGPT** dan backend sifatida foydalanishga qaror qilsangiz
   - ChatGPT seansiga kirish uchun cookie faylini oling
   ```
   $ insidergpt-cookie
   export CHATGPT_COOKIE='<cookie bu yerda>`
   ```
   - Oldingi buyruqdan nusxa oling va uni terminalda ishga tushiring (`export CHATGPT_COOKIE='<cookieni shu yerga qo'ying>'`)
   - “Insidergpt-connection” yordamida ulanishni sinab ko'ring
   - Dasturni “insidergpt” buyrug'i bilan ishga tushiring
3. OpenAI API dan foydalanish uchun
   - API kalitingizni `export OPENAI_KEY='<kalitingiz shu yerda>'` bilan eksport qiling
   - “Insidergpt-connection” yordamida ulanishni sinab ko'ring
4. Ulanish to'g'ri sozlanganligini tekshirish uchun "insidergpt-connection" ni ishga tushirishingiz mumkin. Biroz vaqt o'tgach, siz ChatGPT bilan suhbat namunasini ko'rishingiz kerak. 
5. ChatGPT cookie-fayllari yechimi juda beqaror bo'lishi mumkin. Biz doimo yaxshiroq yechim ustida ishlayapmiz. Agar sizda biron bir fikr bo'lsa yoki biron bir muammoga duch kelsangiz, biz bilan bog'laning.

<!-- Foydalanish -->

## Foydalanish
1. Boshlash uchun "insidergpt --args" ni ishga tushiring.
    - `--reasoning_model` - siz foydalanmoqchi bo'lgan fikrlash modeli.
    - `--useAPI` - OpenAI API-dan foydalanishni xohlaysizmi.
    
2. Penetratsiya testini o'tkazish uchun ko'rsatmalarga amal qiling.
3. Umuman olganda, InsiderGPT chatGPT-ga o'xshash buyruqlarni oladi. Bir nechta asosiy buyruqlar mavjud.
   1. Buyruqlar quyidagilardir: 
      - `help`: yordam xabarini ko'rsatish.
      - `next`: testni bajarish natijasini kiritish va keyingi bosqichga o'tish.
      - `more`: **InsiderGPT** ga joriy bosqichning batafsil ma'lumotlarini tushuntirishga ruxsat berish. Shuningdek, testerni boshqarish uchun yangi kichik vazifalarni hal qiluvchi yaratish.
      - `todo`: topshiriqlar ro'yxatini ko'rsatish.
      - `discuss`: **InsiderGPT** bilan muhokama qilish.
      - `quit`: Dasturdan chiqish va chiqishni jurnal fayli sifatida saqlash (quyidagi **hisobot** bo'limiga qarang).

### Hisobot
1. Penetratsiya testini tugatgandan so'ng, hisobot avtomatik ravishda "logs" papkasi yaratiladi (agar siz "chiqish" buyrug'i bilan chiqsangiz).
2. Hisobotni `python3 utils/report_generator.py <log fayli>` ishga tushirish orqali odam oʻqiy oladigan formatda chop etish mumkin. `sample_insiderGPT_log.txt` hisobot namunasi ham yuklangan.





<p align="right">(<a href="#readme-top">back to top</a>)</p>


