/* SPDX-License-Identifier: GPL-2.0-only */
#include "camss-x1e-parameter-schedule.h"
#include <cassert>
int main(){
 using libcamera::CamssX1EParameterSchedule;
 CamssX1EParameterSchedule s;s.reset();
 for(int i=0;i<4;i++)assert(!s.seedAccepted());
 assert(s.next()==9 && s.seedAccepted()==-EINVAL);
 assert(!s.add() && s.begin(true));auto epoch=s.epoch();auto id=s.next();
 /* A nested image callback adds debt without duplicating an in-flight ID. */
 assert(!s.add() && !s.begin(true) && s.next()==id && s.due()==1);
 assert(!s.complete(epoch,id,0) && s.next()==10);
 /* No free metadata buffer waits for DQBUF, preserving ordered credit. */
 assert(!s.begin(false) && s.due()==1 && s.begin(true));
 assert(!s.complete(epoch,10,0));
 assert(!s.add() && s.begin(true));s.stop();s.reset();
 assert(s.complete(epoch,11,0)==-ESTALE && s.next()==5);
 for(int i=0;i<16;i++)assert(!s.add());
 assert(s.add()==-ENOSPC && s.due()==16);
 s.stop();s.reset();for(int i=0;i<4;i++)assert(!s.seedAccepted());
 assert(!s.add() && s.begin(true));
 assert(s.complete(s.epoch(),10,0)==-EPROTO);
 assert(s.complete(s.epoch(),9,-EIO)==-EIO && !s.begin(true));
 s.stop();assert(s.add()==-ESHUTDOWN);
}
