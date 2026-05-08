import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
import time
from StepperControl import *
from facial_recognition import *
import socket
import threading

def start_command_server(): #sets the RPI as the server to recieve commands from the base station
    COMMAND_PORT = 5001
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", COMMAND_PORT))
    server.listen(5)
    print("Motor command server listening on port", COMMAND_PORT)
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_command_client, args=(conn,), daemon=True).start() #waits for a connection form the base station

def handle_command_client(conn):
    try:
        data = conn.recv(1024).decode().strip() #decodes data and turns incomind messages to plain english
        if data == "UP":
            stepper_motor("Y", "F", 25) #depending on what command is sent then motors are turned
        elif data == "DOWN":
            stepper_motor("Y", "B", 25)
        elif data == "LEFT":
            stepper_motor("X", "F", 25)
        elif data == "RIGHT":
            stepper_motor("X", "B", 25)
    except:
        handle_command_client(conn) #if error occures then the command is retried
    finally:
        conn.close()#if fails again connection is closed



def RGB_LED(Red,Green,Blue): #displays a blue LED to show camera is active and recieving motor controls
    GPIO.output(25,Red)
    GPIO.output(24,Green)
    GPIO.output(19,Blue)


def motor_start():
    try:
        GPIO.setup(25,GPIO.OUT) #RED LED
        GPIO.setup(19,GPIO.OUT) # Green LED
        GPIO.setup(24,GPIO.OUT) # Blue LED
        recieve_prompt_RCMODE("DOWN") #moves motor down when first connected as a test.
    except:
        #GPIO.cleanup()
        recieve_prompt_RCMODE("Error Occured")
    finally:
        GPIO.cleanup()
