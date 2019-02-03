from myhdl import *

@block
def mem(clk, adr, we, di, do):
    
    ram = [Signal(intbv(0)[8:]) for i in range(0xffff)]
    rom = (0x16, 0x0c, 0x00, 0x01, 0x01, 0x10, 0x01, 0x02, 0x10, 0x18, 0x09, 0x00, 0x17)
        
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
    ir, im, ra, rx, rw, sr = (Signal(modbv(0)[8:]) for i in range(6))
    sp = Signal(modbv(0xff)[8:])
    
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
            if ir == 0x17: # rts
                adr.next = sp + 1
                sp.next = sp + 1
            cyc.next = s.E
        elif cyc == s.E: # Todo: rewrite logic with decoded opc
            if ir == 0x01: # lda im
                ra.next = im
                pc.next = pc + 1
            elif ir == 0x02: # lda abs
                adr.next = (do << 8) | im
                pc.next = pc + 2
            elif ir == 0x03: # sta abs
                adr.next = (do << 8) | im
                we.next = 1
                di.next = ra
                pc.next = pc + 2
            elif ir == 0x04: # tax
                rx.next = ra
                rw.next = 1
            elif ir == 0x05: # txa
                ra.next = rx
            elif ir == 0x06: # add im
                ra.next = ra + im
                pc.next = pc + 1
            elif ir == 0x07: # sub im
                ra.next = ra - im
                pc.next = pc + 1
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
                else:
                    pc.next = pc + 1
            elif ir == 0x0e: # jz rel
                if sr[6] != 0:
                    pc.next = pc + im.signed()
                else:
                    pc.next = pc + 1
            elif ir == 0x0f: # dex
                rx.next = rx - 1
                rw.next = 1
            elif ir == 0x10: # pha
                adr.next = sp
                sp.next = sp - 1
                di.next = ra
                we.next = 1
            elif ir == 0x11: # pla
                sp.next = sp + 1
                adr.next = sp + 1
            elif ir == 0x12: # inx
                rx.next = rx + 1
                rw.next = 1
            elif ir == 0x13: # lda abs,x
                adr.next = (do << 8) | im + rx
                pc.next = pc + 2
            elif ir == 0x14: # sta abs,x
                adr.next = (do << 8) | im + rx
                di.next = ra
                pc.next = pc + 2
            elif ir == 0x15: # cmp im
                rw.next = 2
                sr.next = concat((ra-im)>=0x80, (ra-im)==0, sr[6:0])
            elif ir == 0x16: # jsr abs
                adr.next = sp
                sp.next = sp - 1
                di.next = (pc + 2) >> 8
                we.next = 1
            elif ir == 0x17: # rts
                adr.next = sp + 1
                sp.next = sp + 1
            elif ir == 0x18: # jmp
                pc.next = (do << 8) | im
            cyc.next = s.M1
        elif cyc == s.M1:
            if ir == 0x02 or ir == 0x11 or ir == 0x13:
                ra.next = do
            elif ir == 0x16:
                adr.next = sp
                sp.next = sp - 1
                di.next = (pc + 2) & 0xff
                we.next = 1
                pc.next = (do << 8) | im
            elif ir == 0x17:
                pc.next = do
            else:
                we.next = 0
                adr.next = pc
            cyc.next = s.M2
        elif cyc == s.M2:
            if ir == 0x11:
                ra.next = do
                sr.next = concat(do>=0x80, do==0, sr[6:0])
            elif rw == 0:
                sr.next = concat(ra>=0x80, ra==0, sr[6:0])
            elif rw == 1:
                sr.next = concat(rx>=0x80, rx==0, sr[6:0])
            if ir == 0x17:
                pc.next = (do << 8) | (pc & 0xff)
                adr.next = (do << 8) | (pc & 0xff)
            else:
                adr.next = pc
            we.next = 0
            rw.next = 0
            cyc.next = s.F1
                        
    return logic
