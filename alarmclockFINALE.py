import tkinter as tk
from datetime import datetime, timedelta
import winsound, threading, time, os, uuid

# ---------------- Window ----------------
root = tk.Tk()
root.title("Alarm Clock For LEGENDS")
root.geometry("780x720")
root.configure(bg="black")

# ---------------- Data ----------------
alarms = []
sound_dir = r"C:\Windows\Media"

# ---------------- Clock ----------------
clock = tk.Label(root, font=("Consolas",55,"bold"), bg="black", fg="cyan")
clock.place(x=120, y=20)

def update_clock():
    clock.config(text=datetime.now().strftime("%H:%M:%S"))
    root.after(1000, update_clock)

# ---------------- Message ----------------
msg = tk.Label(root, font=("Consolas",16), bg="black", fg="yellow")
msg.place(x=50, y=105)

def set_msg(text):
    msg.config(text=text)

# ---------------- Validation ----------------
def valid_h(v): return v=="" or (v.isdigit() and 0<=int(v)<=23)
def valid_ms(v): return v=="" or (v.isdigit() and 0<=int(v)<=59)
vrh = (root.register(valid_h), "%P")
vrm = (root.register(valid_ms), "%P")

# ---------------- Time Inputs ----------------
h = tk.Spinbox(root, from_=0, to=23, width=4, font=("Consolas",30),
               bg="black", fg="white", justify="center", wrap=True,
               validate="key", validatecommand=vrh)
h.place(x=160, y=240); h.delete(0,"end"); h.insert(0,"00")

m = tk.Spinbox(root, from_=0, to=59, width=4, font=("Consolas",30),
               bg="black", fg="white", justify="center", wrap=True,
               validate="key", validatecommand=vrm)
m.place(x=290, y=240); m.delete(0,"end"); m.insert(0,"00")

s = tk.Spinbox(root, from_=0, to=59, width=4, font=("Consolas",30),
               bg="black", fg="white", justify="center", wrap=True,
               validate="key", validatecommand=vrm)
s.place(x=420, y=240); s.delete(0,"end"); s.insert(0,"00")

# ---------------- Snooze ----------------
tk.Label(root, text="Snooze (min)", font=("Consolas",14), bg="black", fg="white").place(x=160, y=315)
snooze = tk.Spinbox(root, from_=1, to=60, width=5, font=("Consolas",14), bg="black", fg="white", wrap=True)
snooze.place(x=290, y=315); snooze.delete(0,"end"); snooze.insert(0,"5")

# ---------------- Sounds ----------------
tk.Label(root, text="Sound", font=("Consolas",14), bg="black", fg="white").place(x=160, y=350)
sound_var = tk.StringVar()

def load_sounds():
    files = [f for f in os.listdir(sound_dir) if f.lower().endswith(".wav")]
    sound_var.set(files[0] if files else "")
    menu["menu"].delete(0, "end")
    for f in files:
        menu["menu"].add_command(label=f, command=lambda x=f: sound_var.set(x))

menu = tk.OptionMenu(root, sound_var, "")
menu.config(font=("Consolas",12), bg="black", fg="white")
menu.place(x=290, y=350)
load_sounds()

# ---------------- Alarms List + Scroll ----------------
tk.Label(root, text="Alarms", font=("Consolas",14), bg="black", fg="white").place(x=50, y=420)

list_frame = tk.Frame(root, bg="black")
list_frame.place(x=50, y=450)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

box = tk.Listbox(list_frame, width=50, height=10, font=("Consolas",14),
                 bg="black", fg="white", yscrollcommand=scrollbar.set)
box.pack(side="left")
scrollbar.config(command=box.yview)

# ---------------- Buttons frame ----------------
frame = tk.Frame(root, bg="#222222", width=690, height=100)
frame.place(x=50, y=640)

# ---------------- Logic ----------------
def play_sound(name):
    path = os.path.join(sound_dir, name)
    if os.path.exists(path):
        winsound.PlaySound(path, winsound.SND_LOOP | winsound.SND_ASYNC)

def refresh(i):
    a = alarms[i]
    txt = f"{a['time']} - {a['sound']}" + ("  RINGING" if a["ring"] else "")
    box.delete(i); box.insert(i, txt); box.selection_set(i)

def add_alarm():
    t = f"{int(h.get()):02d}:{int(m.get()):02d}:{int(s.get()):02d}"
    alarms.append({"id": uuid.uuid4(), "time": t, "sound": sound_var.get(), "ring": False})
    box.insert(tk.END, f"{t} - {sound_var.get()}")
    set_msg(f"Alarm is set to {t}")

def delete_alarm():
    sel = box.curselection()
    if not sel: return
    i = sel[0]
    del alarms[i]
    box.delete(i)
    set_msg("Alarm deleted")

def stop_alarm():
    sel = box.curselection()
    if not sel: return
    i = sel[0]
    alarms[i]["ring"] = False
    winsound.PlaySound(None, winsound.SND_PURGE)
    refresh(i)
    set_msg("Alarm stopped")

def snooze_alarm():
    sel = box.curselection()
    if not sel: return
    i = sel[0]
    a = alarms[i]
    mins = int(snooze.get())
    hh, mm, ss = map(int, a["time"].split(":"))
    nt = (datetime.now().replace(hour=hh, minute=mm, second=ss) + timedelta(minutes=mins)).strftime("%H:%M:%S")
    a["time"] = nt
    a["ring"] = False
    winsound.PlaySound(None, winsound.SND_PURGE)
    refresh(i)
    set_msg(f"Snoozed for {mins} minutes")

def check():
    while True:
        now = datetime.now().strftime("%H:%M:%S")
        for i, a in enumerate(alarms):
            if a["time"] == now and not a["ring"]:
                a["ring"] = True
                play_sound(a["sound"])
                refresh(i)
                set_msg("WAKE UP!")
        time.sleep(0.5)

# ---------------- Buttons ----------------
tk.Button(frame, text="Add Alarm", font=("Consolas",14,"bold"), bg="#00aaff", fg="white", width=12, command=add_alarm).place(x=10,y=10)
tk.Button(frame, text="Delete", font=("Consolas",14,"bold"), bg="#888888", fg="white", width=12, command=delete_alarm).place(x=170,y=10)
tk.Button(frame, text="Stop", font=("Consolas",14,"bold"), bg="#ff4444", fg="white", width=12, command=stop_alarm).place(x=330,y=10)
tk.Button(frame, text="Snooze", font=("Consolas",14,"bold"), bg="#ffaa00", fg="black", width=12, command=snooze_alarm).place(x=490,y=10)

# ---------------- Start ----------------
update_clock()
threading.Thread(target=check, daemon=True).start()
root.mainloop()
