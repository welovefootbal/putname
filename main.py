import requests
import time
import random
import os
from flask import Flask
from threading import Thread

# === CONFIG ===
ROBX_COOKIE = os.getenv("Roblox_COOKIE")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def log(mesaj):
    print(mesaj)
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": mesaj})
    except:
        pass

def ia_csrf_token(ses):
    res = ses.post("https://auth.roblox.com/v2/logout")
    return res.headers.get("x-csrf-token", "")

def cumpara_item(ses, csrf_token, product_id):
    headers = {"x-csrf-token": csrf_token}
    payload = {"expectedCurrency": 1, "expectedPrice": 0, "expectedSellerId": 1}
    return ses.post(f"https://economy.roblox.com/v1/purchases/products/{product_id}",
                    json=payload, headers=headers)

# === SERVER PENTRU PING ===
app = Flask('')

@app.route('/')
def home():
    return "🔥 Clitchicistul sniper bot is ALIVE!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# === START LOOP CU AUTO-RESTART ===
while True:
    try:
        ses = requests.Session()
        ses.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Cookie": f".ROBLOSECURITY={ROBX_COOKIE}"
        })

        log("[INFO] Încep să iau tokenul CSRF...")
        csrf = ia_csrf_token(ses)

        if csrf:
            log("[SUCCES] Am luat tokenul!")
        else:
            log("[FAIL] Nu am luat tokenul.")

        # === PORNIRE SNIPER ===
        log("[INFO] Încep căutarea de iteme gratuite...")
        log("[INFO] Pornesc sniper-ul UGC...")
        log("[🔄] Sniper-ul a fost pornit și funcționează.")

        vazute = set()
        while True:
            try:
                print("[LOOP] Sniper activ... verific iteme gratuite.")
                res = ses.get("https://catalog.roblox.com/v1/search/items?Category=11&SortType=3&Limit=30")
                data = res.json()

                for item in data.get("data", []):
                    idul = item.get("id")
                    pret = item.get("price", 1)
                    if idul in vazute:
                        continue
                    vazute.add(idul)

                    if pret == 0:
                        nume = item.get("name")
                        log(f"[!] Item găsit GRATIS: {nume} ({idul})")

                        buy_data = ses.get(f"https://economy.roblox.com/v1/assets/{idul}/resellers").json()
                        try:
                            product_id = buy_data["data"][0]["productId"]
                        except:
                            log("[x] Nu am găsit productId. Probabil e sold.")
                            continue

                        r = cumpara_item(ses, csrf, product_id)
                        if r.status_code == 200:
                            log(f"[SUCCES] AM PRINS itemul: {nume}!")
                        else:
                            log(f"[FAIL] Nu am reușit. Cod: {r.status_code}")

                time.sleep(random.uniform(0.7, 1.2))

            except Exception as e:
                log(f"[EROARE LOOP] {e}")
                time.sleep(2)

    except Exception as e:
        log(f"[EROARE GENERALĂ] {e}")
        time.sleep(10)