import numpy as np
import cv2
import win32gui
import win32con
import win32ui
import pyautogui
 
import re
from time import sleep
from PIL import Image
from PIL import ImageGrab
import collections
from pynput.mouse import Listener
import gc

gc.collect()

'''
製作者：JN
參考網址
https://www.codeproject.com/Articles/20651/Capturing-Minimized-Window-A-Kid-s-Trick
https://www.programcreek.com/python/example/62809/win32ui.CreateBitmap
'''
round_time = 0
round_start = 0
check = 0
check_end = 0
startbet = 0
lose_count = 0
switch_acc = 1
whowin = ''
bet_one=''
bet_last=''
status=''
result = 'first'
count = [0,0,0,0]
end = [0,0,0,0]
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

message = np.zeros((500, 450,3), np.uint8)


def FindWindow_bySearch(pattern):
    window_list = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), window_list)
    for each in window_list:
        #print (win32gui.GetWindowText(each))
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
## not use
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
## not use
def mathc_img_bet_banker(image,value): 
    #global count
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/bet_banker.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    
    min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    
    if max_l[1] + h < 270 and 600< max_l[0] + w <1280 :
        
        return int((max_l[0] + w)), int((max_l[1] + h))
    
    
    return 0,0
## not use
def mathc_img_bet_player(image,value): 
    #global count
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/bet_player.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    
    min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    
    if max_l[1] + h < 270 and 600< max_l[0] + w <1280 :
        
        return int((max_l[0] + w)), int((max_l[1] + h))

    
    return 0,0

## not use
def mathc_img_bet_confirm(image,value): 
    #global count
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/confirm.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    
    min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    
    if 100<max_l[1] + h < 270 and 600< max_l[0] + w <1280 :
        
        return int((max_l[0] + w)), int((max_l[1] + h))
    
    
    return 0,0
## 判斷洗牌
def mathc_img_ini(image,value): 
    global count,round_start,status
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/reset1.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    
    min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    
    if 150<max_l[1] + h < 270 and 100< max_l[0] + w <1280 :
        count[0] = 0
        round_start = 1
        status='reset'
        #print ('ini')
        cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
       
    
    return img_rgb
## 判斷結算
def mathc_img_end(image,value): 
    global count,end,check,startbet,check_end,round_time,status
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/end.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    
 
    min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    
    if max_l[1] + h < 270 and 100< max_l[0] + w <1280 :
        
        cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
        check = 0
        check_end = 1
        status='close'
        #end[0] = 2
        #cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
        #bankers.append(((max_l[0] + w)/2, (max_l[1] + h)/2))
    else:
        #print('bet time')
        round_time = 0
        check_end = 0
        end[0] = 0
        startbet = 1
        status='start bet'
   
    
    return img_rgb
    
