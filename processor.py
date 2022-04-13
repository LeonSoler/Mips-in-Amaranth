from ast import With
from re import S
from amaranth import *
from amaranth.sim import *
from enum import Enum, unique
from registers import *
from alu import *
from memory import *
class PROCESSOR(Elaboratable):
    def __init__(self):
        #para debugear
        self.aux = Signal(5)

        self.Reset = Signal()
        #Instruction memory
        self.I_Addr = Signal(32)
        self.I_RdStb = Signal()
        self.I_WrStb = Signal()
        self.I_DataOut = Signal(32)
        self.I_DataIn = Signal(32)
        self.I_mem = Array([Signal(32) for _ in range(132)])
    
        #Data Memory
        self.D_Addr = Signal(32)
        self.D_RdStb = Signal()
        self.D_Wrstb = Signal()
        self.D_DataOut = Signal(32)
        self.D_DataIn = Signal(32)
        self.D_mem = Array([Signal(32) for _ in range(132)])
        
    

    def elaborate(self, platform):
        m = Module()
        pos = ClockDomain("pos")
        neg = ClockDomain("neg", clk_edge="neg")
        neg.clk = pos.clk
        neg.rst = pos.rst
        m.domains += [pos,neg]

        
        #Declaraciones etapa IF
        PC = Signal(32)
        PC_next = Signal(32)
        PC_4 = Signal(32)
        PC_Branch = Signal(32)
        PCSrc = Signal()

        #Declaraciones ID
        ID_instruction = Signal(32)
        ID_PC_4 = Signal(32)
        ID_data1_rd = Signal(32)
        ID_data2_rd = Signal(32)
        ID_immediate = Signal(32)
        ID_RegDst  = Signal()
        ID_ALUSrc = Signal()
        ID_Memto_Reg = Signal()
        ID_Reg_Write = Signal()
        ID_Mem_Read = Signal()
        ID_Mem_Write = Signal()
        ID_Branch = Signal()
        ID_ALUOP = Signal(3)
        ID_sign_ext = Signal(32)
        
        #Señales etapa EX
        EX_RegA = Signal(32) 
        EX_RegB = Signal(32)
        EX_RegD_LW = Signal(5)
        EX_RegD_TR = Signal(5)
        EX_PC_4 = Signal(32)
        EX_immediate = Signal(32)
        EX_Ctrl_RegDst = Signal()
        EX_Ctrl_ALUSrc = Signal() 
        EX_Ctrl_Memto_Reg = Signal()
        EX_Ctrl_Reg_Write = Signal()
        EX_Ctrl_Mem_Read = Signal() 
        EX_Ctrl_Mem_Write = Signal()
        EX_Ctrl_Branch = Signal()
        EX_Ctrl_ALUOP = Signal(3)
        EX_MuxReg = Signal(5)

        ALU_in = Signal(32)
        ALU_Control = Signal(3)
        ALU_result  = Signal(32)
        ALU_zero = Signal()
        AddResultI = Signal(32)

        #Señales etapa MEM
        MEM_PC_Branch = Signal(32)
        MEM_RegDst = Signal(5)
        MEM_Ctrl_Memto_Reg = Signal()
        MEM_Ctrl_Reg_Write = Signal()
        MEM_Ctrl_Mem_Read = Signal()
        MEM_Ctrl_Mem_Write = Signal()
        MEM_Ctrl_Branch = Signal()
        MEM_ALU_Result = Signal(32)
        MEM_ALU_Zero = Signal()
        MEM_RegB = Signal(32)

        #Señales etapa WB
        WB_data_wr = Signal(32)
        WB_Ctrl_Memto_Reg = Signal()
        WB_RegDst = Signal(5)
        WB_Reg_Write = Signal()
        WB_ALU_Result = Signal(32)
        WB_Read_Data = Signal(32)

        D_DataALUIn = Signal(32)

        
        #Comienzo etapa IF
        with m.If(self.Reset):
            m.d.pos += PC.eq(0)
        with m.Else():
            m.d.pos += PC.eq(PC_next)
        
        
        m.d.comb += PC_4.eq(PC + 4)
        
        
        with m.If(PCSrc == 0):
            m.d.comb += PC_next.eq(PC_4)
        with m.Else():
            m.d.comb += PC_next.eq(MEM_PC_Branch)

        m.d.comb+= self.I_Addr.eq(PC)
        m.d.comb+= self.I_RdStb.eq(1)
        m.d.comb+= self.I_WrStb.eq(0)
        m.d.comb+= self.I_DataOut.eq(0)
        inst_memory = MEMORY(self.I_Addr,self.I_DataOut,self.I_RdStb,self.I_WrStb,self.I_DataIn,self.I_mem)
        
        
        # Fin de etapa IF 


        # Registro de segmentacion IF/ID
        with m.If(self.Reset):
            m.d.pos += ID_instruction.eq(0)
            m.d.pos += ID_PC_4.eq(0)
        with m.Else():
            m.d.pos += ID_instruction.eq(self.I_DataIn)
            m.d.pos += ID_PC_4.eq(PC_4)



        #Inicio etapa ID
        registers_inst = REGISTERS(WB_Reg_Write,self.Reset,ID_instruction[21:26],ID_instruction[16:21],WB_RegDst,WB_data_wr,ID_data1_rd,ID_data2_rd)
        
        
        # Sign Extension
        with m.If(ID_instruction[15]== 0):
            m.d.comb += ID_sign_ext.eq(Cat(ID_instruction[0:16],0x0000))
        with m.Else():
            m.d.comb += ID_sign_ext.eq(Cat(ID_instruction[0:16],0xFFFF))

        # Unidad de control
        with m.Switch(ID_instruction[26:32]):
            # R-type
            with m.Case(0b000000):
                m.d.comb += ID_RegDst.eq(1)
                m.d.comb += ID_ALUSrc.eq(0)
                m.d.comb += ID_Memto_Reg.eq(0)
                m.d.comb += ID_Reg_Write.eq(1)
                m.d.comb += ID_Mem_Read.eq(0)
                m.d.comb += ID_Mem_Write.eq(0)
                m.d.comb += ID_Branch.eq(0)
                m.d.comb += ID_ALUOP.eq(0b010)
            # lw
            with m.Case(0b100011):
                m.d.comb += ID_RegDst.eq(0)
                m.d.comb += ID_ALUSrc.eq(1)
                m.d.comb += ID_Memto_Reg.eq(1)
                m.d.comb += ID_Reg_Write.eq(1)
                m.d.comb += ID_Mem_Read.eq(1)
                m.d.comb += ID_Mem_Write.eq(0)
                m.d.comb += ID_Branch.eq(0)
                m.d.comb += ID_ALUOP.eq(0b000)
            # sw
            with m.Case(0b101011):
                m.d.comb += ID_RegDst.eq(0)
                m.d.comb += ID_ALUSrc.eq(1)
                m.d.comb += ID_Memto_Reg.eq(0)
                m.d.comb += ID_Reg_Write.eq(0)
                m.d.comb += ID_Mem_Read.eq(0)
                m.d.comb += ID_Mem_Write.eq(1)
                m.d.comb += ID_Branch.eq(0)
                m.d.comb += ID_ALUOP.eq(0b000)
            # beq
            with m.Case(0b000100):
                m.d.comb += ID_RegDst.eq(0)
                m.d.comb += ID_ALUSrc.eq(0)
                m.d.comb += ID_Memto_Reg.eq(0)
                m.d.comb += ID_Reg_Write.eq(0)
                m.d.comb += ID_Mem_Read.eq(0)
                m.d.comb += ID_Mem_Write.eq(0)
                m.d.comb += ID_Branch.eq(1)
                m.d.comb += ID_ALUOP.eq(0b001)
            # addi
            with m.Case(0b001000):
                m.d.comb += ID_RegDst.eq(0)
                m.d.comb += ID_ALUSrc.eq(1)
                m.d.comb += ID_Memto_Reg.eq(0)
                m.d.comb += ID_Reg_Write.eq(1)
                m.d.comb += ID_Mem_Read.eq(0)
                m.d.comb += ID_Mem_Write.eq(0)
                m.d.comb += ID_Branch.eq(0)
                m.d.comb += ID_ALUOP.eq(0b100)
            # andi
            with m.Case(0b001100):
                m.d.comb += ID_RegDst.eq(0)
                m.d.comb += ID_ALUSrc.eq(1)
                m.d.comb += ID_Memto_Reg.eq(0)
                m.d.comb += ID_Reg_Write.eq(1)
                m.d.comb += ID_Mem_Read.eq(0)
                m.d.comb += ID_Mem_Write.eq(0)
                m.d.comb += ID_Branch.eq(0)
                m.d.comb += ID_ALUOP.eq(0b101)
            # ori
            with m.Case(0b001101):
                m.d.comb += ID_RegDst.eq(0)
                m.d.comb += ID_ALUSrc.eq(1)
                m.d.comb += ID_Memto_Reg.eq(0)
                m.d.comb += ID_Reg_Write.eq(1)
                m.d.comb += ID_Mem_Read.eq(0)
                m.d.comb += ID_Mem_Write.eq(0)
                m.d.comb += ID_Branch.eq(0)
                m.d.comb += ID_ALUOP.eq(0b110)
            # lui
            with m.Case(0b001111):
                m.d.comb += ID_RegDst.eq(0)
                m.d.comb += ID_ALUSrc.eq(1)
                m.d.comb += ID_Memto_Reg.eq(0)
                m.d.comb += ID_Reg_Write.eq(1)
                m.d.comb += ID_Mem_Read.eq(0)
                m.d.comb += ID_Mem_Write.eq(0)
                m.d.comb += ID_Branch.eq(0)
                m.d.comb += ID_ALUOP.eq(0b011)
            with m.Default():
                m.d.comb += ID_RegDst.eq(0)
                m.d.comb += ID_ALUSrc.eq(0)
                m.d.comb += ID_Memto_Reg.eq(0)
                m.d.comb += ID_Reg_Write.eq(0)
                m.d.comb += ID_Mem_Read.eq(0)
                m.d.comb += ID_Mem_Write.eq(0)
                m.d.comb += ID_Branch.eq(0)
                m.d.comb += ID_ALUOP.eq(0b111) # numero que no se usa   
        
        # Fin etapa ID
        
        # Registro de segmentacion ID/EX
        with m.If(self.Reset):
            m.d.pos += EX_RegA.eq(0)
            m.d.pos += EX_RegB.eq(0) 
            m.d.pos += EX_RegD_LW.eq(0)
            m.d.pos += EX_RegD_TR.eq(0)
            m.d.pos += EX_PC_4.eq(0)
            m.d.pos += EX_immediate.eq(0)  
            m.d.pos += EX_Ctrl_RegDst.eq(0)
            m.d.pos += EX_Ctrl_ALUSrc.eq(0)
            m.d.pos += EX_Ctrl_Memto_Reg.eq(0)
            m.d.pos += EX_Ctrl_Reg_Write.eq(0)
            m.d.pos += EX_Ctrl_Mem_Read.eq(0)
            m.d.pos += EX_Ctrl_Mem_Write.eq(0)
            m.d.pos += EX_Ctrl_Branch.eq(0)
            m.d.pos += EX_Ctrl_ALUOP.eq(0)
        with m.Else():
            m.d.pos += EX_RegA.eq(ID_data1_rd)
            m.d.pos += EX_RegB.eq(ID_data2_rd)
            m.d.pos += EX_RegD_LW.eq(ID_instruction[16:21])
            m.d.pos += EX_RegD_TR.eq(ID_instruction[11:16])
            m.d.pos += EX_PC_4.eq(ID_PC_4)
            m.d.pos += EX_immediate.eq(ID_sign_ext)
            m.d.pos += EX_Ctrl_RegDst.eq(ID_RegDst)
            m.d.pos += EX_Ctrl_ALUSrc.eq(ID_ALUSrc)
            m.d.pos += EX_Ctrl_Memto_Reg.eq(ID_Memto_Reg)
            m.d.pos += EX_Ctrl_Reg_Write.eq(ID_Reg_Write)
            m.d.pos += EX_Ctrl_Mem_Read.eq(ID_Mem_Read)
            m.d.pos += EX_Ctrl_Mem_Write.eq(ID_Mem_Write)
            m.d.pos += EX_Ctrl_Branch.eq(ID_Branch)
            m.d.pos += EX_Ctrl_ALUOP.eq(ID_ALUOP)
        
        # Comienzo etapa EX


        with m.If(EX_Ctrl_ALUSrc==1):
            m.d.comb += ALU_in.eq(EX_immediate)
        with m.Else():
            m.d.comb += ALU_in.eq(EX_RegB)

        #and/andi
        with m.If(((EX_Ctrl_ALUOP==0b010) & (EX_immediate[0:6]==0b100100)) | (EX_Ctrl_ALUOP==0b101)):
            m.d.comb+=ALU_Control.eq(0b000)
        #or/ori
        with m.If(((EX_Ctrl_ALUOP== 0b010) & (EX_immediate[0:6]== 0b100101) | (EX_Ctrl_ALUOP==0b110))):
            m.d.comb+=ALU_Control.eq(0b001)
        #add/addi/sw/lw
        with m.If((EX_Ctrl_ALUOP==0b000) | ((EX_Ctrl_ALUOP==0b010) & (EX_immediate[0:6]== 0b100000)) | (EX_Ctrl_ALUOP==0b100)):
            m.d.comb+= ALU_Control.eq(0b010)
        #sub/beq
        with m.If((EX_Ctrl_ALUOP==0b001) | ((EX_Ctrl_ALUOP==0b010) & (EX_immediate[0:6]== 0b100010))):
            m.d.comb+= ALU_Control.eq(0b110)
        #slt
        with m.If((EX_Ctrl_ALUOP==0b010) & (EX_immediate[0:6]==0b101010)):
            m.d.comb+= ALU_Control.eq(0b111)
        #lui
        with m.If(EX_Ctrl_ALUOP==0b011):
            m.d.comb+= ALU_Control.eq(0b100)
                
                
                
        
        
        alu_inst = ALU(ALU_Control,EX_RegA,ALU_in,ALU_result,ALU_zero)
        aux = Signal(32)
        m.d.comb += aux.eq(EX_immediate[0:30].shift_left(2))
        m.d.comb += AddResultI.eq(EX_PC_4 + aux)

        with m.If(EX_Ctrl_RegDst == 0):
            m.d.comb += EX_MuxReg.eq(EX_RegD_LW)
        with m.Else():
            m.d.comb += EX_MuxReg.eq(EX_RegD_TR)

        # Fin etapa EX


        # Registro de segmentacion EX-MEM
        
        with m.If(self.Reset):
            m.d.pos += MEM_PC_Branch.eq(0)
            m.d.pos += MEM_RegDst.eq(0)
            m.d.pos += MEM_Ctrl_Memto_Reg.eq(0) 
            m.d.pos += MEM_Ctrl_Reg_Write.eq(0)
            m.d.pos += MEM_Ctrl_Mem_Read.eq(0)
            m.d.pos += MEM_Ctrl_Mem_Write.eq(0)
            m.d.pos += MEM_Ctrl_Branch.eq(0)
            m.d.pos += MEM_RegB.eq(0)
            m.d.pos += MEM_ALU_Result.eq(0)
        with m.Else():
            m.d.pos += MEM_RegDst.eq(EX_MuxReg)
            m.d.pos += MEM_PC_Branch.eq(AddResultI)
            m.d.pos += MEM_Ctrl_Memto_Reg.eq(EX_Ctrl_Memto_Reg) 
            m.d.pos += MEM_Ctrl_Reg_Write.eq(EX_Ctrl_Reg_Write)
            m.d.pos += MEM_Ctrl_Mem_Read.eq(EX_Ctrl_Mem_Read)
            m.d.pos += MEM_Ctrl_Mem_Write.eq(EX_Ctrl_Mem_Write)
            m.d.pos += MEM_Ctrl_Branch.eq(EX_Ctrl_Branch)
            m.d.pos += MEM_RegB.eq(EX_RegB)
            m.d.pos += MEM_ALU_Zero.eq(ALU_zero)
            m.d.pos += MEM_ALU_Result.eq(ALU_result)
        
        # Inicio etapa MEM

        m.d.comb += self.D_Addr.eq(MEM_ALU_Result)
        m.d.comb += self.D_RdStb.eq(MEM_Ctrl_Mem_Read)
        m.d.comb += self.D_Wrstb.eq(MEM_Ctrl_Mem_Write)
        m.d.comb += self.D_DataOut.eq(MEM_RegB)
        m.d.comb += D_DataALUIn.eq(self.D_DataIn)
        inst_data_memory = MEMORY(self.D_Addr,self.D_DataOut,self.D_RdStb,self.D_Wrstb,self.D_DataIn,self.D_mem)

        with m.If((MEM_Ctrl_Branch==1) & (MEM_ALU_Zero==1)):
            m.d.comb += PCSrc.eq(1)
        with m.Else():
            m.d.comb += PCSrc.eq(0)

        # Fin etapa MEM
        
        # Registro de segmentacion MEM/WB
        with m.If(self.Reset):
            m.d.pos += WB_Ctrl_Memto_Reg.eq(0)
            m.d.pos += WB_RegDst.eq(0)
            m.d.pos += WB_Reg_Write.eq(0)
            m.d.pos += WB_ALU_Result.eq(0)
            m.d.pos += WB_Read_Data.eq(0)
        with m.Else():
            m.d.pos += WB_Ctrl_Memto_Reg.eq(MEM_Ctrl_Memto_Reg)
            m.d.pos += WB_RegDst.eq(MEM_RegDst)
            m.d.pos += WB_Reg_Write.eq(MEM_Ctrl_Reg_Write)
            m.d.pos += WB_ALU_Result.eq(MEM_ALU_Result)
            m.d.pos += WB_Read_Data.eq(D_DataALUIn)
        
        # Inicio etapa WB

        with m.If(WB_Ctrl_Memto_Reg):
            m.d.comb += WB_data_wr.eq(WB_Read_Data)
        with m.Else():
            m.d.comb += WB_data_wr.eq(WB_ALU_Result)

        # Fin etapa WB
        
        m.submodules += [inst_data_memory,inst_memory,alu_inst,registers_inst]

        return m

def proc():
    
    address1 = Signal(32)
    yield dut.Reset.eq(1)
    with open("program1") as file:
        for line in file:
            yield dut.I_mem[address1].eq(int(line.rstrip(),16))
            yield address1.eq(address1+4)
            yield Settle()
    address2 = Signal(32)
    with open("data") as file:
        for line in file:
            yield dut.D_mem[address2].eq(int(line.rstrip(),16))
            yield address2.eq(address2+4)
            yield Settle()
    yield Delay(5e-8)
    
    yield Delay(1.2e-7)
    yield dut.Reset.eq(0)
    yield Delay(1.8e-6)
    

    
dut = PROCESSOR()
sim = Simulator(dut)
sim.add_clock(5e-8,domain="pos")
sim.add_clock(5e-8,domain="neg")
sim.add_process(proc)
with sim.write_vcd("processor.vcd"):
    sim.run()

        

        