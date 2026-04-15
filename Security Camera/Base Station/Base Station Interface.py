import customtkinter
import customtkinter as ctk
from customtkinter import *
from CTkTable import *
import pandas as pd
import CTkTableRowSelector
from CTkTableRowSelector import *

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

        # Spacer rows and columns for centering
        for i in range(10):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        # Font creation and properties
        title_font = ctk.CTkFont(family="Arial", size=30, weight="bold")

        # Object Creation
        database_title = ctk.CTkLabel(self, text="Database Access", font=title_font)
        database_title.grid(row=0, column=2, padx=2, pady=5)

        scrollable_frame = ctk.CTkScrollableFrame(self)
        scrollable_frame.grid(row=1, column=0, columnspan=7, sticky="ew")

        df = pd.read_csv('SecurityDatabase.csv')
        value = []

        v = []
        v.extend(df.columns)
        value.append(v)
        for i, row in df.iterrows():
            value.append([i] + list(row))

        print(value)

        # Table Creation
        table = CTkTable(master=scrollable_frame, row=len(value), column=len(value[0]), values=[df.columns.tolist()] + df.values.tolist())
        table.grid(row=0, column=0, padx=20, pady=20)

        select_row = CTkTableRowSelector(table)


        back_button = ctk.CTkButton(self, text="Back",
                                    command=lambda: controller.show_frame(MainMenu))
        back_button.grid(row=2, column=0, pady=10)


# Security Camera Section
class SecurityCamera(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Spacer rows and columns for centering
        for i in range(5):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        var = StringVar(value="Initial text")
        entry = CTkEntry(self, textvariable=var)
        entry.grid(row=0, column=0, padx=5, pady=5)

        var.set("Updated text!")

        back_button = ctk.CTkButton(self, text="Back",
                                    command=lambda: controller.show_frame(MainMenu))
        back_button.grid(row=1, column=0, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()