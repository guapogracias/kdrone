import tkinter as tk
from PIL import Image, ImageTk
from djitellopy import Tello
import keypress as kp
import numpy as np
import cv2
import math
from time import sleep
import threading

# --- Parameters ---
fSpeed = 117 / 10
aSpeed = 360 / 10
interval = 0.25
dInterval = fSpeed * interval
aInterval = aSpeed * interval

# --- Drone state ---
x, y, yaw = 250, 250, 0
a = 0
flying = False
points = [(x, y)]

# --- Init Tello and keyboard ---
kp.init()
me = Tello()
me.connect()
me.send_command_with_return("command")
me.streamon()

# --- GUI Setup ---
root = tk.Tk()
root.title("Drone Dashboard")

video_label = tk.Label(root)
video_label.grid(row=0, column=0)

path_label = tk.Label(root)
path_label.grid(row=0, column=1)

battery_label = tk.Label(root, text=f"Battery: {me.get_battery()}%", font=("Arial", 12))
battery_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

button_frame = tk.Frame(root)
button_frame.grid(row=1, column=1, sticky="e", padx=10)

takeoff_btn = tk.Button(button_frame, text="Take Off", width=10)
land_btn = tk.Button(button_frame, text="Land", width=10)
takeoff_btn.grid(row=0, column=0, padx=5)
land_btn.grid(row=0, column=1, padx=5)

# --- Movement control ---
def getKeyboardInput():
    global x, y, a, yaw, flying
    lr, fb, ud, yv = 0, 0, 0, 0
    move_distance = 0
    speed = 50

    if kp.getKey("LEFT"):
        lr = -speed
        move_distance = dInterval
        a = -180
    elif kp.getKey("RIGHT"):
        lr = speed
        move_distance = -dInterval
        a = 180

    if kp.getKey("UP"):
        fb = speed
        move_distance = dInterval
        a = 270
    elif kp.getKey("DOWN"):
        fb = -speed
        move_distance = -dInterval
        a = -90

    if kp.getKey("w"):
        ud = speed
    elif kp.getKey("s"):
        ud = -speed

    if kp.getKey("a"):
        yv = -speed
        yaw -= aInterval
    elif kp.getKey("d"):
        yv = speed
        yaw += aInterval

    sleep(interval)

    a += yaw
    x += int(move_distance * math.cos(math.radians(a)))
    y += int(move_distance * math.sin(math.radians(a)))

    return [lr, fb, ud, yv, x, y]

def drawPathCanvas():
    img = np.zeros((500,500, 3), np.uint8)
    for pt in points:
        cv2.circle(img, pt, 5, (0, 0, 255), cv2.FILLED)
    cv2.circle(img, points[-1], 8, (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'({(points[-1][0]-500)/100:.1f},{(points[-1][1]-500)/100:.1f})m',
                (points[-1][0] + 10, points[-1][1] + 30),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return ImageTk.PhotoImage(Image.fromarray(img))

def update():
    global flying

    vals = getKeyboardInput()
    if flying:
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])

    # Update video feed
    frame = me.get_frame_read().frame
    frame = cv2.resize(frame, (500, 500))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(Image.fromarray(frame))
    video_label.configure(image=img)
    video_label.image = img

    # Update path
    if points[-1][0] != vals[4] or points[-1][1] != vals[5]:
        points.append((vals[4], vals[5]))

    path_img = drawPathCanvas()
    path_label.configure(image=path_img)
    path_label.image = path_img

    # Battery
    battery_label.config(text=f"Battery: {me.get_battery()}%")

    root.after(50, update)

# --- Button handlers ---
def takeoff():
    global flying
    if not flying:
        me.takeoff()
        flying = True

def land():
    global flying
    if flying:
        me.land()
        flying = False

takeoff_btn.config(command=takeoff)
land_btn.config(command=land)

# --- Run ---
update()
root.mainloop()