## not use
def mathc_img_whowin(image,value): 
    global count,end,whowin,bet_last,result,lose_count
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    player_win = cv2.imread('Card_Imgs/player_win.png',0) 
    banker_win = cv2.imread('Card_Imgs/banker_win.png',0)
    no_win = cv2.imread('Card_Imgs/no_win.png',0)
    #w, h = template.shape[::-1] 
    player_win_res = cv2.matchTemplate(img_gray,player_win,cv2.TM_CCOEFF_NORMED) 
    banker_win_res = cv2.matchTemplate(img_gray,banker_win,cv2.TM_CCOEFF_NORMED) 
    no_win_res = cv2.matchTemplate(img_gray,no_win,cv2.TM_CCOEFF_NORMED) 
    
    #min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    #if end[0]!=0:
        #return img_rgb
    if player_win_res!=[]:
        w, h = player_win.shape[::-1] 
        min_v,max_v,min_l,max_l = cv2.minMaxLoc(player_win_res)
        if 100< max_l[1] + h < 270 and 400< max_l[0] + w <600 and end[0]!=1:
            count[0] = count[0]+1
            end[0] = 1
            whowin='player'
            if bet_last==whowin:
                #cv2.putText(message, 'bet win', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                result = 'bet win'
                lose_count = 0
                print ('bet win')
            elif bet_last=='':
                #cv2.putText(message, 'no bet', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                result = 'no bet'
                print('no bet')
            else:
                #cv2.putText(message, 'bet lose', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                result = 'bet lose'
                lose_count += 1
                print ('bet lose')
            #cv2.putText(message, 'p win', (50, 250), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
            print('p win')
            print('---')
            cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
    if banker_win_res!=[]:
        w, h = banker_win.shape[::-1] 
        min_v,max_v,min_l,max_l = cv2.minMaxLoc(banker_win_res)
        if 100< max_l[1] + h < 270 and 400< max_l[0] + w <600 and end[0]!=1:
            count[0] = count[0]+1
            end[0] = 1
            whowin='banker'
            if bet_last==whowin:
                #cv2.putText(message, 'bet win', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                result = 'bet win'
                lose_count = 0
                print ('bet win')
            elif bet_last=='':
                #cv2.putText(message, 'no bet', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                result = 'no bet'
                print('no bet')
            else:
                #cv2.putText(message, 'bet lose', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                result = 'bet lose'
                lose_count += 1
                print ('bet lose')
            #cv2.putText(message, 'b win', (50, 250), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
            print('b win')
            print('---')
            cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
    if no_win_res!=[]:
        w, h = no_win.shape[::-1] 
        min_v,max_v,min_l,max_l = cv2.minMaxLoc(no_win_res)
        if 100< max_l[1] + h < 270 and 400< max_l[0] + w <600 and end[0]!=1:
            count[0] = count[0]+1
            end[0] = 1
            print('n win')
            print('---')
            cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
     
    
    
    return img_rgb


## not use
def mathc_img_bankers(image,value): 
    global bankers
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/banker.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    
    min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    
    if max_l[1] + h < 270:
        #cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
        bankers.append(((max_l[0] + w)/2, (max_l[1] + h)/2))
     
    
    return img_rgb
## not use
def mathc_img_cards(image,value): 
    global cards,bankers
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    template = cv2.imread('Card_Imgs/twocard.png',0) 
    w, h = template.shape[::-1] 
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
    min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    

    threshold = value 
    loc = np.where( res >= threshold) 
    #print (res)
    for banker in bankers:
        for pt in zip(*loc[::-1]): 
        
            if abs(banker[0]-((pt[0] + w)/2))<50 and abs(banker[1]-((pt[1] + h)/2))<150 and (pt[1] + h) <270:
                cv2.rectangle(img_rgb, pt, (pt[0] + int(w/2), pt[1] + h), (7,249,151), 2)
                cards.append((pt[0],pt[1],(pt[0] + int(w/2)), (pt[1] + h)))
                break

    
    return img_rgb
## not use
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
                cv2.putText(img_rgb, 'red', (card[0], card[1]), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 0, 255), 1, cv2.LINE_AA)
                colors.append(('banker',card[0],card[1]))

                break
        for black in blacks:
            w, h = black.shape[::-1] 
            res = cv2.matchTemplate(img_gray,black,cv2.TM_CCOEFF_NORMED) 
            threshold = value 
            loc = np.where( res >= threshold)
            for pt in zip(*loc[::-1]): 
                cv2.putText(img_rgb, 'black', (card[0], card[1]), cv2.FONT_HERSHEY_SIMPLEX,
  1, (0, 0, 0), 1, cv2.LINE_AA)
                colors.append(('player',card[0],card[1]))

                break
 
    return img_rgb
