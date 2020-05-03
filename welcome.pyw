import tkinter as tk
import time
 
# 创建主窗口
window = tk.Tk()
window.title('进度条')
window.geometry('630x150+450+300')
 
# 设置下载进度条
tk.Label(window, text='正在生成个性化推荐:', ).place(x=5, y=60)
canvas = tk.Canvas(window, width=465, height=22, bg="white")
canvas.place(x=140, y=60)
 
# 显示下载进度
# 填充进度条
fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="green")
x = 500  # 未知变量，可更改
n = 465 / x  # 465是矩形填充满的次数
for i in range(x):
    n = n + 465 / x
    canvas.coords(fill_line, (0, 0, n, 60))
    window.update()
    time.sleep(0.060)  # 控制进度条流动的速度
 
# 清空进度条
'''fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="white")
x = 500  # 未知变量，可更改
n = 465 / x  # 465是矩形填充满的次数
 
for t in range(x):
    n = n + 465 / x
    # 以矩形的长度作为变量值更新
    canvas.coords(fill_line, (0, 0, n, 60))
    window.update()
    time.sleep(0)  # 时间为0，即飞速清空进度条'''
 

window.destroy()
