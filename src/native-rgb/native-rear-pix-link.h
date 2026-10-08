/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_REAR_PIX_LINK_H
#define NATIVE_REAR_PIX_LINK_H

/* PIX also has an immutable statistics sink. List order is not route identity.
 * The required immutable video edge must exist and be enabled.
 */
static bool native_rear_required_pix_video_link(struct media_pad *source,
                                               struct media_pad *sink)
{
 struct media_link *link;

 if (!source || !sink || !(source->flags & MEDIA_PAD_FL_SOURCE) ||
     !(sink->flags & MEDIA_PAD_FL_SINK))
  return false;
 link = media_entity_find_link(source, sink);
 return link && link->source == source && link->sink == sink &&
        (link->flags & MEDIA_LNK_FL_ENABLED) &&
        (link->flags & MEDIA_LNK_FL_IMMUTABLE);
}
#endif
