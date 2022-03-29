from ast import With
from audioop import add
from amaranth import *
from amaranth.sim import *
from enum import Enum, unique

class MEMORY(Elaboratable):
    def __init__(self):
        self.addr = Signal(32)
        self.dataIn = Signal(32)
        self.rdStb = Signal()
        self.wrStb = Signal()
        self.dataOut = Signal(32)
        self.mem = Array([Signal(32) for _ in range(1024)])



    def ports(self):
        return[self.addr, self.dataIn, self.rdStb, self.wrStb,self.dataOut]
    

    def elaborate(self, platform):
        m = Module()
        pos = ClockDomain("pos")
        neg = ClockDomain("neg", clk_edge="neg")
        neg.clk = pos.clk
        neg.rst = pos.rst
        m.domains += [pos,neg]
            
    
        with m.If(self.wrStb):
            m.d.neg += self.dataIn.eq(self.mem[self.addr])
        with m.If(self.rdStb):
            m.d.neg += self.dataOut.eq(self.mem[self.addr])
             

        return m

def proc():
    address = Signal(32)
    with open("program1") as file:
        for line in file:
            yield dut.mem[address].eq(int(line.rstrip(),16))
            yield address.eq(address+4)
            yield Settle()
    yield Delay(2e-8)
    yield dut.addr.eq(8)
    yield dut.rdStb.eq(1)
    yield Delay(2e-8)
    
dut = MEMORY()
sim = Simulator(dut)
sim.add_clock(2e-8,domain="neg")
sim.add_process(proc)
with sim.write_vcd("memory.vcd"):
    sim.run()
