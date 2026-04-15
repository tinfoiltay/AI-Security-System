# Threading may not be useful at this time as it may be able to be done all in one process as all is needed is sending data
import client
import threading


def client_connection_program(): #this defines the starting function of the file we want to use in the server code
    client.client_program()

def camera_functions_program(): #this defines the starting function of the file we want to use in the GUI code
    pass




if __name__ == '__main__': # if this is the starting program then run this file
    thread_one = threading.Thread(target=client_connection_program) #Defines the first thread and sets the client connection to be run first
    thread_two = threading.Thread(target=camera_functions_program) #Defines the first thread and sets the camera functions to be run second
    thread_one.start() #starts the cleint thread
    thread_two.start() #starts the GUI thread
    thread_one.join() #waits for server thread to finish
    thread_two.join() #waits for GUI thread to finish
    print("BOTH CAMERA AND CLIENT THREAD COMPLETE")