#include <windows.h>
#include <mfapi.h>
#include <mfidl.h>
#include <mfreadwrite.h>
#include <mferror.h>
#include <ks.h>
#include <ksmedia.h>
#include <ksproxy.h>
#include <wrl/client.h>
#include <iostream>
#include <string>
#include <vector>
#include <iomanip>

using Microsoft::WRL::ComPtr;

static const GUID kExtendedCameraControl =
{0x1cb79112,0xc0d2,0x4213,{0x9c,0xa6,0xcd,0x4f,0xdb,0x92,0x79,0x72}};

static const GUID kSensorCamera =
{0x24e552d7,0x6523,0x47f7,{0xa6,0x47,0xd3,0x46,0x5b,0xf1,0xf5,0xca}};

#pragma pack(push, 8)
struct SecureModePayload {
    KSCAMERA_EXTENDEDPROP_HEADER Header;
    KSCAMERA_EXTENDEDPROP_VALUE Value;
};
#pragma pack(pop)

static void print_hr(const char* tag, HRESULT hr) {
    std::cout << tag << " hr=0x" << std::hex << std::setw(8) << std::setfill('0')
              << (unsigned long)hr << std::dec << std::setfill(' ') << "\n";
}

static HRESULT secure_prop(IKsControl* ks, ULONG op, ULONGLONG flags, const char* tag, bool printPayload=true) {
    KSPROPERTY p{};
    p.Set = kExtendedCameraControl;
    p.Id = 36;
    p.Flags = op;

    SecureModePayload d{};
    d.Header.Version = 1;
    d.Header.PinId = 0;
    d.Header.Size = sizeof(d);
    d.Header.Result = 0;
    d.Header.Flags = flags;
    d.Header.Capability = 0;

    ULONG returned = 0;
    HRESULT hr = ks->KsProperty(&p, sizeof(p), &d, sizeof(d), &returned);

    std::cout << "E004AJ_MFKS_" << tag
              << " op=0x" << std::hex << op
              << " hr=0x" << (unsigned long)hr
              << " returned=0x" << returned
              << " version=0x" << d.Header.Version
              << " pin=0x" << d.Header.PinId
              << " size=0x" << d.Header.Size
              << " result=0x" << d.Header.Result
              << " flags=0x" << d.Header.Flags
              << " cap=0x" << d.Header.Capability
              << std::dec << "\n";
    return hr;
}

