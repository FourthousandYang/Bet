import numpy as np
import cv2
import win32gui
import win32con
import win32ui
 
import re
from time import sleep
from PIL import Image
from PIL import ImageGrab
 
'''
製作者：JN
參考網址
https://www.codeproject.com/Articles/20651/Capturing-Minimized-Window-A-Kid-s-Trick
https://www.programcreek.com/python/example/62809/win32ui.CreateBitmap
'''
bets = []
bankers =[]
cards =[]
colors = []
reds = [cv2.imread('Card_Imgs/Diamonds.png',0),cv2.imread('Card_Imgs/Hearts.png',0)
,cv2.imread('Card_Imgs/Diamonds2.png',0),cv2.imread('Card_Imgs/Hearts2.png',0)
,cv2.imread('Card_Imgs/Diamonds3.png',0),cv2.imread('Card_Imgs/Hearts3.png',0)
,cv2.imread('Card_Imgs/Diamonds4.png',0),cv2.imread('Card_Imgs/Hearts4.png',0)]
blacks = [cv2.imread('Card_Imgs/Clubs.png',0),cv2.imread('Card_Imgs/Spades.png',0)
,cv2.imread('Card_Imgs/Clubs2.png',0),cv2.imread('Card_Imgs/Spades2.png',0)
,cv2.imread('Card_Imgs/Clubs3.png',0),cv2.imread('Card_Imgs/Spades3.png',0)
,cv2.imread('Card_Imgs/Clubs4.png',0),cv2.imread('Card_Imgs/Spades4.png',0)]
#red.append(cv2.imread('Card_Imgs/twocard.png',0))
 
def FindWindow_bySearch(pattern):
    window_list = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), window_list)
    for each in window_list:
        print (win32gui.GetWindowText(each))
        if re.search(pattern, win32gui.GetWindowText(each)) is not None:
            return each
 
def getWindow_W_H(hwnd):
    # 取得目標視窗的大小
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    #width = right - left - 15
    #height = bot - top - 11
    return (left, top, right, bot)
 
def getWindow_Img(hwnd):
    # 將 hwnd 換成 WindowLong
    s = win32gui.GetWindowLong(hwnd,win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, s|win32con.WS_EX_LAYERED)
    # 判斷視窗是否最小化
    show = win32gui.IsIconic(hwnd)
    # 將視窗圖層屬性改變成透明    
    # 還原視窗並拉到最前方
    # 取消最大小化動畫
    # 取得視窗寬高
    if show == 1: 
        win32gui.SystemParametersInfo(win32con.SPI_SETANIMATION, 0)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 0, win32con.LWA_ALPHA)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)    
        x, y, width, height = getWindow_W_H(hwnd)        
    # 創造輸出圖層
    hwindc = win32gui.GetWindowDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    # 取得視窗寬高
    x, y, width, height = getWindow_W_H(hwnd)
    # 如果視窗最小化，則移到Z軸最下方
    if show == 1: win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, x, y, width, height, win32con.SWP_NOACTIVATE)
    # 複製目標圖層，貼上到 bmp
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0 , 0), (width, height), srcdc, (8, 3), win32con.SRCCOPY)
    # 將 bitmap 轉換成 np
    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4) #png，具有透明度的
    # 釋放device content
    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())
    # 還原目標屬性
    if show == 1 :
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
        win32gui.SystemParametersInfo(win32con.SPI_SETANIMATION, 1)
    # 回傳圖片
    return img

def mathc_img(image,Target,value): 
    i=0
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread(Target,0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    threshold = value 
    loc = np.where( res >= threshold) 
    for pt in zip(*loc[::-1]): 
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (7,249,151), 2)
        i+=1
    #cv2.imshow('Detected',img_rgb) 
    #cv2.waitKey(0) 
    #cv2.destroyAllWindows()
    print (i)
    return img_rgb    

def mathc_img_bankers(image,value): 
    global bankers
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/banker.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    threshold = value 
    loc = np.where( res >= threshold) 
    for pt in zip(*loc[::-1]): 
        #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (7,249,151), 2)
        bankers.append(((pt[0] + w)/2, (pt[1] + h)/2))
        #bankers.append((pt[0] + w)/2)
    #cv2.imshow('Detected',img_rgb) 
    #cv2.waitKey(0) 
    #cv2.destroyAllWindows()
    
    return img_rgb

def mathc_img_cards(image,value): 
    global cards,bankers
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/twocard.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    threshold = value 
    loc = np.where( res >= threshold) 
    #print (res)
    for banker in bankers:
        for pt in zip(*loc[::-1]): 
        
            if abs(banker[0]-((pt[0] + w)/2))<50 and abs(banker[1]-((pt[1] + h)/2))<150:
                cv2.rectangle(img_rgb, pt, (pt[0] + int(w/2), pt[1] + h), (7,249,151), 2)
                cards.append((pt[0],pt[1],(pt[0] + int(w/2)), (pt[1] + h)))
                break
    #cv2.imshow('Detected',img_rgb) 
    #cv2.waitKey(0) 
    #cv2.destroyAllWindows()
    
    return img_rgb

