from lcd240128_rp2 import LCD240128
from time import sleep_ms

lcd = LCD240128( wr = 14, rd = 13, ce = 12, cd = 11, rst = 10, fs = 1,
                db0 = 9, db1 = 8, db2 = 7, db3 = 6, db4 = 5, db5 = 4, db6 = 3, db7 = 2,
                rotation = 0 )

lcd.fill(0)

radius = 4

x_border = lcd.width - 1
y_border = lcd.height - 1

prev_x = radius
prev_y = radius

x = radius
y = radius

x_speed = 2
y_speed = 2

while True:    
    lcd.ellipse(prev_x, prev_y, radius, radius, 0, True) # clear previos
    lcd.ellipse(x, y, radius, radius, 1, True)
    prev_x = x
    prev_y = y
    
    x += x_speed
    y += y_speed
    
    if x + radius > x_border or x - radius < 0:
        x_speed = -x_speed
        
    if y + radius > y_border or y - radius < 0:
        y_speed = -y_speed    
    
    lcd.show() 


    

