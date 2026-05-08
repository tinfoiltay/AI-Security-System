import customtkinter as ctk
import pandas as pd
import CTkTableRowSelector
from CTkTableRowSelector import *
import socket
import cv2
import pickle
import struct
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__() # Initialises frame

        # Sets the initial size of the system and its title
        self.title("Security System")
        self.geometry("400x400")
        self.resizable(False, False)

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
        for F in (LoginPage, MainMenu, SecurityDatabase, SecurityCamera, LoginDatabase):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage) # Display login page

    def show_frame(self, page):
        # Switch to a frame with different window sizes
        frame = self.frames[page]
        frame.tkraise()

        # Sets the size of the window based on what frame is shown
        if isinstance(frame, LoginPage):
            self.geometry("400x400")
        elif isinstance(frame, MainMenu):
            self.geometry("450x300")
        elif isinstance(frame, SecurityDatabase):
            self.geometry("1000x600")
        elif isinstance(frame, LoginDatabase):
            self.geometry("800x600")
        elif isinstance(frame, SecurityCamera):
            self.geometry("1000x800")


# Login Page Section
class LoginPage(ctk.CTkFrame):

    def check_login(self, controller):
        username = self.entry_username.get().strip() # Gets the inputted username
        password = self.entry_password.get().strip() # gets the inputted password

        try:
            df = pd.read_csv("LoginDatabase.csv") # Loads the login database
        except:
            self.show_message("Error loading login database.") # Error message
            return

        # Check if the correct columns exist
        if "Username" not in df.columns or "Password" not in df.columns:
            self.show_message("Database format error.")
            return

        # Check if username and password can be found in the database
        match = df[(df["Username"] == username) & (df["Password"] == password)]

        if not match.empty:
            controller.show_frame(MainMenu) # Sends the user to the main menu if username and password can be found
        else:
            self.show_message("Invalid username or password.") # Shows error if not

    def show_message(self, message):
        message_window = ctk.CTkToplevel(self) # Opens a window message
        message_window.title("Info")
        message_window.geometry("180x100")

        ctk.CTkLabel(message_window, text=message).grid(row=0, column=0, pady=20) # Displays text
        ctk.CTkButton(message_window, text="OK", command=message_window.destroy).grid(row=1, column=0) # Close button

    def __init__(self, parent, controller):
        super().__init__(parent)

        # Spacer rows and columns for centering
        for i in range(10):
            self.rowconfigure(i, weight=1) #Makes rows expandable
        self.columnconfigure(0, weight=1) # Makes columns expandable

        heading = ctk.CTkFont(family="Arial", size=30, weight="bold") # Creates the font for the heading / title

        label_username = ctk.CTkLabel(self, text="Login to Security", font=heading) # Heading / title creation
        label_username.grid(row=3, column=0, padx=5, pady=5)

        self.entry_username = ctk.CTkEntry(self, placeholder_text="Username") # Username input box
        self.entry_username.grid(row=4, column=0, padx=5, pady=5)

        self.entry_password = ctk.CTkEntry(self, placeholder_text="Password", show="*") # Password input box which hides the entered text
        self.entry_password.grid(row=5, column=0, padx=5, pady=5)

        login_button = ctk.CTkButton(self, text="Login", command=lambda: self.check_login(controller)) # Login button
        login_button.grid(row=6, column=0, padx=5, pady=5)


# Main Menu Section
class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Font creation and properties
        MainMenu_Font = ctk.CTkFont(family="Arial", size=30, weight="bold") # Creates the font for the heading

        # Object Creation
        database_title = ctk.CTkLabel(self, text="Main Menu", font=MainMenu_Font) # Heading / title creation
        database_title.grid(row=0, column=1, padx=2, pady=5)

        # Spacer sections by using rows and columns for positioning
        for i in range(10):
            self.rowconfigure(i, weight=1)
        for i in range(2):
            self.columnconfigure(i, weight=1)

        # Object creation

        # Opens the login database
        button_login_database = ctk.CTkButton(self, text="Login Database", command=lambda: controller.show_frame(LoginDatabase))
        button_login_database.grid(row=4, column=0, padx=2, pady=5)

        # Opens the security database
        button_security_database = ctk.CTkButton(self, text="Security Database", command=lambda: controller.show_frame(SecurityDatabase))
        button_security_database.grid(row=4, column=1, padx=2, pady=5)

        # Opens the security camera
        button_camera = ctk.CTkButton(self, text="Camera Access", command=lambda: controller.show_frame(SecurityCamera))
        button_camera.grid(row=4, column=2, padx=2, pady=5)


