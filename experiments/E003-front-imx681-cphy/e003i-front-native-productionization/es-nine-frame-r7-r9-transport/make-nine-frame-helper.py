#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib
BASE_HELPER_SHA='3788ca6a05747961f523942117925d28b4a2edb91f76a06bb001071ffd238b08'
BASE_SCHED_SHA='50bbb9c59538167241245ea60b57f76e3b7e8979135c88c9ff4a363318ca328f'
ap=argparse.ArgumentParser()
ap.add_argument('helper_in',type=Path);ap.add_argument('schedule_in',type=Path)
ap.add_argument('helper_out',type=Path);ap.add_argument('schedule_out',type=Path)
a=ap.parse_args()
s=a.helper_in.read_text()
assert hashlib.sha256(s.encode()).hexdigest()==BASE_HELPER_SHA
def once(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
once('#define FRAME_COUNT 6U','#define FRAME_COUNT 9U')
once('static const unsigned int expect_index[FRAME_COUNT] = { 0, 1, 2, 3, 0, 1 };','static const unsigned int expect_index[FRAME_COUNT] = { 0, 1, 2, 3, 0, 1, 2, 3, 0 };')
once('void *first_snapshot = NULL, *second_snapshot = NULL;','void *snapshot[FRAME_COUNT] = { NULL };')
once('if (argc != 14) {\n\t\tfprintf(stderr, "usage: %s /dev/videoN R4.bin producer.py producer-out producer-manifest TLBG-prefix 3A-prefix out0 out1 out2 out3 out4 out5\\n", argv[0]);',
     'if (argc != 17) {\n\t\tfprintf(stderr, "usage: %s /dev/videoN R4.bin producer.py producer-out producer-manifest TLBG-prefix 3A-prefix out0 out1 out2 out3 out4 out5 out6 out7 out8\\n", argv[0]);')
once('\tfirst_snapshot = malloc(QC10C_BYTES); second_snapshot = malloc(QC10C_BYTES);\n\tif (!first_snapshot || !second_snapshot) { perror("malloc frame snapshot"); goto out; }',
     '\tfor (i = 0; i < FRAME_COUNT; i++) {\n\t\tsnapshot[i] = malloc(QC10C_BYTES);\n\t\tif (!snapshot[i]) { perror("malloc frame snapshot"); goto out; }\n\t}')
once('printf("AO_PAIR_AUDIT_THREAD_READY ORDER=3A_THEN_TLBG TARGETS=1..6\\n");','printf("AO_PAIR_AUDIT_THREAD_READY ORDER=3A_THEN_TLBG TARGETS=1..9\\n");')
once('''\t\tif (i == 0 || i == 1) {\n\t\t\tvoid *snapshot = i == 0 ? first_snapshot : second_snapshot;\n\t\t\tmemcpy(snapshot, map[i], QC10C_BYTES); memset(map[i], 0, QC10C_BYTES);\n\t\t\tif (qbuf_index(vfd, type, i)) pin_until_reboot("live re-QBUF failed");\n\t\t\tprintf("LIVE_REQUEUE_INDEX=%u AFTER_SEQUENCE=%u\\n", i, i); fflush(stdout);\n\t\t}\n''',
'''\t\tmemcpy(snapshot[i], map[b.index], QC10C_BYTES);\n\t\tif (i < 5U) {\n\t\t\tmemset(map[b.index], 0, QC10C_BYTES);\n\t\t\tif (qbuf_index(vfd, type, b.index)) pin_until_reboot("live re-QBUF failed");\n\t\t\tprintf("LIVE_REQUEUE_INDEX=%u AFTER_SEQUENCE=%u\\n", b.index, i); fflush(stdout);\n\t\t}\n''')
once('printf("DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..6 WRITES=%u RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6\\n",',
     'printf("DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..9 WRITES=%u RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6\\n",')
once('''\tif (save_file(argv[8], first_snapshot, QC10C_BYTES) || save_file(argv[9], second_snapshot, QC10C_BYTES) ||\n\t    save_file(argv[10], map[2], QC10C_BYTES) || save_file(argv[11], map[3], QC10C_BYTES) ||\n\t    save_file(argv[12], map[0], QC10C_BYTES) || save_file(argv[13], map[1], QC10C_BYTES)) {\n\t\tperror("save QC10C output"); goto out;\n\t}\n\tprintf("PASS: six-frame regression plus producer-derived R5/R6 and paired TL_BG/3A generations 1..6 (AO collector)\\n");\n''',
'''\tfor (i = 0; i < FRAME_COUNT; i++) {\n\t\tif (save_file(argv[8 + i], snapshot[i], QC10C_BYTES)) {\n\t\t\tperror("save QC10C output"); goto out;\n\t\t}\n\t}\n\tprintf("PASS: nine-frame transport plus producer-derived R5..R9 and paired TL_BG/3A generations 1..9 (AO collector)\\n");\n''')
once('free(audit_stats3a); free(audit_tlbg); free(iq); free(second_snapshot); free(first_snapshot);',
     'for (i = 0; i < FRAME_COUNT; i++) free(snapshot[i]);\n\tfree(audit_stats3a); free(audit_tlbg); free(iq);')
# Critical invariants must remain exactly bounded.
assert s.count('if (target <= 6U) {')==1
assert s.count('if (target >= 2U && target <= 4U) {')==1
a.helper_out.write_text(s)
h=a.schedule_in.read_text()
assert hashlib.sha256(h.encode()).hexdigest()==BASE_SCHED_SHA
assert h.count('#define E003I_DB_FRAME_COUNT 6U')==1
h=h.replace('#define E003I_DB_FRAME_COUNT 6U','#define E003I_DB_FRAME_COUNT 9U')
a.schedule_out.write_text(h)
print('HELPER_SHA='+hashlib.sha256(s.encode()).hexdigest())
print('SCHEDULE_H_SHA='+hashlib.sha256(h.encode()).hexdigest())
