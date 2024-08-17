VERSION = "v1.0.2"


import tkinter as tk
from tkinter import ttk, font 
from tkinter import filedialog
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import sv_ttk
import os
import time
import random
import sys
import webbrowser
from client import *

import speedtest
from multiprocessing.pool import ThreadPool
import threading
import requests
import zipfile


file_processing: list = []
information: list = []
address_client: str = os.getcwd()
address_saved_file: str = os.getcwd() + "./Downloaded Files"
error: str = ""


HEADING_SIZE = 14
HEADING_2_SIZE = 11
WORD_SIZE = 10

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MenuBar(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)

        self.update_app(VERSION, False)

        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Open File", command=self.open_file)
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_command(label="Clear Processing", command=self.clear_processing)
        file_menu.add_command(label="Clear History", command=self.clear_history)
        file_menu.add_command(label="Clear Messages", command=self.clear_messages)
        file_menu.add_separator()
        file_menu.add_command(label="Reset Server", command=self.reset_server)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=parent.quit)
        self.add_cascade(label="Tasks", menu=file_menu)
        
        setting_menu = tk.Menu(self, tearoff=0)
        sub_menu = tk.Menu(setting_menu, tearoff=0)
        sub_menu.add_command(label="Light", command=lambda: sv_ttk.set_theme("light"))
        sub_menu.add_command(label="Dark", command=lambda: sv_ttk.set_theme("dark"))
        setting_menu.add_cascade(
            label="Theme",
            menu=sub_menu,
        )
        setting_menu.add_command(label="Address Saved File", command=self.change_address_saved_file)
        self.add_cascade(label="Settings", menu=setting_menu)

        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        help_menu.add_command(label="Contact Support", command=lambda: webbrowser.open("https://www.facebook.com/profile.php?id=100012655329823"))
        help_menu.add_command(label="Update", command=lambda: self.update_app(VERSION, True))
        self.add_cascade(label="Help", menu=help_menu)

    def set_dependencies(self, list_file_processing, list_file_processed, client_server_folder, process_frame):
        self.list_file_processing = list_file_processing
        self.list_file_processed = list_file_processed
        self.client_server_folder = client_server_folder
        self.process_frame = process_frame

    def clear_messages(self):
        self.process_frame.text.delete("1.0", "end")

    def change_address_saved_file(self):
        global address_saved_file
        address_saved_file = filedialog.askdirectory()
        if address_saved_file == "":
            return
        self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + f" SUCCESS: Address saved file has been changed to {address_saved_file}\n", "success")
        self.process_frame.text.insert("end", "----------------------------------\n", "info")
        self.process_frame.text.yview_moveto(1)

    def about(self):
        messagebox.showinfo("About", "This is a simple client-server application. It allows you to download files from the server and upload files to the server.\n ----------------- \n The application is developed by a group of 3 students: Nguyễn Đình Mạnh, Châu Đình Phúc, Nguyễn Trọng Nhân.")    

    def theme(self):
        sv_ttk.set_theme("dark") if sv_ttk.get_theme() == "light" else sv_ttk.set_theme("light")
    
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path == "":
            return
        name_file = os.path.basename(file_path)
        data = (file_path, name_file, "Upload")
        self.list_file_processing.update_treeview_processing(data)

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path == "":
            return
        # Delete all item in tree
        for item in self.client_server_folder.tree_Client.get_children():
            self.client_server_folder.tree_Client.delete(item)
        # Add new item
        self.client_server_folder.list_folder(self.client_server_folder.tree_Client, '', folder_path)
        global address_client
        address_client = folder_path

        self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + f" SUCCESS: Folder {folder_path} has been opened\n", "success")
        self.process_frame.text.insert("end", "----------------------------------\n", "info")
        self.process_frame.text.yview_moveto(1)

    def reset_server(self):
        self.client_server_folder.tree_Server.delete(*self.client_server_folder.tree_Server.get_children())
        self.client_server_folder.list_files()


        self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + " SUCCESS: Server folder has been reset\n", "success")
        self.process_frame.text.insert("end", "----------------------------------\n", "info")
        self.process_frame.text.yview_moveto(1)

    def update_app(self, current_version, announcement):
        try:
            url = f"https://api.github.com/repos/doanxem99/ClientServer/releases"
            response = requests.get(url)
            # Get the latest release info
            if response.status_code == 200:
                release_info = response.json()
                zip_url = release_info[0].get('zipball_url')
                latest_version = release_info[0].get('tag_name')
                if latest_version > current_version:
                    answer = messagebox.askokcancel("Update", f"A new version {latest_version} is available. Do you want to update?")
                    if answer:
                        with open("./update.zip", "wb") as file:
                            response_zip = requests.get(zip_url)
                            file.write(response_zip.content)
                        with zipfile.ZipFile("./update.zip") as zip_ref:
                            zip_ref.extractall(".")
                        os.remove("./update.zip")
                        # Move the new version to the current directory
                        os.system(f"mv ./doanxem99-ClientServer-*/* ./")
                        os.system(f"rm -rf ./doanxem99-ClientServer-*")
                        messagebox.showinfo("Update", "The application has been updated. Please restart the application.")
                elif announcement == True:
                    messagebox.showinfo("Update", "You are using the latest version.")
                    
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Update", "Error: Cannot connect to the server. Please check your internet connection.")

    def clear_processing(self):
        self.list_file_processing.erase_all_data()
        file_processing.clear()

        self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + " SUCCESS: All files have been cleared\n", "success")
        self.process_frame.text.insert("end", "----------------------------------\n", "info")
        self.process_frame.text.yview_moveto(1)
    def clear_history(self):
        self.list_file_processed.erase_all_data()

        self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + " SUCCESS: All history has been cleared\n", "success")
        self.process_frame.text.insert("end", "----------------------------------\n", "info")
        self.process_frame.text.yview_moveto(1)

