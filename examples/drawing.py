from lcd240128 import LCD240128
from time import sleep

lcd = LCD240128( wr = 14, rd = 13, ce = 12, cd = 11, rst = 10, fs = 1,
                db0 = 9, db1 = 8, db2 = 7, db3 = 6, db4 = 5, db5 = 4, db6 = 3, db7 = 2,
                rotation = 0 )

SCREEN_WIDTH  = lcd.width
SCREEN_HEIGHT = lcd.height

lcd.fill(0) # clear

lcd.ellipse(35, 35, 30, 30, 1, True)
lcd.ellipse(80, 95, 30, 30, 1)

lcd.pixel(35, 35, 0)
lcd.pixel(80, 95, 1)

lcd.rect(100, 5, 50, 50, 1, True)
lcd.rect(150, 70, 50, 50, 1)

for y in range(SCREEN_HEIGHT // 4):
    lcd.line(0, 0, SCREEN_WIDTH, y * 4 , 1)

lcd.show()