## 色表
def getColorList():
    dict = collections.defaultdict(list)
 
    # 黑色
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 46])
    color_list = []
    color_list.append(lower_black)
    color_list.append(upper_black)
    dict['black'] = color_list
 
    # # #灰色
    # # lower_gray = np.array([0, 0, 46])
    # # upper_gray = np.array([180, 43, 220])
    # # color_list = []
    # # color_list.append(lower_gray)
    # # color_list.append(upper_gray)
    # # dict['gray']=color_list
 
    # # 白色
    # lower_white = np.array([0, 0, 221])
    # upper_white = np.array([180, 30, 255])
    # color_list = []
    # color_list.append(lower_white)
    # color_list.append(upper_white)
    # dict['white'] = color_list
 
    #红色
    lower_red = np.array([156, 43, 46])
    upper_red = np.array([180, 255, 255])
    color_list = []
    color_list.append(lower_red)
    color_list.append(upper_red)
    dict['red']=color_list
 
    # 红色2
    lower_red = np.array([0, 43, 46])
    upper_red = np.array([10, 255, 255])
    color_list = []
    color_list.append(lower_red)
    color_list.append(upper_red)
    dict['red2'] = color_list
 
    # #橙色
    # lower_orange = np.array([11, 43, 46])
    # upper_orange = np.array([25, 255, 255])
    # color_list = []
    # color_list.append(lower_orange)
    # color_list.append(upper_orange)
    # dict['orange'] = color_list
 
    # #黄色
    # lower_yellow = np.array([26, 43, 46])
    # upper_yellow = np.array([34, 255, 255])
    # color_list = []
    # color_list.append(lower_yellow)
    # color_list.append(upper_yellow)
    # dict['yellow'] = color_list
 
    #绿色
    lower_green = np.array([35, 43, 46])
    upper_green = np.array([77, 255, 255])
    color_list = []
    color_list.append(lower_green)
    color_list.append(upper_green)
    dict['green'] = color_list
 
    # #青色
    # lower_cyan = np.array([78, 43, 46])
    # upper_cyan = np.array([99, 255, 255])
    # color_list = []
    # color_list.append(lower_cyan)
    # color_list.append(upper_cyan)
    # dict['cyan'] = color_list
 
    #蓝色
    lower_blue = np.array([100, 43, 46])
    upper_blue = np.array([124, 255, 255])
    color_list = []
    color_list.append(lower_blue)
    color_list.append(upper_blue)
    dict['blue'] = color_list
 
    # # 紫色
    # lower_purple = np.array([125, 43, 46])
    # upper_purple = np.array([155, 255, 255])
    # color_list = []
    # color_list.append(lower_purple)
    # color_list.append(upper_purple)
    # dict['purple'] = color_list
 
    return dict


