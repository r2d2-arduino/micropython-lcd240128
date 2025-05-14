"""
v 0.1.4

LCD24064 is a FrameBuffer based MicroPython driver for the graphical
LiquidCrystal LCD24064 display
Сonnection: Data bus 8-bit

Project path: https://github.com/r2d2-arduino/micropython-lcd240128
MIT Licenze

Author: Derkach Arthur

Pinout
==============================
1    FG      Frame Ground
2    GND     Ground
3    Vcc     +5V
4    Vo      Operating voltage for LCD
5    WR      Data Write
6    RD      Data Read     
7    CE      Chip Enabled
8    CD      Code / Data
9    RST     Reset L: Active
10   DB0     }
..   DB..    } Data bus 8-bit
17   DB7     }
18   FS      Font Size: 0 = 8x8, 1 = 6x8
19   Vout    -10V Out voltage for LCD driving
20   A       +5V backlight Anode
21   K       GND backlight Kathode 

4 and 19 pins are used to adjust the display contrast through a resistor.
I use a 1 Mega Ohm variable resistor. Acceptable contrast ~270kOm

"""
from framebuf import FrameBuffer, MONO_HLSB, MONO_HMSB, MONO_VLSB
from time import sleep_us, sleep_ms, ticks_ms, ticks_diff
from machine import Pin

