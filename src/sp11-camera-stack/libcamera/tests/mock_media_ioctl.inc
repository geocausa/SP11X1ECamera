/* Simulated kernel boundary: tests the two independent topology ioctls. */
static const Topology *mockTop = nullptr;
static int mockMode = 0;
static int mockStep = 0;
static int fakeIoctl(int fd, unsigned long op, void *raw)
{
    if (fd != 17 || !mockTop) return -1;
    if (op == MEDIA_IOC_DEVICE_INFO) {
        auto &info = *static_cast<media_device_info *>(raw);
        std::strcpy(info.driver, mockMode == 1 ? "not-camss" : "qcom-camss");
        std::strcpy(info.bus_info, mockMode == 7 ?
                    "platform:wrong.isp" : "platform:acb7000.isp");
        return 0;
    }
    if (op != MEDIA_IOC_G_TOPOLOGY || (mockMode == 4 && mockStep == 1))
        return -1;
    auto &t = *static_cast<media_v2_topology *>(raw);
    const unsigned step = (++mockStep % 2) ? 1 : 2;
    t.topology_version = step == 2 && mockMode == 2 ? 8 : 7;
    t.num_entities = static_cast<unsigned>(mockTop->entities.size());
    t.num_interfaces = static_cast<unsigned>(mockTop->interfaces.size());
    t.num_pads = static_cast<unsigned>(mockTop->pads.size());
    t.num_links = static_cast<unsigned>(mockTop->links.size());
    if (mockMode == 6) ++t.num_links;
    if (step == 2) {
        if (!t.ptr_entities || !t.ptr_interfaces || !t.ptr_pads ||
            !t.ptr_links) return -1;
        std::memcpy(reinterpret_cast<void *>(t.ptr_entities),
                    mockTop->entities.data(),
                    mockTop->entities.size() * sizeof(media_v2_entity));
        std::memcpy(reinterpret_cast<void *>(t.ptr_interfaces),
                    mockTop->interfaces.data(),
                    mockTop->interfaces.size() * sizeof(media_v2_interface));
        std::memcpy(reinterpret_cast<void *>(t.ptr_pads),
                    mockTop->pads.data(),
                    mockTop->pads.size() * sizeof(media_v2_pad));
        std::memcpy(reinterpret_cast<void *>(t.ptr_links),
                    mockTop->links.data(),
                    mockTop->links.size() * sizeof(media_v2_link));
        if (mockMode == 5)
            reinterpret_cast<media_v2_link *>(t.ptr_links)[44].flags = MEDIA_LNK_FL_DYNAMIC;
        if (mockMode == 3) --t.num_pads;
    }
    return 0;
}
