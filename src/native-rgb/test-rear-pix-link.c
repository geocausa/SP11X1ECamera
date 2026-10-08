/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#define MEDIA_PAD_FL_SOURCE 1U
#define MEDIA_PAD_FL_SINK 2U
#define MEDIA_LNK_FL_ENABLED 1U
#define MEDIA_LNK_FL_IMMUTABLE 2U
struct media_pad { unsigned flags; };
struct media_link { struct media_pad *source,*sink; unsigned flags; };
static struct media_link *edges[2];
static bool wrong_result;
static struct media_link *media_entity_find_link(struct media_pad *source,struct media_pad *sink)
{
 if(wrong_result)return edges[0];
 for(unsigned i=0;i<2;i++)
  if(edges[i]&&edges[i]->source==source&&edges[i]->sink==sink)return edges[i];
 return NULL;
}
#include "native-rear-pix-link.h"
static unsigned assertions;
#define CHECK(x) do { assertions++;if(!(x))abort(); } while(0)
int main(void)
{
 struct media_pad source={MEDIA_PAD_FL_SOURCE},video={MEDIA_PAD_FL_SINK};
 struct media_pad stats={MEDIA_PAD_FL_SINK},other={MEDIA_PAD_FL_SINK};
 struct media_link v={&source,&video,MEDIA_LNK_FL_ENABLED|MEDIA_LNK_FL_IMMUTABLE};
 struct media_link m={&source,&stats,MEDIA_LNK_FL_ENABLED|MEDIA_LNK_FL_IMMUTABLE};
 for(unsigned order=0;order<2;order++){
  edges[order]=&v;edges[1-order]=&m;
  CHECK(native_rear_required_pix_video_link(&source,&video));
  v.flags=MEDIA_LNK_FL_IMMUTABLE;
  CHECK(!native_rear_required_pix_video_link(&source,&video));
  v.flags=MEDIA_LNK_FL_ENABLED;
  CHECK(!native_rear_required_pix_video_link(&source,&video));
  v.flags=MEDIA_LNK_FL_ENABLED|MEDIA_LNK_FL_IMMUTABLE;
  CHECK(!native_rear_required_pix_video_link(&source,&other));
  CHECK(!native_rear_required_pix_video_link(NULL,&video));
  CHECK(!native_rear_required_pix_video_link(&source,NULL));
  source.flags=MEDIA_PAD_FL_SINK;
  CHECK(!native_rear_required_pix_video_link(&source,&video));source.flags=MEDIA_PAD_FL_SOURCE;
  video.flags=MEDIA_PAD_FL_SOURCE;
  CHECK(!native_rear_required_pix_video_link(&source,&video));video.flags=MEDIA_PAD_FL_SINK;
  edges[order]=NULL;
  CHECK(!native_rear_required_pix_video_link(&source,&video));edges[order]=&v;
 }
 edges[0]=&m;edges[1]=&v;wrong_result=true;
 CHECK(!native_rear_required_pix_video_link(&source,&video));
 printf("{\"assertions\":%u,\"metadata_first_video_found\":true,\"both_link_orders_checked\":true}\n",assertions);
 return 0;
}
