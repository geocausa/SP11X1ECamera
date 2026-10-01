#!/usr/bin/env python3
"""Create an unarmed, single-use bounded Windows cold-AEC metadata observer."""
import argparse,pathlib,re,json
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011BU-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("existing identity must be audited; never reuse")
a.output.mkdir(parents=True)
bs=chr(92);win=bs.join(["C:","Users","Geoca","Documents","SP11CameraPrivate",a.identity]);cap=win+bs+"capture"
def save(n,lines):(a.output/(n+".cmd")).write_text(chr(10).join(lines)+chr(10))
def dump(n,addr,size):return f".writemem {cap}{bs}{n}.bin {addr} {addr}+0x{size-1:x}"
def script(n):return chr(34)+"$$><"+(win+bs+n+".cmd").replace(bs,bs+bs)+chr(34)
save("first",[
 '.printf "E011BU_FIRST tid=%x processor=%p out=%p returned=%x\\n",@$tid,@x19,@sp+0xc50,@w0',
 'r $t0=@sp+0xc50; r $t17=@$tid',
 dump("FIRST_OUT","@sp+0xc50",2072),"g"])
save("second",[
 '.printf "E011BU_SECOND tid=%x processor=%p out=%p returned=%x\\n",@$tid,@x19,@sp+0x1470,@w0',
 dump("SECOND_OUT","@sp+0x1470",2072),"g"])
save("publish",[
 '.printf "E011BU_PUBLISH tid=%x node=%p req=%I64u tag=%x bytes=%I64u src=%p firstPtrMatch=%u firstTidMatch=%u\\n",@$tid,@x0,@x1,@x2,@x3,@x4,(@x4==@$t0),(@$tid==@$t17)',
 'r $t1=@x0; r $t2=@$tid; r $t3=@x1; r $t13=1',
 dump("PUBLISH_OUT","@x4",2072),dump("PUBLISH_NODE","@x0",1280),
 '.if (poi(@x0+0x4b0)!=0) { '+dump("PUBLISH_POOL","poi(@x0+0x4b0)",720)+' }',
 'bp3 /1 QcDeviceMFT8380+0x83abd8 '+script("publish-after"),"g"])
save("publish-after",[
 '.printf "E011BU_PUBLISH_AFTER tid=%x sameTid=%u result=%x\\n",@$tid,(@$tid==@$t2),@w0',"g"])
save("write",[
 '.printf "E011BU_WRITE tid=%x store=%p tag=%x src=%p bytes=%I64u callerRVA=%I64x sameTid=%u\\n",@$tid,@x0,@x1,@x2,@x3,@lr-QcDeviceMFT8380,(@$tid==@$t2)',
 'r $t4=@x0; r $t14=1',
 dump("WRITE_OUT","@x2",2072),dump("WRITE_STORE","@x0",128),
 'bp5 /1 QcDeviceMFT8380+0x5d6ef8 '+script("write-after"),"g"])
save("write-after",[
 '.printf "E011BU_WRITE_AFTER tid=%x sameTid=%u result=%x\\n",@$tid,(@$tid==@$t2),@w0',
 dump("WRITE_STORE_AFTER","@$t4",128),"g"])
save("reader",[
 '.printf "E011BU_READER tid=%x node=%p pool=%p index=%u tag=%x offset=%I64u callerRVA=%I64x\\n",@$tid,@x0,poi(@x0+0x4b0),@x3,dwo(@x1+@x3*4),@x4,@lr-QcDeviceMFT8380',
 'r $t5=@x0; r $t6=poi(@x0+0x4b0); r $t8=@$tid',
 dump("READER_NODE","@x0",1280),dump("READER_POOL","poi(@x0+0x4b0)",720),"g"])
save("read",[
 '.printf "E011BU_READ tid=%x store=%p tag=%x callerRVA=%I64x sameStore=%u sameReaderTid=%u\\n",@$tid,@x0,@x1,@lr-QcDeviceMFT8380,(@x0==@$t4),(@$tid==@$t8)',
 'r $t7=@x0; r $t15=1',
 dump("READ_STORE","@x0",128),
 'bp8 /1 QcDeviceMFT8380+0x5d5180 '+script("read-after"),"g"])
