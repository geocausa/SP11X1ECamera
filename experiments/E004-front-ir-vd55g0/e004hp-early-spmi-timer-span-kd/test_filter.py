#!/usr/bin/env python3
"""E004hp: purely offline truth-table for the deployed KD span filter."""
START=0xee3e
END_INCLUSIVE=0xee41
MAX_BYTES=256

def match(selector,count):
    if type(selector) is not int or not 0<=selector<=0xffffffff:
        raise ValueError("invalid packed SPMI selector")
    if type(count) is not int or not 0<=count<=0xffffffff:
        raise ValueError("invalid full 32-bit count")
    addr=selector&0xffff
    return (0<count<=MAX_BYTES and addr<=END_INCLUSIVE and
            addr+count>START)

def main():
    positives=((0xee3e,1),(0xee41,1),(0xee3d,2),
               (0xee3b,4),(0xee40,4),(0xedff,256),
               (0xee00,63),(0x0001ee3e,1),(0x0011ee3e,1),
               (0x0002ee3f,2))
    negatives=((0xee3d,1),(0xee42,1),(0xee00,62),
               (0xed00,256),(0xee3e,0),(0xee3e,257),
               (0x00019246,1),(0x0001fffe,4),
               (0x0001ee42,8),(0xee41,0))
    for selector,count in positives:
        assert match(selector,count),(hex(selector),count)
    for selector,count in negatives:
        assert not match(selector,count),(hex(selector),count)
    for selector,count in ((-1,1),(2**32,1),(0,-1),(0,2**32),
                           (True,1),(1,True)):
        try:match(selector,count)
        except ValueError:pass
        else:raise AssertionError("E004HP_INVALID_SELECTOR_OR_COUNT_ACCEPTED")
    print("E004HP_OFFLINE_EARLY_SPMI_W2_W4_TIMER_SPAN_FILTER=PASS")
    print("E004HP_OVERLAP_POSITIVE",len(positives),
          "NONOVERLAP_NEGATIVE",len(negatives),"MALFORMED_NEGATIVE",6)
    print("E004HP_FIRST_EARLY_NON_TIMER_0X00019246_ONE_BYTE=CORRECTLY_EXCLUDED")

if __name__=="__main__":main()
