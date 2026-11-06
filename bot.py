import os
import random
import sqlite3
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN") or "8759561926:AAEpxHjnYupFQGyavmOgyY-y0Fw8BFt8r3k"

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! .env faylingizni tekshiring")

bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8192450042  # Sizning Telegram ID raqamingiz

def init_db():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        custom_id INTEGER UNIQUE
    )
    """)
    conn.commit()
    conn.close()

init_db()

def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Mavjud emas"
    first_name = message.from_user.first_name or "Ism yo'q"

    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT custom_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        custom_id = row[0]
        conn.close()
        return custom_id
    else:
        while True:
            custom_id = random.randint(10000000, 99999999)
            cursor.execute("SELECT user_id FROM users WHERE custom_id = ?", (custom_id,))
            if not cursor.fetchone():
                break

        cursor.execute("INSERT INTO users (user_id, username, first_name, custom_id) VALUES (?, ?, ?, ?)",
                       (user_id, username, first_name, custom_id))
        conn.commit()
        conn.close()

        admin_text = (
            f"👤 Yangi foydalanuvchi botga kirdi!\n\n"
            f"🆔 Unikal ID: `{custom_id}`\n"
            f"👤 Ismi: {first_name}\n"
            f"🔗 Username: @{username}\n"
            f"🆔 Telegram ID: `{user_id}`"
        )
        try:
            bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
        except Exception as e:
            print(f"Adminga xabar yuborishda xatolik: {e}")

        return custom_id

# 10 ta qiyin umumiy mantiqiy savollar bazasi (10 tilda)
questions_data = [
    {
        "q": {
            "uz": "Bir xonada 3 ta o'g'il bola o'tiribdi. Ularning har birining bittadan singlisi bor. Xonada jami nechta kishi bor?",
            "ru": "В комнате сидят 3 мальчика. У каждого из них есть по меньшей мере по одной сестре. Сколько всего человек в комнате?",
            "en": "There are 3 boys sitting in a room. Each of them has one sister. How many people are in the room in total?",
            "tr": "Bir odada 3 erkek çocuk oturuyor. Her birinin birer kız kardeşi var. Odada toplam kaç kişi var?",
            "uz_lat": "Bir xonada 3 ta o'g'il bola o'tiribdi. Ularning har birining bittadan singlisi bor. Xonada jami nechta kishi bor?",
            "es": "Hay 3 niños sentados en una habitación. Cada uno de ellos tiene una hermana. ¿Cuántas personas hay en total en la habitación?",
            "de": "In einem Raum sitzen 3 Jungen. Jeder von ihnen hat eine Schwester. Wie viele Personen sind insgesamt im Raum?",
            "fr": "Il y a 3 garçons assis dans une pièce. Chacun d'eux a une sœur. Combien y a-t-il de personnes au total dans la pièce ?",
            "ar": "يوجد 3 أولاد يجلسون في غرفة. لكل منهم أخت واحدة. كم عدد الأشخاص في الغرفة إجمالاً؟",
            "fa": "۳ پسر در یک اتاق نشسته‌اند. هر کدام از آن‌ها یک خواهر دارند. در مجموع چند نفر در اتاق هستند؟"
        },
        "options": {
            "uz": ["6", "3", "4", "5"],
            "ru": ["6", "3", "4", "5"],
            "en": ["6", "3", "4", "5"],
            "tr": ["6", "3", "4", "5"],
            "uz_lat": ["6", "3", "4", "5"],
            "es": ["6", "3", "4", "5"],
            "de": ["6", "3", "4", "5"],
            "fr": ["6", "3", "4", "5"],
            "ar": ["6", "3", "4", "5"],
            "fa": ["6", "3", "4", "5"]
        },
        "correct": {
            "uz": "4", "ru": "4", "en": "4", "tr": "4", "uz_lat": "4", "es": "4", "de": "4", "fr": "4", "ar": "4", "fa": "4"
        }
    },
    {
        "q": {
            "uz": "Meni sotib olganda rangim qora, ishlatganda qizil, tashlab yuborganda kulrang bo'laman. Men niman?",
            "ru": "Когда меня покупают — я черный, когда используют — красный, когда выбрасывают — серый. Кто я?",
            "en": "When you buy me I am black, when you use me I am red, when you throw me away I am gray. What am I?",
            "tr": "Beni satın aldığında siyahım, kullandığında kırmızı, attığında griyim. Ben neyim?",
            "uz_lat": "Meni sotib olganda rangim qora, ishlatganda qizil, tashlab yuborganda kulrang bo'laman. Men niman?",
            "es": "Cuando me compras soy negro, cuando me usas soy rojo, cuando me tiras soy gris. ¿Qué soy?",
            "de": "Wenn du mich kaufst, bin ich schwarz, wenn du mich benutzt, bin ich rot, wenn du mich wegwirfst, bin ich grau. Was bin ich?",
            "fr": "Quand tu m'achètes je suis noir, quand tu m'utilises je suis rouge, quand tu me jetteras je suis gris. Qui suis-je ?",
            "ar": "عندما تشتريني أكون أسود، وعندما تستخدمني أكون أحمر، وعندما ترميني أكون رمادياً. من أنا؟",
            "fa": "وقتی مرا می‌خروی سیاهم، وقتی استفاده می‌کنی قرمزم، وقتی دور می‌اندازی خاکستری هستم. من چیستم؟"
        },
        "options": {
            "uz": ["Ko'mir", "Qalam", "Shina", "Temir"],
            "ru": ["Уголь", "Карандаш", "Шина", "Железо"],
            "en": ["Coal", "Pencil", "Tire", "Iron"],
            "tr": ["Kömür", "Kalem", "Lastik", "Demir"],
            "uz_lat": ["Ko'mir", "Qalam", "Shina", "Temir"],
            "es": ["Carbón", "Lápiz", "Neumático", "Hierro"],
            "de": ["Kohle", "Bleistift", "Reifen", "Eisen"],
            "fr": ["Charbon", "Crayon", "Pneu", "Fer"],
            "ar": ["فحم", "قلم رصاص", "إطار", "حديد"],
            "fa": ["زغال", "مداد", "لاستیک", "آهن"]
        },
        "correct": {
            "uz": "Ko'mir", "ru": "Уголь", "en": "Coal", "tr": "Kömür", "uz_lat": "Ko'mir", "es": "Carbón", "de": "Kohle", "fr": "Charbon", "ar": "فحم", "fa": "زغال"
        }
    },
    {
        "q": {
            "uz": "Qaysi idishni to'la bo'lsa ham, bo'sh bo'lsa ham og'irligi o'zgarmaydi?",
            "ru": "Какой сосуд весит одинаково как полным, так и пустым?",
            "en": "Which container weighs the same whether it is full or empty?",
            "tr": "Hangi kap dolu veya boş olsun aynı ağırlıktadır?",
            "uz_lat": "Qaysi idishni to'la bo'lsa ham, bo'sh bo'lsa ham og'irligi o'zgarmaydi?",
            "es": "¿Qué recipiente pesa lo mismo esté lleno o vacío?",
            "de": "Welcher Behälter wiegt gleich viel, egal ob er voll oder leer ist?",
            "fr": "Quel récipient pèse la même chose qu'il soit plein ou vide ?",
            "ar": "ما هو الوعاء الذي يزن نفس الوزن سواء كان مليئاً أو فارغاً؟",
            "fa": "کدام ظرف چه پر باشد و چه خالی، وزن یکسانی دارد؟"
        },
        "options": {
            "uz": ["G'alvir (Elak)", "Choynak", "Stakan", "Idish yo'q"],
            "ru": ["Решето", "Чайник", "Стакан", "Такого нет"],
            "en": ["Sieve", "Teapot", "Glass", "None"],
            "tr": ["Elek", "Çaydanlık", "Bardak", "Yok"],
            "uz_lat": ["G'alvir (Elak)", "Choynak", "Stakan", "Idish yo'q"],
            "es": ["Colador", "Tetera", "Vaso", "Ninguno"],
            "de": ["Sieb", "Teekanne", "Glas", "Keiner"],
            "fr": ["Tamis", "Théière", "Verre", "Aucun"],
            "ar": ["غربال", "إبريق شاي", "كوب", "لا يوجد"],
            "fa": ["الک", "قوری", "لیوان", "هیچ‌کدام"]
        },
        "correct": {
            "uz": "G'alvir (Elak)", "ru": "Решето", "en": "Sieve", "tr": "Elek", "uz_lat": "G'alvir (Elak)", "es": "Colador", "de": "Sieb", "fr": "Tamis", "ar": "غربال", "fa": "الک"
        }
    },
    {
        "q": {
            "uz": "Qaysi so'z hamma tilda noto'g'ri talaffuz qilinadi?",
            "ru": "Какое слово во всех языках произносится неправильно?",
            "en": "Which word is pronounced incorrectly in all languages?",
            "tr": "Hangi kelime tüm dillerde yanlış telaffuz edilir?",
            "uz_lat": "Qaysi so'z hamma tilda noto'g'ri talaffuz qilinadi?",
            "es": "¿Qué palabra se pronuncia incorrectamente en todos los idiomas?",
            "de": "Welches Wort wird in allen Sprachen falsch ausgesprochen?",
            "fr": "Quel mot est mal prononcé dans toutes les langues ?",
            "ar": "ما هي الكلمة التي يُنطق بها بشكل خاطئ في جميع اللغات؟",
            "fa": "کدام کلمه در تمام زبان‌ها به اشتباه تلفظ می‌شود؟"
        },
        "options": {
            "uz": ["'Noto'g'ri' so'zi", "'Xato' so'zi", "Har qanday so'z", "Bunday so'z yo'q"],
            "ru": ["Слово 'Неправильно'", "Слово 'Ошибка'", "Любое слово", "Такого слова нет"],
            "en": ["The word 'Incorrect'", "The word 'Wrong'", "Any word", "No such word"],
            "tr": ["'Yanlış' kelimesi", "'Hata' kelimesi", "Herhangi bir kelime", "Böyle bir kelime yok"],
            "uz_lat": ["'Noto'g'ri' so'zi", "'Xato' so'zi", "Har qanday so'z", "Bunday so'z yo'q"],
            "es": ["La palabra 'Incorrecto'", "La palabra 'Error'", "Cualquier palabra", "No existe"],
            "de": ["Das Wort 'Falsch'", "Das Wort 'Fehler'", "Jedes Wort", "Gibt es nicht"],
            "fr": ["Le mot 'Incorrect'", "Le mot 'Erreur'", "N'importe quel mot", "Aucun mot"],
            "ar": ["كلمة 'خطأ'", "كلمة 'غير صحيح'", "أي كلمة", "لا توجد كلمة"],
            "fa": ["کلمه 'نادرست'", "کلمه 'خطا'", "هر کلمه‌ای", "چنین کلمه‌ای وجود ندارد"]
        },
        "correct": {
            "uz": "'Noto'g'ri' so'zi", "ru": "Слово 'Неправильно'", "en": "The word 'Incorrect'", "tr": "'Yanlış' kelimesi", "uz_lat": "'Noto'g'ri' so'zi", "es": "La palabra 'Incorrecto'", "de": "Das Wort 'Falsch'", "fr": "Le mot 'Incorrect'", "ar": "كلمة 'خطأ'", "fa": "کلمه 'نادرست'"
        }
    },
    {
        "q": {
            "uz": "Qaysi oyda 28 kun bor?",
            "ru": "В каком месяце есть 28 дней?",
            "en": "Which month has 28 days?",
            "tr": "Hangi ayda 28 gün vardır?",
            "uz_lat": "Qaysi oyda 28 kun bor?",
            "es": "¿Qué mes tiene 28 días?",
            "de": "Welcher Monat hat 28 Tage?",
            "fr": "Quel mois a 28 jours ?",
            "ar": "ما هو الشهر الذي يحتوي على 28 يوماً؟",
            "fa": "کدام ماه ۲۸ روز دارد؟"
        },
        "options": {
            "uz": ["Faqat Fevral", "Hamma oylarda", "Faqat kabisa yilida", "Mart oyida"],
            "ru": ["Только Февраль", "Во всех месяцах", "Только в високосный год", "В Марте"],
            "en": ["Only February", "All months", "Only in leap years", "March"],
            "tr": ["Sadece Şubat", "Tüm aylarda", "Sadece artık yılda", "Mart"],
            "uz_lat": ["Faqat Fevral", "Hamma oylarda", "Faqat kabisa yilida", "Mart oyida"],
            "es": ["Solo febrero", "Todos los meses", "Solo en años bisiestos", "Marzo"],
            "de": ["Nur Februar", "Alle Monate", "Nur im Schaltjahr", "März"],
            "fr": ["Seulement février", "Tous les mois", "Seulement les années bissextiles", "Mars"],
            "ar": ["فبراير فقط", "جميع الشهور", "في السنة الكبيسة فقط", "مارس"],
            "fa": ["فقط فوریه", "همه ماه‌ها", "فقط در سال کبیسه", "مارس"]
        },
        "correct": {
            "uz": "Hamma oylarda", "ru": "Во всех месяцах", "en": "All months", "tr": "Tüm aylarda", "uz_lat": "Hamma oylarda", "es": "Todos los meses", "de": "Alle Monate", "fr": "Tous les mois", "ar": "جميع الشهور", "fa": "همه ماه‌ها"
        }
    },
    {
        "q": {
            "uz": "Siz poygada ikkinchi o'rinda kelayotgan odamni quvib o'tdingiz. Hozir nechagachi o'rindasiz?",
            "ru": "Вы обогнали человека, бегущего на втором месте. Какое место вы теперь занимаете?",
            "en": "You pass the person in second place in a race. What place are you in now?",
            "tr": "Bir yarışta ikinci sıradaki kişiyi geçtin. Şu anda kaçıncı sıradasın?",
            "uz_lat": "Siz poygada ikkinchi o'rinda kelayotgan odamni quvib o'tdingiz. Hozir nechagachi o'rindasiz?",
            "es": "Adelantas a la persona que va en segundo lugar en una carrera. ¿En qué puesto estás ahora?",
            "de": "Du überholst den Zweiten in einem Rennen. Welchen Platz belegst du jetzt?",
            "fr": "Vous dépassez la personne en deuxième position dans une course. quelle est votre place maintenant ?",
            "ar": "لقد تجاوزت الشخص الذي يحتل المركز الثاني في السباق. في أي مركز أنت الآن؟",
            "fa": "شما از فردی که در جایگاه دوم مسابقه قرار دارد سبقت می‌گیرید. حالا در چه جایگاهی هستید؟"
        },
        "options": {
            "uz": ["1-o'rin", "2-o'rin", "3-o'rin", "Oxirgi"],
            "ru": ["1 место", "2 место", "3 место", "Последнее"],
            "en": ["1st place", "2nd place", "3rd place", "Last"],
            "tr": ["1. sıra", "2. sıra", "3. sıra", "Son"],
            "uz_lat": ["1-o'rin", "2-o'rin", "3-o'rin", "Oxirgi"],
            "es": ["1er lugar", "2do lugar", "3er lugar", "Último"],
            "de": ["1. Platz", "2. Platz", "3. Platz", "Letzter"],
            "fr": ["1ère place", "2e place", "3e place", "Dernier"],
            "ar": ["المركز الأول", "المركز الثاني", "المركز الثالث", "الأخير"],
            "fa": ["رتبه اول", "رتبه دوم", "رتبه سوم", "آخر"]
        },
        "correct": {
            "uz": "2-o'rin", "ru": "2 место", "en": "2nd place", "tr": "2. sıra", "uz_lat": "2-o'rin", "es": "2do lugar", "de": "2. Platz", "fr": "2e place", "ar": "المركز الثاني", "fa": "رتبه دوم"
        }
    },
    {
        "q": {
            "uz": "Uchta traktor 3 soatda 3 gektar yer haydasa, 1 ta traktor 1 gektar erni necha soatda haydaydi?",
            "ru": "Если 3 трактора за 3 часа вспахивают 3 гектара земли, то за сколько часов 1 трактор вспашет 1 гектар?",
            "en": "If 3 tractors plow 3 hectares of land in 3 hours, how many hours does 1 tractor take to plow 1 hectare?",
            "tr": "3 traktör 3 saatte 3 hektar tarlayı sürerse, 1 traktör 1 hektar tarlayı kaç saatte sürer?",
            "uz_lat": "Uchta traktor 3 soatda 3 gektar yer haydasa, 1 ta traktor 1 gektar erni necha soatda haydaydi?",
            "es": "Si 3 tractores aran 3 hectáreas en 3 horas, ¿cuántas horas tarda 1 tractor en arar 1 hectárea?",
            "de": "Wenn 3 Traktoren in 3 Stunden 3 Hektar pflügen, wie viele Stunden braucht 1 Traktor für 1 Hektar?",
            "fr": "Si 3 tracteurs labourent 3 hectares en 3 heures, combien d'heures faut-il à 1 tracteur pour labourer 1 hectare ?",
            "ar": "إذا كانت 3 جرارات تحرث 3 هكتارات في 3 ساعات، فكم ساعة يستغرق جرار واحد لحرث هكتار واحد؟",
            "fa": "اگر ۳ تراکتور در ۳ ساعت ۳ هکتار زمین شخم بزنند، ۱ تراکتور ۱ هکتار را در چند ساعت شخم می‌زند؟"
        },
        "options": {
            "uz": ["3 soat", "1 soat", "9 soat", "0.5 soat"],
            "ru": ["3 часа", "1 час", "9 часов", "0.5 часа"],
            "en": ["3 hours", "1 hour", "9 hours", "0.5 hours"],
            "tr": ["3 saat", "1 saat", "9 saat", "0.5 saat"],
            "uz_lat": ["3 soat", "1 soat", "9 soat", "0.5 soat"],
            "es": ["3 horas", "1 hora", "9 horas", "0.5 horas"],
            "de": ["3 Stunden", "1 Stunde", "9 Stunden", "0.5 Stunden"],
            "fr": ["3 heures", "1 heure", "9 heures", "0.5 heures"],
            "ar": ["3 ساعات", "ساعة واحدة", "9 ساعات", "0.5 ساعة"],
            "fa": ["۳ ساعت", "۱ ساعت", "۹ ساعت", "۰.۵ ساعت"]
        },
        "correct": {
            "uz": "3 soat", "ru": "3 часа", "en": "3 hours", "tr": "3 saat", "uz_lat": "3 soat", "es": "3 horas", "de": "3 Stunden", "fr": "3 heures", "ar": "3 ساعات", "fa": "۳ ساعت"
        }
    },
    {
        "q": {
            "uz": "Daraxtda 10 ta qush o'tirgandi. Ovchi ulardan 1 tasini otib o'ldirdi. Daraxtda nechta qush qoldi?",
            "ru": "На дереве сидело 10 птиц. Охотник подстрелил 1. Сколько птиц осталось на дереве?",
            "en": "There were 10 birds sitting on a tree. A hunter shot 1. How many birds were left on the tree?",
            "tr": "Ağaçta 10 kuş oturuyordu. Avcı 1'ini vurdu. Ağaçta kaç kuş kaldı?",
            "uz_lat": "Daraxtda 10 ta qush o'tirgandi. Ovchi ulardan 1 tasini otib o'ldirdi. Daraxtda nechta qush qoldi?",
            "es": "Había 10 pájaros en un árbol. Un cazador disparó a 1. ¿Cuántos pájaros quedaron en el árbol?",
            "de": "Auf einem Baum saßen 10 Vögel. Ein Jäger schoss 1 ab. Wie viele Vögel blieben auf dem Baum?",
            "fr": "Il y avait 10 oiseaux sur un arbre. Un chasseur en a tiré 1. Combien d'oiseaux sont restés sur l'arbre ?",
            "ar": "كانت هناك 10 طيور على شجرة. أطلق صياد النار على واحد. كم طائراً بقي على الشجرة؟",
            "fa": "۱۰ پرنده روی درخت نشسته بودند. یک شکارچی یکی را زد. چند پرنده روی درخت ماند؟"
        },
        "options": {
            "uz": ["0 ta", "9 ta", "8 ta", "1 ta"],
            "ru": ["0", "9", "8", "1"],
            "en": ["0", "9", "8", "1"],
            "tr": ["0", "9", "8", "1"],
            "uz_lat": ["0 ta", "9 ta", "8 ta", "1 ta"],
            "es": ["0", "9", "8", "1"],
            "de": ["0", "9", "8", "1"],
            "fr": ["0", "9", "8", "1"],
            "ar": ["0", "9", "8", "1"],
            "fa": ["۰", "۹", "۸", "۱"]
        },
        "correct": {
            "uz": "0 ta", "ru": "0", "en": "0", "tr": "0", "uz_lat": "0 ta", "es": "0", "de": "0", "fr": "0", "ar": "0", "fa": "۰"
        }
    },
    {
        "q": {
            "uz": "Qaysi narsa suvga cho'kmaydi va yonmaydi?",
            "ru": "Что в воде не тонет и в огне не горит?",
            "en": "What does not sink in water and does not burn in fire?",
            "tr": "Sudan batmayan ve ateşde yanmayan şey nedir?",
            "uz_lat": "Qaysi narsa suvga cho'kmaydi va yonmaydi?",
            "es": "¿Qué cosa no se hunde en el agua ni se quema en el fuego?",
            "de": "Was geht im Wasser nicht unter und brennt im Feuer nicht?",
            "fr": "Qu'est-ce qui ne coule pas dans l'eau et ne brûle pas dans le feu ?",
            "ar": "ما هو الشيء الذي لا يغرق في الماء ولا يحترق في النار؟",
            "fa": "چه چیزی در آب غرق نمی‌شود و در آتش نمی‌سوزد؟"
        },
        "options": {
            "uz": ["Muz", "Yog'och", "Tosh", "Temir"],
            "ru": ["Лед", "Дерево", "Камень", "Железо"],
            "en": ["Ice", "Wood", "Stone", "Iron"],
            "tr": ["Buz", "Odun", "Taş", "Demir"],
            "uz_lat": ["Muz", "Yog'och", "Tosh", "Temir"],
            "es": ["Hielo", "Madera", "Piedra", "Hierro"],
            "de": ["Eis", "Holz", "Stein", "Eisen"],
            "fr": ["Glace", "Bois", "Pierre", "Fer"],
            "ar": ["ثلج", "خشب", "حجر", "حديد"],
            "fa": ["یخ", "چوب", "سنگ", "آهن"]
        },
        "correct": {
            "uz": "Muz", "ru": "Лед", "en": "Ice", "tr": "Buz", "uz_lat": "Muz", "es": "Hielo", "de": "Eis", "fr": "Glace", "ar": "ثلج", "fa": "یخ"
        }
    },
    {
        "q": {
            "uz": "Qaysi so'z doimo 'noto'g'ri' deb o'qiladi?",
            "ru": "Какое слово всегда читается как 'неправильно'?",
            "en": "Which word is always read incorrectly?",
            "tr": "Hangi kelime her zaman yanlış okunur?",
            "uz_lat": "Qaysi so'z doimo 'noto'g'ri' deb o'qiladi?",
            "es": "¿Qué palabra siempre se lee incorrectamente?",
            "de": "Welches Wort wird immer falsch gelesen?",
            "fr": "Quel mot se lit toujours de manière incorrecte ?",
            "ar": "ما هي الكلمة التي تُقرأ دائماً بشكل خاطئ؟",
            "fa": "کدام کلمه همیشه به اشتباه خوانده می‌شود؟"
        },
        "options": {
            "uz": ["'Noto'g'ri'", "'Xato'", "'To'g'ri'", "Barchasi"],
            "ru": ["'Неправильно'", "'Ошибка'", "'Правильно'", "Все"],
            "en": ["'Incorrect'", "'Wrong'", "'Right'", "All"],
            "tr": ["'Yanlış'", "'Hata'", "'Doğru'", "Tümü"],
            "uz_lat": ["'Noto'g'ri'", "'Xato'", "'To'g'ri'", "Barchasi"],
            "es": ["'Incorrecto'", "'Error'", "'Correcto'", "Todos"],
            "de": ["'Falsch'", "'Fehler'", "'Richtig'", "Alle"],
            "fr": ["'Incorrect'", "'Erreur'", "'Correct'", "Tous"],
            "ar": ["'خطأ'", "'غير صحيح'", "'صحيح'", "الكل"],
            "fa": ["'نادرست'", "'خطا'", "'درست'", "همه"]
        },
        "correct": {
            "uz": "'Noto'g'ri'", "ru": "'Неправильно'", "en": "'Incorrect'", "tr": "'Yanlış'", "uz_lat": "'Noto'g'ri'", "es": "'Incorrecto'", "de": "'Falsch'", "fr": "'Incorrect'", "ar": "'خطأ'", "fa": "'نادرست'"
        }
    }
]

languages = {
    "uz": {
        "name": "O'zbekcha 🇺🇿",
        "welcome": "Salom! Mantiqiy savollar va duel botiga xush kelibsiz.",
        "lang_changed": "Til O'zbek tiliga o'zgartirildi ✅",
        "game_over": "🏁 Duel yakunlandi!\nSizning natijangiz: {score}/10\n\nYana o'ynashni xohlasangiz, saytimizdan foydalanishingizni so'raymiz: duelum.netlify.app",
        "menu_admin": "👑 Admin",
        "menu_duel": "⚔️ Duel boshlash",
        "menu_insta": "📸 Instagram",
        "menu_youtube": "▶️ YouTube",
        "menu_site": "🌐 Sayt",
        "menu_lang": "🌐 Tilni o'zgartirish"
    },
    "uz_lat": {
        "name": "O'zbek (Lotin) 🇺🇿",
        "welcome": "Salom! Mantiqiy savollar va duel botiga xush kelibsiz.",
        "lang_changed": "Til O'zbek tiliga o'zgartirildi ✅",
        "game_over": "🏁 Duel yakunlandi!\nSizning natijangiz: {score}/10\n\nYana o'ynashni xohlasangiz, saytimizdan foydalaning: duelum.netlify.app",
        "menu_admin": "👑 Admin",
        "menu_duel": "⚔️ Duel boshlash",
        "menu_insta": "📸 Instagram",
        "menu_youtube": "▶️ YouTube",
        "menu_site": "🌐 Sayt",
        "menu_lang": "🌐 Tilni o'zgartirish"
    },
    "ru": {
        "name": "Русский 🇷🇺",
        "welcome": "Привет! Добро пожаловать в бот логических вопросов.",
        "lang_changed": "Язык изменен на русский ✅",
        "game_over": "🏁 Дуэль завершена!\nВаш результат: {score}/10\n\nЕсли хотите сыграть еще, воспользуйтесь сайтом: duelum.netlify.app",
        "menu_admin": "👑 Админ",
        "menu_duel": "⚔️ Начать дуэль",
        "menu_insta": "📸 Instagram",
        "menu_youtube": "▶️ YouTube",
        "menu_site": "🌐 Сайт",
        "menu_lang": "🌐 Изменить язык"
    },
    "en": {
        "name": "English 🇬🇧",
        "welcome": "Hello! Welcome to the logical questions duel bot.",
        "lang_changed": "Language changed to English ✅",
        "game_over": "🏁 Duel Over!\nYour score: {score}/10\n\nIf you want to play again, use our website: duelum.netlify.app",
        "menu_admin": "👑 Admin",
        "menu_duel": "⚔️ Start Duel",
        "menu_insta": "📸 Instagram",
        "menu_youtube": "▶️ YouTube",
        "menu_site": "🌐 Website",
        "menu_lang": "🌐 Change language"
    },
    "tr": {
        "name": "Türkçe 🇹🇷",
        "welcome": "Merhaba! Mantıksal sorular düello botuna hoş geldiniz.",
        "lang_changed": "Dil Türkçe olarak değiştirildi ✅",
        "game_over": "🏁 Düello Bitti!\nPuanınız: {score}/10\n\nTekrar oynamak için sitemizi kullanın: duelum.netlify.app",
        "menu_admin": "👑 Yönetici",
        "menu_duel": "⚔️ Düello Başlat",
        "menu_insta": "📸 Instagram",
        "menu_youtube": "▶️ YouTube",
        "menu_site": "🌐 Site",
        "menu_lang": "🌐 Dili değiştir"
    },
    "es": {
        "name": "Español 🇪🇸",
        "welcome": "¡Hola! Bienvenido al bot de duelos de preguntas lógicas.",
        "lang_changed": "Idioma cambiado a español ✅",
        "game_over": "🏁 ¡Duelo terminado!\nTu puntuación: {score}/10\n\nVisita nuestro sitio: duelum.netlify.app",
        "menu_admin": "👑 Admin",
        "menu_duel": "⚔️ Iniciar Duelo",
        "menu_insta": "📸 Instagram",
        "menu_youtube": "▶️ YouTube",
        "menu_site": "🌐 Sitio web",
        "menu_lang": "🌐 Cambiar idioma"
    },
    "de": {
        "name": "Deutsch 🇩🇪",
        "welcome": "Hallo! Willkommen beim Logikfragen-Duell-Bot.",
        "lang_changed": "Sprache auf Deutsch geändert ✅",
        "game_over": "🏁 Duell beendet!\nDein Punktestand: {score}/10\n\nNutze unsere Website: duelum.netlify.app",
        "menu_admin": "👑 Admin",
        "menu_duel": "⚔️ Duell starten",
        "menu_insta": "📸 Instagram",
        "menu_youtube": "▶️ YouTube",
        "menu_site": "🌐 Website",
        "menu_lang": "🌐 Sprache ändern"
    },
    "fr": {
        "name": "Français 🇫🇷",
        "welcome": "Bonjour ! Bienvenue sur le bot de duel de questions logiques.",
        "lang_changed": "Langue changée en français ✅",
        "game_over": "🏁 Duel terminé !\nVotre score : {score}/10\n\nVisitez notre site : duelum.netlify.app",
        "menu_admin": "👑 Admin",
        "menu_duel": "⚔️ Commencer le duel",
        "menu_insta": "📸 Instagram",
        "menu_youtube": "▶️ YouTube",
        "menu_site": "🌐 Site web",
        "menu_lang": "🌐 Changer de langue"
    },
    "ar": {
        "name": "العربية 🇸🇦",
        "welcome": "أهلاً بك! مرحباً بك في بوت مبارزة الأسئلة المنطقية.",
        "lang_changed": "تم تغيير اللغة إلى العربية ✅",
        "game_over": "🏁 انتهت المبارزة!\nنتيجتك: {score}/10\n\nاستخدم موقعنا: duelum.netlify.app",
        "menu_admin": "👑 المشرف",
        "menu_duel": "⚔️ بدء المبارزة",
        "menu_insta": "📸 إنستغرام",
        "menu_youtube": "▶️ يوتيوب",
        "menu_site": "🌐 الموقع",
        "menu_lang": "🌐 تغيير اللغة"
    },
    "fa": {
        "name": "فارسی 🇮🇷",
        "welcome": "سلام! به ربات دوئل سوالات منطقی خوش آمدید.",
        "lang_changed": "زبان به فارسی تغییر یافت ✅",
        "game_over": "🏁 دوئل تمام شد!\nامتیاز شما: {score}/10\n\nاز وب‌سایت ما بازدید کنید: duelum.netlify.app",
        "menu_admin": "👑 ادمین",
        "menu_duel": "⚔️ شروع دوئل",
        "menu_insta": "📸 اینستاگرام",
        "menu_youtube": "▶️ یوتیوب",
        "menu_site": "🌐 وب‌سایت",
        "menu_lang": "🌐 تغییر زبان"
    }
}

user_languages = {}
active_duels = {}

def get_lang(user_id):
    return user_languages.get(user_id, "uz")

def get_reply_keyboard(lang_code):
    lang = languages[lang_code]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_duel = types.KeyboardButton(lang["menu_duel"])
    btn_admin = types.KeyboardButton(lang["menu_admin"])
    btn_lang = types.KeyboardButton(lang["menu_lang"])
    btn_insta = types.KeyboardButton(lang["menu_insta"])
    btn_youtube = types.KeyboardButton(lang["menu_youtube"])
    btn_site = types.KeyboardButton(lang["menu_site"])

    markup.add(btn_duel, btn_admin)
    markup.add(btn_lang)
    markup.add(btn_insta, btn_youtube, btn_site)
    return markup

def send_language_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, data in languages.items():
        btn = types.InlineKeyboardButton(text=data["name"], callback_data=f"set_lang:{code}")
        buttons.append(btn)
    markup.add(*buttons)
    bot.send_message(chat_id, "🌍 Tilni tanlang / Choose language:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    custom_id = register_user(message)
    lang_code = get_lang(user_id)
    lang = languages[lang_code]

    text = f"{lang['welcome']}\n\n🆔 Sizning 8 xonali ID raqamingiz: `{custom_id}`"
    markup = get_reply_keyboard(lang_code)
    bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def send_help(message):
    text = (
        "🤖 Bot buyruqlari:\n"
        "/start - Botni ishga tushirish\n"
        "/help - Yordam olish\n"
        "/duel - 10 ta qiyin mantiqiy savollik duel boshlash\n"
        "/language - Tilni o'zgartirish (10 ta til)"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['language'])
def choose_language_cmd(message):
    send_language_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang:"))
def set_language_callback(call):
    user_id = call.from_user.id
    lang_code = call.data.split(":")[1]
    user_languages[user_id] = lang_code
    lang = languages[lang_code]
    bot.answer_callback_query(call.id, lang["lang_changed"])
    markup = get_reply_keyboard(lang_code)

    bot.send_message(call.message.chat.id, f"✅ {lang['lang_changed']}", reply_markup=markup)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

@bot.message_handler(func=lambda msg: any(msg.text == lang["menu_duel"] for lang in languages.values()) or msg.text == "/duel")
def start_duel(message):
    user_id = message.from_user.id
    lang_code = get_lang(user_id)

    shuffled_questions = random.sample(questions_data, len(questions_data))

    active_duels[user_id] = {
        "questions": shuffled_questions,
        "current_index": 0,
        "score": 0,
        "lang_code": lang_code
    }

    send_duel_question(message.chat.id, user_id)

def send_duel_question(chat_id, user_id):
    duel = active_duels.get(user_id)
    if not duel:
        return

    index = duel["current_index"]
    lang_code = duel["lang_code"]

    if index >= 10:
        lang = languages[lang_code]
        score = duel["score"]
        text = lang["game_over"].format(score=score)

        markup = get_reply_keyboard(lang_code)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        del active_duels[user_id]
        return

    q = duel["questions"][index]

    question_text = q["q"].get(lang_code, q["q"]["uz"])
    options = q["options"].get(lang_code, q["options"]["uz"]).copy()

    if isinstance(q["correct"], dict):
        correct_val = q["correct"].get(lang_code, q["correct"]["uz"])
    else:
        correct_val = q["correct"]

    random.shuffle(options)

    markup = types.InlineKeyboardMarkup(row_width=1)
    for opt in options:
        is_correct_flag = "1" if opt == correct_val else "0"
        btn = types.InlineKeyboardButton(text=opt, callback_data=f"ans:{is_correct_flag}")
        markup.add(btn)

    text = (
        f"🧠 Mantiqiy Duel (Savol {index + 1}/10)\n\n"
        f"❓ {question_text}"
    )
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("ans:"))
def handle_duel_answer(call):
    user_id = call.from_user.id
    if user_id not in active_duels:
        bot.answer_callback_query(call.id, "Duel allaqachon tugagan.")
        return

    _, is_correct = call.data.split(":")
    duel = active_duels[user_id]

    if is_correct == "1":
        duel["score"] += 1
        bot.answer_callback_query(call.id, "✅ To'g'ri!")
    else:
        bot.answer_callback_query(call.id, "❌ Noto'g'ri!")

    duel["current_index"] += 1

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    send_duel_question(call.message.chat.id, user_id)

@bot.message_handler(func=lambda message: True)
def handle_menu_and_text(message):
    user_id = message.from_user.id
    text = message.text
    lang_code = get_lang(user_id)
    lang = languages[lang_code]

    if any(text == l["menu_admin"] for l in languages.values()):
        bot.reply_to(message, "👑 Bot administratori: @u7bbek", parse_mode="Markdown")
        return

    if any(text == l["menu_lang"] for l in languages.values()):
        send_language_menu(message.chat.id)
        return

    if any(text == l["menu_insta"] for l in languages.values()):
        bot.reply_to(message, "📸 Instagram sahifamiz:\nhttps://instagram.com/shoooxe", parse_mode="Markdown")
        return

    if any(text == l["menu_youtube"] for l in languages.values()):
        bot.reply_to(message, "▶️ YouTube kanalimiz:\nhttps://youtube.com/@shoooxe", parse_mode="Markdown")
        return

    if any(text == l["menu_site"] for l in languages.values()):
        bot.reply_to(message, "🌐 Rasmiy saytimiz:\nhttps://duelum.netlify.app", parse_mode="Markdown")
        return

    bot.reply_to(message, "Kechirasiz, bu buyruq topilmadi. Duel boshlash uchun tugmani bosing yoki /duel yuboring.", parse_mode="Markdown")

if __name__ == '__main__':
    commands = [
        telebot.types.BotCommand("start", "Botni ishga tushirish"),
        telebot.types.BotCommand("help", "Yordam"),
        telebot.types.BotCommand("duel", "10 ta qiyin mantiqiy savollik duel boshlash"),
        telebot.types.BotCommand("language", "Tilni o'zgartirish (10 ta til)")
    ]
    bot.set_my_commands(commands)

    print("Bot ishga tushdi...")
    bot.infinity_polling()
