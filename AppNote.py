#Import Libraries
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import time

#Setup Process
root = tk.Tk()
root.title("My Notepad")
root.geometry("800x600")

text_area = tk.Text(root, wrap='word', undo=True)
text_area.pack(expand=True, fill='both')

status_var = tk.StringVar()
status_var.set("Welcome to My Notepad")
status_bar = tk.Label(root, textvariable=status_var, anchor='w')
status_bar.pack(side='bottom', fill='x')

recent_files = []
recent_file_path = "recent.txt"
current_file_path = None  # Holds currently open file path

# Creating backups directory if not exists
os.makedirs("backups", exist_ok=True)

#Functions Implementation
def load_recent_files():
    if os.path.exists(recent_file_path):
        with open(recent_file_path, 'r') as f:
            files = [line.strip() for line in f if os.path.isfile(line.strip())]
            return files[:5]
    return []

def save_recent_files():
    with open(recent_file_path, 'w') as f:
        for file in recent_files[:5]:
            f.write(file + '\n')

def update_recent_files_menu():
    recent_menu.delete(0, tk.END)
    for file in recent_files:
        recent_menu.add_command(label=file, command=lambda f=file: open_recent_file(f))

def add_to_recent_files(path):
    if path in recent_files:
        recent_files.remove(path)
    recent_files.insert(0, path)
    save_recent_files()
    update_recent_files_menu()

def open_recent_file(file_path):
    global current_file_path
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, file.read())
        current_file_path = file_path
        root.title(f"{file_path} - My Notepad")
        status_var.set(f"Opened: {file_path}")
        add_to_recent_files(file_path)
    else:
        messagebox.showerror("File Not Found", "This file no longer exists.")
        recent_files.remove(file_path)
        save_recent_files()
        update_recent_files_menu()

def new_file():
    global current_file_path
    text_area.delete(1.0, tk.END)
    current_file_path = None
    root.title("Untitled - My Notepad")
    status_var.set("New File Created")

def open_file():
    global current_file_path
    file_path = filedialog.askopenfilename(defaultextension=".txt",
                                           filetypes=[("Text Files", ".txt"), ("All Files", ".*")])
    if file_path:
        with open(file_path, "r") as file:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, file.read())
        current_file_path = file_path
        root.title(f"{file_path} - My Notepad")
        status_var.set(f"Opened: {file_path}")
        add_to_recent_files(file_path)

def save_file():
    global current_file_path
    if not current_file_path:
        current_file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                        filetypes=[("Text Files", ".txt"), ("All Files", ".*")])
    if current_file_path:
        with open(current_file_path, "w") as file:
            file.write(text_area.get(1.0, tk.END))
        root.title(f"{current_file_path} - My Notepad")
        status_var.set(f"Saved: {current_file_path}")
        add_to_recent_files(current_file_path)
        create_backup(current_file_path)

def create_backup(path):
    if os.path.exists(path):
        filename = os.path.basename(path)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"backups/{filename}_{timestamp}.bak"
        with open(path, 'r') as original, open(backup_name, 'w') as backup:
            backup.write(original.read())
        status_var.set(f"Backup created: {backup_name}")

def auto_save():
    if current_file_path:
        with open(current_file_path, 'w') as file:
            file.write(text_area.get(1.0, tk.END))
        status_var.set(f"Auto-saved at {time.strftime('%H:%M:%S')}")
    root.after(30000, auto_save)  # 30 seconds

def exit_app():
    if messagebox.askokcancel("Exit", "Do you want to quit?"):
        root.destroy()

def find_text():
    word = simpledialog.askstring("Find", "Enter text to find:")
    if word:
        text_area.tag_remove("found", "1.0", tk.END)
        start_pos = "1.0"
        while True:
            start_pos = text_area.search(word, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(word)}c"
            text_area.tag_add("found", start_pos, end_pos)
            start_pos = end_pos
        text_area.tag_config("found", background="yellow", foreground="red")
        status_var.set(f"Results highlighted for '{word}'")

def make_bold():
    try:
        text_area.tag_add("bold", "sel.first", "sel.last")
        text_area.tag_config("bold", font=('Arial', 14, 'bold'))
        status_var.set("Bold text applied")
    except:
        messagebox.showinfo("Warning", "Please select text first!")

def make_italic():
    try:
        text_area.tag_add("italic", "sel.first", "sel.last")
        text_area.tag_config("italic", font=('Arial', 14, 'italic'))
        status_var.set("Italic text applied")
    except:
        messagebox.showinfo("Warning", "Please select text first!")

def update_status(event=None):
    content = text_area.get(1.0, "end-1c")
    words = len(content.split())
    characters = len(content)
    status_var.set(f"Words: {words} | Characters: {characters}")

text_area.bind('<KeyRelease>', update_status)

#Menu Bar
menu_bar = tk.Menu(root)

# File Menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", accelerator="Ctrl+N", command=new_file)
file_menu.add_command(label="Open", accelerator="Ctrl+O", command=open_file)
file_menu.add_command(label="Save", accelerator="Ctrl+S", command=save_file)

# Recent Files Submenu
recent_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Recent Files", menu=recent_menu)

# Exiting App Menu
file_menu.add_separator()
file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=exit_app)
menu_bar.add_cascade(label="File", menu=file_menu)

# Edit Menu
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Find", accelerator="Ctrl+F", command=find_text)
edit_menu.add_command(label="Bold", accelerator="Ctrl+B", command=make_bold)
edit_menu.add_command(label="Italic", accelerator="Ctrl+I", command=make_italic)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

root.config(menu=menu_bar)

#Shortcuts
root.bind("<Control-n>", lambda e: new_file())
root.bind("<Control-o>", lambda e: open_file())
root.bind("<Control-s>", lambda e: save_file())
root.bind("<Control-q>", lambda e: exit_app())
root.bind("<Control-f>", lambda e: find_text())
root.bind("<Control-b>", lambda e: make_bold())
root.bind("<Control-i>", lambda e: make_italic())

#Load Recents and Auto Save
recent_files = load_recent_files()
update_recent_files_menu()
auto_save()

root.mainloop()
