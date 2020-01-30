import win32gui
dc = win32gui.GetDC(0)
for __ in range(1024):
    print("enter crtl + c to quit")
while(True):
    win32gui.Rectangle(dc, 100, 900, 1800, 975)