## 判斷顏色
def get_color(frame):
    #print('go in get_color')
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    maxsum = -100
    color = None
    color_dict = getColorList()
    for d in color_dict:
        mask = cv2.inRange(hsv,color_dict[d][0],color_dict[d][1])
        #cv2.imwrite(d+'.jpg',mask)
        binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
        binary = cv2.dilate(binary,None,iterations=2)
        img, cnts, hiera = cv2.findContours(binary.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        sum = 0
        for c in cnts:
            sum+=cv2.contourArea(c)
        if sum > maxsum :
            maxsum = sum
            color = d
 
    return color
## 判斷誰贏(顏色)
def img_whowin(image): 
    global count,end,whowin,bet_last,result,lose_count,check_end,round_time
    
    #img_rgb = image
    # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    # player_win = cv2.imread('Card_Imgs/player_win.png',0) 
    # banker_win = cv2.imread('Card_Imgs/banker_win.png',0)
    # no_win = cv2.imread('Card_Imgs/no_win.png',0)
    # #w, h = template.shape[::-1] 
    # player_win_res = cv2.matchTemplate(img_gray,player_win,cv2.TM_CCOEFF_NORMED) 
    # banker_win_res = cv2.matchTemplate(img_gray,banker_win,cv2.TM_CCOEFF_NORMED) 
    # no_win_res = cv2.matchTemplate(img_gray,no_win,cv2.TM_CCOEFF_NORMED) 
    # print (len(player_win_res) , len(banker_win_res), len(no_win_res))
    #whowin_image = image[174:224,476:506]
    #cv2.rectangle(img_rgb, (476,174), (506, 224), (7,249,151), 2)
    
    
    #if end[0] !=1 and len(player_win_res) !=0 and len(banker_win_res)!=0 and len(no_win_res)!=0:
    #print ('in')
    #print (end[0],check_end)
    
    if end[0] !=1 and check_end==1:
        #sleep(1)
        #round_time += 1
        #print ('in')
        #print (cr)
        #print ('wait')
        #sleep(14)
        #print ('go')
        #print (round_time)
        #if round_time > 13:
            cr=get_color(image)
            #cv2.imwrite('cr.jpg',image)
            #print (cr)
            if cr =='red' or cr =='red2' :
                    count[0] = count[0]+1
                    end[0] = 1
                    whowin='banker'
                    if bet_last==whowin:
                        #cv2.putText(message, 'bet win', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                        result = 'bet win'
                        lose_count = 0
                        print ('bet win')
                    elif bet_last=='':
                        #cv2.putText(message, 'no bet', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                        result = 'no bet'
                        print('no bet')
                    else:
                        #cv2.putText(message, 'bet lose', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                        result = 'bet lose'
                        lose_count += 1
                        print ('bet lose')
                    #cv2.putText(message, 'b win', (50, 250), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                    print('b win')
                    print('---')
                    
            if cr =='blue':
                    count[0] = count[0]+1
                    end[0] = 1
                    whowin='player'
                    if bet_last==whowin:
                        #cv2.putText(message, 'bet win', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                        result = 'bet win'
                        lose_count = 0
                        print ('bet win')
                    elif bet_last=='':
                        #cv2.putText(message, 'no bet', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                        result = 'no bet'
                        print('no bet')
                    else:
                        #cv2.putText(message, 'bet lose', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                        result = 'bet lose'
                        lose_count += 1
                        print ('bet lose')
                    #cv2.putText(message, 'p win', (50, 250), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                    print('p win')
                    print('---')
            if cr=='green' :
                count[0] = count[0]+1
                end[0] = 1
                whowin='no one'
                result = 'no win'
                print('n win')
                print('---')
    #return img_rgb
## 判斷誰贏
def mathc_img_whowin1(image,value): 
    global count,end,whowin,bet_last,result,lose_count
    img_rgb = image
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
    player_win = cv2.imread('Card_Imgs/player_win.png',0) 
    banker_win = cv2.imread('Card_Imgs/banker_win.png',0)
    no_win = cv2.imread('Card_Imgs/no_win.png',0)
    #w, h = template.shape[::-1] 
    player_win_res = cv2.matchTemplate(img_gray,player_win,cv2.TM_CCOEFF_NORMED) 
    banker_win_res = cv2.matchTemplate(img_gray,banker_win,cv2.TM_CCOEFF_NORMED) 
    no_win_res = cv2.matchTemplate(img_gray,no_win,cv2.TM_CCOEFF_NORMED) 
    
    #min_v,max_v,min_l,max_l = cv2.minMaxLoc(res)
    #if end[0]!=0:
        #return img_rgb
    
    threshold = value
    if player_win_res!=[]:
        w, h = player_win.shape[::-1] 
        
        min_v,max_v,min_l,max_l = cv2.minMaxLoc(player_win_res)
        if 50< max_l[1] + h/2 < 200 and 300< max_l[0] + w/2 <500 :
            
            #img_whowin(image)
            img_whowin(img_rgb[max_l[1]:max_l[1] + h,max_l[0]:max_l[0] + w])
            cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
            cv2.imwrite('cr1.jpg',img_rgb)
        
    if banker_win_res!=[]:
        w, h = banker_win.shape[::-1]
        
        min_v,max_v,min_l,max_l = cv2.minMaxLoc(banker_win_res)
        if 50< max_l[1] + h/2 < 300 and 300< max_l[0] + w/2 <500 :
            
            #img_whowin(image)
            img_whowin(img_rgb[max_l[1]:max_l[1] + h,max_l[0]:max_l[0] + w])
            cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
            cv2.imwrite('cr1.jpg',img_rgb)
        
    if no_win_res!=[]:
        w, h = no_win.shape[::-1]
        
        min_v,max_v,min_l,max_l = cv2.minMaxLoc(no_win_res)
        if 50< max_l[1] + h/2 < 200 and 300< max_l[0] + w/2 <500 :
            
            #img_whowin(image)
            img_whowin(img_rgb[max_l[1]:max_l[1] + h,max_l[0]:max_l[0] + w])
            cv2.rectangle(img_rgb, max_l, (max_l[0] + w, max_l[1] + h), (7,249,151), 2)
            cv2.imwrite('cr1.jpg',img_rgb)
     
    
    
    return img_rgb


## 判斷牌色
def mathc_img_color_one(image,value): 
    global cards,bankers,colors,end
    img_rgb = image
     
    #card = [562,175,634,280]
    card = [569+5,181+5,579+5,205+5]
    
    #hh = (card[3]-card[1])/2
    #ww = (card[2]-card[0])*4/5
    if end[0]==1:
        scolor = get_color(img_rgb[card[1]:card[3],card[0]:card[2]])
        cv2.rectangle(img_rgb, (card[0],card[1]), (card[2],card[3]), (7,249,151), 2)
        if scolor=='red' or scolor=='red2':
            cv2.putText(img_rgb, 'red', (card[0], card[1]), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 0, 255), 1, cv2.LINE_AA)
            colors.append(('banker',card[0],card[1],card[2],card[3]))
        if scolor=='black':
            cv2.putText(img_rgb, 'black', (card[0], card[1]), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 0, 0), 1, cv2.LINE_AA)
            colors.append(('player',card[0],card[1],card[2],card[3]))
    #img_gray = cv2.cvtColor(img_rgb[card[1]:card[3]-int(hh),card[0]:card[2]], cv2.COLOR_BGR2GRAY)
    #img_gray = img_rgb[card[1]:card[3],card[0]:card[2]]
    #scale_percent = 500 # percent of original size
    #width = int(img_gray.shape[1] * scale_percent / 100)
    #height = int(img_gray.shape[0] * scale_percent / 100)
    #dim = (width, height)
    #img = cv2.resize(img_gray, dim, interpolation = cv2.INTER_AREA)
    #cv2.imshow('card',img) 
    # for red in reds:
        # #cv2.rectangle(img_rgb, (583,161), (643,258), (7,249,151), 2)
        # cv2.rectangle(img_rgb, (card[0],card[1]), (card[2],card[3]), (7,249,151), 2)
        # w, h = red.shape[::-1] 
        # res = cv2.matchTemplate(img_gray,red,cv2.TM_CCOEFF_NORMED) 
        # threshold = value 
        # loc = np.where( res >= threshold)
        # for pt in zip(*loc[::-1]): 
            # cv2.rectangle(img_rgb, (583,161), (643,258), (7,249,151), 2)
            # cv2.putText(img_rgb, 'red', (card[0], card[1]), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 0, 255), 1, cv2.LINE_AA)
            # colors.append(('banker',card[0],card[1]))
           
            # break
    # for black in blacks:
        # #cv2.rectangle(img_rgb, (583,161), (643,258), (7,249,151), 2)
        # cv2.rectangle(img_rgb, (card[0],card[1]), (card[2],card[3]), (7,249,151), 2)
        # w, h = black.shape[::-1] 
        # res = cv2.matchTemplate(img_gray,black,cv2.TM_CCOEFF_NORMED) 
        # threshold = value 
        # loc = np.where( res >= threshold)
        # for pt in zip(*loc[::-1]): 
            # cv2.rectangle(img_rgb, (583,161), (643,258), (7,249,151), 2)
            # cv2.putText(img_rgb, 'black', (card[0], card[1]), cv2.FONT_HERSHEY_SIMPLEX,
