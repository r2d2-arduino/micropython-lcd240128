from lcd240128 import LCD240128
from time import sleep
from bitmaps import sun, suncloud, rain, rainlight, snowman

lcd = LCD240128( wr = 14, rd = 13, ce = 12, cd = 11, rst = 10, fs = 1,
                db0 = 9, db1 = 8, db2 = 7, db3 = 6, db4 = 5, db5 = 4, db6 = 3, db7 = 2,
                rotation = 0 )
  
bitmaps = [sun, suncloud, rain, rainlight, snowman]
size = 16

for i in range( len( bitmaps ) ):
    lcd.fill(0) # clear
    bitmap = bitmaps[ i ]
    for x in range( 15 ):
        for y in range( 8 ):
            lcd.draw_bitmap( bitmap, x * size, y * size, 1 )
    lcd.show( )
    sleep( 1 )
    