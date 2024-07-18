import tkinter as tk
from tkinter import Label
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import sv_ttk
import os
import threading
import time
import random
import sys
import webbrowser


FileProcessing: list = []
Information: list = []
Error = ""

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def ListFolder(tree, parent, path):
    for p in os.listdir(path):
        abspath = os.path.join(path, p)
        isdir = os.path.isdir(abspath)
        oid = tree.insert(parent, 'end', text=p, open=False)
        if isdir:
            ListFolder(tree, oid, abspath)

class MenuBar(tk.Menu):
    def __init__(self, parent, list_file, client_server_folder):
        super().__init__(parent)

        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Open File", command=lambda: self.open_file(list_file))
        file_menu.add_command(label="Open Folder", command=lambda: self.open_folder(client_server_folder))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=parent.quit)
        self.add_cascade(label="Tasks", menu=file_menu)
        
        setting_menu = tk.Menu(self, tearoff=0)
        setting_menu.add_command(label="Theme", command=self.theme)
        self.add_cascade(label="Settings", menu=setting_menu)

        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        help_menu.add_command(label="Contact Support", command=lambda: webbrowser.open("https://www.facebook.com/profile.php?id=100012655329823"))
        self.add_cascade(label="Help", menu=help_menu)

    def about(self):
        messagebox.showinfo("About", "This is a simple client-server application. It allows you to download files from the server and upload files to the server.\n ----------------- \n The application is developed by a group of 3 students: Nguyễn Đình Mạnh, Châu Đình Phúc, Nguyễn Trọng Nhân.")

        

    def theme(self):
        sv_ttk.set_theme("dark") if sv_ttk.get_theme() == "light" else sv_ttk.set_theme("light")
    
    def open_file(self, list_file):
        file_path = filedialog.askopenfilename()
        name_file = os.path.basename(file_path)
        data = (file_path, name_file, "Download")
        list_file.update_treeview_processing(data)
        FileProcessing.append(data)

    def open_folder(self, client_server_folder):
        folder_path = filedialog.askdirectory()
        # Delete all item in tree
        for item in client_server_folder.tree_Client.get_children():
            client_server_folder.tree_Client.delete(item)
        # Add new item
        ListFolder(client_server_folder.tree_Client, '', folder_path)


class InputPerson(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        custom_label = ttk.Label(self, text="Information", font=("Arial", 14, "bold"))
        self['labelwidget'] = custom_label
        self.columnconfigure(0, weight=1)

        self.add_widgets()

        self.bind_widgets()

    def add_widgets(self):
        self.label_name = ttk.Label(self, text="Name:")
        self.label_name.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="w")
        self.name = ttk.Entry(self)
        self.name.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")

        self.label_email = ttk.Label(self, text="Email:")
        self.label_email.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="w")
        self.email = ttk.Entry(self)
        self.email.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="ew")

    def bind_widgets(self):
        self.name.bind("<FocusOut>", self.validate_name)
        self.name.bind("<FocusIn>", self.validate_name)
        self.name.bind("<KeyRelease>", self.validate_name)

        self.email.bind("<FocusOut>", self.validate_email)
        self.email.bind("<FocusIn>", self.validate_email)
        self.email.bind("<KeyRelease>", self.validate_email)

    def validate_name(self, *_):
        for character in self.name.get():
            if character == " ":
                continue
            if character.isdigit():
                self.name.state(["invalid"])
                return False
            if character.isidentifier() == False:
                self.name.state(["invalid"])
                return False
        self.name.state(["!invalid"])
        return True

    def validate_email(self, *_):
        if self.email.get() == "":
            self.email.state(["!invalid"])
            return True
        if "@" in self.email.get() and "." in self.email.get():
            self.email.state(["!invalid"])
            return True
        self.email.state(["invalid"])
        return False


class RadioButton(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


        self.add_widgets()

    def add_widgets(self):

        self.methods = ttk.LabelFrame(self)
        self.methods.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="nsew")

        img = Image.open(resource_path("assets/dragon3.png"))
        img = img.resize((150, 100))
        icon = ImageTk.PhotoImage(img)
        self.icon = ttk.Label(self, image=icon)
        # Keep a reference to the image to prevent garbage collection
        self.icon.image = icon
        self.icon.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="s")

        custom_label = ttk.Label(self.methods, text="Methods", font=("Arial", 14, "bold"))
        self.methods['labelwidget'] = custom_label

        self.methods.var = tk.StringVar(value="Download")

        # Upload and Download radio buttons
        self.radio_1 = ttk.Radiobutton(self.methods, text="Upload", variable=self.methods.var, value="Upload", state="disabled")
        self.radio_1.grid(row=0, column=0, padx=5, pady=10, sticky="w")

        self.radio_1 = ttk.Radiobutton(self.methods, text="Download", variable=self.methods.var, value="Download", state="disabled")
        self.radio_1.grid(row=0, column=1, padx=(10, 5), pady=10, sticky="w")

