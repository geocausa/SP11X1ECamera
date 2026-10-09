/* SPDX-License-Identifier: GPL-2.0-only */
/* Exclusive rear-worker cache of physically mapped, proof-retired FULL leases.
 * Retirement requires the caller's original all10 consumed-address/owner proof.
 * Entries remain exposed=true to record past exposure. Only a validated take
 * moves an entry into a fresh, unexposed generation; no stop fact is fabricated.
 * All retained mappings are physically freed only after four physical stops.
 */
#define NATIVE_REAR_FULL_CACHE_CAPACITY 4U
struct native_rear_full_cache_entry {
 struct native_rear_video_lease lease;
 u64 owner, generation;
};
struct native_rear_full_cache {
 struct native_rear_full_cache_entry entry[NATIVE_REAR_FULL_CACHE_CAPACITY];
 u64 owner;
 u32 hits, misses, stored, evicted;
 bool active;
};
static struct native_rear_full_cache native_rear_full_cache;

static bool native_rear_full_cache_entry_empty(const struct native_rear_full_cache_entry *e)
{
 return !e->owner && !e->generation && !e->lease.dbuf && !e->lease.attachment &&
        !e->lease.table && !e->lease.acquired && !e->lease.exposed && !e->lease.stop_proven &&
        !e->lease.span.y_iova && !e->lease.span.uv_iova && !e->lease.span.mapped_bytes;
}
static bool native_rear_full_cache_is_active(void)
{
 return native_rear_full_cache.active;
}
static bool native_rear_full_cache_idle(void)
{
 unsigned int i;
 if (native_rear_full_cache.active || native_rear_full_cache.owner)
  return false;
 for (i=0;i<NATIVE_REAR_FULL_CACHE_CAPACITY;i++) {
  const struct native_rear_full_cache_entry *e=&native_rear_full_cache.entry[i];
  if (!native_rear_full_cache_entry_empty(e))
   return false;
 }
 return true;
}
static int native_rear_full_cache_begin(u64 owner)
{
 if (!owner || !native_rear_full_cache_idle())
  return -EBUSY;
 memset(&native_rear_full_cache,0,sizeof(native_rear_full_cache));
 native_rear_full_cache.owner=owner;
 native_rear_full_cache.active=true;
 return 0;
}
static bool native_rear_full_cache_entry_valid(const struct native_rear_full_cache_entry *e,u64 owner)
{
 return e && owner && e->owner==owner && e->generation &&
        native_rear_video_lease_valid(&e->lease) && e->lease.exposed &&
        !e->lease.stop_proven;
}
static bool native_rear_full_cache_overlap(const struct native_rear_video_lease *a,
                                           const struct native_rear_video_lease *b)
{
 return a->dbuf==b->dbuf || a->attachment==b->attachment || a->table==b->table ||
        (a->span.y_iova<=b->span.y_iova ?
         b->span.y_iova-a->span.y_iova<a->span.mapped_bytes :
         a->span.y_iova-b->span.y_iova<b->span.mapped_bytes);
}
static int native_rear_full_cache_disjoint(const struct native_rear_video_lease *lease,u64 owner)
{
 unsigned int i;
 if (!native_rear_full_cache.active)
  return native_rear_full_cache_idle() ? 0 : -EPROTO;
 if (!owner || owner!=native_rear_full_cache.owner ||
     !native_rear_video_lease_valid(lease))
  return -ESTALE;
 for (i=0;i<NATIVE_REAR_FULL_CACHE_CAPACITY;i++) {
  const struct native_rear_full_cache_entry *e=&native_rear_full_cache.entry[i];
  if (!e->lease.acquired) {
   if (!native_rear_full_cache_entry_empty(e))
    return -EPROTO;
   continue;
  }
  if (!native_rear_full_cache_entry_valid(e,owner))
   return -EPROTO;
  if (native_rear_full_cache_overlap(lease,&e->lease))
   return -EADDRINUSE;
 }
 return 0;
}
/* Return 0 on a move into cache, 1 to use the original physical unmap path.
 * Negative return changes nothing: caller pins the uncertain generation.
 */
