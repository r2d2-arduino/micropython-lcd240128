from lcd240128_rp2 import LCD240128
lcd = LCD240128( wr = 14, rd = 13, ce = 12, cd = 11, rst = 10, fs = 1,
                db0 = 9, db1 = 8, db2 = 7, db3 = 6, db4 = 5, db5 = 4, db6 = 3, db7 = 2,
                rotation = 0 )

lcd.fill(0) # clear

lcd.load_bmp("tree240x128.bmp", 0, 0)

lcd.show()