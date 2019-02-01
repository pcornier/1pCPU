
from myhdl import *

@block
def mem(clk, adr, we, di, do):
    
    ram = [Signal(intbv(0)[8:]) for i in range(0xffff)]
    rom = (0x01, 0x0a, 0x04, 0x0f,  0x0d, 0xfd, 0x0)
        
    @always(clk.posedge)
    def logic():
        if we:
            ram[adr.val].next = di
        else:
            if adr < len(rom):
                do.next = rom[adr.val]
            else:
                do.next = ram[adr.val]
        
    return logic

@block
def processor(clk, rst, di, do, adr, we):

    s = enum('F1','F2','D','E','M1','M2')
    pc = Signal(modbv(0)[16:])
    cyc = Signal(s.F1)
    ir, im, ra, rb, sr = (Signal(modbv(0)[8:]) for i in range(5))
    
    @always(clk.posedge)
    def logic():
        if rst:
            rst.next = 0
            pc.next = 0
            adr.next = 0
        elif cyc == s.F1:
            adr.next = pc + 1
            pc.next = pc + 1
            cyc.next = s.F2
        elif cyc == s.F2:
            adr.next = pc + 1
            ir.next = do
            cyc.next = s.D
        elif cyc == s.D: # Todo: extract addressing mode from ir
            im.next = do
            cyc.next = s.E
        elif cyc == s.E: # Todo: rewrite logic with decoded opc
            if ir == 0x01: # lda im
                ra.next = im
                pc.next = pc + 1
            elif ir == 0x02: # lda abs
                adr.next = (do << 8) | im
            elif ir == 0x03: # sta abs
                adr.next = (do << 8) | im
                we.next = 1
                di.next = ra
                pc.next = pc + 2
            elif ir == 0x04: # tab
                rb.next = ra
            elif ir == 0x05: # tba
                ra.next = rb
                pc.next = pc + 2
            elif ir == 0x06: # adb
                ra.next = ra + rb
            elif ir == 0x07: # sbb
                ra.next = ra - rb
            elif ir == 0x08: # and im
                ra.next = ra & im
                pc.next = pc + 1
            elif ir == 0x09: # or im
                ra.next = ra | im
                pc.next = pc + 1
            elif ir == 0x0a: # xor im
                ra.next = ra ^ im
                pc.next = pc + 1
            elif ir == 0x0b: # lsa
                ra.next = ra << 1
            elif ir == 0x0c: # rsa
                ra.next = ra >> 1
            elif ir == 0x0d: # jnz rel
                if sr[6] == 0:
                    pc.next = pc + im.signed()
            elif ir == 0x0e: # jz rel
                if sr[6] != 0:
                    pc.next = pc + im.signed()
            elif ir == 0x0f: # dec
                ra.next = ra - 1
            cyc.next = s.M1
        elif cyc == s.M1:
            we.next = 0
            adr.next = pc
            sr.next = concat(sr[7], ra == 0, sr[6:0])
            cyc.next = s.M2
        elif cyc == s.M2:
            adr.next = pc
            if ir == 0x02: ra.next = do
            cyc.next = s.F1
                        
    return logic