# Database Page Section
class SecurityDatabase(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Spacer sections by using rows and columns for positioning
        for i in range(10):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        # Font creation and properties
        title_font = ctk.CTkFont(family="Arial", size=30, weight="bold")

        # Object Creation
        database_title = ctk.CTkLabel(self, text="Security Database", font=title_font) # Page title
        database_title.grid(row=0, column=2, padx=2, pady=5)

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...") # Search entry box
        self.search_entry.grid(row=1, column=2, padx=5, pady=5)

        search_button = ctk.CTkButton(self, text="Search", command=self.search_records) # Search button
        search_button.grid(row=1, column=3, padx=5, pady=5)

        reset_button = ctk.CTkButton(self, text="Reset", command=self.load_table) # Reset button
        reset_button.grid(row=1, column=4, padx=5, pady=5)

        self.scrollable_frame = ctk.CTkScrollableFrame(self) # A frame that allows scorlling
        self.scrollable_frame.grid(row=2, column=0, columnspan=7, sticky="ew")

        add_button = ctk.CTkButton(self, text="Add Record", command=self.add_record) # Add button
        add_button.grid(row=3, column=1, padx=5, pady=5)

        edit_button = ctk.CTkButton(self, text="Edit Selected", command=self.edit_record) # Edit button
        edit_button.grid(row=3, column=2, padx=5, pady=5)

        delete_button = ctk.CTkButton(self, text="Delete Selected", command=self.delete_record) # Delete buttom
        delete_button.grid(row=3, column=3, padx=5, pady=5)

        back_button = ctk.CTkButton(self, text="Back", command=lambda: controller.show_frame(MainMenu)) # Back to main menu button
        back_button.grid(row=3, column=0, pady=10)

        self.df = pd.read_csv('SecurityDatabase.csv') # Loads the database
        self.table = None
        self.row_selector = None
        self.current_df = None

        self.load_table() # Display table on load

    # Function for re-loading the table
    def load_table(self, df=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy() # Clears existing table

        if df is None:
            df = self.df

        self.current_df = df.reset_index(drop=True) # Resets the row numbers

        # Creates the table
        self.table = CTkTable(master=self.scrollable_frame, row=len(self.current_df) + 1, column=len(self.current_df.columns), values=[self.current_df.columns.tolist()] + self.current_df.values.tolist())
        self.table.grid(row=0, column=0, padx=20, pady=20)

        self.row_selector = CTkTableRowSelector(self.table) # Enables the rows to be selected

    def search_records(self):
        query = self.search_entry.get().strip().lower() # Takes the inputted search text

        # Reloads the table if its empty
        if query == "":
            self.load_table()
            return

        # Row filters
        mask = self.df.apply(lambda col: col.astype(str).str.lower().str.contains(query)).any(axis=1)
        filtered_df = self.df[mask]
        self.load_table(df=filtered_df)

    def get_selected_row(self):
        try:
            selected = self.row_selector.selected_rows # Gets the selected rows

            if not selected:
                return None # If nothing is seletce, return nothing

            # Adjusts the index to include header
            return list(selected)[0] - 1

        except Exception:
            return None # Erorr catch returns nothing

    # Function for adding a record
    def add_record(self):
        add_window = ctk.CTkToplevel(self) # Sets up the window for adding
        add_window.title("Add Record")
        add_window.geometry("300x350")

        entries = {} # Stores input fields

        # Column label
        for i, column_name in enumerate(self.df.columns):
            label = ctk.CTkLabel(add_window, text=column_name)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = ctk.CTkEntry(add_window) # Opens the input window
            entry.grid(row=i, column=1, padx=10, pady=5)

            entries[column_name] = entry # Stores inputted data

        # Function for saving new record
        def save_new_record():
            new_row = {}

            for column_name, entry in entries.items():
                new_row[column_name] = entry.get() # Gets the input values

            # Saves the entered data to the file
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)  # Adds the row
            self.df.to_csv("SecurityDatabase.csv", index=False) # Saves the file
            add_window.destroy() # Closes the window
            self.load_table() # Table is refreshed

        save_button = ctk.CTkButton(add_window, text="Save", command=save_new_record) # Save button
        save_button.grid(row=len(self.df.columns), column=0, columnspan=2, pady=10)

    # Function for editing a selected record/row
    def edit_record(self):
        row_index = self.get_selected_row() # Gets the selected row

        if row_index is None or row_index < 0:
            self.show_message("Please select a row to edit.") # If error occurs, it's displayed
            return

        row_data = self.current_df.iloc[row_index] # Gets row data

        edit_window = ctk.CTkToplevel(self) # Creates edit window
        edit_window.title("Edit Record")
        edit_window.geometry("300x350")

        # Everything below here works exactly the same as the adding, but instead it changes the selected rows values
        # I will not be repeating the steps
        entries = {}

        for i, column_name in enumerate(self.current_df.columns):
            label = ctk.CTkLabel(edit_window, text=column_name)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = ctk.CTkEntry(edit_window)
            entry.insert(0, str(row_data[column_name])) # Fills the edit window with the selected rows values
            entry.grid(row=i, column=1, padx=10, pady=5)

            entries[column_name] = entry

        def save_changes():
            real_index = self.current_df.index[row_index]

            for column_name, entry in entries.items():
                new_value = entry.get()
                self.df[column_name] = self.df[column_name].astype(str)
                self.df.at[real_index, column_name] = new_value

            self.df = self.df.infer_objects()
            self.df.to_csv("SecurityDatabase.csv", index=False)
            edit_window.destroy()
            self.load_table()

        save_button = ctk.CTkButton(edit_window, text="Save", command=save_changes)
        save_button.grid(row=len(self.current_df.columns), column=0, columnspan=2, pady=10)

    # Function for deleting a record
    def delete_record(self):
        row_index = self.get_selected_row() # Gets the selected row/record

        if row_index is None or row_index < 0:
            self.show_message("Please select a row to delete.")
            return

        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("Confirm Delete")
        confirm_window.geometry("250x120")

        # Opens a window that ensures that the user wants to delete a row
        ctk.CTkLabel(confirm_window, text="Are you sure you want to delete this record?").grid(row=0, column=0, columnspan=2, pady=15)

        # Function for confirming the deletion
        def confirm_delete():
            real_index = self.current_df.index[row_index]
            self.df = self.df.drop(index=real_index).reset_index(drop=True) # Deletes the row
            self.df.to_csv("SecurityDatabase.csv", index=False) # Saves the deletion
            confirm_window.destroy()
            self.load_table()

        yes_button = ctk.CTkButton(confirm_window, text="Yes", command=confirm_delete)
        yes_button.grid(row=1, column=0, padx=10, pady=10)

        no_button = ctk.CTkButton(confirm_window, text="No", command=confirm_window.destroy)
        no_button.grid(row=1, column=1, padx=10, pady=10)

    def show_message(self, message):
        message_window = ctk.CTkToplevel(self)
        message_window.title("Info")
        message_window.geometry("220x100")

        ctk.CTkLabel(message_window, text=message).grid(row=0, column=0, pady=20)
        ctk.CTkButton(message_window, text="OK", command=message_window.destroy).grid(row=1, column=0)


# This section database section works exactly the same as the previous, it's simply just managing a different file
# Login Database Section
class LoginDatabase(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Spacer rows and columns for centering
        for i in range(10):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        # Font creation and properties
        title_font = ctk.CTkFont(family="Arial", size=30, weight="bold")

        # Object Creation
        login_database_title = ctk.CTkLabel(self, text="Login Database", font=title_font)
        login_database_title.grid(row=0, column=2, padx=2, pady=5)

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
        self.search_entry.grid(row=1, column=2, padx=5, pady=5)

        search_button = ctk.CTkButton(self, text="Search", command=self.search_records)
        search_button.grid(row=1, column=3, padx=5, pady=5)

        reset_button = ctk.CTkButton(self, text="Reset", command=self.load_table)
        reset_button.grid(row=1, column=4, padx=5, pady=5)

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=2, column=0, columnspan=7, sticky="ew")

        add_button = ctk.CTkButton(self, text="Add Record", command=self.add_record)
        add_button.grid(row=3, column=1, padx=5, pady=5)

        edit_button = ctk.CTkButton(self, text="Edit Selected", command=self.edit_record)
        edit_button.grid(row=3, column=2, padx=5, pady=5)

        delete_button = ctk.CTkButton(self, text="Delete Selected", command=self.delete_record)
        delete_button.grid(row=3, column=3, padx=5, pady=5)

        back_button = ctk.CTkButton(self, text="Back",
                                    command=lambda: controller.show_frame(MainMenu))
        back_button.grid(row=3, column=0, pady=10)

        self.df = pd.read_csv('LoginDatabase.csv')
        self.table = None
        self.row_selector = None
        self.current_df = None

        self.load_table()

    def load_table(self, df=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if df is None:
            df = self.df

        self.current_df = df.reset_index(drop=True)

        self.table = CTkTable(master=self.scrollable_frame, row=len(self.current_df) + 1, column=len(self.current_df.columns), values=[self.current_df.columns.tolist()] + self.current_df.values.tolist())
        self.table.grid(row=0, column=0, padx=20, pady=20)

        self.row_selector = CTkTableRowSelector(self.table)

    def search_records(self):
        query = self.search_entry.get().strip().lower()

        if query == "":
            self.load_table()
            return

        mask = self.df.apply(lambda col: col.astype(str).str.lower().str.contains(query)).any(axis=1)

        filtered_df = self.df[mask]
        self.load_table(df=filtered_df)

    def get_selected_row(self):
        try:
            selected = self.row_selector.selected_rows

            if not selected:
                return None

            return list(selected)[0] - 1

        except Exception:
            return None

    def add_record(self):
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add Record")
        add_window.geometry("300x200")

        entries = {}

        for i, column_name in enumerate(self.df.columns):
            label = ctk.CTkLabel(add_window, text=column_name)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = ctk.CTkEntry(add_window)
            entry.grid(row=i, column=1, padx=10, pady=5)

            entries[column_name] = entry

        def save_new_record():
            new_row = {}

            for column_name, entry in entries.items():
                new_row[column_name] = entry.get()

            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
            self.df.to_csv("LoginDatabase.csv", index=False)
            add_window.destroy()
            self.load_table()

        save_button = ctk.CTkButton(add_window, text="Save", command=save_new_record)
        save_button.grid(row=len(self.df.columns), column=0, columnspan=2, pady=10)

    def edit_record(self):
        row_index = self.get_selected_row()

        if row_index is None or row_index < 0:
            self.show_message("Please select a row to edit.")
            return

        row_data = self.current_df.iloc[row_index]

        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Record")
        edit_window.geometry("300x200")

        entries = {}

        for i, column_name in enumerate(self.current_df.columns):
            label = ctk.CTkLabel(edit_window, text=column_name)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = ctk.CTkEntry(edit_window)
            entry.insert(0, str(row_data[column_name]))
            entry.grid(row=i, column=1, padx=10, pady=5)

            entries[column_name] = entry

        def save_changes():
            real_index = self.current_df.index[row_index]

            for column_name, entry in entries.items():
                new_value = entry.get()
                self.df[column_name] = self.df[column_name].astype(str)
                self.df.at[real_index, column_name] = new_value

            self.df = self.df.infer_objects()
            self.df.to_csv("LoginDatabase.csv", index=False)
            edit_window.destroy()
            self.load_table()

        save_button = ctk.CTkButton(edit_window, text="Save", command=save_changes)
        save_button.grid(row=len(self.current_df.columns), column=0, columnspan=2, pady=10)

    def delete_record(self):
        row_index = self.get_selected_row()

        if row_index is None or row_index < 0:
            self.show_message("Please select a row to delete.")
            return

        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("Confirm Delete")
        confirm_window.geometry("250x120")

        ctk.CTkLabel(confirm_window, text="Are you sure you want to delete this record?").grid(row=0, column=0, columnspan=2, pady=15)

        def confirm_delete():
            real_index = self.current_df.index[row_index]
            self.df = self.df.drop(index=real_index).reset_index(drop=True)
            self.df.to_csv("LoginDatabase.csv", index=False)
            confirm_window.destroy()
            self.load_table()

        yes_button = ctk.CTkButton(confirm_window, text="Yes", command=confirm_delete)
        yes_button.grid(row=1, column=0, padx=10, pady=10)

        no_button = ctk.CTkButton(confirm_window, text="No", command=confirm_window.destroy)
        no_button.grid(row=1, column=1, padx=10, pady=10)

    def show_message(self, message):
        message_window = ctk.CTkToplevel(self)
        message_window.title("Info")
        message_window.geometry("220x100")

        ctk.CTkLabel(message_window, text=message).grid(row=0, column=0, pady=20)
        ctk.CTkButton(message_window, text="OK", command=message_window.destroy).grid(row=1, column=0)


# Security Camera Section
class SecurityCamera(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Spacer sections by using rows and columns for positioning
        for i in range(10):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        # List of allowed camera IPs
        self.camera_ips = [
            "10.226.6.165",
            "10.226.7.165",
            "10.226.8.165",
            "10.226.9.165",
            "10.226.10.165",
            "10.226.11.165"
        ]

        self.camera_labels = [] # Stores the labels for each of the security cameras

        # Grid setup for each of the individual cameras
        camera_positions = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2)
        ]

        for i in range(6):
            ip = self.camera_ips[i] # Gets the IP
            row, column = camera_positions[i] # Gets the correct grid location by matching the IP to the grid spot

            camera_frame = ctk.CTkFrame(self) # Frame for each security camera
            camera_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

            camera_frame.rowconfigure(0, weight=0)
            camera_frame.rowconfigure(1, weight=1)
            camera_frame.rowconfigure(2, weight=0)
            camera_frame.columnconfigure(0, weight=1)

            ip_label = ctk.CTkLabel(camera_frame, text=ip) # Displays the IP
            ip_label.grid(row=0, column=0, padx=5, pady=5)

            camera_label = ctk.CTkLabel(camera_frame, text="No Feed") # Displaus the camera footage
            camera_label.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

            self.camera_labels.append(camera_label)

            button_frame = ctk.CTkFrame(camera_frame) # Creates a frame for the camera movement buttons
            button_frame.grid(row=2, column=0, pady=5)

            button_frame.rowconfigure(0, weight=1)
            button_frame.rowconfigure(1, weight=1)
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)
            button_frame.columnconfigure(2, weight=1)

            # Each of these are motor control buttons to move the camera
            up_button = ctk.CTkButton(button_frame, text="▲", width=40)
            up_button.grid(row=0, column=1, padx=2, pady=2)

            left_button = ctk.CTkButton(button_frame, text="◀", width=40)
            left_button.grid(row=1, column=0, padx=2, pady=2)

            down_button = ctk.CTkButton(button_frame, text="▼", width=40)
            down_button.grid(row=1, column=1, padx=2, pady=2)

            right_button = ctk.CTkButton(button_frame, text="▶", width=40)
            right_button.grid(row=1, column=2, padx=2, pady=2)

            import threading # Allows the camera to always be running
            threading.Thread(target=self.start_camera, args=(ip, camera_label), daemon=True).start() # Starts the thread

        back_button = ctk.CTkButton(self, text="Back", command=lambda: controller.show_frame(MainMenu)) # Back button
        back_button.grid(row=2, column=0, pady=10)

    def start_camera(self, ip, camera_label):

        port = 5000 + self.camera_ips.index(ip) # Assigns each camera a unique port

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creates socket
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Uses the address
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(1) # Finds a conenction

        print("Waiting for connection from", ip, "on port", port)

        while True:
            conn, addr = server_socket.accept() # Once the connection is found, it's accepted

            if addr[0] != ip:
                print("Rejected connection from", addr[0], "on port", port)
                conn.close()
                continue

            print("Connected from:", addr)

            data = b"" # Buffers for incoming data
            payload_size = struct.calcsize("Q")

            while True:

                while len(data) < payload_size:
                    packet = conn.recv(4096) # receives the data
                    if not packet:
                        break
                    data += packet

                if len(data) < payload_size:
                    break

                packed_msg_size = data[:payload_size] # Extracts message size
                data = data[payload_size:]

                msg_size = struct.unpack("Q", packed_msg_size)[0] # Unpacks the size of the message

                while len(data) < msg_size:
                    packet = conn.recv(4096)
                    if not packet:
                        break
                    data += packet

                frame_data = data[:msg_size] # Takes the frame
                data = data[msg_size:]

                frame = pickle.loads(frame_data) # Decodes the frame
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR) # Converts it to an image

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Sets the right colour options
                img = Image.fromarray(frame) # Convert to PIL image

                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 200)) # CustomTkinter converter

                camera_label.configure(image=ctk_img, text="") # Displays the footage
                camera_label.image = ctk_img

            conn.close() # Close connection
            camera_label.configure(image=None, text="No Feed") # Reset the camera feed if disconnected


if __name__ == "__main__":
    app = App() # Create the app instance
    app.mainloop() # Runs the application