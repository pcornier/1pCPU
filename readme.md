
This is my entry for a one page 8bit CPU in MyHDL.

It has 64k of RAM with a small ROM that overlaps RAM from zero. It has 16 instructions but no opc decoding implemented yet, it's all hard-coded.

![gtkwave](screenshot.png)

The small ROM program::

```asm
    lda #$0a
    loop:
        tab (b = a)
        dec (a = a-1)
        jnz loop
    nop
```