# 1, (0, 0, 0), 1, cv2.LINE_AA)
            # colors.append(('player',card[0],card[1]))
           
            # break
    #sleep(0.5)
    #print (colors)
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
        
    i = []
    for bet in bets:
        
        print(bet[4])
        i.append(bet[4])
    #if len(bets) == 4 and max(i)>800 and min(i)<200:
    if len(set(i)) >= 4 and max(i)>800 and min(i)<200:
        print (set(i))
        
        return 1
    else:
        return 0
## 選擇籌碼
def select_money(value):
    x50=981
    y50=798
    x100=1038
    y100=798
    x500=1093
    y500=798
    x1000=1154
    y1000=798
    x5000=1206
    y5000=798
    if value==50:
        pyautogui.click(x=x50,y=y50,button='left')
    elif value==100:
        pyautogui.click(x=x100,y=y100,button='left')
    elif value==500:
        pyautogui.click(x=x500,y=y500,button='left')
    elif value==1000:
        pyautogui.click(x=x1000,y=y1000,button='left')
    elif value==5000:
        pyautogui.click(x=x5000,y=y5000,button='left')
##下誰
def bet_who(who,times,ok=0):
    wbx=883
    wby=106
    wpx=719
    wby=106
    wcx=806
    wcy=233
    if who=='banker':
        pyautogui.click(x=wbx,y=wby,button='left')
        pyautogui.click(clicks=times-1)
    if who=='player':
        pyautogui.click(x=wpx,y=wby,button='left')
        pyautogui.click(clicks=times-1)
    if ok == 1:
        pyautogui.click(x=wcx,y=wcy,button='left')

