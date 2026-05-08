import RPi.GPIO as GPIO
import time

def stepper_motor(axis,direction,amount):
    # Setting up GPIO pins
    if axis == "X":
        IN1 = 23
        IN2 = 16
        IN3 = 20
        IN4 = 18
    elif axis == "Y":
        IN1 = 6
        IN2 = 13
        IN3 = 17
        IN4 = 22

    motor_pins = [IN1, IN2, IN3, IN4] #defining motorpins for the step sequence
    delay = 0.002 #using 0.002 as the delay gives a good speed
    STEPS_PER_REVOLUTION = amount
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)

    # Half step sequence
    half_step_seq = [
        [1, 0, 0, 1],
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1]
    ]


    def set_step(step_values):
        for pin, value in zip(motor_pins, step_values):
            GPIO.output(pin, value)

    # Rotate motor forward
    def step_forward(delay, steps):
        for _ in range(steps):
            for step in half_step_seq:
                set_step(step)
                time.sleep(delay)

    # Rotate motor backward
    def step_backward(delay, steps):
        for _ in range(steps):
            for step in reversed(half_step_seq):
                set_step(step)
                time.sleep(delay)


    if direction == "F":
        step_forward(delay, STEPS_PER_REVOLUTION)
    elif direction == "B":
        step_backward(delay, STEPS_PER_REVOLUTION)