int wmain() {
    std::cout << std::unitbuf; std::wcout << std::unitbuf;
    std::cout << "E004AJ_MFKS_STAGE=ENTER\n";
    static_assert(sizeof(KSCAMERA_EXTENDEDPROP_HEADER) == 32, "header size");
    static_assert(sizeof(KSCAMERA_EXTENDEDPROP_VALUE) == 8, "value size");
    static_assert(sizeof(SecureModePayload) == 40, "secure payload size");

    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (FAILED(hr)) { print_hr("CoInitializeEx", hr); return 2; }
    hr = MFStartup(MF_VERSION);
    if (FAILED(hr)) { print_hr("MFStartup", hr); CoUninitialize(); return 3; }

    ComPtr<IMFMediaSource> source;
    ComPtr<IKsControl> ks;
    ComPtr<IMFSourceReader> reader;
    ComPtr<IMFMediaType> selected;
    bool secureEnabled = false;
    int rc = 1;

    IMFActivate** activates = nullptr;
    UINT32 count = 0;
    ComPtr<IMFAttributes> enumAttrs;
    hr = MFCreateAttributes(&enumAttrs, 3);
    if (FAILED(hr)) { print_hr("MFCreateAttributes", hr); goto cleanup; }
    hr = enumAttrs->SetGUID(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE, MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_GUID);
    if (FAILED(hr)) { print_hr("SetGUID", hr); goto cleanup; }
    hr = enumAttrs->SetGUID(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_CATEGORY, kSensorCamera);
    if (FAILED(hr)) { print_hr("SetSensorCategory", hr); goto cleanup; }
    hr = MFEnumDeviceSources(enumAttrs.Get(), &activates, &count);
    if (FAILED(hr)) { print_hr("MFEnumDeviceSources", hr); goto cleanup; }

    std::cout << "E004AJ_MFKS_DEVICE_COUNT=" << count << "\n";
    IMFActivate* chosen = nullptr;
    for (UINT32 i = 0; i < count; ++i) {
        WCHAR* name = nullptr; UINT32 nlen = 0;
        WCHAR* link = nullptr; UINT32 llen = 0;
        activates[i]->GetAllocatedString(MF_DEVSOURCE_ATTRIBUTE_FRIENDLY_NAME, &name, &nlen);
        activates[i]->GetAllocatedString(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK, &link, &llen);
        std::wcout << L"E004AJ_MFKS_DEVICE idx=" << i
                   << L" name=" << (name ? name : L"<null>")
                   << L" link=" << (link ? link : L"<null>") << L"\n";
        if (name && std::wstring(name) == L"Surface IR Camera Front") chosen = activates[i];
        CoTaskMemFree(name); CoTaskMemFree(link);
    }
    if (!chosen) {
        std::cout << "E004AJ_MFKS_FAIL=no_ir_device\n";
        goto cleanup;
    }

    hr = chosen->ActivateObject(IID_PPV_ARGS(&source));
    print_hr("E004AJ_MFKS_ACTIVATE", hr);
    if (FAILED(hr)) goto cleanup;

    hr = source.As(&ks);
    print_hr("E004AJ_MFKS_QI_IKsControl", hr);
    if (FAILED(hr)) goto cleanup;

    hr = secure_prop(ks.Get(), KSPROPERTY_TYPE_GET, 0, "GET_BEFORE");
    if (FAILED(hr)) goto cleanup;

    hr = MFCreateSourceReaderFromMediaSource(source.Get(), nullptr, &reader);
    print_hr("E004AJ_MFKS_SOURCE_READER", hr);
    if (FAILED(hr)) goto cleanup;

    hr = reader->SetStreamSelection(MF_SOURCE_READER_ALL_STREAMS, FALSE);
    if (FAILED(hr)) { print_hr("E004AJ_MFKS_DESELECT", hr); goto cleanup; }
    hr = reader->SetStreamSelection(MF_SOURCE_READER_FIRST_VIDEO_STREAM, TRUE);
    if (FAILED(hr)) { print_hr("E004AJ_MFKS_SELECT_VIDEO", hr); goto cleanup; }

    for (DWORD i = 0; i < 64; ++i) {
        ComPtr<IMFMediaType> mt;
        hr = reader->GetNativeMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, i, &mt);
        if (hr == MF_E_NO_MORE_TYPES) break;
        if (FAILED(hr)) continue;
        GUID subtype{};
        UINT32 w=0,h=0,num=0,den=0;
        mt->GetGUID(MF_MT_SUBTYPE, &subtype);
        MFGetAttributeSize(mt.Get(), MF_MT_FRAME_SIZE, &w, &h);
        MFGetAttributeRatio(mt.Get(), MF_MT_FRAME_RATE, &num, &den);
        WCHAR sub[64]{};
        StringFromGUID2(subtype, sub, 64);
        std::wcout << L"E004AJ_MFKS_TYPE idx=" << i << L" subtype=" << sub
                   << L" dims=" << w << L"x" << h << L" fps=" << num << L"/" << den << L"\n";
        if (!selected && subtype == MFVideoFormat_NV12 && w == 644 && h == 604) selected = mt;
    }
    if (!selected) {
        std::cout << "E004AJ_MFKS_FAIL=no_nv12_644x604\n";
        goto cleanup;
    }

    hr = reader->SetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, nullptr, selected.Get());
    print_hr("E004AJ_MFKS_SET_TYPE", hr);
    if (FAILED(hr)) goto cleanup;

    hr = secure_prop(ks.Get(), KSPROPERTY_TYPE_SET, KSCAMERA_EXTENDEDPROP_SECUREMODE_ENABLED, "SET_ENABLE_AFTER_STREAM");
    if (FAILED(hr)) goto cleanup;
    secureEnabled = true;

    hr = secure_prop(ks.Get(), KSPROPERTY_TYPE_GET, 0, "GET_AFTER_ENABLE");
    if (FAILED(hr)) goto cleanup;

    int frames = 0;
    for (int tries = 0; tries < 240 && frames < 12; ++tries) {
        DWORD streamIndex = 0, flags = 0;
        LONGLONG ts = 0;
        ComPtr<IMFSample> sample;
        hr = reader->ReadSample(MF_SOURCE_READER_FIRST_VIDEO_STREAM, 0, &streamIndex, &flags, &ts, &sample);
        if (FAILED(hr)) { print_hr("E004AJ_MFKS_READ", hr); goto cleanup; }
        if (sample) {
            DWORD buffers = 0; sample->GetBufferCount(&buffers);
            DWORD total = 0;
            ComPtr<IMFMediaBuffer> buf;
            if (SUCCEEDED(sample->ConvertToContiguousBuffer(&buf))) buf->GetCurrentLength(&total);
            ++frames;
            std::cout << "E004AJ_MFKS_FRAME n=" << frames << " ts=" << ts
                      << " buffers=" << buffers << " bytes=" << total
                      << " flags=0x" << std::hex << flags << std::dec << "\n";
        }
    }
    std::cout << "E004AJ_MFKS_ACQUIRED=" << frames << "\n";
    if (frames < 3) goto cleanup;

    std::cout << "E004AJ_MFKS_LIVE_GATE\n" << std::flush;
    {
        std::string line;
        std::getline(std::cin, line);
        std::cout << "E004AJ_MFKS_GATE_RELEASE=" << line << "\n";
    }

    reader.Reset();
    hr = secure_prop(ks.Get(), KSPROPERTY_TYPE_SET, KSCAMERA_EXTENDEDPROP_SECUREMODE_DISABLED, "SET_DISABLE");
    print_hr("E004AJ_MFKS_DISABLE_RESULT", hr);
    if (SUCCEEDED(hr)) secureEnabled = false;
    secure_prop(ks.Get(), KSPROPERTY_TYPE_GET, 0, "GET_AFTER_DISABLE");
    rc = 0;

cleanup:
    if (reader) reader.Reset();
    if (secureEnabled && ks) {
        HRESULT dhr = secure_prop(ks.Get(), KSPROPERTY_TYPE_SET, KSCAMERA_EXTENDEDPROP_SECUREMODE_DISABLED, "CLEANUP_DISABLE");
        print_hr("E004AJ_MFKS_CLEANUP_DISABLE_RESULT", dhr);
        secureEnabled = false;
    }
    if (source) source->Shutdown();
    selected.Reset();
    ks.Reset();
    source.Reset();
    enumAttrs.Reset();
    if (activates) {
        for (UINT32 i = 0; i < count; ++i) if (activates[i]) activates[i]->Release();
        CoTaskMemFree(activates);
    }
    MFShutdown();
    CoUninitialize();
    std::cout << "E004AJ_MFKS_END rc=" << rc << "\n";
    return rc;
}


