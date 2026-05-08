from threading import Thread
from basestation_controls import motor_start as channel_A
from facial_recognition import Camera_Start as channel_B

ThreadA = Thread(target= channel_A)
ThreadB = Thread(target= channel_B)

ThreadA.start()
ThreadB.start()

ThreadA.join()
ThreadB.join()