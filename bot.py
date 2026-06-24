import telebot
import feedparser
import time
import os
import re
import pycountry
import flag
from deep_translator import GoogleTranslator


# ================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_ID = "@AFGaziz"

RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "http://feeds.reuters.com/reuters/topNews",
    "http://feeds.foxnews.com/foxnews/latest",
    "https://www.france24.com/en/rss",
    "https://rss.dw.com/xml/rss-en-all",
    "http://rss.cnn.com/rss/edition_world.rss",
    "https://www.theguardian.com/world/rss",
    "https://www.rt.com/rss/news/"
]


if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not found in Environment Variables")


bot = telebot.TeleBot(BOT_TOKEN)

translator = GoogleTranslator(
    source="auto",
    target="fa"
)


sent_news = set()


# ================= FUNCTIONS =================


def clean_text(text):
    return re.sub(
        "<.*?>",
        "",
        text
    )


def get_country_flag(text):

    for country in pycountry.countries:

        if country.name.lower() in text.lower():

            try:
                return flag.flag(country.alpha_2)

            except:
                pass

    return "🌍"



def get_image_url(entry):

    try:

        if "media_content" in entry:
            return entry.media_content[0]["url"]


        if "links" in entry:

            for link in entry.links:

                if "image" in link.get("type",""):

                    return link.get("href")


        if "summary" in entry:

            img = re.search(
                r'<img.*?src="(.*?)"',
                entry.summary
            )

            if img:
                return img.group(1)


    except:
        pass


    return None




def translate(text):

    try:

        if not text:
            return ""

        return translator.translate(
            text[:1200]
        )

    except Exception as e:

        print(
            "Translate error:",
            e
        )

        return text





def send_news():

    for rss in RSS_FEEDS:


        print(
            "Checking:",
            rss
        )


        try:

            feed = feedparser.parse(rss)


        except Exception as e:

            print(
                "RSS error:",
                e
            )

            continue



        for entry in feed.entries:


            news_id = entry.get(
                "id",
                entry.get("link")
            )


            if news_id in sent_news:
                continue



            try:


                title = entry.title

                summary = clean_text(
                    entry.get(
                        "summary",
                        ""
                    )
                )



                country = get_country_flag(
                    title + summary
                )



                title_fa = translate(title)

                summary_fa = translate(summary)



                message = (

                    f"{country} <b>{title_fa}</b>\n\n"

                    f"{summary_fa}\n\n"

                    f"🔗 <a href='{entry.link}'>منبع خبر</a>\n"

                    f"🆔 {CHANNEL_ID}"

                )



                image = get_image_url(entry)



                if image:


                    bot.send_photo(
                        CHANNEL_ID,
                        image,
                        caption=message,
                        parse_mode="HTML"
                    )


                else:


                    bot.send_message(
                        CHANNEL_ID,
                        message,
                        parse_mode="HTML"
                    )



                print(
                    "Sent:",
                    title
                )


                sent_news.add(news_id)



                time.sleep(60)



            except Exception as e:


                print(
                    "News error:",
                    e
                )

                continue





# ================= START =================


print(
    "News Bot Started..."
)



while True:


    try:

        send_news()


        print(
            "Cycle complete. Waiting..."
        )


    except Exception as e:

        print(
            "Main error:",
            e
        )


    time.sleep(30)