##下注
def bet_money(lose_times,who):
    if lose_times == 0:

        select_money(100)
        bet_who(who,1,1)
        
    elif lose_times == 1:
        select_money(100)
        bet_who(who,2,1)
    elif lose_times == 2:
        select_money(100)
        bet_who(who,4,1)
    elif lose_times == 3:
        select_money(500)
        #sleep(0.5)
        bet_who(who,1)
        select_money(100)
        #sleep(0.5)
        bet_who(who,3)
        select_money(50)
        #sleep(0.5)
        bet_who(who,1,1)
    elif lose_times == 4:
        select_money(1000)
        bet_who(who,1)
        select_money(500)
        bet_who(who,1)
        select_money(100)
        bet_who(who,2,1)
    elif lose_times == 5:
        select_money(1000)
        bet_who(who,3)
        select_money(500)
        bet_who(who,1,1)
        
    elif lose_times == 6:
        select_money(5000)
        bet_who(who,1)
        select_money(1000)
        bet_who(who,2)
        select_money(100)
        bet_who(who,2,1)
    elif lose_times == 7:
        select_money(5000)
        bet_who(who,2)
        select_money(1000)
        bet_who(who,4)
        select_money(500)
        bet_who(who,1)
        select_money(100)
        bet_who(who,3,1)
    elif lose_times == 8:
        select_money(5000)
        bet_who(who,6)
        select_money(100)
        bet_who(who,4,1)
## 切換帳號
def switch(acc):
    global switch_acc
    if acc == 1:
        switch_acc = 1
        pyautogui.click(x=116,y=17,button='left')
    if acc == 2:
        switch_acc = 2
        pyautogui.click(x=378,y=17,button='left')
    