class ClientServerFolder(ttk.LabelFrame):
    def __init__(self, parent, list_file, radio_button):
        super().__init__(parent)

        custom_label = ttk.Label(self, text="Folder", font=("Arial", 14, "bold"))
        self['labelwidget'] = custom_label


        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # If user choose tab download, the radio button is Download
        self.notebook.bind("<<NotebookTabChanged>>", lambda event: radio_button.methods.var.set("Download") if self.notebook.index("current") == 0 else radio_button.methods.var.set("Upload"))
        self.add_widgets(list_file)

    def add_widgets(self, list_file):

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
        )

        self.scrollbar_v.config(command=self.tree_Server.yview)
        self.scrollbar_h.config(command=self.tree_Server.xview)
        self.tree_Server.pack(expand=True, fill="both")
        ListFolder(self.tree_Server, '', '.')

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
        )

        self.scrollbar_v.config(command=self.tree_Client.yview)
        self.scrollbar_h.config(command=self.tree_Client.xview)
        self.tree_Client.pack(expand=True, fill="both")
        ListFolder(self.tree_Client, '', '.')


        # Bind double-click event
        self.tree_Server.bind("<Double-1>", lambda event: self.on_double_click(list_file, "Download"))
        self.tree_Client.bind("<Double-1>", lambda event: self.on_double_click(list_file, "Upload"))


    def on_double_click(self, list_file, method):
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
        file_path = self.get_full_path(item)

        data = (file_path, name_item, method)
        list_file.update_treeview_processing(data)

    def get_full_path(self, item):
        path = [self.tree.item(item, 'text')]
        parent = self.tree.parent(item)
        while parent:
            path.insert(0, self.tree.item(parent, 'text'))
            parent = self.tree.parent(parent)
        return os.path.join(*path)

class ProcessButton(ttk.Frame):
    def __init__(self, parent, list_file, input_person):
        super().__init__(parent, padding=15)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Download progress bar
        self.progress = ttk.Progressbar(self, length = 200, mode = "determinate", value = 0, maximum = 100)
        self.progress.grid(row = 0, column = 0, padx = 5, pady = 10, sticky="ew")

        # Percentage
        # Clear the progress label when the progress bar is full
        self.progress_label = ttk.Label(self, text="0%", font=("Arial", 12, "bold"))
        self.progress_label.place(in_=self.progress, relx=0.5, rely=0.5, anchor="center")

        # Button
        self.button = ttk.Button(self, text="RUN", style="Accent.TButton", command=lambda: self.start_downloads(list_file, input_person))
        self.button.grid(row=2, column=0, padx=5, pady=(5, 5), sticky="ew")

        # List of Error and Warning messages
        self.tree = ttk.Treeview(self, columns=(1), height=3, show="headings")
        self.tree.grid(row=3, column=0, padx=5, pady=0, sticky="nsew")

        self.tree.heading(1, text="Message")
        self.tree.column(1, width=200)

        self.tree.tag_configure("warning", foreground="orange")
        self.tree.tag_configure("error", foreground="red")
        self.tree.tag_configure("success", foreground="green")

    def error_message(self, input_person):
        # If list of files processing is empty, display an error message
        if len(FileProcessing) == 0:
            self.tree.insert("", "end", values=("ERROR: No files to process",), tags="error")
            return True
        # If the name and email is provided but not correct, display an error message
        if input_person.validate_name() == False:
            self.tree.insert("", "end", values=("ERROR: Name information is not correct",), tags="error")
            return True
        if input_person.validate_email() == False:
            self.tree.insert("", "end", values=("ERROR: Email information is not correct",), tags="error")
            return True
        return False

    # Simulate download
    def start_downloads(self, list_file, input_person):
        # Delete all item in tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.error_message(input_person) == True:
            self.button.configure(style="Toolbutton.TButton")
            return
        else:
            self.button.configure(style="Accent.TButton")

        # If the name and email fields are empty, display an warning message
        if input_person.name.get() == "":
            self.tree.insert("", "end", values=("WARNING: Name information is not found, choose default: Anonymous",), tags="warning")
        if input_person.email.get() == "":
            self.tree.insert("", "end", values=("WARNING: Email information is not found, choose default: Anonymous",), tags="warning")

        # Start download
        self.progress["value"] = 0
        while self.progress["value"] < 100:
            time.sleep(0.1)
            rand = random.randint(1, 10)
            if (self.progress["value"] + rand) > 100:
                self.progress["value"] = 100
            else:
                self.progress["value"] += rand
            self.progress_label["text"] = f"{int(self.progress['value'])}%"
            self.update_idletasks()

        # If the download is successful, display a success message with name, email, method, and number of files processed
        downloaded = 0
        uploaded = 0
        for item in FileProcessing:
            if item[2] == "Download":
                downloaded += 1
            else:
                uploaded += 1
        self.tree.insert("", "end", values=(f"SUCCESS: {downloaded} files is downloaded, {uploaded} files is uploaded",), tags="success")
        self.tree.insert("", "end", values=(f"Name: {"Anonymous" if input_person.name.get() == "" else input_person.name.get()}",), tags="success")
        self.tree.insert("", "end", values=(f"Email: {"Anonymous" if input_person.email.get() == "" else input_person.email.get()}",), tags="success")

        self.tree.yview_moveto(1)

        list_file.update_treeview_processed()


