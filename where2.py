from pynput.mouse import Listener
import pyautogui as pag

def on_click(x, y, button, pressed):
    
    if pressed:
        if str(button)=='Button.left':
            x,y = pag.position()
            print ('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
            posStr = "Position:" + str(x).rjust(4)+','+str(y).rjust(4)
            print(posStr)
        if str(button)=='Button.right':
            return False
    # if pressed:
        # print ('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))


with Listener( on_click=on_click) as listener:
    listener.join()