static int native_rear_full_cache_retire(struct native_rear_video_lease *lease,
                                         u64 owner,u64 generation)
{
 unsigned int i, free_slot=NATIVE_REAR_FULL_CACHE_CAPACITY;
 int ret;
 if (!native_rear_full_cache.active)
  return native_rear_full_cache_idle() ? 1 : -EPROTO;
 if (!owner || owner!=native_rear_full_cache.owner || !generation ||
     !native_rear_video_lease_valid(lease) || !lease->exposed || lease->stop_proven)
  return -ESTALE;
 ret=native_rear_full_cache_disjoint(lease,owner);
 if (ret)
  return ret;
 for (i=0;i<NATIVE_REAR_FULL_CACHE_CAPACITY;i++)
  if (!native_rear_full_cache.entry[i].lease.acquired) {
   free_slot=i;
   break;
  }
 if (free_slot==NATIVE_REAR_FULL_CACHE_CAPACITY) {
  native_rear_full_cache.evicted++;
  return 1; /* Already proven retired; original unmap remains permitted. */
 }
 native_rear_full_cache.entry[free_slot]=(struct native_rear_full_cache_entry){
  .lease=*lease,.owner=owner,.generation=generation};
 memset(lease,0,sizeof(*lease)); /* Move ownership exactly once. */
 native_rear_full_cache.stored++;
 return 0;
}
static int native_rear_full_cache_take(struct dma_buf *dbuf,size_t bytes,u64 owner,
                                       struct native_rear_video_lease *out)
{
 unsigned int i;
 if (!native_rear_full_cache.active)
  return native_rear_full_cache_idle() ? -ENOENT : -EPROTO;
 if (!dbuf || !out || owner!=native_rear_full_cache.owner || !owner ||
     bytes<NATIVE_REAR_NV12_BYTES)
  return -ESTALE;
 if (out->acquired || out->attachment || out->table || out->exposed || out->stop_proven ||
     out->span.y_iova || out->span.uv_iova || out->span.mapped_bytes)
  return -EBUSY;
 for (i=0;i<NATIVE_REAR_FULL_CACHE_CAPACITY;i++) {
  struct native_rear_full_cache_entry *e=&native_rear_full_cache.entry[i];
  struct native_rear_video_dma span;
  int ret;
  if (!e->lease.acquired) {
   if (!native_rear_full_cache_entry_empty(e))
    return -EPROTO;
   continue;
  }
  if (!native_rear_full_cache_entry_valid(e,owner))
   return -EPROTO;
  if (e->lease.dbuf!=dbuf)
   continue;
  ret=native_rear_video_dma_table(e->lease.table,bytes,&span);
  if (ret || span.y_iova!=e->lease.span.y_iova ||
      span.uv_iova!=e->lease.span.uv_iova || span.mapped_bytes!=e->lease.span.mapped_bytes)
   return -EPROTO;
  *out=e->lease;
  out->exposed=false; /* New generation, backed by exact retired-entry proof. */
  memset(e,0,sizeof(*e));
  native_rear_full_cache.hits++;
  return 0;
 }
 native_rear_full_cache.misses++;
 return -ENOENT;
}
static int native_rear_full_cache_stop_check(u64 owner,bool csid,bool bus,bool rtcdm,bool source)
{
 unsigned int i,j;
 if (!native_rear_full_cache.active)
  return native_rear_full_cache_idle() ? 0 : -EPROTO;
 if (!owner || owner!=native_rear_full_cache.owner || !csid || !bus || !rtcdm || !source)
  return -EBUSY;
 for (i=0;i<NATIVE_REAR_FULL_CACHE_CAPACITY;i++) {
  const struct native_rear_full_cache_entry *e=&native_rear_full_cache.entry[i];
  if (!e->lease.acquired) {
   if (!native_rear_full_cache_entry_empty(e))
    return -EPROTO;
   continue;
  }
  if (!native_rear_full_cache_entry_valid(e,owner))
   return -EPROTO;
  for (j=0;j<i;j++)
   if (native_rear_full_cache.entry[j].lease.acquired &&
       native_rear_full_cache_overlap(&e->lease,&native_rear_full_cache.entry[j].lease))
    return -EADDRINUSE;
 }
 return 0;
}
static int native_rear_full_cache_flush(struct vfe_device *vfe,u64 owner,
                                        bool csid,bool bus,bool rtcdm,bool source)
{
 unsigned int i,count=0;
 int ret=native_rear_full_cache_stop_check(owner,csid,bus,rtcdm,source);
 if (ret || !native_rear_full_cache.active)
  return ret;
 for (i=0;i<NATIVE_REAR_FULL_CACHE_CAPACITY;i++) {
  struct native_rear_full_cache_entry *e=&native_rear_full_cache.entry[i];
  if (!e->lease.acquired)
   continue;
  ret=native_rear_video_lease_stop(&e->lease,csid,bus,rtcdm,source);
  if (ret)
   return ret;
  ret=native_rear_video_lease_put(&e->lease);
  if (ret)
   return ret;
  memset(e,0,sizeof(*e));
  count++;
 }
 native_rear_full_cache.active=false;
 native_rear_full_cache.owner=0;
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_FULL_CACHE_FLUSH owner=%llu released=%u all_stops=15 idle=%u pixel_bytes_read=0\n",
  (unsigned long long)owner,count,native_rear_full_cache_idle());
 return native_rear_full_cache_idle() ? 0 : -EPROTO;
}
static void native_rear_full_cache_observe(struct vfe_device *vfe)
{
 unsigned int i,count=0;
 for (i=0;i<NATIVE_REAR_FULL_CACHE_CAPACITY;i++)
  if (native_rear_full_cache.entry[i].lease.acquired)
   count++;
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_FULL_CACHE owner=%llu active=%u hits=%u misses=%u stored=%u evicted=%u retained=%u capacity=4 physical_unmaps_deferred=1 pixel_bytes_read=0\n",
  (unsigned long long)native_rear_full_cache.owner,native_rear_full_cache.active,
  native_rear_full_cache.hits,native_rear_full_cache.misses,
  native_rear_full_cache.stored,native_rear_full_cache.evicted,count);
}
