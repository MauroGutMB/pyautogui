import time
import msvcrt

import pyautogui

print("Press 'p' to print current position. Press Ctrl+C to stop.")
try:
	while True:
		if msvcrt.kbhit():
			key = msvcrt.getch()
			if key in (b"p", b"P"):
				x, y = pyautogui.position()
				print(f"X={x} Y={y}, ({x}, {y})")
		time.sleep(0.05)
except KeyboardInterrupt:
	print("Stopped.")