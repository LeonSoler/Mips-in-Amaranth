from ast import With
from audioop import add
from amaranth import *
from amaranth.sim import *
from enum import Enum, unique

class MEMORY(Elaboratable):
    def __init__(self, Addr: Signal(32), DataIn: Signal(32), RdStb: Signal(), WrStb: Signal(), DataOut: Signal(32),mem : Array([Signal(32) for _ in range(132)])):
        self.Addr = Addr
        self.DataIn = DataIn
        self.RdStb = RdStb
        self.WrStb = WrStb
        self.DataOut = DataOut
        #memoria de 1024 palabras de 32 bits
        self.mem = mem
    

    def elaborate(self, platform):
        m = Module()
            
        with m.If(self.WrStb):
            m.d.neg += self.mem[self.Addr].eq(self.DataIn)
        with m.Elif(self.RdStb):
            m.d.neg += self.DataOut.eq(self.mem[self.Addr])
             
        return m
