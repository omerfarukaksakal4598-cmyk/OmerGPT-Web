import tkinter as tk
from tkinter import messagebox

# =========================
# YAPAY ZEKA CEVAP FONKSİYONU
# =========================
def ai_answer(text):
    t = text.lower().strip()

    # Selamlaşma
    if t in ["selam", "selamün aleyküm", "selamun aleykum", "merhaba"]:
        return "Aleyküm selam 😊"

    # Hal hatır
    if t in ["nasılsın", "naber"]:
        return "İyiyim, teşekkür ederim 😊"

    # Hesaplama
    if t.startswith("hesapla"):
        try:
            expr = t.replace("hesapla", "")
            result = eval(expr)
            return f"Sonuç: {result}"
        except:
            return "Hesaplama hatası."

    # Oruç bilgisi
    if "oruç" in t:
        return (
            "Oruç, İslam'da imsak vaktinden iftara kadar "
            "yemek, içmek ve bazı davranışlardan uzak durmaktır."
        )

    # Hava durumu (offline örnek)
    if "hava" in t:
        return "Canlı hava durumu için internet gerekir."

    # Bilinmeyen
    return "Bu konuda bilgim yok."


# =========================
# MESAJ GÖNDERME
# =========================
def send():
    user_text = entry.get().strip()
    if not user_text:
        return

    # Kullanıcı mesajı
    chat_box.insert("end", f"Sen: {user_text}\n")
    entry.delete(0, "end")

    # Yapay zeka cevabı
    reply = ai_answer(user_text)
    chat_box.insert("end", f"🤖 Yapay Zeka: {reply}\n\n")
    chat_box.see("end")


# =========================
# MİNİ OYUN
# =========================
def mini_game():
    messagebox.showinfo(
        "Mini Oyun",
        "🎮 Mini oyun yakında eklenecek!"
    )


# =========================
# ARAYÜZ
# =========================
root = tk.Tk()
root.title("Akıllı Chatbot + Oyun")
root.geometry("700x500")

chat_box = tk.Text(root, font=("Arial", 11))
chat_box.pack(expand=True, fill="both")

entry = tk.Entry(root, font=("Arial", 11))
entry.pack(fill="x", padx=5, pady=5)

button_frame = tk.Frame(root)
button_frame.pack()

send_btn = tk.Button(button_frame, text="Gönder", width=15, command=send)
send_btn.pack(side="left", padx=5)

game_btn = tk.Button(button_frame, text="Mini Oyun", width=15, command=mini_game)
game_btn.pack(side="left", padx=5)

root.mainloop()
