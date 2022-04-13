from ast import Del, With
from operator import neg
from amaranth import *
from amaranth.sim import *
from enum import Enum, unique
from amaranth.lib.coding import Encoder

class REGISTERS(Elaboratable):
    def __init__(self,wr: Signal(), reset: Signal(), reg1_rd : Signal(5),reg2_rd: Signal(5),reg_wr: Signal(5), data_wr: Signal(32), data1_rd : Signal(32), data2_rd: Signal(32)):
        self.reset = reset
        self.wr = wr
        self.reg1_rd = reg1_rd
        self.reg2_rd = reg2_rd
        self.reg_wr = reg_wr
        self.data_wr = data_wr
        self.data1_rd = data1_rd
        self.data2_rd = data2_rd
        
        self.mem = Array([Signal(32) for _ in range(32)])

    
    
    def elaborate(self, platform):
        m = Module()
        
        m.d.comb += self.data1_rd.eq(Mux(self.reg1_rd==0, 0, self.mem[self.reg1_rd]))
        m.d.comb += self.data2_rd.eq(Mux(self.reg2_rd==0, 0, self.mem[self.reg2_rd]))
        with m.If(self.reset):
            for i in range(32):
                m.d.neg += self.mem[i].eq(0)
        with m.If(self.wr):
            m.d.neg += self.mem[self.reg_wr].eq(self.data_wr)
        
        


        return m


    
    

        
