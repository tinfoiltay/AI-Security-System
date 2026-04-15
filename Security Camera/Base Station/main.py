# ADD THREADING MULTI RUN SERVER CONNECTION AND Base station code
import server
import threading


def server_connection_program(): #this defines the starting function of the file we want to use in the server code
    server.server_program()

def base_station_program(): #this defines the starting function of the file we want to use in the GUI code
    pass


if __name__ == '__main__': # if this is the starting program then run this file
    thread_one = threading.Thread(target=server_connection_program) #Defines the first thread and sets the server connection to be run first
    thread_two = threading.Thread(target=base_station_program) #Defines the first thread and sets the GUI connection to be run second
    thread_one.start() #starts the server thread
    thread_two.start() #starts the GUI thread
    thread_one.join() #waits for server thread to finish
    thread_two.join() #waits for GUI thread to finish
    print("BOTH GUI AND SERVER THREAD COMPLETE")