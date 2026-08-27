#include <errno.h>
#include <fcntl.h>
#include <linux/media.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <stdint.h>
#include <unistd.h>

static struct media_v2_entity *find_ent(struct media_v2_entity *e, unsigned n, __u32 id) {
    for (unsigned i=0;i<n;i++) if (e[i].id==id) return &e[i];
    return NULL;
}
static struct media_v2_pad *find_pad(struct media_v2_pad *p, unsigned n, __u32 id) {
    for (unsigned i=0;i<n;i++) if (p[i].id==id) return &p[i];
    return NULL;
}
int main(int argc,char **argv){
    const char *dev = argc>1?argv[1]:"/dev/media0";
    int fd=open(dev,O_RDONLY|O_CLOEXEC); if(fd<0){perror("open");return 1;}
    struct media_v2_topology t={0};
    if(ioctl(fd,MEDIA_IOC_G_TOPOLOGY,&t)<0){perror("G_TOPOLOGY sizing");return 2;}
    struct media_v2_entity *e=calloc(t.num_entities,sizeof(*e));
    struct media_v2_interface *in=calloc(t.num_interfaces,sizeof(*in));
    struct media_v2_pad *p=calloc(t.num_pads,sizeof(*p));
    struct media_v2_link *l=calloc(t.num_links,sizeof(*l));
    if(!e||!in||!p||!l){perror("calloc");return 3;}
    t.ptr_entities=(uintptr_t)e; t.ptr_interfaces=(uintptr_t)in; t.ptr_pads=(uintptr_t)p; t.ptr_links=(uintptr_t)l;
    if(ioctl(fd,MEDIA_IOC_G_TOPOLOGY,&t)<0){perror("G_TOPOLOGY data");return 4;}
    printf("TOPOLOGY version=%llu entities=%u pads=%u links=%u interfaces=%u\n",(unsigned long long)t.topology_version,t.num_entities,t.num_pads,t.num_links,t.num_interfaces);
    for(unsigned i=0;i<t.num_entities;i++) if(strstr(e[i].name,"ov13858")||strstr(e[i].name,"csiphy1"))
        printf("ENTITY id=%u name='%s' function=0x%x flags=0x%x\n",e[i].id,e[i].name,e[i].function,e[i].flags);
    int found=0;
    for(unsigned i=0;i<t.num_links;i++){
        struct media_v2_pad *sp=find_pad(p,t.num_pads,l[i].source_id), *dp=find_pad(p,t.num_pads,l[i].sink_id);
        if(!sp||!dp) continue;
        struct media_v2_entity *se=find_ent(e,t.num_entities,sp->entity_id), *de=find_ent(e,t.num_entities,dp->entity_id);
        if(!se||!de) continue;
        if((strstr(se->name,"ov13858")&&strstr(de->name,"csiphy1")) || (strstr(se->name,"csiphy1")&&strstr(de->name,"ov13858"))){
            printf("MATCH source='%s' pad=%u -> sink='%s' pad=%u flags=0x%08x enabled=%s immutable=%s data_link=%s\n",
              se->name,sp->index,de->name,dp->index,l[i].flags,
              (l[i].flags&MEDIA_LNK_FL_ENABLED)?"yes":"no",
              (l[i].flags&MEDIA_LNK_FL_IMMUTABLE)?"yes":"no",
              ((l[i].flags&MEDIA_LNK_FL_LINK_TYPE)==MEDIA_LNK_FL_DATA_LINK)?"yes":"no");
            found=1;
        }
    }
    close(fd); return found?0:5;
}
