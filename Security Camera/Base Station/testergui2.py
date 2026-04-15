import socket
import cv2
import pickle
import struct
import threading
import customtkinter as ctk
from PIL import Image, ImageTk

host = "0.0.0.0"
port = 5000


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Raspberry Pi Camera")
        self.geometry("800x600")

        self.label = ctk.CTkLabel(self, text="")
        self.label.pack(expand=True, fill="both")

        threading.Thread(target=self.receive_stream, daemon=True).start()

    def receive_stream(self):

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)

        print("Waiting for connection...")
        conn, addr = server_socket.accept()
        print("Connected from:", addr)

        data = b""
        payload_size = struct.calcsize("Q")

        while True:

            while len(data) < payload_size:
                packet = conn.recv(4096)
                if not packet:
                    return
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                packet = conn.recv(4096)
                if not packet:
                    return
                data += packet

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            # Convert OpenCV -> Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update GUI
            self.label.configure(image=imgtk)
            self.label.image = imgtk


app = App()
app.mainloop()