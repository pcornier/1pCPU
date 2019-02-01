
from pCPU import mem, processor
from myhdl import *

@block
def sim():
    
    clk = Signal(bool(0))
    rst = Signal(bool(1))
    we = Signal(bool(0))
    adr = Signal(modbv(0)[16:])
    di = Signal(modbv(0)[8:])
    do = Signal(modbv(0)[8:])
    mi = mem(clk, adr, we, di, do)
    cpu = processor(clk, rst, di, do, adr, we)

    @always(delay(2))
    def stimulus():
        clk.next = not clk

    return stimulus, mi, cpu


tb = sim()
tb.config_sim(
    trace=True,
    tracebackup=False,
    filename='dump'
)
tb.run_sim(800)
