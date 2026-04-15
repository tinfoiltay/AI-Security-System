import socket
import io
import struct
from PIL import Image
import matplotlib.pyplot as pl

def server_program():
    # get the hostname
    host =  "0.0.0.0" # listens to everything
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    server_socket.bind((host, port))  # bind host address and port together
    #For server connections we need to set the server or generate / display its IP and for every camera connection
    #the IP address needs to be manually typed to establish the connection

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    print("Server hostname:", socket.gethostname()) #Get hosts name
    #conn, address = server_socket.accept()  # accept new connection


    conn, address = server_socket.accept()[0].makefile('rb')
    print("Connection from: " + str(address))

    try:
        img = None
        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            # data = conn.recv(1024).decode()

            image_len = struct.unpack('<L', conn.read(struct.calsize('<L')))[0]
            if not image_len:
                break

            image_stream = io.BytesIO()
            image_stream.write(conn.read(image_len))

            image_stream.seek(0)
            image = Image.open(image_stream)

            if img is None:
                img = pl.imshow(image)
            else:
                img.set_data(image)

            pl.pause(0.01)
            pl.draw()

            print('Image is %dx%d' & image.size)
            image.verify()
            print('Image is verified')

    except:
        pass
    #finally:
        #conn.close()
        #server_socket.close()

            #if not data:
                # if data is not received break
                #break
            #print("from connected user: " + str(data))
            #data = input(' -> ')
            #conn.send(data.encode())  # send data to the client

        #onn.close()  # close the connection

    server_program()