class InputInfor(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        custom_label = ttk.Label(self, text="Server Settings", font=("Arial", HEADING_SIZE, "bold"))
        self['labelwidget'] = custom_label

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.add_widgets()
        self.bind_widgets()
    
    def set_dependencies(self, process_frame):
        self.process_frame = process_frame

    def add_widgets(self):
        self.label_ip_address = ttk.Label(self, text="IP Address: ", font=("Arial", HEADING_2_SIZE))
        self.label_ip_address.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        self.ip_address = ttk.Entry(self, width=5)
        self.ip_address.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.image_process_button = Image.open(resource_path("assets/process_button.png"))
        self.image_process_button = self.image_process_button.resize((30, 20))
        self.image_process_button = ImageTk.PhotoImage(self.image_process_button)
        self.process_button = ttk.Button(self, image=self.image_process_button, style="Accent.TButton", command=lambda: self.process())
        self.process_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.label_number_thread = ttk.Label(self, text="Number of Threads: ", font=("Arial", HEADING_2_SIZE))
        self.label_number_thread.grid(row=2, column=0, padx=0, pady=0, sticky="w")

        self.number_thread = ttk.Scale(self, from_=1, to=5, orient="horizontal", length=50)
        self.number_thread.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        # Display the current value of the scale
        self.number_thread.set(5)
        self.display_number_thread = ttk.Combobox(self, values=[i for i in range(1, 6)], width=2)
        self.display_number_thread.grid(row=3, column=1, padx=5, pady=0, sticky="ew")
        self.display_number_thread.set(5)

    def bind_widgets(self):
        self.ip_address.bind("<FocusOut>", self.validate_ip_address)
        self.ip_address.bind("<FocusIn>", self.validate_ip_address)
        self.ip_address.bind("<KeyRelease>", self.validate_ip_address)

        self.number_thread.bind("<ButtonRelease-1>", self.update_combobox_number_thread)
        self.number_thread.bind("<Enter>", lambda event: self.number_thread.config(cursor="hand2"))
        self.number_thread.bind("<Leave>", lambda event: self.number_thread.config(cursor="arrow"))

        self.display_number_thread.bind("<<ComboboxSelected>>", self.update_scale_number_thread)
        self.display_number_thread.bind("<Enter>", lambda event: self.display_number_thread.config(cursor="hand2"))
        self.display_number_thread.bind("<Leave>", lambda event: self.display_number_thread.config(cursor="arrow"))

        self.process_button.bind("<Enter>", lambda event: self.process_button.config(cursor="hand2"))
        self.process_button.bind("<Leave>", lambda event: self.process_button.config(cursor="arrow"))

    def process(self, event=None):
        if self.validate_ip_address() == False:
            self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + " ERROR: Invalid IP Address\n", "error")
            self.process_frame.text.insert("end", "Please enter a valid IP Address\n", "error")
            self.process_frame.text.insert("end", "----------------------------------\n", "info")
            self.process_frame.text.yview_moveto(1)
            return
        global address_saved_file
        status = do_request([self.ip_address.get(), "IP"], address_saved_file)
        if status != "OK":
            print(status)
            self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + " ERROR: Cannot connect to the server\n", "error")
            self.process_frame.text.insert("end", "Please check your IP Address\n", "error")
            self.process_frame.text.insert("end", "----------------------------------\n", "info")
            self.process_frame.text.yview_moveto(1)
            return
        global SERVER_IP
        SERVER_IP = self.ip_address.get()
        self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + f" SUCCESS: IP Address has been changed to {SERVER_IP}\n", "success")
        self.process_frame.text.insert("end", "----------------------------------\n", "info")
        self.process_frame.text.yview_moveto(1)

    def update_combobox_number_thread(self, event=None):
        number_thread = int(self.number_thread.get())
        self.display_number_thread.set(number_thread)

    def update_scale_number_thread(self, event=None):
        number_thread = int(self.display_number_thread.get())
        self.number_thread.set(number_thread)



    def validate_ip_address(self, event=None):
        ip_address = self.ip_address.get()
        if ip_address == "":
            self.ip_address["foreground"] = "black"
            return True
        try:
            socket.inet_aton(ip_address)
            self.ip_address["foreground"] = "white"
            return True
        except socket.error:
            self.ip_address["foreground"] = "red"
            return False

        


