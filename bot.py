import logging
import random
import json
import os
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
import threading

# Server Web minimal pentru Render / UptimeRobot
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Botul este activ 24/7!", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)

# Pornim serverul web pe un fir de execuție separat (thread)
threading.Thread(target=run_web, daemon=True).start()

# --- De aici începe codul tău existent pentru bot ---
TOKEN = "8973901312:AAF0jq2rfuqHe1ltkgVR7fsdoqlvhs6aw-c"
FISIER_CONTOR = "contor_borde1.json"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def incarc_contor():
    if os.path.exists(FISIER_CONTOR):
        try:
            with open(FISIER_CONTOR, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salveaza_contor(date):
    with open(FISIER_CONTOR, "w") as f:
        json.dump(date, f)

borde_memorate = incarc_contor()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global borde_memorate
    text = update.message.text.strip()
    
    if text.isdigit() and len(text) == 4:
        await update.message.reply_text("Solicitarea este in curs de procesare.")

        if text in borde_memorate:
            borde_memorate[text] += 1
            if borde_memorate[text] > 9999:
                borde_memorate[text] = 1000
        else:
            borde_memorate[text] = random.randint(1000, 9900)
            
        salveaza_contor(borde_memorate)

        ultimele_cifre = borde_memorate[text]
        bilet_nr = f"{text}{ultimele_cifre:04d}"
        
        acum = datetime.now(timezone.utc) + timedelta(hours=3)
        data_str = acum.strftime("%d.%m.%Y")
        ora_str = acum.strftime("%H:%M")
        
        mesaj_raspuns = (
            f"Bilet electronic nr. \n"
            f" {bilet_nr} \n"
            f" Data {data_str} ora {ora_str} \n"
            f" Valabil 1 ora \n"
            f" Pret 7 MDL \n"
            f" Numar de bord {text}"
        )
        await update.message.reply_text(mesaj_raspuns)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()