def mathc_img_color(image,value): 
    global cards,bankers,colors
    img_rgb = image
     
    for card in cards:
        hh = (card[3]-card[1])/2
        #ww = (card[2]-card[0])*4/5
        img_gray = cv2.cvtColor(img_rgb[card[1]:card[3]-int(hh),card[0]:card[2]], cv2.COLOR_BGR2GRAY) 
        #cv2.imshow('card',img_gray) 
        for red in reds:
            w, h = red.shape[::-1] 
            res = cv2.matchTemplate(img_gray,red,cv2.TM_CCOEFF_NORMED) 
            threshold = value 
            loc = np.where( res >= threshold)
            for pt in zip(*loc[::-1]): 
                cv2.putText(img_rgb, 'red', (card[0], card[1]), cv2.FONT_HERSHEY_SIMPLEX,
  1, (0, 0, 255), 1, cv2.LINE_AA)
                colors.append(('player ',card[0],card[1]))
                #if abs(banker[0]-((pt[0] + w)/2))<50 and abs(banker[1]-((pt[1] + h)/2))<150:
                    #cv2.rectangle(img_rgb, pt, (pt[0] + int(w/2), pt[1] + h), (7,249,151), 2)
                    #cards.append(((pt[0] + int(w/2)), (pt[1] + h)))
                #return img_rgb
                break
        for black in blacks:
            w, h = black.shape[::-1] 
            res = cv2.matchTemplate(img_gray,black,cv2.TM_CCOEFF_NORMED) 
            threshold = value 
            loc = np.where( res >= threshold)
            for pt in zip(*loc[::-1]): 
                cv2.putText(img_rgb, 'black', (card[0], card[1]), cv2.FONT_HERSHEY_SIMPLEX,
  1, (0, 0, 0), 1, cv2.LINE_AA)
                colors.append(('banker',card[0],card[1]))
                #if abs(banker[0]-((pt[0] + w)/2))<50 and abs(banker[1]-((pt[1] + h)/2))<150:
                    #cv2.rectangle(img_rgb, pt, (pt[0] + int(w/2), pt[1] + h), (7,249,151), 2)
                    #cards.append(((pt[0] + int(w/2)), (pt[1] + h)))
                #return img_rgb
                break
    #cv2.imshow('Detected',img_rgb) 
    #cv2.waitKey(0) 
    #cv2.destroyAllWindows()
    return img_rgb
    
def mathc_img_bet(image,value): 
    global bets
    #bets=[]
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/bet.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    threshold = value 
    loc = np.where( res >= threshold) 
    for pt in zip(*loc[::-1]): 
        #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (7,249,151), 2)
        #print("1")
        if len(bets) !=0:
            for bet in bets:
                #print("2")
                #print (bet[4])
                if abs(bet[4]-((pt[1] + h/2)))>50:
                    bets.append((pt[0],pt[1],(pt[0] + w), (pt[1] + h),(pt[1] + h/2)))
        else:
            bets.append((pt[0],pt[1],(pt[0] + w), (pt[1] + h),(pt[1] + h/2)))
        #bets.append((pt[0],pt[1],(pt[0] + w), (pt[1] + h),(pt[1] + h/2)))
        #bankers.append((pt[0] + w)/2)
    #cv2.imshow('Detected',img_rgb) 
    #cv2.waitKey(0) 
    #cv2.destroyAllWindows()
    #print(len(bets))
    i = []
    for bet in bets:
        
        #print(bet[4])
        i.append(bet[4])
    #if len(bets) == 4 and max(i)>800 and min(i)<200:
    if len(set(i)) >= 4 and max(i)>800 and min(i)<200:
        #print (set(i))
        
        return 1
    else:
        return 0
 
hwnd = FindWindow_bySearch("CaliBet")

#Target=('Card_Imgs/banker.png')
init = 0
 
while True:
    sleep(0.03)
    x, y, width, height = getWindow_W_H(hwnd)
    #print (getWindow_W_H(hwnd))
    #pic = ImageGrab.grabclipboard()
    #if isinstance(pic, Image.Image):
    #    continue
    #sleep(1)
    bankers =[]
    cards =[]
    colors = []
    pil_image = ImageGrab.grab(bbox=(x, y, width, height))
    
    frame = cv2.cvtColor(np.asarray(pil_image),cv2.COLOR_RGB2BGR)
    if init==0:
        check = mathc_img_bet(frame,0.85)
    
        if check==0 :
            bets=[]
            continue
        else:
            init =1
    
    #frame = mathc_img(frame,'Card_Imgs/bet.png',0.9)
    ###
    
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    kernel_size = 3
    blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size), 0)

    low_threshold = 1
    high_threshold = 10
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    #print (len(bets))
    for bet in bets:
        cv2.rectangle(frame, (bet[0],bet[1]), (bet[2], bet[3]), (7,249,151), 2)
    mtimg = mathc_img_bankers(frame,0.8)
    mtimg = mathc_img_cards(frame,0.55)
    mtimg = mathc_img_color(frame,0.9)
    for color in colors:
        for bet in bets:
            if bet[3]>color[2]>bet[1]:
                ##cv2.putText(mtimg, color[0], (bet[0]+int(bet[2]/2), bet[1]+int(bet[3]/2)), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                cv2.putText(mtimg, color[0], (bet[0], bet[1]), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
    ###
    
    scale_percent = 50 # percent of original size
    width = int(mtimg.shape[1] * scale_percent / 100)
    height = int(mtimg.shape[0] * scale_percent / 100)
    dim = (width, height)
    reimage = cv2.resize(mtimg, dim, interpolation = cv2.INTER_AREA)
    
    
    #pil_image = ImageGrab.grab()
    #print (pic.size)
    #pil_image = pic.crop(box=(x,y,width-x,height-y))
    
    
    
    #frame = getWindow_Img(hwnd)
    cv2.imshow("screen box", reimage)
    #cv2.imshow("screen box", frame)
    #cv2.imshow("edges box", edges)
    k = cv2.waitKey(30)&0xFF #64bits! need a mask
    if k ==27:
        cv2.destroyAllWindows()
        break