class CheckConnection(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, padding=5)
        self.add_widgets()
        self.bind_widgets()

    def add_widgets(self):
        custom_label = ttk.Label(self, text="Check Connection", font=("Arial", HEADING_SIZE, "bold"))
        self["labelwidget"] = custom_label

        for i in range(8):
            self.rowconfigure(i, weight=1)

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)

        self.label_download = ttk.Label(self, text="Download: ", font=("Arial", HEADING_2_SIZE))
        self.label_download.grid(row=0, column=0, padx=2, pady=(5, 2), sticky="we")

        self.progress_download = ttk.Progressbar(self, length=165, mode="determinate", value=0, maximum=100)
        self.progress_download.grid(row=1, column=0, padx=2, pady=2, sticky="we")

        self.label_upload = ttk.Label(self, text="Upload: ", font=("Arial", HEADING_2_SIZE))
        self.label_upload.grid(row=2, column=0, padx=2, pady=2, sticky="we")

        self.progress_upload = ttk.Progressbar(self, length=165, mode="determinate", value=0, maximum=100)
        self.progress_upload.grid(row=3, column=0, padx=2, pady=2, sticky="we")

        self.label_ping = ttk.Label(self, text="Ping: ", font=("Arial", HEADING_2_SIZE))
        self.label_ping.grid(row=4, column=0, padx=2, pady=2, sticky="we")

        self.progress_ping = ttk.Progressbar(self, length=165, mode="determinate", value=0, maximum=100)
        self.progress_ping.grid(row=5, column=0, padx=2, pady=(2, 2), sticky="we")

        self.progress_complete = ttk.Progressbar(self, length=200, mode="determinate", value=0, maximum=100, orient="vertical")
        self.progress_complete.grid(row=0, column=1, rowspan=6, padx=2, pady=(2, 2), sticky="we")


        self.button = ttk.Button(self, text="Test", style="Accent.TButton", command=self.start_speed_test)
        self.button.grid(row=6, column=0, columnspan=2, padx=2, pady=(2, 5), sticky="we")

    def bind_widgets(self):
        self.button.bind("<Enter>", lambda event: self.button.config(cursor="hand2"))
        self.button.bind("<Leave>", lambda event: self.button.config(cursor="arrow"))

    def start_speed_test(self):
        self.progress_download["value"] = 0
        self.progress_upload["value"] = 0
        self.progress_ping["value"] = 0
        self.progress_complete["value"] = 0

        self.button.config(state=tk.DISABLED)
        threading.Thread(target=self.run_speed_test).start()

    def run_speed_test(self):
        pool = ThreadPool(processes=4)
        pool.apply_async(self.animation_progress, (self.progress_complete, 0, 95))

        self.get_speed_results()

        # Download speed
        self.progress_download["value"] = self.download_speed / 1000000
        # Upload speed
        self.progress_upload["value"] = self.upload_speed / 1000000
        # Ping
        self.progress_ping["value"] = self.ping

        self.progress_complete["value"] = 100

        # Update the label
        self.label_download["text"] = f"Download: {self.download_speed / 1000000:.2f} Mbps"
        self.label_upload["text"] = f"Upload: {self.upload_speed / 1000000:.2f} Mbps"
        self.label_ping["text"] = f"Ping: {self.ping:.2f} ms"
        if self.ping > 120:
            self.label_ping["foreground"] = "red"
        elif self.ping > 50:
            self.label_ping["foreground"] = "orange"
        else:
            self.label_ping["foreground"] = "green"
        if self.download_speed < 1000000 * 5:
            self.label_download["foreground"] = "red"
        elif self.download_speed < 5000000 * 5:
            self.label_download["foreground"] = "orange"
        else:
            self.label_download["foreground"] = "green"
        if self.upload_speed < 1000000 * 3:
            self.label_upload["foreground"] = "red"
        elif self.upload_speed < 5000000 * 3:
            self.label_upload["foreground"] = "orange"
        else:
            self.label_upload["foreground"] = "green"

        # Animate the progress bar with threading
        pool.apply_async(self.animation_progress, (self.progress_complete, 95, 100))

        pool.apply_async(self.animation_speed, (self.download_speed / 1000000, self.progress_download, 1))
        pool.apply_async(self.animation_speed, (self.upload_speed / 1000000, self.progress_upload, 1))
        pool.apply_async(self.animation_speed, (max(0, min(120.0 - self.ping, 100)), self.progress_ping, 1))
        
        self.button.config(state=tk.NORMAL)

    def get_speed_results(self):
        st = speedtest.Speedtest()
        self.download_speed = st.download()
        self.upload_speed = st.upload()
        self.ping = st.results.ping

    def animation_speed(self, speed_value, progress_bar, scaling_factor):
        max_value = speed_value * scaling_factor
        increment = max_value / 100 
        for i in range(int(max_value) + 1):
            if i > 0.9 * max_value:
                break
            progress_bar['value'] = i
            progress_bar.update()
            time.sleep(0.02)

    def animation_progress(self, progress_bar, begin, end):
        for i in range(begin, end + 1):
            progress_bar['value'] = i
            progress_bar.update()
            time.sleep(0.20)