save("read-after",[
 '.printf "E011BU_READ_AFTER tid=%x src=%p sameTid=%u\\n",@$tid,@x0,(@$tid==@$t8)',
 'r $t9=@x0',
 '.if (@x0!=0) { '+dump("READ_OUT","@x0",2072)+' }',"g"])
save("cold",[
 '.printf "E011BU_COLD tid=%x dst=%p src=%p bytes=%I64u metadataSrcMatch=%u readerTidMatch=%u\\n",@$tid,@x0,@x1,@x2,(@x1==@$t9),(@$tid==@$t8)',
 'r $t10=@x0; r $t11=@x1; r $t12=@$tid; r $t16=1',
 dump("COLD_SOURCE","@x1",2072),dump("COLD_BEFORE","@x0",2072),
 'bp10 /1 QcDeviceMFT8380+0x73c094 '+script("cold-after"),"g"])
save("cold-after",[
 '.printf "E011BU_COLD_AFTER tid=%x sameTid=%u returnedDstMatch=%u\\n",@$tid,(@$tid==@$t12),(@x0==@$t10)',
 dump("COLD_AFTER","@$t10",2072),dump("COLD_SOURCE_AFTER","@$t11",2072),"g"])
save("arm",[
 'r $t0=0; r $t1=0; r $t2=0; r $t3=0; r $t4=0; r $t5=0; r $t6=0; r $t7=0; r $t8=0; r $t9=0; r $t10=0; r $t11=0; r $t12=0; r $t13=0; r $t14=0; r $t15=0; r $t16=0; r $t17=0',
 'bp0 /1 QcDeviceMFT8380+0x83aa20 '+script("first"),
 'bp1 /1 QcDeviceMFT8380+0x83aad4 '+script("second"),
 'bp2 /1 QcDeviceMFT8380+0x83abd4 '+script("publish"),
 'bp4 QcDeviceMFT8380+0x5c44c8 ".if ((@x1==0x5000001c)&&(@lr==QcDeviceMFT8380+0x5d6ef8)&&(@$t13==1)&&(@$t14==0)&&(@$tid==@$t2)) { '+script("write").strip('"')+' } .else { g }"',
 'bp6 QcDeviceMFT8380+0x5d4d30 ".if ((@x3==2)&&(dwo(@x1+8)==0x5000001c)&&(@lr>=QcDeviceMFT8380+0x73b730)&&(@lr<QcDeviceMFT8380+0x73c298)&&(@$t5==0)) { '+script("reader").strip('"')+' } .else { g }"',
 'bp7 QcDeviceMFT8380+0x5c4d78 ".if ((@x1==0x5000001c)&&(@lr==QcDeviceMFT8380+0x5d5180)&&(@$t5!=0)&&(@$t15==0)&&(@$tid==@$t8)) { '+script("read").strip('"')+' } .else { g }"',
 'bp9 /1 QcDeviceMFT8380+0x73c090 '+script("cold"),
 '.printf "E011BU_ARMED_BOUNDED_METADATA_LINEAGE\\n"',"bl"])
save("oracle",[".logopen "+win+"\\cdb-observer.raw","sxe ld:QcDeviceMFT8380.dll",'.printf "E011BU_WAIT_OWNER_MODULE\\n"',"g"])
ranges=[("FIRST",0x83aa10,32),("SECOND",0x83aac4,32),("PUBLISH",0x83abbc,32),("NODEWRITE",0x5d6a18,64),("WRITERET",0x5d6ee4,40),("NODEREAD",0x5d4d30,64),("READRET",0x5d5168,40),("STOREWRITE",0x5c44c8,64),("STOREREAD",0x5c4d78,64),("COLD",0x73c074,36),("READTAGS",0x1439208,20),("PUBTAGS",0x1483f38,8)]
save("qualify",['.printf "E011BU_MODULE_BASE base=%p\\n",QcDeviceMFT8380']+[dump("CODE_"+n,"QcDeviceMFT8380+0x"+format(v,"x"),z) for n,v,z in ranges])
print(json.dumps({"experiment":"E011BU","scripts":len(list(a.output.glob("*.cmd"))),"maximum_first_published_configurations":1,"maximum_store_writes_reads_cold_copies":1,"runtime_armed":False}))
