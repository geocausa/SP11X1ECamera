# SPDX-License-Identifier: GPL-2.0-only
"""Reverse exactly the declared read-only stop diagnostic for baseline proof."""
DIAGNOSTIC='#ifdef __KERNEL__\n dev_info(camss->dev,\n  "NATIVE_REAR_STOP_ADMISSION both=%u ledgers=%u faulted=%u programmed0=%u programmed1=%u active0=%u active1=%u fault0=%u fault1=%u pending0=%u pending1=%u owner0=%llu owner1=%llu expected_owner=%llu generation0=%llu generation1=%llu\\n",\n  e008h_rear_both_complete(pair, owner_epoch),pair->ledgers_bound,pair->faulted,\n  pair->programmed[0],pair->programmed[1],pair->frame[0].active,pair->frame[1].active,\n  pair->frame[0].faulted,pair->frame[1].faulted,pair->frame[0].pending,pair->frame[1].pending,\n  pair->frame[0].owner_epoch,pair->frame[1].owner_epoch,owner_epoch,\n  pair->frame[0].request_generation,pair->frame[1].request_generation);\n#endif\n'
def undo_stop_diagnostic(text):
 assert text.count(DIAGNOSTIC)==1,"stop diagnostic delta drift"
 return text.replace(DIAGNOSTIC,"",1)
