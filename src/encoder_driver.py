'''!    @file       encoder_driver.py
        @brief      A driver for working with a quadrature incremental encoder.
        @details    Encapsulates functionality of encoder attached to the motor.
                    This class sets up pins to control the encoder and methods
                    to read and zero (reset) the angular position of the motor
                    in units of "ticks". Position reading is based on an 
                    algorithm that accounts for overflow and underflow.
 
        @author     Juan Luna

        @date       2022-01-26 Original file
        @date       2022-12-30 Modified for portfolio update
'''

import pyb
import utime

class EncoderDriver:
    '''! @brief      Driver class for the quadrature incremental encoder.
         @details    Objects of this class can be used to instantiate encoder
                     objects to control two encoders, each attach to one motor.
    '''
    def __init__ (self, enc1_pin, enc2_pin, timer):
        '''! @brief      Initializes objects of the EncoderDriver class.
             @param  enc1_pin    Encoder pin object for first timer channel.
             @param  enc2_pin    Encoder pin object for second timer channel.
             @param  timer       Timer object for program timing.  
        '''
        # Encoder pin objects for two channels
        self.enc1_pin = enc1_pin
        self.enc2_pin = enc2_pin

        # Encoder timer object
        self.timer = timer

        # Encoder timer channel setup

        ## @brief       Channel object "1" for motor timer.
        self.tim_ch1    = timer.channel(1, mode = pyb.Timer.ENC_AB,
                                            pin = self.enc1_pin)
        ## @brief       Channel object "2" for motor timer.
        self.tim_ch2     = timer.channel(2, mode = pyb.Timer.ENC_AB,
                                             pin = self.enc2_pin)

        ## @brief        Timer period, defined as largets 16-bit number
        self.period     = 2**16 - 1

        #  Variables to be used in EncoderDriver class methods

        ## @brief           Difference between consecutive tick counts
        self.delta_val      = 0
        ## @brief           Previous recorded encoder tick value
        self.last_tick      = 0
        ## @brief           Latest recorded encoder tick value
        self.new_tick       = 0
        ## @brief           Encoder position that accounts for overflow/underflow
        self.true_position  = 0
        
    def read(self):
        '''! @brief      Reads current position of encoder.
             @details    Algorithm accounting for overflow and underflow is
                         implemented to return current encoder position.
        '''
        
        # Save last encoder reading
        self.last_tick = self.new_tick
        # Take a new encoder reading
        self.new_tick = self.timer.counter()
        # Calculate difference between last two readings
        self.delta_val = self.new_tick - self.last_tick
        
        # Accounting for overflow or underflow
        if (self.delta_val > 0.5*self.period):
            self.delta_val -= self.period
        elif (self.delta_val < -0.5*self.period):
            self.delta_val += self.period

        self.true_position += self.delta_val
        return(self.true_position)

    def zero(self):
        '''! @brief      Resets (zeroes) the position of the encoder.
        '''
        self.true_position = 0

if __name__ == '__main__':
    # The following code tests the functionality of the motor driver.

    # Define pin objects for encoder channels for encoder 1
    ENC1A_pin = pyb.Pin.cpu.B6
    ENC1B_pin = pyb.Pin.cpu.B7

    # Define pin objects for encoder channels for encoder 2
    ENC2A_pin = pyb.Pin.cpu.C6
    ENC2B_pin = pyb.Pin.cpu.C7

    # Define timer objects of specified prescaler and frequency.
    tim_ENC_A = pyb.Timer(4, prescaler = 0, period = 2**16 - 1)
    tim_ENC_B = pyb.Timer(8, prescaler = 0, period = 2**16 - 1)

    # Create encoder driver objects for both encoders
    enc_A = EncoderDriver(ENC1A_pin, ENC1B_pin, tim_ENC_A)
    enc_B = EncoderDriver(ENC2A_pin, ENC2B_pin, tim_ENC_B)
    
    # Test code
    while True :
        print("Encoder position :" + enc_A.read())
        # print("Encoder position :" + enc_B.read())
        utime.sleep_ms(25)