# List of files that have been processed or are in the process of being processed
class ListFile(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        custom_label = ttk.Label(self, text="List Files", font=("Arial", 14, "bold"))
        self['labelwidget'] = custom_label

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.add_widgets()

    def add_widgets(self):
        self.list_file_processing = ttk.LabelFrame(self, text="Files Processing")
        self.list_file_processing.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.list_file_processed = ttk.LabelFrame(self, text="Files Processed")
        self.list_file_processed.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

        self.list_file_processing.columnconfigure(0, weight=1)
        self.list_file_processing.rowconfigure(0, weight=1)

        # Treeview for files processing
        self.tree_processing = ttk.Treeview(self.list_file_processing, columns=(1, 2), height=6, show="headings")
        self.tree_processing.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.tree_processing.heading(1, text="File Name")
        self.tree_processing.heading(2, text="Status")

        self.tree_processing.column(1, width=200)
        self.tree_processing.column(2, width=100)

        # Erase data when user double-clicks on the file
        self.tree_processing.bind(
            "<Double-1>", lambda event: self.erase_treeview_data(self.tree_processing.selection()[0]))

        # Treeview for files processed
        self.tree_processed = ttk.Treeview(self.list_file_processed, columns=(1, 2), height=6, show="headings")
        self.tree_processed.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.tree_processed.heading(1, text="File Name")
        self.tree_processed.heading(2, text="Status")

        self.tree_processed.column(1, width=200)
        self.tree_processed.column(2, width=100)

    def erase_treeview_data(self, selected_item):
        for item in FileProcessing:
            if item == self.tree_processing.item(selected_item)["values"][0]:
                FileProcessing.remove(item)
                break
        if selected_item:
            self.tree_processing.delete(selected_item)


    def update_treeview_processing(self, data):

        FileProcessing.append(data)

        self.tree_processing.insert("", "end", values=((data[1], data[2] + "ing")))

        # Scroll to the last item
        self.tree_processing.yview_moveto(1)

    def update_treeview_processed(self):

        for item in self.tree_processing.get_children():
            self.tree_processing.delete(item)


        for file_data in FileProcessing:
            self.tree_processed.insert("", "end", values=(file_data[1], file_data[2] + "ed"))

        FileProcessing.clear()

        self.tree_processed.yview_moveto(1)

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        for index in range(2):
            self.columnconfigure(index, weight=1)
            self.rowconfigure(index, weight=1)


        input_person = InputPerson(self)
        input_person.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        radio_button = RadioButton(self)
        radio_button.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        list_file = ListFile(self)
        # rowspace is no longer needed
        list_file.grid(row=0, column=2, rowspan=2, padx=10, pady=(10, 0), sticky="nsew")
        client_server_folder = ClientServerFolder(self, list_file, radio_button)
        client_server_folder.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nsew")
        process_button = ProcessButton(self, list_file, input_person)
        process_button.grid(row=1, column=1, padx=10, pady=(0, 0), sticky="nsew")

        menu_bar = MenuBar(self, list_file, client_server_folder)
        parent.config(menu=menu_bar)

def main():
    root = tk.Tk()
    root.title("Client-Server Application")
    root.resizable("false", "false")
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

    # # Fix the blurry text on Windows
    # try:
    #     from ctypes import windll
    #     windll.shcore.SetProcessDpiAwareness(1)
    #     # Adjust font size globally
    #     font_size = 10
    #     style = ttk.Style()
    #     style.configure("TLabel", font=("Arial", font_size))


    # finally:
    root.mainloop()


if __name__ == "__main__":
    main()
