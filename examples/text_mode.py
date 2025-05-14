from lcd240128 import LCD240128

lcd = LCD240128( wr = 14, rd = 13, ce = 12, cd = 11, rst = 10, fs = 1,
                db0 = 9, db1 = 8, db2 = 7, db3 = 6, db4 = 5, db5 = 4, db6 = 3, db7 = 2,
                rotation = 0 )

lcd.init_text_mode() # main settings for text mode

lcd.set_command( 0x24, 0, 0 ) # set address pointer to: 0,0

for s in range(128):
    lcd.set_command( 0xC0, s ) # draw one symbol 
