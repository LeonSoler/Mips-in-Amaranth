from ast import With
from amaranth import *
from amaranth.sim import *
from enum import Enum, unique

class ALU(Elaboratable):
    def __init__(self,i_sel: Signal(3),i_a: Signal(32),i_b: Signal(32),o_result: Signal(32),o_zero: Signal()):
        self.i_sel = i_sel
        self.i_a = i_a 
        self.i_b = i_b
        self.o_result = o_result
        self.o_zero = o_zero
    
    

    def elaborate(self, platform):
        m = Module()
        
        with m.Switch(self.i_sel):
            with m.Case(0b000):
                m.d.comb +=self.o_result.eq(self.i_a & self.i_b)
            with m.Case(0b001):
                m.d.comb +=self.o_result.eq(self.i_a | self.i_b)
            with m.Case(0b010):
                m.d.comb +=self.o_result.eq(self.i_a + self.i_b)
            with m.Case(0b110):
                m.d.comb +=self.o_result.eq(self.i_a - self.i_b)
            with m.Case(0b111):
                with m.If(self.i_a < self.i_b):
                    m.d.comb +=self.o_result.eq(1)  
                with m.Else():  
                    m.d.comb +=self.o_result.eq(0)  
            with m.Case(0b100):
                m.d.comb +=self.o_result.eq(self.i_b.shift_left(16))
            with m.Default():
                m.d.comb +=self.o_result.eq(0)

        with m.If(self.o_result==0):
            m.d.comb +=self.o_zero.eq(1)
        with m.Else():
            m.d.comb +=self.o_zero.eq(0)

        return m



    