class ClientServerFolder(ttk.LabelFrame):
    def __init__(self, parent, process_frame):
        super().__init__(parent)

        self.folder_image = Image.open(resource_path("assets/folder2.png"))
        self.folder_image = self.folder_image.resize((30, 30))
        self.folder_image = ImageTk.PhotoImage(self.folder_image)

        self.custom_label = ttk.Label(self, text="Client-Server Folder", 
                                      image=self.folder_image, compound="left", 
                                      font=("Arial", HEADING_SIZE, "bold"))
        self['labelwidget'] = self.custom_label

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.process_frame = process_frame
        self.add_widgets()

    def set_dependencies(self, list_file_processing):
        self.list_file_processing = list_file_processing

    def add_widgets(self):

        # Server and Client tabs
        self.Server = ttk.Frame(self.notebook)
        self.notebook.add(self.Server, text="Server")

        self.Client = ttk.Frame(self.notebook)
        self.notebook.add(self.Client, text="Client")

        # Server
        self.scrollbar_v = ttk.Scrollbar(self.Server, orient="vertical")
        self.scrollbar_v.pack(side="right", fill="y")
        self.scrollbar_h = ttk.Scrollbar(self.Server, orient="horizontal")
        self.scrollbar_h.pack(side="bottom", fill="x")

        self.tree_Server = ttk.Treeview(
            self.Server,
            columns=(1),
            height=10,
            selectmode="browse",
            show=("tree",),
            yscrollcommand=self.scrollbar_v.set,
            xscrollcommand=self.scrollbar_h.set,
            cursor="hand2"
        )

        self.scrollbar_v.config(command=self.tree_Server.yview)
        self.scrollbar_h.config(command=self.tree_Server.xview)
        self.tree_Server.pack(expand=True, fill="both")
        self.list_files()


        # Client
        self.scrollbar_v = ttk.Scrollbar(self.Client, orient="vertical")
        self.scrollbar_v.pack(side="right", fill="y")
        self.scrollbar_h = ttk.Scrollbar(self.Client, orient="horizontal")
        self.scrollbar_h.pack(side="bottom", fill="x")

        self.tree_Client = ttk.Treeview(
            self.Client,
            columns=1,
            height=10,
            selectmode="browse",
            show=("tree",),
            yscrollcommand=self.scrollbar_v.set,
            xscrollcommand=self.scrollbar_h.set,
            cursor="hand2"
        )

        self.scrollbar_v.config(command=self.tree_Client.yview)
        self.scrollbar_h.config(command=self.tree_Client.xview)
        self.tree_Client.pack(expand=True, fill="both")
        self.list_folder(self.tree_Client, '', '.')
        self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + " SUCCESS: Client folder has been opened\n", "success")
        self.process_frame.text.insert("end", "Current directory: " + os.getcwd() + "\n", "success")
        self.process_frame.text.insert("end", "----------------------------------\n", "info")


        # Bind double-click event
        self.tree_Server.bind("<Double-1>", lambda event: self.on_double_click("Download"))
        self.tree_Client.bind("<Double-1>", lambda event: self.on_double_click("Upload"))

    def on_double_click(self, method):
        if method == "Download":
            self.tree = self.tree_Server
        else:
            self.tree = self.tree_Client
        item = self.tree.selection()[0]
        name_item = self.tree.item(item, 'text')
        # Check if the item is a file
        is_file = False
        for character in name_item:
            if character == ".":
                is_file = True
                break

        if is_file == False:
            return
        file_path = address_client + "/" + self.get_full_path(item)

        data = (file_path, name_item, method)
        self.list_file_processing.update_treeview_processing(data)

    def get_full_path(self, item):
        path = [self.tree.item(item, 'text')]
        parent = self.tree.parent(item)
        while parent:
            path.insert(0, self.tree.item(parent, 'text'))
            parent = self.tree.parent(parent)
        return os.path.join(*path)
    
    def list_files(self):
        (error, data) = call_list()
        if error != "":
            messagebox.showerror("Error", "An error occurred while connecting to the server \n --------------- \n " + "You must enter the correct IP Address to connect to the server")
            self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + " ERROR: An error occurred while connecting to the server\n", "error")
            self.process_frame.text.insert("end", "You must enter the correct IP Address to connect to the server\n", "error")
            self.process_frame.text.insert("end", "----------------------------------\n", "info")
            self.process_frame.text.yview_moveto(1)
        else: 
            self.convert_data_server(data)
            self.process_frame.text.insert("end", time.strftime("%H:%M:%S") + " SUCCESS: Server folder has been opened\n", "success")
            self.process_frame.text.insert("end", "----------------------------------\n", "info")

    def convert_data_server(self, data):
        parent: list = [''] 
        prev_level = 0
        for item in data:
            if item == "":
                continue
            level, name = item.split(' ', 1)
            # print(level + "  |   " + name)
            level = int(level)
            pa = self.tree_Server.insert(parent[level - 1], 'end', text=name)
                    
            if level == len(parent):
                parent.append(pa)
            else:
                parent[level] = pa

    def list_folder(self, tree, parent, path):
        try:
            for p in os.listdir(path):
                abspath = os.path.join(path, p)
                isdir = os.path.isdir(abspath)
                oid = tree.insert(parent, 'end', text=p, open=False)
                if isdir:
                    self.list_folder(tree, oid, abspath)
        except PermissionError:
            # Skip directories that raise a permission error
            pass
            


class ProcessFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=20)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=20)

        self.add_widgets()
        self.bind_widgets()

    def add_widgets(self):
        
        # Download progress bar
        self.progress = ttk.Progressbar(self, length = 300, mode = "determinate", value = 0, maximum = 100)
        self.progress.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="new")

        # Percentage
        # Clear the progress label when the progress bar is full
        self.progress_label = ttk.Label(self, text="0%", font=("Arial", WORD_SIZE, "bold"))
        self.progress_label.place(in_=self.progress, relx=0.5, rely=0.5, anchor="center")

        # Button
        self.image_reset = Image.open(resource_path("assets/reset_button_2.png"))
        self.image_reset = self.image_reset.resize((30, 20))
        self.image_reset = ImageTk.PhotoImage(self.image_reset)
        self.reset_button = ttk.Button(self, image=self.image_reset, style="Accent.TButton", command=self.reset_server)
        self.reset_button.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="new")

        self.button = ttk.Button(self, text="RUN", style="Accent.TButton", command=self.prepare_download, width=15)
        self.button.grid(row=1, column=1, columnspan=2, padx=(5, 5), pady=5, sticky="nwe")

        self.image_folder = Image.open(resource_path("assets/folder.png"))
        self.image_folder = self.image_folder.resize((30, 20))
        self.image_folder = ImageTk.PhotoImage(self.image_folder)
        self.folder_button = ttk.Button(self, image=self.image_folder, style="Accent.TButton", command=self.open_folder)
        self.folder_button.grid(row=1, column=3, padx=5, pady=5, sticky="new")

        self.file_image = Image.open(resource_path("assets/file3.png"))
        self.file_image = self.file_image.resize((30, 20))
        self.file_image = ImageTk.PhotoImage(self.file_image)
        self.file_button = ttk.Button(self, image=self.file_image, style="Accent.TButton", command=self.open_file)
        self.file_button.grid(row=1, column=4, padx=(5, 10), pady=5, sticky="new")

        # List of Error and Warning messages using scrolltext like ttk
        self.text = tk.Text(self, wrap="word", height=8, width=25, font=("Arial", WORD_SIZE))
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=vsb.set)
        self.text.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")


        self.text.tag_configure("error", foreground="red")
        self.text.tag_configure("warning", foreground="orange")
        self.text.tag_configure("success", foreground="green")
        self.text.tag_configure("info", foreground="white")

    def bind_widgets(self):
        self.reset_button.bind("<Enter>", lambda event: self.show_tip("reset"))
        self.reset_button.bind("<Leave>", lambda event: self.hide_tip("reset"))

        self.button.bind("<Enter>", lambda event: self.show_tip("run"))
        self.button.bind("<Leave>", lambda event: self.hide_tip("run"))

        self.folder_button.bind("<Enter>", lambda event: self.show_tip("folder"))
        self.folder_button.bind("<Leave>", lambda event: self.hide_tip("folder"))

        self.file_button.bind("<Enter>", lambda event: self.show_tip("file"))
        self.file_button.bind("<Leave>", lambda event: self.hide_tip("file"))

    def show_tip(self, option, event=None):
        if option == "reset":
            self.tip = tk.Label(self, text="Reset Server", bg="black", fg="white")
            self.tip.place(in_=self.reset_button, relx=0.5, rely=1.5, anchor="center")
        elif option == "run":
            self.tip = tk.Label(self, text="Start Download/Upload", bg="black", fg="white")
            self.tip.place(in_=self.button, relx=0.5, rely=1.5, anchor="center")
        elif option == "folder":
            self.tip = tk.Label(self, text="Open Folder", bg="black", fg="white")
            self.tip.place(in_=self.folder_button, relx=0.5, rely=1.5, anchor="center")
        elif option == "file":
            self.tip = tk.Label(self, text="Open File", bg="black", fg="white")
            self.tip.place(in_=self.file_button, relx=0.5, rely=1.5, anchor="center")


    def hide_tip(self, option, event=None):
        self.tip.place_forget()
        

    def reset_server(self):
        self.menu_bar.reset_server()

    def open_folder(self):
        self.menu_bar.open_folder()
    
    def open_file(self):
        self.menu_bar.open_file()

    def set_dependencies(self, list_file_processing, list_file_processed, input_person, menu_bar):
        self.list_file_processing = list_file_processing
        self.list_file_processed = list_file_processed
        self.input_person = input_person
        self.menu_bar = menu_bar

    def error_message(self):
        # If list of files processing is empty, display an error message
        if len(file_processing) == 0:
            self.text.insert("end", time.strftime("%H:%M:%S") + " ERROR: No files to process\n", "error")
            self.text.insert("end", "Please select files to process\n", "error")
            self.text.insert("end", "----------------------------------\n", "info")   

            self.text.yview_moveto(1)
            return True
        return False
    
    def delete_tree(self):
        self.text.delete("1.0", "end")


    def prepare_download(self):
        self.text.insert("end", time.strftime("%H:%M:%S") + " SUCCESS: Start processing files\n", "success")
        self.text.insert("end", "Number of threads: " + do_request([str(int(self.input_person.number_thread.get())), "MAX_THREADS"], address_saved_file) + "\n", "success")
        self.text.insert("end", "WARNING: The process may take a long time to complete\n", "warning")
        self.text.insert("end", "Please wait...\n", "info")
        self.text.insert("end", "----------------------------------\n", "info")
        self.text.yview_moveto(1)
        bruh = threading.Thread(target=self.start_downloads).start()


    # Simulate download
    def start_downloads(self):


        if self.error_message() == True:
            self.button.configure(style="Toolbutton.TButton")
            return
        else:
            self.button.configure(style="Accent.TButton")

            self.text.yview_moveto(1)   
        global address_saved_file

        # Stimulation download progress bar
        self.progress["value"] = 0
        
        downloaded = 0
        uploaded = 0
        error_files = 0
        
        # Upload and download files
        size = len(file_processing)
        for item in file_processing:
            if item[2] == "Download":
                downloaded += 1
                request = [item[1], item[2]]
            else:
                uploaded += 1
                request = [item[0], item[2]]
            status = do_request(request, address_saved_file)
            if status == "Done":
                self.text.insert("end", time.strftime("%H:%M:%S") + f" SUCCESS: File {item[1]} is {item[2]}ed\n", "success")
                self.text.insert("end", "----------------------------------\n", "info")
                self.text.yview_moveto(1)
                self.list_file_processed.update_treeview_processed(item)
            else:
                self.text.insert("end", time.strftime("%H:%M:%S") + f" ERROR: File {item[1]} cannot be {item[2]}ed\n", "error")
                self.text.insert("end", status + "\n", "error")
                self.text.insert("end", "----------------------------------\n", "info")
                self.text.yview_moveto(1)
                if item[2] == "Download":
                    downloaded -= 1
                else:
                    uploaded -= 1
                error_files += 1
            self.progress["value"] += (file_processing.index(item) + 1) * 100 / size
            self.progress_label["text"] = f"{int(self.progress['value'])}%"
            self.update_idletasks()
        self.progress["value"] = 100
        self.progress_label["text"] = "100%"
        self.update_idletasks()


            
        # Display the result
        if error_files == 0:
            self.text.insert("end", time.strftime("%H:%M:%S") + " SUCCESS: All files have been processed.\n", "success")
        else:
            self.text.insert("end", time.strftime("%H:%M:%S") + f" ERROR: {error_files} files cannot be processed.\n", "error")
        self.text.insert("end", f"{downloaded} files have been downloaded.\n", "success")
        self.text.insert("end", f"{uploaded} files have been uploaded\n", "success")
        self.text.insert("end", f"All downloaded files are saved at {address_saved_file}\n", "success")
        self.text.insert("end", "----------------------------------\n", "info")

        self.text.yview_moveto(1)

        file_processing.clear()
        self.list_file_processing.erase_all_data()


