import socket
import cv2
import pickle
import struct
import numpy as np

host = "0.0.0.0"
port = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print("Waiting for connection...")
conn, addr = server_socket.accept()
print("Connected from:", addr)

data = b""
payload_size = struct.calcsize("Q")  # 8 bytes

while True:

    # Receive message size
    while len(data) < payload_size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    if len(data) < payload_size:
        break

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]

    msg_size = struct.unpack("Q", packed_msg_size)[0]

    # Receive frame data
    while len(data) < msg_size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    cv2.imshow("Raspberry Pi Camera", frame)

    if cv2.waitKey(1) == 27:
        break

conn.close()