LCD_WIDTH   = const(240)
LCD_HEIGHT  = const(128)
LCD_BUFFSIZE = const( LCD_WIDTH * LCD_HEIGHT // 8 )
LCD_COLUMNS = const( LCD_WIDTH // 8 )
LCD_FIX0    = const(0)

class LCD240128( FrameBuffer ):

    def __init__( self, wr, rd, ce, cd, rst, fs, db0, db1, db2, db3, db4, db5, db6, db7, rotation = 0 ):
        ''' Main constructor '''
        
        #Initialization of pins
        self.wr  = Pin( wr, Pin.OUT, value = 1 )
        self.rd  = Pin( rd, Pin.OUT, value = 1 )
        self.ce  = Pin( ce, Pin.OUT, value = 1 )
        self.cd  = Pin( cd, Pin.OUT, value = 0 )
        self.fs  = Pin( fs, Pin.OUT, value = 0 ) # font size: 0 = 8x8, 1 = 6x8
        self.rst = Pin( rst, Pin.OUT, value = 0 )
        
        self.db0 = Pin( db0, Pin.OUT )
        self.db1 = Pin( db1, Pin.OUT )
        self.db2 = Pin( db2, Pin.OUT )
        self.db3 = Pin( db3, Pin.OUT )
        self.db4 = Pin( db4, Pin.OUT )
        self.db5 = Pin( db5, Pin.OUT )
        self.db6 = Pin( db6, Pin.OUT )
        self.db7 = Pin( db7, Pin.OUT )

        self.height = LCD_HEIGHT
        self.width  = LCD_WIDTH
        
        self._rotation = rotation
        self._text_wrap = False
        self._font = None
        
        if rotation == 1:
            pxl_direct = MONO_HMSB
        else:
            pxl_direct = MONO_HLSB
        
        # Initialize the FrameBuffer
        self.buffer = bytearray( LCD_BUFFSIZE ) 
        super().__init__( self.buffer, self.width, self.height, pxl_direct )

        self._init()
        
    def _init( self ):
        ''' Display init (Graphic mode) '''
        self.reset()
        
        self.set_command( 0x42, 0, 0 ) # set graphic home address: low high
        self.set_command( 0x43, LCD_COLUMNS, LCD_FIX0 ) # set graphic area: col 0 (hres/8)
        self.set_command( 0x90 | 8 | 0 | 0 | 0 ) # display mode: +8=Graph, +4=Text, +2=Cursor, +1=Blink
        self.set_command( 0x80 ) # mode set: 0 or 1 xor 3 and | 0x08 ext cg
        #self.set_command( 0xD0, 1, LCD_FIX0 ) # reverse on/off
        
    def init_text_mode( self ):
        ''' Text mode init '''
        self.reset()
        
        self.set_command( 0x40, 0, 0 ) # set text home address: low high addr
        self.set_command( 0x41, LCD_COLUMNS, LCD_FIX0 ) # set text area: col 0 (number of columns of text (8 pix wide)
        self.set_command( 0x90 | 0 | 4 | 2 | 1 ) # display mode: +8=Graph, +4=Text, +2=Cursor, +1=Blink
        self.set_command( 0x80 ) # mode set: 0 or 1 xor 3 and | 0x08 ext cg
        self.set_command( 0x21, 0, 0 ) # set cursor position: x, y
        self.set_command( 0xA0 | 7 ) # cursor height: 0..7
        #self.set_command( 0xD0, 1, LCD_FIX0 ) # reverse on/off
        self.set_command( 0x50, 2, LCD_FIX0 ) # blink speed: 0..7 (2 - default)
        self.set_command( 0x60, 1, LCD_FIX0 ) # cursor auto move on/off
        self.set_command( 0x70, 2, LCD_FIX0 ) # font select: 2..3
        
        self.clear_space()        
        
    def reset( self ):
        ''' Display reset '''
        self.rst(0)
        sleep_ms(10)
        self.rst(1)
        sleep_ms(1)
    
    def clear_space( self ):
        ''' Fill display by Space symbols (for Text mode) '''
        self.set_command( 0x24, 0, 0 )
        total_sectors = LCD_BUFFSIZE // 8
        if self.fs.value() == 1:
            total_sectors = LCD_BUFFSIZE // 6
            
        for _ in range( total_sectors ):
            self.set_command( 0xC0, 0 )

    @micropython.viper
    def lcd_write( self, data: int, is_cmd: int ):
        ''' Send data to lcd '''
        self.cd.value( is_cmd )   
        self.ce.value(0)

        self.db0.value( data & 1 )
        self.db1.value( data & (1 << 1) )
        self.db2.value( data & (1 << 2) )
        self.db3.value( data & (1 << 3) )
        self.db4.value( data & (1 << 4) )
        self.db5.value( data & (1 << 5) )
        self.db6.value( data & (1 << 6) )
        self.db7.value( data & (1 << 7) )        
        
        self.wr.value(0)
        self.wr.value(1)
        
        self.ce.value(1)

    def read_data( self, is_status ):
        ''' Read data from lcd '''
        self.cd.value( is_status )
            
        self.ce.value(0)
        self.rd.value(0)
        
        data  = self.db0.value()
        data |= self.db1.value() << 1
        data |= self.db2.value() << 2
        data |= self.db3.value() << 3
        data |= self.db4.value() << 4
        data |= self.db5.value() << 5
        data |= self.db6.value() << 6
        data |= self.db7.value() << 7
        
        self.rd.value(1)
        self.ce.value(1)
        
        return data  
    
    @micropython.viper
    def wait_for_ready( self ):
        ''' Waits until the display is busy '''
        ce = self.ce
        rd = self.rd
        db0 = self.db0
        db1 = self.db1
        
        db0.init( 0 ) # Pin.IN
        db1.init( 0 ) # Pin.IN
        
        self.cd.value(1)
        self.wr.value(1)
        
        ready = 0

        while ready < 3:
            ce.value( 0 )
            rd.value( 0 )
            
            ready = int( db0.value() ) | ( int( db1.value() ) << 1 )
            
            rd.value( 1 )
            ce.value( 1 )
        
        db0.init( 1 ) # Pin.OUT
        db1.init( 1 ) # Pin.OUT
    
    def set_command( self, cmd, data1 = None, data2 = None ):
        ''' Send command to lcd '''
        if data1 != None:
            self.wait_for_ready()
            self.lcd_write( data1, 0 )
            
        if data2 != None:
            self.wait_for_ready()
            self.lcd_write( data2, 0 )
            
        self.wait_for_ready()
        self.lcd_write( cmd, 1 )

    @micropython.viper
    def show( self ):
        ''' Send FrameBuffer to LCD '''
        rotation = int( self._rotation )
        buffer = ptr8( self.buffer )
        cd, ce, rd, wr = self.cd, self.ce, self.rd, self.wr        
        db0, db1, db2, db3, db4, db5, db6, db7 = self.db0, self.db1, self.db2, self.db3, self.db4, self.db5, self.db6, self.db7

        self.set_command( 0x24, 0, 0 )
        self.set_command( 0xB0 ) # Auto Write - Start

        ce.value( 0 )
        for i in range( LCD_BUFFSIZE ):
            # check ready to write
            db3.init( 0 )  # Pin.IN          
            cd.value( 1 )

            ready = 0
            while ready == 0:
                rd.value( 0 )                
                ready = int( db3.value() )                
                rd.value( 1 )
            
            # Send data
            db3.init( 1 ) # Pin.OUT
            cd.value( 0 )   
            
            if rotation == 1:
                data = buffer[LCD_BUFFSIZE - 1 - i]
            else:
                data = buffer[i]
            
            db0.value( data & 1 )
            db1.value( data & 2 )
            db2.value( data & 4 )
            db3.value( data & 8 )
            db4.value( data & 16 )
            db5.value( data & 32 )
            db6.value( data & 64 )
            db7.value( data & 128 )        
            
            wr.value( 0 )
            wr.value( 1 )
            
        ce.value(1)
        self.set_command( 0xB2 ) # Auto Write - End

    def set_inversion( self, on = 1 ):
        ''' Set display inversion '''
        self.set_command( 0xD0, int(on), LCD_FIX0 )
            
    @micropython.viper
    def _reverse_bits( self, byte: int ) -> int:
        ''' Reverse bits 0100 0111 => 1110 0010
        Args
        byte (int): Income byte
        Return (int): Reversed byte
        '''
        result = 0
        if byte & 1: result |= 1 << 7
        if (byte >> 1) & 1: result |= 1 << 6
        if (byte >> 2) & 1: result |= 1 << 5
        if (byte >> 3) & 1: result |= 1 << 4
        if (byte >> 4) & 1: result |= 1 << 3
        if (byte >> 5) & 1: result |= 1 << 2
        if (byte >> 6) & 1: result |= 1 << 1
        if (byte >> 7) & 1: result |= 1
        return result               
            
    def set_font(self, font):
        """ Set font for text
        Args
        font (module): Font module generated by font_to_py.py
        """
        self._font = font

    def set_text_wrap(self, on = True):
        """ Set text wrapping """
        self._text_wrap = bool( on )  

    def draw_text(self, text, x, y, color = 1):
        """ Draw text on display
        Args
        x (int) : Start X position
        y (int) : Start Y position
        """
        x_start = x
        screen_height = self.height
        screen_width  = self.width
        wrap = self._text_wrap
        
        font = self._font

        if font == None:
            print("Font not set")
            return False

        for char in text:   
            glyph = font.get_ch(char)
            glyph_height = glyph[1]
            glyph_width  = glyph[2]
            
            if char == " ": # double size for space
                x += glyph_width
                
            if wrap and (x + glyph_width > screen_width): # End of row
                x = x_start
                y += glyph_height                

            #if y + glyph_height > screen_height: # End of screen
            #    break
            
            #fb = FrameBuffer(bytearray(glyph[0]), glyph_width, glyph_height, MONO_HLSB)
            #self.blit(fb, x, y, 1 - color)
            self.draw_bitmap(glyph, x, y, color)
            x += glyph_width

    @micropython.viper
    def draw_bitmap(self, bitmap, x:int, y:int, color:int):
        """ Draw a bitmap on display
        Args
        bitmap (bytes): Bitmap data
        x      (int): Start X position
        y      (int): Start Y position
        color  (int): Color 0 or 1
        """
        data   = ptr8(bitmap[0]) #memoryview to bitmap
        height = int(bitmap[1])
        width  = int(bitmap[2])
        
        i = 0
        for h in range(height):
            bit_len = 0
            while bit_len < width:
                byte = data[i]
                xpos = bit_len + x
                ypos = h + y                
                #Drawing pixels when bit = 1
                if (byte >> 7) & 1:
                    self.pixel(xpos    , ypos, color)
                if (byte >> 6) & 1:
                    self.pixel(xpos + 1, ypos, color)
                if (byte >> 5) & 1:
                    self.pixel(xpos + 2, ypos, color)
                if (byte >> 4) & 1:
                    self.pixel(xpos + 3, ypos, color)
                if (byte >> 3) & 1:
                    self.pixel(xpos + 4, ypos, color)
                if (byte >> 2) & 1:
                    self.pixel(xpos + 5, ypos, color)
                if (byte >> 1) & 1:
                    self.pixel(xpos + 6, ypos, color)
                if byte & 1:
                    self.pixel(xpos + 7, ypos, color)

                bit_len += 8
                i += 1

    def load_bmp( self, filename, x = 0, y = 0, color = 1 ):
        """ Load monochromatic BMP image on buffer
        Args
        filename (string): filename of image, example: "rain.bmp"
        x (int) : Start X position
        y (int) : Start Y position
        color  (int): Color 0 or 1
        """
        f = open(filename, 'rb')

        if f.read(2) == b'BM':  #header
            dummy    = f.read(8)
            offset   = int.from_bytes(f.read(4), 'little')
            dummy    = f.read(4) #hdrsize
            width    = int.from_bytes(f.read(4), 'little')
            height   = int.from_bytes(f.read(4), 'little')
            planes   = int.from_bytes(f.read(2), 'little')
            depth    = int.from_bytes(f.read(2), 'little')
            compress = int.from_bytes(f.read(4), 'little')

            if planes == 1 and depth == 1 and compress == 0: #compress method == uncompressed
                f.seek(offset)
                
                self.send_bmp_to_buffer( f, x, y, width, height, color)
            else:
                print("Unsupported planes, depth, compress:", planes, depth, compress )
                
        f.close()    
        
    @micropython.viper
    def send_bmp_to_buffer( self, f, x:int, y:int, width:int, height:int, color:int):
        """ Send bmp-file to buffer
        Args
        f (object File) : Image file
        x (int) : Start X position
        y (int) : Start Y position        
        width (int): Width of image frame
        height (int): Height of image frame
        color  (int): Color 0 or 1
        """        
        block_size = ((width + 31) // 32) * 4  
        total_size = height * block_size
        bitmap_size = height * width // 8
        
        bitmap = bytearray(bitmap_size)
        bitmap_buffer = ptr8(bitmap)
        
        image_data = f.read(total_size)
        image_buffer = ptr8(image_data)
        
        row_bytes = width // 8
        for row in range(height): 
            byte_offset = row_bytes * row 
            block_offset = block_size * row 
            for byte in range(row_bytes): 
                if color == 1:
                    bitmap_buffer[bitmap_size - 1 - byte_offset - byte] = image_buffer[block_offset + row_bytes - 1 - byte] ^ 0xff
                else:
                    bitmap_buffer[bitmap_size - 1 - byte_offset - byte] = image_buffer[block_offset + row_bytes - 1 - byte]

        fb = FrameBuffer(bitmap, width, height, MONO_HLSB)
        self.blit(fb, 0, 0)  