# List of files that have been processed or are in the process of being processed
class FilesProcessing(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        custom_label = ttk.Label(self, text="Files Processing", font=("Arial", HEADING_SIZE, "bold"))
        self['labelwidget'] = custom_label

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.add_widgets()

    def add_widgets(self):

        # Treeview for files processing
        self.tree_processing = ttk.Treeview(
            self, columns=(1, 2), show="headings", cursor="hand2")
        self.tree_processing.pack(expand=True, fill="both")

    
        self.tree_processing.heading(1, text="File Name")
        self.tree_processing.heading(2, text="Status")

        self.tree_processing.column(1, width=200)
        self.tree_processing.column(2, width=100)

        self.tree_processing.drop_target_register(DND_FILES)
        self.tree_processing.dnd_bind("<<Drop>>", self.drop)

        # Erase data when user double-clicks on the file
        self.tree_processing.bind(
            "<Double-1>", lambda event: self.erase_treeview_data(self.tree_processing.selection()[0]))
        
    def set_dependencies(self, process_frame):
        self.process_frame = process_frame

    def drop(self, event):
        file_path = event.data
        # Delete the file:// prefix and '}' or '{' characters
        for character in "{}":
            file_path = file_path.replace(character, "")


        name_file = os.path.basename(file_path)
        data = (file_path, name_file, "Upload")
        self.update_treeview_processing(data)

    def erase_treeview_data(self, selected_item):
        for item in file_processing:
            if item[1] == self.tree_processing.item(selected_item, 'values')[0]:
                file_processing.remove(item)
                break
        if selected_item:
            self.tree_processing.delete(selected_item)

    def erase_all_data(self):
        for item in self.tree_processing.get_children():
            self.tree_processing.delete(item)
        file_processing.clear()

    def update_treeview_processing(self, data):
        if len(file_processing) == 0:
            self.process_frame.progress["value"] = 0
            self.process_frame.progress_label["text"] = "0%"
        file_processing.append(data)
        self.tree_processing.insert("", "end", values=((data[1], data[2] + "ing")))

        # Scroll to the last item
        self.tree_processing.yview_moveto(1)


class FilesProcessed(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        custom_label = ttk.Label(self, text="Files Processed", font=("Arial", HEADING_SIZE, "bold"))
        self['labelwidget'] = custom_label

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.add_widgets()

    def add_widgets(self):

        # Treeview for files processed
        self.tree_processed = ttk.Treeview(
            self, columns=(1, 2, 3), show="headings")
        self.tree_processed.pack(expand=True, fill="both")
        self.tree_processed.heading(1, text="Time")
        self.tree_processed.heading(2, text="File Name")
        self.tree_processed.heading(3, text="Status")

        self.tree_processed.column(1, width=65)
        self.tree_processed.column(2, width=150)
        self.tree_processed.column(3, width=85)
    def update_treeview_processed(self, file_data):
        current_time = time.strftime("%H:%M:%S")

        self.tree_processed.insert("", "end", values=(current_time ,file_data[1], file_data[2] + "ed"))

        self.tree_processed.yview_moveto(1)
    
    def erase_all_data(self):
        for item in self.tree_processed.get_children():
            self.tree_processed.delete(item)
        
    
class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)


        self.upper_frame = ttk.Frame(self)
        self.upper_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.upper_frame.rowconfigure(0, weight=1)
        self.upper_frame.columnconfigure(0, weight=1)
        self.upper_frame.columnconfigure(1, weight=2)
        self.upper_frame.columnconfigure(2, weight=1)

        self.lower_frame = ttk.Frame(self)
        self.lower_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.lower_frame.rowconfigure(0, weight=1)
        self.lower_frame.columnconfigure(0, weight=1)
        self.lower_frame.columnconfigure(1, weight=20)
        self.lower_frame.columnconfigure(2, weight=5)

        check_connection = CheckConnection(self.lower_frame)
        input_person = InputInfor(self.lower_frame)
        process_frame = ProcessFrame(self.lower_frame)

        list_files_processing = FilesProcessing(self.upper_frame)
        list_files_processed = FilesProcessed(self.upper_frame)
        client_server_folder = ClientServerFolder(self.upper_frame, process_frame)

        menu_bar = MenuBar(self)

        list_files_processing.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="nsew")
        list_files_processed.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        client_server_folder.grid(row=0, column=1, padx=10, pady=(0, 0), sticky="nsew")

        check_connection.grid(row=0, column=2, padx=0, pady=(0, 10), sticky="nsew")
        input_person.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="nsew")
        process_frame.grid(row=0, column=1, padx=10, pady=(0, 0), sticky="nsew")

        list_files_processing.set_dependencies(process_frame)
        client_server_folder.set_dependencies(list_files_processing)
        process_frame.set_dependencies(list_files_processing, list_files_processed, input_person, menu_bar)
        input_person.set_dependencies(process_frame)
        menu_bar.set_dependencies(list_files_processing, list_files_processed, client_server_folder, process_frame)
        parent.config(menu=menu_bar)

def import_account():
    with open(resource_path("assets/user.txt"), "r") as file:
        for line in file.readlines():
            info = line.strip().split(" ")
            if info[0] == "" or info[1] == "":
                break
            information.append((info[0], info[1]))
def export_account():
    with open(resource_path("assets/user.txt"), "w") as file:
        for item in information:
            file.write(item[0] + " " + item[1] + "\n")
def main():

    # Import account information from the file
    import_account()

    root = TkinterDnD.Tk()
    root.title("Client-Server Application")
    root.iconphoto(False, tk.PhotoImage(file=resource_path("assets/icon-8.png")))

    sv_ttk.set_theme("dark")
    
    window_width = 1200
    window_height = 650

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")


    app = App(root)
    app.pack(expand=True, fill="both")

    root.mainloop()

if __name__ == "__main__":
    main()