def on_click(x, y, button, pressed):
    
    # if pressed:
        # if str(button)=='Button.left':
            # print ('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
        # if str(button)=='Button.right':
            # return False
    if pressed:
        print ('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))

## 主程式
# with Listener( on_click=on_click) as listener:
    # listener.join()
    
hwnd = FindWindow_bySearch("CaliBet")
#Target=('Card_Imgs/banker.png')
init = 0
pyautogui.FAILSAFE= False

x, y, width, height = getWindow_W_H(hwnd)
pil_image = ImageGrab.grab(bbox=(x, y, width, height))
frame = cv2.cvtColor(np.asarray(pil_image),cv2.COLOR_RGB2BGR)
bx,by = mathc_img_bet_banker(frame,1)
px,py = mathc_img_bet_player(frame,1)
#cx,cy = mathc_img_bet_confirm(frame,1)

while(bx!=0 and by!=0 and px!=0 and py!=0):
    
    sleep(0.03)
    message.fill(0) #= np.zeros((500, 600), np.uint8)
    x, y, width, height = getWindow_W_H(hwnd)
    #print (getWindow_W_H(hwnd))
    #pic = ImageGrab.grabclipboard()
    #if isinstance(pic, Image.Image):
    #    continue
    #sleep(1)
    bankers =[]
    cards =[]
    colors = []
    if lose_count>9:
        lose_count = 0
    if (lose_count == 8 or lose_count == 9)  and switch_acc == 2:
        switch(2)
    else:
        if switch_acc != 1:
            switch(1)
    if result=='bet win' and count[0]>=51:
        bets=[]
        whowin = ''
        bet_one=''
        bet_last=''
        result = 'first'
        count[0] = 0
        round_start = 0
        continue
    pil_image = ImageGrab.grab(bbox=(x, y, width, height))
    
    frame = cv2.cvtColor(np.asarray(pil_image),cv2.COLOR_RGB2BGR)
    # if init==0:
        # #check = mathc_img_bet(frame,0.85)
        
        # if check==0 :
            # #print ('check')
            # bets=[]
            # continue
        # else:
            # init =1
    
    #frame = mathc_img(frame,'Card_Imgs/bet.png',0.9)
    ###
    
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    kernel_size = 3
    blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size), 0)

    low_threshold = 1
    high_threshold = 10
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    #print (len(bets))
    # for bet in bets:
        # cv2.rectangle(frame, (bet[0],bet[1]), (bet[2], bet[3]), (7,249,151), 2)
    
    #x=1028-50,y=276
    
    cv2.circle(frame,(1028-50,296),10,(0,0,255),-1)
    cv2.circle(frame,(1150-50,115),10,(0,255,0),-1)
    cv2.circle(frame,(932-50,115),10,(255,0,0),-1)
    #print (bx,by,px,py)
    mtimg = mathc_img_ini(frame,0.9)
    mtimg = mathc_img_end(frame,0.9)
    #mtimg = mathc_img_whowin(frame,0.9)
    #img_whowin(frame)
    mtimg = mathc_img_whowin1(frame,0.8)
    #mtimg = mathc_img_bankers(frame,0.8)
    #mtimg = mathc_img_cards(frame,0.55)
    mtimg = mathc_img_color_one(frame,0.9)
    
    '''
    for color in colors:
        for bet in bets:
            if bet[3]>color[2]>bet[1]:
                ##cv2.putText(mtimg, color[0], (bet[0]+int(bet[2]/2), bet[1]+int(bet[3]/2)), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                cv2.putText(mtimg, color[0], (bet[0], bet[1]), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
                #print (color)
                if color[0] =='banker':
                    bet_one = 'banker'
                    #print ('banker')
                    # check=1
                    # pyautogui.click(x=bx,y=by,button='left')
                if color[0] =='player':
                    bet_one = 'player'
                    #print ('player')
                    # check=1
                    # pyautogui.click(x=px,y=py,button='left')
    '''
    #print (colors)
    if colors!=[]:
        if colors[0][0] =='banker' :
            bet_one = 'banker'
            #print ('banker')
            
        if colors[0][0] =='player' :
            bet_one = 'player'
            # ('player')
    # if check==0:
        # if bet_last==whowin:
            # print('win')
        # elif bet_last=='':
            # print('no bet')
        # else:
            # print('lose')
    '''
    if bet_one =='banker' and startbet == 1 and check==0:
        sleep(1)
        check=1
        startbet = 0
        #pyautogui.click(x=bx,y=by,button='left')
        cv2.circle(frame,(bx-50,by-50),10,(0,0,255),-1)
        
        pyautogui.moveTo(bx-50,by-50)
        pyautogui.click(clicks=1)
        #pyautogui.doubleClick()
        #print('click')
        #pyautogui.click(x=cx,y=cy,button='left')1028, 276
        cv2.circle(frame,(1028,276),10,(0,0,255),-1)
        pyautogui.click(x=1028,y=276,button='left')
        #print('click_c')
        bet_last='banker'
        bet_one=''
    if bet_one =='player' and startbet == 1 and check==0:
        sleep(1)
        check=1
        startbet = 0
        cv2.circle(frame,(px-50,py-50),10,(0,0,255),-1)
        pyautogui.moveTo(px-50,py-50)
        #pyautogui.click(x=px,y=py,button='left')
        #pyautogui.doubleClick()
        pyautogui.click(clicks=1)
        #print('click')
        #pyautogui.click(x=cx,y=cy,button='left')
        cv2.circle(frame,(1028,276),10,(0,0,255),-1)
        pyautogui.click(x=1028,y=276,button='left')
        #print('click_c')
        bet_last='player'
        bet_one=''
    '''
    #print (bet_one)
    if bet_one =='banker' and startbet == 1  :
        sleep(1)
        check=1
        startbet = 0
        #pyautogui.click(x=bx,y=by,button='left')
        bet_money(lose_count,bet_one)
        #print('click_c')
        bet_last='banker'
        bet_one=''
        #cv2.putText(message, "Status: betting", (50, 300), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
        status='betting'
        #print ('bet')
    if bet_one =='player' and startbet == 1  :
        sleep(1)
        check=1
        startbet = 0
        bet_money(lose_count,bet_one)
        #print('click_c')
        bet_last='player'
        bet_one=''
        status='betting'
        #cv2.putText(message, "Status: betting", (50, 300), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
        #print ('bet')
    
    
    ###
    cv2.putText(mtimg, str(count[0]), (100, 100), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4, cv2.LINE_AA)
    scale_percent = 50 # percent of original size
    width = int(mtimg.shape[1] * scale_percent / 100)
    height = int(mtimg.shape[0] * scale_percent / 100)
    dim = (width, height)
    reimage = cv2.resize(mtimg, dim, interpolation = cv2.INTER_AREA)
    
    
    #pil_image = ImageGrab.grab()
    #print (pic.size)
    #pil_image = pic.crop(box=(x,y,width-x,height-y))
    
    
    cv2.putText(message, "Count: "+str(count[0])+" Lose Count: "+str(lose_count), (50, 50), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    cv2.putText(message, "Who Win: "+whowin, (50, 100), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4,)
    cv2.putText(message, "Bet Result: "+result, (50, 150), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    cv2.putText(message, "Which Bet: "+bet_one, (50, 200), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    cv2.putText(message, "Last Bet: "+bet_last, (50, 250), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    # if check_end==1:
        # cv2.putText(message, "Status: close", (50, 300), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    # #cv2.putText(message, "Last Bet: "+bet_last, (50, 250), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    # if round_start ==1:
        # cv2.putText(message, "Status: reset", (50, 300), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    # if startbet == 1:
        # cv2.putText(message, "Status: start bet", (50, 300), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    cv2.putText(message, "Status: "+status, (50, 300), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 4)
    
    #message = cv2.add(message,mtimg[colors[1]:colors[3],colors[0]:colors[2]])
    #frame = getWindow_Img(hwnd)
    cv2.namedWindow("Message",1)
    cv2.imshow("Message", message)
    cv2.moveWindow('Message',1005,106)
    #cv2.imshow("screen box", reimage)
    hwnd1 = FindWindow_bySearch("Message")
    win32gui.SetForegroundWindow(hwnd1)
    #cv2.imshow("screen box", frame)
    #cv2.imshow("edges box", edges)
    k = cv2.waitKey(30)&0xFF #64bits! need a mask
    if k ==27:
        cv2.destroyAllWindows()
        break