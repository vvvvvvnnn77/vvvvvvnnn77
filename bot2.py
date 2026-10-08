import logging
import random
import json
import os
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = "8617433370:AAEPxL8kPhTFpkMhI1ohu9K8FIGvzJaF1c8"
FISIER_CONTOR = "contor_borde2.json"

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
        
        # Ora curentă reală a Moldovei (UTC+3)
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