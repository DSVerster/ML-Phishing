import tkinter as tk
from tkinter import messagebox, scrolledtext

import requests

API_URL = "http://127.0.0.1:5050"


def get_text():
    text = email_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("No email", "Please paste an email first.")
    return text


def call_api(route, text, timeout):
    try:
        response = requests.post(f"{API_URL}/{route}", json={"text": text}, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        messagebox.showerror("API not running", "Could not connect to the API.\nStart it with: uvicorn api.main:app --port 5050")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    return None


def check_email():
    text = get_text()
    if not text:
        return
    result = call_api("predict", text, timeout=10)
    if result is None:
        return

    prob = result["phishing_probability"]
    if result["label"] == "phishing":
        result_label.config(text=f"PHISHING  ({prob * 100:.1f}% confidence)", fg="white", bg="#c0392b")
    else:
        result_label.config(text=f"LEGIT  ({(1 - prob) * 100:.1f}% confidence)", fg="white", bg="#27ae60")


def explain_email():
    text = get_text()
    if not text:
        return

    explain_box.config(state=tk.NORMAL)
    explain_box.delete("1.0", tk.END)
    explain_box.insert(tk.END, "Working out which words mattered... (about 20 seconds)")
    window.update()

    result = call_api("explain", text, timeout=120)
    explain_box.delete("1.0", tk.END)
    if result is None:
        explain_box.config(state=tk.DISABLED)
        return

    explain_box.insert(tk.END, "Words that influenced the result:\n\n")
    for item in result["words"]:
        if item["weight"] > 0:
            explain_box.insert(tk.END, f"  {item['word']:<20} -> phishing  ({item['weight']:+.4f})\n", "phish")
        else:
            explain_box.insert(tk.END, f"  {item['word']:<20} -> legit     ({item['weight']:+.4f})\n", "legit")
    explain_box.config(state=tk.DISABLED)


def clear():
    email_box.delete("1.0", tk.END)
    result_label.config(text="Paste an email and click Check Email", fg="black", bg="#ecf0f1")
    explain_box.config(state=tk.NORMAL)
    explain_box.delete("1.0", tk.END)
    explain_box.config(state=tk.DISABLED)


window = tk.Tk()
window.title("Phishing Email Detector")
window.geometry("650x720")

tk.Label(window, text="Phishing Email Detector", font=("Arial", 18, "bold")).pack(pady=10)

email_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, height=10, font=("Arial", 11))
email_box.pack(padx=15, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(window)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Check Email", command=check_email, width=15, font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Explain", command=explain_email, width=12, font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Clear", command=clear, width=10, font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

result_label = tk.Label(window, text="Paste an email and click Check Email", font=("Arial", 14, "bold"), bg="#ecf0f1", width=40, height=2)
result_label.pack(pady=5)

explain_box = tk.Text(window, height=12, font=("Consolas", 11), state=tk.DISABLED, bg="#fafafa")
explain_box.tag_config("phish", foreground="#c0392b")
explain_box.tag_config("legit", foreground="#27ae60")
explain_box.pack(padx=15, pady=10, fill=tk.BOTH)

window.mainloop()