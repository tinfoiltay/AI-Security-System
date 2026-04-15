import customtkinter
import customtkinter as ctk
from customtkinter import *
from CTkTable import *
import pandas as pd
import CTkTableRowSelector
from CTkTableRowSelector import *
import socket
import cv2
import pickle
import struct
import threading
from PIL import Image, ImageTk
import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Sets the initial size of the system and its title
        self.title("Security System")
        self.geometry("400x400")

        # Creates a container for the different frames
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = ctk.CTkFrame(self)

        # Rows and columns configuration
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.container.grid(row=0, column=0, sticky="nsew")

        # Store pages
        self.frames = {}
        for F in (LoginPage, MainMenu, SecurityDatabase, SecurityCamera):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def show_frame(self, page):
        # Switch to a frame with different window sizes
        frame = self.frames[page]
        frame.tkraise()

        # Sets the size of the window based on what frame is shown
        if isinstance(frame, LoginPage):
            self.geometry("400x400")
        elif isinstance(frame, MainMenu):
            self.geometry("600x400")
        elif isinstance(frame, SecurityDatabase):
            self.geometry("1000x800")
        elif isinstance(frame, SecurityCamera):
            self.geometry("800x600")


# Login Page Section
class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Spacer rows and columns for centering
        for i in range(10):
            self.rowconfigure(i, weight=1)
        self.columnconfigure(0, weight=1)

        heading = ctk.CTkFont(family="Arial", size=30, weight="bold")

        label_username = ctk.CTkLabel(self, text="Login to Security", font=heading)
        label_username.grid(row=3, column=0, padx=5, pady=5)

        entry_username = ctk.CTkEntry(self, placeholder_text="Username")
        entry_username.grid(row=4, column=0, padx=5, pady=5)

        entry_password = ctk.CTkEntry(self, placeholder_text="Password")
        entry_password.grid(row=5, column=0, padx=5, pady=5)

        login_button = ctk.CTkButton(self, text="Login",
                                     command=lambda: controller.show_frame(MainMenu))
        login_button.grid(row=6, column=0, padx=5, pady=5)


# Main Menu Section
class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Spacer rows and columns for centering
        for i in range(10):
            self.rowconfigure(i, weight=1)
        for i in range(2):
            self.columnconfigure(i, weight=1)

        # Object creation
        label_database = ctk.CTkLabel(self, text="Database Access")
        label_database.grid(row=3, column=0, padx=2, pady=5)

        label_camera = ctk.CTkLabel(self, text="Camera Access")
        label_camera.grid(row=3, column=1, padx=2, pady=5)

        button_database = ctk.CTkButton(self, text="Database",
                                        command=lambda: controller.show_frame(SecurityDatabase))
        button_database.grid(row=6, column=0, padx=2, pady=5)

        button_camera = ctk.CTkButton(self, text="Camera",
                                      command=lambda: controller.show_frame(SecurityCamera))
        button_camera.grid(row=6, column=1, padx=2, pady=5)


# Database Page Section
class SecurityDatabase(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        for i in range(10):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        title_font = ctk.CTkFont(family="Arial", size=30, weight="bold")

        database_title = ctk.CTkLabel(self, text="Database Access", font=title_font)
        database_title.grid(row=0, column=2, padx=2, pady=5)

        scrollable_frame = ctk.CTkScrollableFrame(self)
        scrollable_frame.grid(row=1, column=0, columnspan=7, sticky="ew")

        # Load CSV
        self.df = pd.read_csv("SecurityDatabase.csv")

        values = [self.df.columns.tolist()] + self.df.values.tolist()

        # Track selected row
        self.selected_row = None

        # Table click function
        def table_click(cell):
            row = cell["row"]

            if row == 0:
                return

            self.selected_row = row
            data = self.table.get_row(row)

            for i, entry in enumerate(self.entries):
                entry.delete(0, "end")
                entry.insert(0, data[i])

        # Create table
        self.table = CTkTable(
            master=scrollable_frame,
            row=len(values),
            column=len(values[0]),
            values=values,
            command=table_click
        )

        self.table.grid(row=0, column=0, padx=20, pady=20)

        # ----------------
        # ENTRY BOXES
        # ----------------

        self.entries = []

        for i, col in enumerate(self.df.columns):

            label = ctk.CTkLabel(self, text=col)
            label.grid(row=3, column=i, padx=5)

            entry = ctk.CTkEntry(self)
            entry.grid(row=4, column=i, padx=5)

            self.entries.append(entry)

        # ----------------
        # FUNCTIONS
        # ----------------

        def update_row():

            if self.selected_row is None:
                return

            new_values = [e.get() for e in self.entries]

            for col, value in enumerate(new_values):
                self.table.insert(self.selected_row, col, value)

        def add_row():

            new_values = [e.get() for e in self.entries]

            self.table.add_row(values=new_values)

        def delete_row():

            if self.selected_row is None:
                return

            self.table.delete_row(self.selected_row)
            self.selected_row = None

        def save_csv():

            rows = []

            for r in range(1, self.table.rows):
                rows.append(self.table.get_row(r))

            df = pd.DataFrame(rows, columns=self.df.columns)
            df.to_csv("SecurityDatabase.csv", index=False)

        # ----------------
        # BUTTONS
        # ----------------

        update_button = ctk.CTkButton(self, text="Update Row", command=update_row)
        update_button.grid(row=5, column=0, pady=10)

        add_button = ctk.CTkButton(self, text="Add Row", command=add_row)
        add_button.grid(row=5, column=1)

        delete_button = ctk.CTkButton(self, text="Delete Row", command=delete_row)
        delete_button.grid(row=5, column=2)

        save_button = ctk.CTkButton(self, text="Save CSV", command=save_csv)
        save_button.grid(row=5, column=3)

        back_button = ctk.CTkButton(self, text="Back",
                                    command=lambda: controller.show_frame(MainMenu))
        back_button.grid(row=6, column=0, pady=10)

# Security Camera Section
import socket
import cv2
import pickle
import struct
import threading
from PIL import Image, ImageTk
import customtkinter as ctk

class SecurityCamera(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        for i in range(5):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        # Label where the video will appear
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.grid(row=0, column=0, padx=10, pady=10)

        back_button = ctk.CTkButton(
            self,
            text="Back",
            command=lambda: controller.show_frame(MainMenu)
        )
        back_button.grid(row=1, column=0, pady=10)

        # Start camera thread
        self.running = True
        threading.Thread(target=self.receive_camera, daemon=True).start()


    def receive_camera(self):

        host = "10.132.96.192"   # change to your server IP
        port = 5000

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        data = b""
        payload_size = struct.calcsize("Q")

        while self.running:

            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    return
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            # Convert OpenCV -> Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update GUI
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk


if __name__ == "__main__":
    app = App()
    app.mainloop()