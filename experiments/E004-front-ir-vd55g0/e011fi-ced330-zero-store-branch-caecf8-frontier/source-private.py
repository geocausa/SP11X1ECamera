#!/usr/bin/env python3
"""E011FI private prototype: exact CED330 zero store/branch to same-thread CAECF8 frontier."""
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *

ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
EL_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011el-joined-parent-mode-parser-prefix/RESULT.json'
EL_REFS=ROOT/'experiments/E004-front-ir-vd55g0/e011el-joined-parent-mode-parser-prefix/GLOBAL-REFS-SAFE.json'
EM_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011em-cfd550-cfcc18-validation-prefix/RESULT.json'
DY_SOURCE=ROOT/'experiments/E004-front-ir-vd55g0/e011dy-original-cold-runtime-context-receiver/SOURCE-SAFE.json'
EN_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011en-joined-cfd410-cb6520-prefix/RESULT.json'
OUT=Path(__file__).resolve().parent
EW_DIR=ROOT/'experiments/E004-front-ir-vd55g0/e011ew-source-exact-createfilew-failure-branch'
EW_RESULT=EW_DIR/'RESULT.json'
EW_AUTH=EW_DIR/'WINDOWS-AUTHORITY-SAFE.json'
EO_WINDOWS_SAFE=ROOT/'experiments/E004-front-ir-vd55g0/e011eo-native-selected-field-zero-branch/WINDOWS-SAFE.json'
EO_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011eo-native-selected-field-zero-branch/RESULT.json'
EP_WINDOWS=ROOT/'experiments/E004-front-ir-vd55g0/e011ep-native-callback-cache-branch/WINDOWS-SAFE.json'
EP_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ep-native-callback-cache-branch/RESULT.json'
EQ_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011eq-cb76b0-conversion-query-prefix/RESULT.json'
EXACT_API=ROOT/'experiments/E004-front-ir-vd55g0/e011er-exact-conversion-query-allocator-frontier/EXACT-API-SAFE.json'
CM_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/RESULT.json'
CM_BOOT=ROOT/'experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/BOOTSTRAP-SAFE.json'
API_OUTPUT=EW_DIR/'EXACT-API-OUTPUT-SAFE.json'
ES_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011es-exact-allocator-output-conversion-return/RESULT.json'
ET_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011et-post-conversion-cfd570-call-frontier/RESULT.json'
EU_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011eu-startup-lowio-lifetime-cfd570-prefix/RESULT.json'
EV_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ev-joined-cc08e8-createfilew-frontier/RESULT.json'
CM_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/source-private.py'
LOW_LIFE=EW_DIR/'LOWIO-LIFETIME-SAFE.json'
CV_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cv-original-slot-thread-producer/source-private.py'
CV_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011cv-original-slot-thread-producer/RESULT.json'
CV_PIN='e979d0d4046f485f74cacbfa9403681da03edcb69751866e8715fd26a7b6e870'
assert hashlib.sha256(CV_PATH.read_bytes()).hexdigest()==CV_PIN
spcv=importlib.util.spec_from_file_location('ey_cv',CV_PATH);CV=importlib.util.module_from_spec(spcv);spcv.loader.exec_module(CV);CV.CO.authority()
CVR=json.loads(CV_RESULT.read_text());assert CVR['status']=='PASS_BOUNDED_ORIGINAL_SLOT_AND_THREAD_PRODUCER' and CVR['thread_object_bytes']==968
FH_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fh-ced0d8-zero-return-ced330-frontier/RESULT.json'
FHR=json.loads(FH_RESULT.read_text());assert FHR['status']=='PASS_CED0D8_ZERO_RETURN_TO_CED330_FRONTIER' and FHR['next_source_RVA']=='0xced330' and not FHR['outer_result_store_executed']
FG_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fg-selected-lock-release-ced194-frontier/RESULT.json'
FGR=json.loads(FG_RESULT.read_text());assert FGR['status']=='PASS_SELECTED_LOCK_RELEASE_TO_CED194_FRONTIER' and FGR['next_source_RVA']=='0xced194' and FGR['selected_object_lock_released']
FF_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ff-cc60e0-selected-cleanup-lock-release-frontier/RESULT.json'
FFR=json.loads(FF_RESULT.read_text());assert FFR['status']=='PASS_CC60E0_SELECTED_CLEANUP_TO_LOCK_RELEASE_FRONTIER' and FFR['next_source_RVA']=='0xced190' and not FFR['CB3480_executed']
FE_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fe-cfa9c0-error-branch-cc60e0-frontier/RESULT.json'
FER=json.loads(FE_RESULT.read_text());assert FER['status']=='PASS_CFA9C0_ERROR_BRANCH_TO_CC60E0_FRONTIER' and FER['next_source_RVA']=='0xced188' and not FER['CC60E0_executed']
FC_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fc-caller-index0-lowio-release/RESULT.json'
FB_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fb-cfd410-parent-return-cfcc9c-frontier/RESULT.json'
FA_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fa-current-76byte-parent-cleanup/RESULT.json'
EZ_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ez-cfd570-error-return-parent-frontier/RESULT.json'
EY_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ey-current-thread-fls-caec20-error-propagation/RESULT.json'
EYR=json.loads(EY_RESULT.read_text());assert EYR['status']=='PASS_CURRENT_THREAD_FLS_CAEC20_ERROR_PROPAGATION' and EYR['next_source_RVA']=='0xcfd704' and not EYR['current_UTF16_owner_released']
CW_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011cw-original-file-thread-cleanup/RESULT.json'
CW_AUTH=ROOT/'experiments/E004-front-ir-vd55g0/e011cw-original-file-thread-cleanup/CODE-AUTHORITY-SAFE.json'
EJ_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ej-slot3-stream-object-native-front-correlation/RESULT.json'
EJ_SOURCE=ROOT/'experiments/E004-front-ir-vd55g0/e011ej-slot3-stream-object-native-front-correlation/SOURCE-SAFE.json'
CWR=json.loads(CW_RESULT.read_text());CWA=json.loads(CW_AUTH.read_text())
assert CWR['status']=='PASS_BOUNDED_ORIGINAL_FILE_ERROR_THREAD_JOIN_AND_CLEANUP' and CWR['original_error3_maps_to_OS3_CRT2'] and CWR['UTF16_owned74byte_owner_released']
assert CWA['thread_OS_error_offset']==36 and CWA['thread_CRT_error_offset']==32 and CWA['original_OS_error3_maps_to_CRT_error2']
assert hashlib.sha256(CW_AUTH.read_bytes()).hexdigest()=='bdc6a3b56f0f119082c52a2626ab98b5d01cefaf8f184788fa08885b09d7f516'
EJR=json.loads(EJ_RESULT.read_text());EJS=json.loads(EJ_SOURCE.read_text())
assert EJR['status']=='PASS_BOUNDED_ORIGINAL_SLOT3_STREAM_OBJECT_AND_NATIVE_FRONT_EXISTING_SLOT_CORRELATION' and EJR['source_runtime_CRT_image_flag']=='0x80000000'
assert EJS['source_runtime_CRT_image_flag_inherited_qualified'] and EJS['owned_object_contents_qualified'] and EJS['owned_resource_initialization_and_return_lock_qualified']
assert all(d['object_flag20']==0x2000 and d['object_field24']==0xffffffff and d['owned_resource_lock_held_on_return'] for d in EJS['details'])

sp=importlib.util.spec_from_file_location('em_ec',EC_PATH);EC=importlib.util.module_from_spec(sp);sp.loader.exec_module(EC)
EWR=json.loads(EW_RESULT.read_text()); assert EWR['status']=='PASS_SOURCE_EXACT_CREATEFILEW_FAILURE_TO_GETLASTERROR_FRONTIER' and EWR['next_source_RVA']=='0xcfd6fc' and not EWR['GetLastError_executed']
EWA=json.loads(EW_AUTH.read_text()); assert EWA['status']=='WINDOWS_REFERENCE_COMPLETE_PENDING_SOURCE_REPLAY' and EWA['same_boot_exact_OS_contract']['invalid_handle'] and EWA['same_boot_exact_OS_contract']['handle_signed']==-1 and EWA['same_boot_exact_OS_contract']['last_error']==3 and not EWA['live_debug_notes']['exact_source_callsite_breakpoint_observed']
EL=json.loads(EL_RESULT.read_text()); REFS=json.loads(EL_REFS.read_text()); EM=json.loads(EM_RESULT.read_text()); DY=json.loads(DY_SOURCE.read_text()); EN=json.loads(EN_RESULT.read_text()); WIN=json.loads(EO_WINDOWS_SAFE.read_text()); EO=json.loads(EO_RESULT.read_text()); EPWIN=json.loads(EP_WINDOWS.read_text()); EP=json.loads(EP_RESULT.read_text()); EQ=json.loads(EQ_RESULT.read_text()); APIQ=json.loads(EXACT_API.read_text()); CMR=json.loads(CM_RESULT.read_text()); CMB=json.loads(CM_BOOT.read_text()); APIO=json.loads(API_OUTPUT.read_text()); ES=json.loads(ES_RESULT.read_text()); ET=json.loads(ET_RESULT.read_text()); EU=json.loads(EU_RESULT.read_text()); EV=json.loads(EV_RESULT.read_text()); LIFE=json.loads(LOW_LIFE.read_text())
spcm=importlib.util.spec_from_file_location('eu_cm',CM_PATH);CM=importlib.util.module_from_spec(spcm);spcm.loader.exec_module(CM);_,CM_IMPORTS=CM.authority()
assert EL['status']=='PASS_JOINED_PARENT_MODE_PARSER_PREFIX'
assert EL['CFA2E0_mode_parser_return_qualified'] and EL['next_source_RVA']=='0xcfa9bc'
assert EL['next_call_target_RVA']=='0xcfd550' and not EL['deeper_CFD550_CFCC18_effects_qualified']
assert REFS['target_RVA']=='0x16a382c' and all(x['type']=='READ' for x in REFS['refs'])
assert EM['status']=='PASS_JOINED_CFD550_CFCC18_VALIDATION_PREFIX' and EM['next_source_RVA']=='0xcfcc98' and EM['next_call_target_RVA']=='0xcfd410'
AUTH={x['RVA']:x for x in DY['runtime_initial_value_model_authority']}
assert AUTH['0x16a2a84']['accepted_owned_initial_value']==0 and not AUTH['0x16a2a84']['native_runtime_selection_qualified']
assert AUTH['0x16072d8']['file_initial_sha256']=='507987659945beb7bcd11ae53dece55517a2979fc4e3ea4c9683bdceb5fd0f3f'
assert AUTH['0x16072d8']['initial_pointer_targets_RVA']==['0x1607180','0x1607650'] and not AUTH['0x16072d8']['native_runtime_selection_qualified']
assert EN['status']=='PASS_JOINED_CFD410_CB6520_PREFIX' and EN['next_source_RVA']=='0xcfd46c' and EN['next_dependency_RVA']=='0x160718c'
NATIVE=WIN['native_prestart_after_initialize_before_start']
assert NATIVE['runtime_flag_RVA']=='0x16a2a84' and NATIVE['runtime_flag_value_u32']==0
assert NATIVE['first_pointer_target_RVA']=='0x1607180' and NATIVE['selected_field_RVA']=='0x160718c' and NATIVE['selected_field_value_u32']==0
assert WIN['independent_KD_read_confirmed_selected_field_zero'] and not WIN['exact_CFD46C_instruction_breakpoint_observed']
assert NATIVE['second_pointer_not_file_static_0x1607650'] and NATIVE['global_pointer_0x16a2a88_not_file_static_0x1607180'] and not WIN['broad_file_initial_state_persistence_qualified']
assert EO['status']=='PASS_NATIVE_QUALIFIED_SELECTED_FIELD_ZERO_BRANCH' and EO['next_source_RVA']=='0xcfd498'
assert EPWIN['status']=='PASS_NATIVE_PRESTART_CALLBACK_STATE' and EPWIN['native_prestart_fptable_slot_populated']
assert EPWIN['native_prestart_fptable_target_matches_source_identified_callback'] and EPWIN['native_callback_return_u32']==1
assert EPWIN['native_callback_implementation_process_local_comparison_qualified'] and EPWIN['native_FrameServer_comparison_equal']
assert EP['status']=='PASS_NATIVE_QUALIFIED_CALLBACK_CACHE_BRANCH' and EP['next_source_RVA']=='0xcfd4e4' and EP['next_call_target_RVA']=='0xcb76b0'
assert EQ['status']=='PASS_CB76B0_CONVERSION_QUERY_PREFIX' and EQ['next_source_RVA']=='0xcb8dd0' and EQ['next_dependency_RVA']=='0xf7e2e8'
assert APIQ['status']=='PASS_EXACT_38BYTE_ORIGINAL_API_QUERY' and APIQ['input_bytes_including_NUL']==38 and APIQ['original_API_return_characters']==38 and APIQ['UTF16_bytes']==76
assert APIQ['input_sha256']=='cf8019b95989baec9a5e624ee52c5fb9732f092a41c3f68eee04edbbb5bd0146' and APIQ['source_codepage']==0 and APIQ['flags']==9
assert APIO['status']=='PASS_EXACT_38BYTE_ORIGINAL_API_OUTPUT' and APIO['input_sha256']==APIQ['input_sha256'] and APIO['output_bytes']==76 and APIO['output_characters']==38
assert not APIO['original_API_size_query'] and not APIO['original_size_or_conversion_result_stub']
assert CMR['status']=='PASS_BOUNDED_ORIGINAL_CRT_OBJECT_PRODUCERS' and CMB['authority']['process_heap_handle_global_RVA'].lower()=='0x16a3240'
assert 'GetProcessHeap owned opaque handle' in CMR['OS_contracts'] and 'HeapAlloc guarded zeroed aligned16 memory' in CMR['OS_contracts']
assert ES['status']=='PASS_EXACT_ALLOCATOR_OUTPUT_CONVERSION_RETURN' and ES['next_source_RVA']=='0xcfd4e8' and ES['next_parent_call_site_RVA']=='0xcfd514'
assert ET['status']=='PASS_POST_CONVERSION_CFD570_CALL_FRONTIER' and ET['next_source_RVA']=='0xcfd514' and not ET['CFD570_executed']
assert EV['status']=='PASS_JOINED_CC08E8_CREATEFILEW_FRONTIER' and EV['next_source_RVA']=='0xcfd658' and not EV['CreateFileW_executed']
assert EU['status']=='PASS_STARTUP_LOWIO_LIFETIME_JOIN_CFD570_PREFIX' and EU['next_source_RVA']=='0xcfd5e8' and not EU['CC08E8_executed']
assert LIFE['status']=='PASS_SOURCE_LOWIO_LIFETIME_TO_FIRST_CFD570_CALL' and LIFE['startup_lowIO_state_survives_to_joined_camera_frontier_under_owned_lifecycle_contract']

PINS={
 'ced150_prefix':(0xced150,40,'b75b47b09fe1ca8f817adc3fa7a0d2c68677d9a7ffeb114b28105ab81c79e107'),
 'cfa968_prefix':(0xcfa968,84,'755ef730439f971c72e1d9a660802309c270587d0809819d97aaef9cb31e585b'),
 'cfa2e0_body':(0xcfa2e0,572,'070aa336c2fc41e4a63ca94aa3940496ebd50e64d86d6a4a2ba3448521605ca7'),
 'cfd550_wrapper':(0xcfd550,32,'6753ebc03040f6e33599e13fce3985bc2a9baaf2b61d53ee3c004d1ad48d712f'),
 'cfcc18_prefix':(0xcfcc18,128,'98d2d102534288426b43734dc1049ac15596f0418fc6245ca950ba8a1b3c774b'),
 'cfd410_to_pointed_field_frontier':(0xcfd410,92,'a6e8a04d21a424fd31b63e8ca8609e3bfa78ea32bf6f30420b471815957b974e'),
 'cb6520_body':(0xcb6520,160,'663db5108d386bc5f9d14b5fdfaca9f9a5166dbfde19b498f8d99d054d1c9381'),
 'cfd46c_zero_field_branch':(0xcfd46c,44,'935bed6536b1e422108e988195f412c78652b11b4f5f1427c0bf12492d068158'),
 'cb9f68_callback_cache_helper':(0xcb9f68,96,'bcccce70775ee06c49deff53f1ebd475a949e303992537b81bc6a0d5bf113a73'),
 'cfg_nop':(0x1a8c0,4,'110f46b5b35c069160560c6ad6786f647dd44e8760a52a46fc22dbbcd7630b91'),
 'cfd498_native_callback_branch':(0xcfd498,80,'e4e1851f56a7171079a7a999579f0997af573bb19f23911fe5650987eda6287c'),
 'cb76b0_complete_conversion':(0xcb76b0,400,'5c60d8e0aae3e5fa7746ade2b6980b474205ffb456de104e651453d24ad7eac6'),
 'cb16c0_allocator':(0xcb16c0,156,'ccb3ae76b686072064c09317bd42691ba0447a13173d4647095ce46ee0c4f741'),
 'cfd4e8_to_cfd570_call':(0xcfd4e8,48,'4e22575edd58465838878cfda6919353728252a836f5b1c358976ac46272ac84'),
 'cfd570_to_lowio_call':(0xcfd570,124,'31725afb3bc6524054b5d7bd24ea9985045f42c0824d6fdf614ebb96b47b2367'),
 'cfd0b0_parser_prefix':(0xcfd0b0,64,'7cdf908405da8f2bf5066fc78d1a79ae3a36d3470a4ee54da40e82f05200a23f'),
 'cc08e8_record_claim':(0xcc08e8,336,'b459d880f69ef88c4113c88c7a0263d41d3eb32034e26b542e3e23c80d55ba04'),
 'cfd5e8_to_createfile':(0xcfd5e8,116,'aa03098bcff894b9a7dafb8495dabb6c1d07ba07508e15a36d4e4bffa3ef0353'),
 'cfd658_to_getlasterror_frontier':(0xcfd658,0xa4,'3e7507e0276365e81f71f835d70e9c3ddb515b06289f6425a7b8f1fe073417e0'),
 'cfd6f4_to_caec20_frontier':(0xcfd6f4,16,'191e4c617cee668e8148b2beff14800429d14302c070c17c8f73a5a6e5ad2bfc'),
 'cb8d88_codepage_dispatch_prefix':(0xcb8d88,72,'70ac927af0a3009ed041ac3a545c7f747c3470ca054940159629106dadde62eb'),
 'caec20_error_propagation':(0xcaec20,104,'49b469da15a36843771a041dbed824866d1a63fab369f31c8dcd926e837fe3d8'),
 'caeb48_error_map':(0xcaeb48,208,'28078ae44e1a7f3f1a010ed7ac8c2d768455b4594adc9ac1e9f155de7501efdd'),
 'cb41d0_thread_getter':(0xcb41d0,208,'630ce1896c115d70ec5b7ddd1d73da90357b1e18c048100c0cd42f0b0b131171'),
 'cba180_fls_dispatch':(0xcba180,12,'ce24ebab91a4d43f124b2aa77f011de4c2605593d51eb3d35df34ef8d14c5970'),
 'cfd704_branch':(0xcfd704,4,'0c21a75383c5c84661cb0ba1fdd2686b70d7cdb23e017e9ecb2d33e495993b15'),
 'cfd5dc_error_return':(0xcfd5dc,12,'849e7e2dd92812325c4c0752e489d93e32f82707ce1c8cea592043368bbc4377'),
 'caecf8_get_crt_error_ptr':(0xcaecf8,48,'6b41612413027b0b4b8256683c4dde51000a09db65befe011d7ae4137898ec76'),
 'cfd980_epilogue':(0xcfd980,32,'11b7ba645a358731cd93d26dac4d19420ab0d60ab7b9dce2970da4ba79e019b1'),
 'cfd518_parent_cleanup_prefix':(0xcfd518,0x34,'573b1261075911719a5294e987aa0c4fc9c4796ad071d1531b3f914e916a01af'),
 'cfd52c_parent_epilogue':(0xcfd52c,0x20,'5a1bdccde19caf7a5f2045f3d5f8dcded0dce37227e8a5c5dda4af20984a8199'),
 'cfcc98_call_return_site':(0xcfcc98,8,'54d18a6e5a232dc8bdb3395f28efe72d72bff6efc654af520fb0223758c0638d'),
 'cfcc9c_lowio_release_prefix':(0xcfcc9c,0x48,'a2d4cd31428c3bc75cab20db83b8a06203eb019c7af4b0111b0e6f48e0837d94'),
 'cc08c0_record_leave_wrapper':(0xcc08c0,0x28,'74a242228c5e957323c2ab2ce79f43f5139b4b7c59cd7a31c6e55877c381b01c'),
 'cfcce4_error_tail':(0xcfcce4,0x10,'53427232778ca6db96e34cb0970837b9c1929b1a946a9ccbe799a8c431fdae57'),
 'cfcc4c_epilogue':(0xcfcc4c,0x14,'ef7497dbd76063180fd49c0d52121277e05bd5f91357fa83288f516d83d9fc31'),
 'cfa9bc_call_return_site':(0xcfa9bc,8,'aec8ccb785066f1528514800d145bfdde381b6c2cb429503cedfb569dddd356f'),
 'cfa99c_error_epilogue':(0xcfa99c,0x70,'a269bb0f2a9c5414231b341ddc0cd87e3b3cf85974002001000663a6daae8f45'),
 'ced178_cleanup_frontier':(0xced178,0x14,'0491a5bb7241e05aee1fdcbb9bc500e336a4d8dc544edb8249a18e33c5a4b6b5'),
 'cc60e0_selected_cleanup':(0xcc60e0,0x24,'04665a3f0f31bf3e8ef04241ab41d0eca1fcbc5d8ff887b5c1a6d94b8903daf3'),
 'atomic_exchange_fallback':(0x12d0,0x2c,'a00c1cd4ab861384e3948714dfca8ab422d8c960798199b1ddbdc2e2d3103a47'),
 'ced18c_release_frontier':(0xced18c,0x0c,'335fed31a55d8405235b52834d5b8d1edf1d013d0435f2e7dee16e4f5fe8cfe8'),
 'cb3480_leave_wrapper':(0xcb3480,0x10,'833bc6a86ea0a3739a5bec70eee7290dad5683ab40e36ac81eb141dd3580bb61'),
 'ced194_zero_result_branch':(0xced194,8,'22f1f76ccc6db9e41ac142dfeda0102c6d9e0b9fe56fbae2a234cd796ed6f422'),
 'ced110_epilogue':(0xced110,0x14,'ef7497dbd76063180fd49c0d52121277e05bd5f91357fa83288f516d83d9fc31'),
 'ced330_caller_frontier':(0xced330,8,'530d1d30f2178c11fe7d45935277aff2d7cbb2c8dd7e96c1a2f608aabc8ec21d'),
 'cb1650_free_wrapper':(0xcb1650,0x60,'791d78b8cb56ad9d29749ab08270ed56583998fee4b4e5f9e8ea2e1397841047'),
}
for _,(r,z,h) in PINS.items(): assert hashlib.sha256(EC.PE.get_data(r,z)).hexdigest()==h
EC.PE.parse_data_directories(); _imports={i.name.decode():i.address-EC.PE.OPTIONAL_HEADER.ImageBase for d in EC.PE.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}; assert _imports['CreateFileW']==0xf7e3b8 and _imports['GetLastError']==0xf7e468

GLOBAL_RVA=0x16a382c
sec=next(s for s in EC.PE.sections if s.VirtualAddress<=GLOBAL_RVA<s.VirtualAddress+s.Misc_VirtualSize)
off=GLOBAL_RVA-sec.VirtualAddress
assert sec.Characteristics&0x80000000 and off+4>sec.SizeOfRawData
MODE_RVA=EC.MODE_RVA
assert hashlib.sha256(EC.MODE).hexdigest()==EC.MODE_AUTH['sha256'] and len(EC.MODE)==2 and EC.MODE[-1]==0

def reject(fn,cases):
 n=0
 for x in cases:
  try:fn(*x)
  except AssertionError:n+=1
  else:raise AssertionError(('altered accepted',fn.__name__,x))
 return n
def eq(got,want): assert got==want

def validate_lowio_join(ptr,count,block_sha,lifetime_ok,expected_ptr,expected_sha):
 assert lifetime_ok and ptr==expected_ptr and ptr!=0 and count==64 and block_sha==expected_sha

def validate_current_cleanup(flag,ptr,size,sha,expected_ptr,expected_sha,old_geometry_reused):
 assert flag==1 and ptr==expected_ptr and ptr!=0 and size==76 and sha==expected_sha and not old_geometry_reused

def validate_thread_join(ptr,next_alloc,size,sha,slot,flag,global_slot,getter_cell,getter,x18,teb,old_cleanup_reused):
 assert ptr==next_alloc and ptr!=0 and size==968 and sha=='82cb660ea695ecf98f75078812709ec115e7d6cbe77b1bab548700bd074d999a'
 assert slot in (1,16,37,63) and flag==1 and global_slot==slot and getter_cell==getter and getter!=0 and x18==teb and teb!=0
 assert not old_cleanup_reused

def one_case(sel_bias):
 c=EC.Case(0,0,0x80000000,0,0,0,0xa5);c.run();u=c.u;n=c.n
 assert [f['entry'] for f in c.ec_frames]==[0xced2f0,0xced0d8,0xcc6078,0xcc6108]
 # Join already-qualified E011EJ/E011EK return state, then replay original E011EL path.
 child=c.ec_frames.pop()
 for r,v in child['saved'].items():u.reg_write(r,v)
 cc6078=c.ec_frames.pop()
 for r,v in cc6078['saved'].items():u.reg_write(r,v)
 assert [f['entry'] for f in c.ec_frames]==[0xced2f0,0xced0d8]
 c.ec_lock_held=False
 selected=0x93001000+((sel_bias+15)&~15)
 u.mem_map(0x93000000,0x10000);u.mem_write(0x93000000,b'\xa5'*0x10000);u.mem_write(selected,b'\0'*88)
 u.mem_write(selected+20,struct.pack('<I',0x2000));u.mem_write(selected+24,struct.pack('<I',0xffffffff))
 selected_lock_held=True
 runtime_atomic_flag=n.base+0x1607b00
 assert int.from_bytes(u.mem_read(runtime_atomic_flag,4),'little')==0
 u.mem_write(runtime_atomic_flag,struct.pack('<I',0x80000000)) # source-qualified E011EJ/CN process-runtime handoff, not native replay
 assert int.from_bytes(u.mem_read(runtime_atomic_flag,4),'little')==0x80000000
 callback_page=0x94000000; callback_target=callback_page+0x100; os_query_target=callback_page+0x200; heap_alloc_target=callback_page+0x300; createfile_target=callback_page+0x400; getlasterror_target=callback_page+0x500; heap_free_target=callback_page+0x600
 u.mem_map(callback_page,0x1000);u.mem_write(callback_page,b'\xa7'*0x1000)
 owned_heap=0x95000000; owned_heap_size=0x10000; heap_handle=owned_heap+0x100; utf_output=owned_heap+0x2000+((sel_bias+15)&~15)
 u.mem_map(owned_heap,owned_heap_size);u.mem_write(owned_heap,b'\xa9'*owned_heap_size)
 fptable_slot=n.base+0x1b60000
 assert int.from_bytes(u.mem_read(fptable_slot,8),'little')==0
 u.mem_write(fptable_slot,struct.pack('<Q',callback_target))
 u.mem_write(n.base+0xf7e2e8,struct.pack('<Q',os_query_target))
 u.mem_write(n.base+0x16a3240,struct.pack('<Q',heap_handle));u.mem_write(n.base+0xf7e280,struct.pack('<Q',heap_alloc_target));u.mem_write(n.base+0xf7e278,struct.pack('<Q',heap_free_target));u.mem_write(n.base+0xf7e3b8,struct.pack('<Q',createfile_target));u.mem_write(n.base+0xf7e468,struct.pack('<Q',getlasterror_target))
 assert int.from_bytes(u.mem_read(n.base+0xf7e7b8,8),'little')==n.base+0x1a8c0
 # Join only the source-qualified process-attach lowIO producer state whose teardown is outside the accepted live-camera interval.
 boot=CM.Bootstrap(sel_bias,0,CM_IMPORTS);boot.run();assert boot.allocs[0][1]==64*72
 low_ptr=boot.allocs[0][0];low_block=bytes(boot.u.mem_read(low_ptr,64*72));low_sha=hashlib.sha256(low_block).hexdigest()
 assert int.from_bytes(boot.u.mem_read(boot.n.base+0x16a2a90,8),'little')==low_ptr and int.from_bytes(boot.u.mem_read(boot.n.base+0x16a2e90,4),'little')==64
 assert boot.global_mutex(7) in boot.lock_objects and all(low_ptr+72*k in boot.lock_objects for k in range(64)) and not any(boot.depths.values())
 low_global7=n.base+0x16a2fd8; low_record0=low_ptr; low_depths={low_global7:0,low_record0:0}
 assert boot.global_mutex(7)-boot.n.base==0x16a2fd8
 u.mem_map(boot.own,boot.extent);u.mem_write(boot.own,b'\xa5'*boot.extent);u.mem_write(low_ptr,low_block)
 u.mem_write(n.base+0x16a2a90,struct.pack('<Q',low_ptr));u.mem_write(n.base+0x16a2e90,struct.pack('<I',64))
 validate_lowio_join(low_ptr,64,low_sha,True,low_ptr,low_sha)
 # Join the independently source-qualified CRT/FLS slot+thread producer into the current camera process model.
 slot_axes={0:1,1:16,40:37,1230:63};slot=slot_axes[sel_bias]
 cv_case=CV.Case(sel_bias,slot,3,4);cv_detail=cv_case.run()
 assert cv_detail['original_published_getter_returns_exact_968_byte_owner'] and cv_detail['original_error_restore_preserves_input']
 assert cv_detail['thread_allocation_bytes']==968 and cv_detail['fresh_slot_owned_fixture']==slot and cv_detail['initial_thread_error_fixture']==3
 thread_ptr=cv_case.thread;thread_bytes=bytes(cv_case.u.mem_read(thread_ptr,968));thread_sha=hashlib.sha256(thread_bytes).hexdigest()
 assert thread_sha=='82cb660ea695ecf98f75078812709ec115e7d6cbe77b1bab548700bd074d999a'
 thread_page=thread_ptr&~0xfff;assert thread_ptr==boot.next_alloc and bytes(u.mem_read(thread_ptr-32,1032))==b'\xa5'*1032
 u.mem_write(thread_ptr,thread_bytes);boot.allocs.append((thread_ptr,968));boot.next_alloc=(thread_ptr+968+64+4095)&~4095
 teb=cv_case.teb;fls_data=cv_case.data;fls_slab=cv_case.slab;getter=cv_case.getter
 for at in (teb,fls_data,fls_slab):
  u.mem_map(at,8192,CV.UC_PROT_READ|CV.UC_PROT_WRITE);u.mem_write(at,bytes(cv_case.u.mem_read(at,8192)))
 getter_page=getter&~0xfff;u.mem_map(getter_page,0x1000,CV.UC_PROT_READ|CV.UC_PROT_EXEC);u.mem_write(getter_page,bytes(cv_case.u.mem_read(getter_page,0x1000)))
 u.mem_write(n.base+0x16a2a80,b'\x01');u.mem_write(n.base+0x1607168,struct.pack('<I',slot));u.mem_write(n.base+0x1b60018,struct.pack('<Q',getter))
 u.reg_write(UC_ARM64_REG_X18,teb)
 assert int.from_bytes(u.mem_read(n.base+0x1607168,4),'little')==slot and int.from_bytes(u.mem_read(n.base+0x1b60018,8),'little')==getter
 assert int.from_bytes(u.mem_read(teb+0x68,4),'little')==3
 result_slot=c.dw_entry_sp-1536
 u.mem_write(result_slot,struct.pack('<Q',selected))
 u.reg_write(UC_ARM64_REG_X0,result_slot);u.reg_write(UC_ARM64_REG_PC,n.base+0xced150);u.reg_write(UC_ARM64_REG_LR,n.base+0xced150)

 assert int.from_bytes(u.mem_read(n.base+GLOBAL_RVA,4),'little')==0
 assert hashlib.sha256(bytes(u.mem_read(n.base+MODE_RVA,2))).hexdigest()==EC.MODE_AUTH['sha256']
 before_image=bytes(u.mem_read(n.base,EC.PE.OPTIONAL_HEADER.SizeOfImage))
 before_selected=bytes(u.mem_read(selected,88))
 before_output=bytes(u.mem_read(c.dw_entry_sp-1392,640))
 before_owned_heap=bytes(u.mem_read(owned_heap,owned_heap_size))
 before_lowio=bytes(u.mem_read(low_ptr,64*72))
 before_stack=bytes(u.mem_read(n.stack,65536));before_thread=bytes(u.mem_read(thread_page,0x1000));before_teb=bytes(u.mem_read(teb,8192));before_fls_data=bytes(u.mem_read(fls_data,8192));before_fls_slab=bytes(u.mem_read(fls_slab,8192))
 expected_thread=bytearray(before_thread);native_getter_reads=[];ey_state={'stack_before':None,'stack_model':None}

 calls=[];reads=[];mode_reads=[];keywrites=[];en_reads=[];en_writes=[];pointed_reads=[];callback_reads=[];cfg_reads=[];conversion_iat_reads=[];heap_reads=[];lowio_api_events=[];lowio_writes=[];neg=0;parser_saved=None;cfd_saved=None;cfd570_saved=None;cb_saved=None;cb9_saved=None;allocator_saved=None;callback_invocations=0;callback_returns=0;os_query_calls=0;os_output_calls=0;heap_calls=0;heap_free_calls=0;createfile_calls=0;getlasterror_calls=0;thread_getter_entries=0;thread_getter_returns=0;thread_calls=0;native_getter_instructions=0;ey_source_visits=0;ey_pending={};ey_writes=[];fi_writes=[];stop={'hit':False}
 ey_ranges=((0xcaec20,0xcaec88),(0xcaeb48,0xcaec18),(0xcb41d0,0xcb42a0),(0xcba180,0xcba18c),(0xcfd704,0xcfd708),(0xcfd5dc,0xcfd5e8),(0xcaecf8,0xcaed28),(0xcfd980,0xcfd9a0))
 owner={'live':True,'released':False};fa_pending={};fa_writes=[];fc_pending={};fc_writes=[];fc_reads=[];fd_pending={};fd_writes=[];ff_writes=[];ff_reads=[];cfcc_saved=None
 def in_ey_source(r):return any(lo<=r<hi for lo,hi in ey_ranges)
 def rr(uu,name):return EC.DR.reg(uu,name)
 neg+=reject(validate_lowio_join,[(low_ptr+8,64,low_sha,True,low_ptr,low_sha),(low_ptr,63,low_sha,True,low_ptr,low_sha),(low_ptr,64,'0'*64,True,low_ptr,low_sha),(low_ptr,64,low_sha,False,low_ptr,low_sha),(0,64,low_sha,True,low_ptr,low_sha),(low_ptr,64,low_sha,True,low_ptr+8,low_sha)])
 tj=(thread_ptr,thread_ptr,968,thread_sha,slot,1,slot,getter,getter,teb,teb,False)
 neg+=reject(validate_thread_join,[
  (thread_ptr+16,*tj[1:]),(thread_ptr,thread_ptr+16,*tj[2:]),(thread_ptr,thread_ptr,960,*tj[3:]),
  (thread_ptr,thread_ptr,968,'0'*64,*tj[4:]),(thread_ptr,thread_ptr,968,thread_sha,0,*tj[5:]),
  (thread_ptr,thread_ptr,968,thread_sha,slot,0,*tj[6:]),(thread_ptr,thread_ptr,968,thread_sha,slot,1,slot+1,*tj[7:]),
  (thread_ptr,thread_ptr,968,thread_sha,slot,1,slot,getter+8,getter,teb,teb,False),
  (thread_ptr,thread_ptr,968,thread_sha,slot,1,slot,getter,getter,teb,teb,True)])
 validate_thread_join(*tj)
 expected_en_writes=[
  (0xcfd430,-1800,8,0),(0xcfd430,-1792,8,0),
  (0xcfd438,-1784,8,0),(0xcfd438,-1776,8,0),
  (0xcfd440,-1768,8,0),(0xcfd448,-1760,1,0),
  (0xcb6534,-1808,1,0),
  (0xcb655c,-1824,8,n.base+0x1607180),(0xcb655c,-1816,8,n.base+0x1607650),
 ]
 expected_keywrites=[
   (0xcfa9a8,-1600,4,0),
   (0xcfcc30,-1656,8,c.dw_entry_sp-1600),
   (0xcfcc64,-1600,4,0xffffffff),
   (0xcfcc78,-1664,4,0),
   (0xcfcc78,-1660,4,0),
 ]
 def check_args(got,want,bads):
  nonlocal neg
  eq(got,want); neg+=reject(eq,[(x,want) for x in bads])

 def code(uu,pc,z,_):
  nonlocal neg,parser_saved,cfd_saved,cfd570_saved,cb_saved,cb9_saved,allocator_saved,callback_invocations,callback_returns,os_query_calls,os_output_calls,heap_calls,heap_free_calls,createfile_calls,getlasterror_calls,thread_getter_entries,cfcc_saved,thread_getter_returns,thread_calls,native_getter_instructions,ey_source_visits,selected_lock_held
  assert not ey_pending,('pending EY store before next instruction',ey_pending);assert not fa_pending,('pending FA store before next instruction',fa_pending)
  if pc in (c.apis['EnterCriticalSection'],c.apis['LeaveCriticalSection']):
   name='EnterCriticalSection' if pc==c.apis['EnterCriticalSection'] else 'LeaveCriticalSection';recv=uu.reg_read(UC_ARM64_REG_X0);ret=uu.reg_read(UC_ARM64_REG_LR);spv=uu.reg_read(UC_ARM64_REG_SP)
   k=len(lowio_api_events); expected=[('EnterCriticalSection',low_global7,n.base+0xcc090c,c.dw_entry_sp-2192),('EnterCriticalSection',low_record0,n.base+0xcc09cc,c.dw_entry_sp-2192),('LeaveCriticalSection',low_global7,n.base+0xcc0978,c.dw_entry_sp-2192),('LeaveCriticalSection',low_record0,n.base+0xcfcce4,c.dw_entry_sp-1680),('LeaveCriticalSection',selected+48,n.base+0xced194,c.dw_entry_sp-1552)][k]
   got=(name,recv,ret,spv);eq(got,expected)
   neg+=reject(eq,[((name,recv+8,ret,spv),expected),((name,recv,ret+4,spv),expected),((name,recv,ret,spv+16),expected),(('LeaveCriticalSection' if name=='EnterCriticalSection' else 'EnterCriticalSection',recv,ret,spv),expected)])
   if k<4:
    assert recv in low_depths
    if name=='EnterCriticalSection': assert low_depths[recv]==0;low_depths[recv]=1
    else: assert low_depths[recv]==1;low_depths[recv]=0
    label='LOWIO_'+name.upper()+('_GLOBAL7' if recv==low_global7 else '_RECORD0')
   else:
    assert name=='LeaveCriticalSection' and recv==selected+48 and selected_lock_held and owner['released'] and not owner['live']
    selected_lock_held=False;label='SELECTED_LEAVECRITICALSECTION_LOCK_RELEASED'
   saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};uu.reg_write(UC_ARM64_REG_X0,c.api_clobber);uu.reg_write(UC_ARM64_REG_PC,ret);assert all(uu.reg_read(reg)==v for reg,v in saved.items())
   lowio_api_events.append(got);calls.append(label);return
  if pc==heap_free_target:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_W1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP),owner['live'])
   want=(heap_handle,0,utf_output,n.base+0xcb1680,c.dw_entry_sp-1888,True);eq(got,want)
   assert hashlib.sha256(bytes(uu.mem_read(utf_output,76))).hexdigest()==APIO['output_sha256']
   neg+=reject(eq,[((got[0]+8,*got[1:]),want),((got[0],1,*got[2:]),want),((got[0],got[1],got[2]+2,*got[3:]),want),((got[0],got[1],got[2],got[3]+4,got[4],True),want),((got[0],got[1],got[2],got[3],got[4]+16,True),want),((*got[:5],False),want)])
   saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};owner['live']=False;owner['released']=True;uu.reg_write(UC_ARM64_REG_W0,1);uu.reg_write(UC_ARM64_REG_PC,got[3]);assert all(uu.reg_read(reg)==v for reg,v in saved.items())
   heap_free_calls+=1;calls.append('OWNED_HEAPFREE:RETURN_SUCCESS_CURRENT_76');return
  if pc==heap_alloc_target:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_W1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP),True)
   want=(heap_handle,0,76,n.base+0xcb1700,c.dw_entry_sp-1968,True);eq(got,want)
   neg+=reject(eq,[((got[0]+8,*got[1:]),want),((got[0],1,*got[2:]),want),((got[0],got[1],78,*got[3:]),want),((got[0],got[1],got[2],got[3]+4,got[4],True),want),((got[0],got[1],got[2],got[3],got[4]+16,True),want),((*got[:5],False),want)])
   assert bytes(uu.mem_read(utf_output-32,108))==b'\xa9'*108
   saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};uu.reg_write(UC_ARM64_REG_X0,utf_output);uu.reg_write(UC_ARM64_REG_PC,got[3]);assert all(uu.reg_read(reg)==v for reg,v in saved.items())
   heap_calls+=1;calls.append('OWNED_HEAPALLOC:RETURN_76');return
  if pc==os_query_target:
   got=(uu.reg_read(UC_ARM64_REG_W0),uu.reg_read(UC_ARM64_REG_W1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_W3),uu.reg_read(UC_ARM64_REG_X4),uu.reg_read(UC_ARM64_REG_W5),uu.reg_read(UC_ARM64_REG_LR),True)
   if got[6]==n.base+0xcb7788:
    want=(0,9,c.dw_entry_sp-1392,0xffffffff,0,0,n.base+0xcb7788,True);eq(got,want)
    bad=[]
    for k in range(6):
     x=list(got);x[k]=(x[k]+1)&(0xffffffffffffffff if k in (2,4) else 0xffffffff);bad.append((tuple(x),want))
    bad.extend([((*got[:6],got[6]+4,True),want),((*got[:7],False),want)]);neg+=reject(eq,bad)
    saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};uu.reg_write(UC_ARM64_REG_W0,APIQ['original_API_return_characters']);uu.reg_write(UC_ARM64_REG_PC,got[6]);assert all(uu.reg_read(reg)==v for reg,v in saved.items())
    os_query_calls+=1;calls.append('ORIGINAL_API_CONTRACT:QUERY_RETURN_38');return
   want=(0,9,c.dw_entry_sp-1392,0xffffffff,utf_output,38,n.base+0xcb7824,True);eq(got,want);assert heap_calls==1
   bad=[]
   for k in range(6):
    x=list(got);x[k]=(x[k]+1)&(0xffffffffffffffff if k in (2,4) else 0xffffffff);bad.append((tuple(x),want))
   bad.extend([((*got[:6],got[6]+4,True),want),((*got[:7],False),want)]);neg+=reject(eq,bad)
   data=bytes(uu.mem_read(c.dw_entry_sp-1392,38));wide=data.decode('utf-8').encode('utf-16-le');assert len(wide)==76 and hashlib.sha256(wide).hexdigest()==APIO['output_sha256']
   assert bytes(uu.mem_read(utf_output,76))==b'\xa9'*76;uu.mem_write(utf_output,wide)
   saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};uu.reg_write(UC_ARM64_REG_W0,APIO['original_API_return_characters']);uu.reg_write(UC_ARM64_REG_PC,got[6]);assert all(uu.reg_read(reg)==v for reg,v in saved.items())
   os_output_calls+=1;calls.append('ORIGINAL_API_CONTRACT:OUTPUT_RETURN_38');return
  if pc==createfile_target:
   sec=uu.reg_read(UC_ARM64_REG_X3)
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_W1),uu.reg_read(UC_ARM64_REG_W2),sec,uu.reg_read(UC_ARM64_REG_W4),uu.reg_read(UC_ARM64_REG_W5),uu.reg_read(UC_ARM64_REG_X6),uu.reg_read(UC_ARM64_REG_LR),True)
   want=(utf_output,0x80000000,1,c.dw_entry_sp-2000,3,128,0,n.base+0xcfd65c,True);eq(got,want)
   assert bytes(uu.mem_read(sec,24))==struct.pack('<QQII',24,0,1,0)
   assert EWA['source_exact_CreateFileW']['path']=='C:\\data\\test\\camxoverridesettings.txt' and EWA['same_boot_filesystem']=={'file_exists':False,'parent_directory_exists':False}
   neg+=reject(eq,[((got[0]+2,*got[1:]),want),((got[0],0,*got[2:]),want),((got[0],got[1],0,*got[3:]),want),((got[0],got[1],got[2],got[3]+8,*got[4:]),want),((*got[:4],2,*got[5:]),want),((*got[:5],0,*got[6:]),want),((*got[:6],1,*got[7:]),want),((*got[:7],got[7]+4,True),want),((*got[:8],False),want)])
   saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};uu.reg_write(UC_ARM64_REG_X0,0xffffffffffffffff);uu.reg_write(UC_ARM64_REG_PC,got[7]);assert all(uu.reg_read(reg)==v for reg,v in saved.items())
   createfile_calls+=1;calls.append('WINDOWS_OS_CONTRACT:CREATEFILEW_INVALID_HANDLE_ERROR_PATH_NOT_FOUND');return
  if pc==getlasterror_target:
   got=(uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP),EWA['same_boot_exact_OS_contract']['last_error'],True)
   want=(n.base+0xcfd700,c.dw_entry_sp-2096,3,True);eq(got,want)
   neg+=reject(eq,[((got[0]+4,got[1],got[2],True),want),((got[0],got[1]+16,got[2],True),want),((got[0],got[1],2,True),want),((got[0],got[1],got[2],False),want)])
   saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};uu.reg_write(UC_ARM64_REG_W0,3);uu.reg_write(UC_ARM64_REG_PC,got[0]);assert all(uu.reg_read(reg)==v for reg,v in saved.items())
   getlasterror_calls+=1;calls.append('WINDOWS_OS_CONTRACT:GETLASTERROR_RETURN_3');return
  if pc==callback_target:
   got=(pc,uu.reg_read(UC_ARM64_REG_LR),EPWIN['native_callback_return_u32'],True);want=(callback_target,n.base+0xcb9fb4,1,True);eq(got,want)
   neg+=reject(eq,[((pc+4,got[1],got[2],True),want),((pc,got[1]+4,got[2],True),want),((pc,got[1],0,True),want),((pc,got[1],got[2],False),want)])
   saved={reg:uu.reg_read(reg) for reg in EC.NONVOL}
   uu.reg_write(UC_ARM64_REG_W0,1);uu.reg_write(UC_ARM64_REG_PC,got[1])
   assert all(uu.reg_read(reg)==v for reg,v in saved.items())
   callback_invocations+=1;calls.append('NATIVE_CALLBACK:RETURN_1');return
  if getter<=pc<getter+0x80:
   native_getter_instructions+=1
  if pc==getter:
   assert uu.reg_read(UC_ARM64_REG_W0)==slot and uu.reg_read(UC_ARM64_REG_X18)==teb and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcb4210
   thread_getter_entries+=1;calls.append('NATIVE_FLS_GETTER:ENTRY');
  r=pc-n.base
  if in_ey_source(r):
   ey_source_visits+=1
   raw=EC.PE.get_data(r,4);assert bytes(uu.mem_read(pc,4))==raw
   ins=list(EC.C.disasm(raw,r));assert len(ins)==1;i=ins[0]
   if i.mnemonic.startswith(('stp','str','stur')):
    mem=next(op.mem for op in i.operands if op.type==3);assert not mem.index
    at=rr(uu,EC.C.reg_name(mem.base))+mem.disp
    ops=i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
    for k,op in enumerate(ops):
     name=EC.C.reg_name(op.reg);width=16 if name.startswith('q') else 8 if name in ('fp','lr') or name.startswith(('x','d')) else 2 if i.mnemonic.endswith('h') else 1 if i.mnemonic.endswith('b') else 4
     value=rr(uu,name)&((1<<(width*8))-1);address=at+k*width
     for j in range(0,width,8):
      size=min(8,width-j);ey_pending[address+j,size]=(value>>(8*j))&((1<<(8*size))-1)
  if r==0xced174:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3))
   want=(c.dw_entry_sp-1392,n.base+MODE_RVA,128,selected)
   check_args(got,want,[(got[0]+8,*got[1:]),(got[0],got[1]+1,got[2],got[3]),(got[0],got[1],127,got[3]),(got[0],got[1],got[2],got[3]+8),(0,*got[1:])])
   calls.append('CED174:CFA968')
  elif r==0xcfa2e0:
   assert uu.reg_read(UC_ARM64_REG_X0)==n.base+MODE_RVA and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfa990
   parser_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};calls.append('CFA98C:CFA2E0')
  elif r==0xcfa990:
   assert parser_saved is not None
   assert uu.reg_read(UC_ARM64_REG_X0)==0x100000000 and (uu.reg_read(UC_ARM64_REG_X1)&0xffffffff)==1
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1616
   assert all(uu.reg_read(reg)==v for reg,v in parser_saved.items())
  elif r==0xcfa9bc:
   local=c.dw_entry_sp-1600
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4)&0xffffffff)
   want=(local,c.dw_entry_sp-1392,0,128,384)
   check_args(got,want,[(got[0]+4,*got[1:]),(got[0],got[1]+8,*got[2:]),(got[0],got[1],1,got[3],got[4]),(got[0],got[1],got[2],127,got[4]),(got[0],got[1],got[2],got[3],385)])
   calls.append('CFA9BC:CFD550')
  elif r==0xcfd550:
   local=c.dw_entry_sp-1600
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4)&0xffffffff)
   want=(local,c.dw_entry_sp-1392,0,128,384)
   check_args(got,want,[(got[0]+8,*got[1:]),(got[0],got[1]+1,*got[2:]),(got[0],got[1],2,got[3],got[4]),(got[0],got[1],got[2],129,got[4]),(got[0],got[1],got[2],got[3],383)])
   calls.append('CFD550:TAIL_CFCC18')
  elif r==0xcfcc18:
   local=c.dw_entry_sp-1600;cfcc_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL}
   link=(uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP));link_want=(n.base+0xcfa9c0,c.dw_entry_sp-1616);eq(link,link_want)
   neg+=reject(eq,[((link[0]+4,link[1]),link_want),((link[0],link[1]+16),link_want)])
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1)&0xffffffff,uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4),uu.reg_read(UC_ARM64_REG_X5)&0xffffffff)
   want=(c.dw_entry_sp-1392,0,128,384,local,1)
   check_args(got,want,[(got[0]+8,*got[1:]),(got[0],1,*got[2:]),(got[0],got[1],127,*got[3:]),(got[0],got[1],got[2],385,got[4],got[5]),(got[0],got[1],got[2],got[3],got[4]+4,got[5])])
   calls.append('CFCC18:VALIDATION_PREFIX')
  elif r==0xcfcc98:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4)&0xffffffff,uu.reg_read(UC_ARM64_REG_X5)&0xffffffff,uu.reg_read(UC_ARM64_REG_X6)&0xffffffff)
   want=(c.dw_entry_sp-1664,c.dw_entry_sp-1600,c.dw_entry_sp-1392,0,128,384,1)
   check_args(got,want,[(got[0]+4,*got[1:]),(got[0],got[1]+4,*got[2:]),(got[0],got[1],got[2]+8,*got[3:]),(got[0],got[1],got[2],1,*got[4:]),(got[0],got[1],got[2],got[3],got[4],got[5],0)])
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1600,4),'little')==0xffffffff
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1664,8),'little')==0
   assert selected_lock_held and not c.ec_lock_held
   calls.append('CFCC98:CFD410')
  elif r==0xcfd410:
   cfd_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL}
   got=(uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP));want=(n.base+0xcfcc9c,c.dw_entry_sp-1680);eq(got,want)
   neg+=reject(eq,[((got[0]+4,got[1]),want),((got[0],got[1]+16),want)])
   calls.append('CFD410:ENTRY_RETURN_LINK_CFCC9C')
  elif r==0xcb6520:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_LR))
   want=(c.dw_entry_sp-1832,0,c.dw_entry_sp-1856,n.base+0xcfd464)
   check_args(got,want,[(got[0]+8,*got[1:]),(got[0],1,*got[2:]),(got[0],got[1],got[2]+16,got[3]),(got[0],got[1],got[2],got[3]+4)])
   cb_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};calls.append('CFD460:CB6520')
  elif r==0xcfd464:
   assert cb_saved is not None and all(uu.reg_read(reg)==v for reg,v in cb_saved.items())
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856 and uu.reg_read(UC_ARM64_REG_X0)==c.dw_entry_sp-1832
   calls.append('CB6520:RETURN')
  elif r==0xcfd46c:
   assert cfd_saved is not None and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856
   assert uu.reg_read(UC_ARM64_REG_X8)==n.base+0x1607180 and (uu.reg_read(UC_ARM64_REG_W9)&0xffffffff)==0xfde9
   calls.append('CFD46C:NATIVE_QUALIFIED_SELECTED_FIELD_READ')
  elif r==0xcfd470:
   assert pointed_reads==[(0xcfd46c,0x160718c,4,0)]
   assert (uu.reg_read(UC_ARM64_REG_W8)&0xffffffff)==0 and (uu.reg_read(UC_ARM64_REG_W9)&0xffffffff)==0xfde9
   calls.append('CFD470:ZERO_FIELD_COMPARE')
  elif r==0xcfd498:
   assert pointed_reads==[(0xcfd46c,0x160718c,4,0)] and selected_lock_held and not c.ec_lock_held
   calls.append('CFD498:CB9F68_CALL')
  elif r==0xcb9f68:
   assert uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfd49c and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856
   cb9_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};calls.append('CB9F68:ENTRY_POPULATED_SLOT')
  elif r==0xf5d430:
   assert uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcb9fb0 and uu.reg_read(UC_ARM64_REG_X15)==callback_target
   calls.append('CB9FAC:CFG_CHECK')
  elif r==0x1a8c0:
   assert uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcb9fb0
   calls.append('CFG:NOP_RETURN')
  elif r==0xcb9fb4:
   assert uu.reg_read(UC_ARM64_REG_W0)==1 and callback_invocations==1
   callback_returns+=1;calls.append('CB9FB4:CALLBACK_RETURN_1')
  elif r==0xcfd49c:
   assert cb9_saved is not None and all(uu.reg_read(reg)==v for reg,v in cb9_saved.items())
   assert uu.reg_read(UC_ARM64_REG_W0)==1 and callback_returns==1
   calls.append('CB9F68:RETURN_NATIVE_1')
  elif r==0xcfd4c0:
   assert uu.reg_read(UC_ARM64_REG_W0)==1 and (uu.reg_read(UC_ARM64_REG_W8)&0xff)==0
   calls.append('CFD4C0:NATIVE_RESULT_ONE_BRANCH')
  elif r==0xcfd4d4:
   assert (uu.reg_read(UC_ARM64_REG_W8)&0xff)==0
   calls.append('CFD4D4:SELECT_MODE_ZERO')
  elif r==0xcfd4e4:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_W3))
   want=(c.dw_entry_sp-1392,c.dw_entry_sp-1800,c.dw_entry_sp-1840,0);eq(got,want)
   neg+=reject(eq,[((got[0]+8,*got[1:]),want),((got[0],got[1]+8,got[2],got[3]),want),((got[0],got[1],got[2]+8,got[3]),want),((got[0],got[1],got[2],1),want)])
   calls.append('CFD4E4:CB76B0_CALL')
  elif r==0xcb76b0:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_W3),uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP))
   want=(c.dw_entry_sp-1392,c.dw_entry_sp-1800,c.dw_entry_sp-1840,0,n.base+0xcfd4e8,c.dw_entry_sp-1856);eq(got,want)
   assert bytes(uu.mem_read(got[0],37))==before_output[:37] and all(before_output[:37]) and before_output[37:]==bytes(len(before_output)-37)
   calls.append('CB76B0:ENTRY_NONEMPTY_SOURCE')
  elif r==0xcb76fc:
   assert uu.reg_read(UC_ARM64_REG_X21)==c.dw_entry_sp-1392 and uu.reg_read(UC_ARM64_REG_X19)==c.dw_entry_sp-1800 and (uu.reg_read(UC_ARM64_REG_W20)&0xffffffff)==0
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1392,1),'little')!=0
   calls.append('CB76FC:NONEMPTY_INPUT')
  elif r==0xcb776c:
   calls.append('CB776C:CONVERSION_QUERY_SETUP')
  elif r==0xcb7784:
   got=(uu.reg_read(UC_ARM64_REG_W0),uu.reg_read(UC_ARM64_REG_W1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_W3),uu.reg_read(UC_ARM64_REG_X4),uu.reg_read(UC_ARM64_REG_W5),uu.reg_read(UC_ARM64_REG_SP))
   want=(0,9,c.dw_entry_sp-1392,0xffffffff,0,0,c.dw_entry_sp-1920);eq(got,want)
   bad=[]
   for k in range(6):
    x=list(got);x[k]=(x[k]+1)&(0xffffffffffffffff if k in (2,4) else 0xffffffff);bad.append((tuple(x),want))
   x=list(got);x[6]+=16;bad.append((tuple(x),want));neg+=reject(eq,bad)
   calls.append('CB7784:CB8D88_QUERY_CALL')
  elif r==0xcb8d88:
   lr=uu.reg_read(UC_ARM64_REG_LR);assert lr in (n.base+0xcb7788,n.base+0xcb7824) and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1920
   calls.append('CB8D88:ENTRY_MODE_ZERO_'+('QUERY' if lr==n.base+0xcb7788 else 'OUTPUT'))
  elif r==0xcb8dcc:
   lr=uu.reg_read(UC_ARM64_REG_LR);assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==0 and (uu.reg_read(UC_ARM64_REG_W1)&0xffffffff)==9
   assert uu.reg_read(UC_ARM64_REG_X2)==c.dw_entry_sp-1392 and (uu.reg_read(UC_ARM64_REG_W3)&0xffffffff)==0xffffffff
   if lr==n.base+0xcb7788:
    assert uu.reg_read(UC_ARM64_REG_X4)==0 and (uu.reg_read(UC_ARM64_REG_W5)&0xffffffff)==0;calls.append('CB8DCC:MULTIBYTE_QUERY_ARGS_PRESERVED')
   else:
    assert lr==n.base+0xcb7824 and uu.reg_read(UC_ARM64_REG_X4)==utf_output and (uu.reg_read(UC_ARM64_REG_W5)&0xffffffff)==38;calls.append('CB8DCC:MULTIBYTE_OUTPUT_ARGS_PRESERVED')
  elif r==0xcb8dd0:
   lr=uu.reg_read(UC_ARM64_REG_LR);assert lr in (n.base+0xcb7788,n.base+0xcb7824)
   got=(r,uu.reg_read(UC_ARM64_REG_SP),lr,0xf7e2e8,True);want=(0xcb8dd0,c.dw_entry_sp-1920,lr,0xf7e2e8,True);eq(got,want)
   neg+=reject(eq,[((r+4,*got[1:]),want),((r,got[1]+16,*got[2:]),want),((r,got[1],got[2]+4,got[3],True),want),((r,got[1],got[2],got[3]+8,True),want),((r,got[1],got[2],got[3],False),want)])
   calls.append('CB8DD0:MULTIBYTETOWIDECHAR_IAT_READ_'+('QUERY' if lr==n.base+0xcb7788 else 'OUTPUT'))
  elif r==0xcb8dd4:
   lr=uu.reg_read(UC_ARM64_REG_LR);assert uu.reg_read(UC_ARM64_REG_X8)==os_query_target and lr in (n.base+0xcb7788,n.base+0xcb7824)
   calls.append('CB8DD4:MULTIBYTETOWIDECHAR_TAILCALL_'+('QUERY' if lr==n.base+0xcb7788 else 'OUTPUT'))
  elif r==0xcb7788:
   assert os_query_calls==1 and (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==38
   calls.append('CB7788:QUERY_RETURN_38')
  elif r==0xcb77b0:
   assert uu.reg_read(UC_ARM64_REG_X23)==38 and uu.reg_read(UC_ARM64_REG_X24)==38
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1776,8),'little')==0
   calls.append('CB77B0:QUERY_NONZERO_CAPACITY_COMPARE')
  elif r==0xcb77bc:
   assert uu.reg_read(UC_ARM64_REG_X23)==38 and uu.reg_read(UC_ARM64_REG_X5)==0
   calls.append('CB77BC:NEEDS_OWNED_ALLOCATION')
  elif r==0xcb77d0:
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1760,1),'little')==0
   calls.append('CB77D0:COLD_ALLOCATION_FLAG_ZERO')
  elif r==0xcb77d8:
   got=(r,uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X22),uu.reg_read(UC_ARM64_REG_SP),True);want=(0xcb77d8,76,c.dw_entry_sp-1784,c.dw_entry_sp-1920,True);eq(got,want)
   neg+=reject(eq,[((r+4,*got[1:]),want),((r,78,*got[2:]),want),((r,got[1],got[2]+8,got[3],True),want),((r,got[1],got[2],got[3]+16,True),want),((r,got[1],got[2],got[3],False),want)])
   calls.append('CB77D8:CB16C0_ALLOCATOR_CALL_76')
  elif r==0xcb16c0:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP));assert got==(76,n.base+0xcb77dc,c.dw_entry_sp-1920)
   allocator_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};calls.append('CB16C0:ENTRY_76')
  elif r==0xcb1700:
   assert heap_calls==1 and uu.reg_read(UC_ARM64_REG_X0)==utf_output and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1968;calls.append('CB16C0:HEAPALLOC_RETURN')
  elif r==0xcb77dc:
   assert allocator_saved is not None and all(uu.reg_read(reg)==v for reg,v in allocator_saved.items())
   assert uu.reg_read(UC_ARM64_REG_X0)==utf_output and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1920;calls.append('CB16C0:RETURN_OWNED_76')
  elif r==0xcb7820:
   got=(uu.reg_read(UC_ARM64_REG_W0),uu.reg_read(UC_ARM64_REG_W1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_W3),uu.reg_read(UC_ARM64_REG_X4),uu.reg_read(UC_ARM64_REG_W5));assert got==(0,9,c.dw_entry_sp-1392,0xffffffff,utf_output,38)
   calls.append('CB7820:CB8D88_OUTPUT_CALL')
  elif r==0xcb7824:
   assert os_output_calls==1 and (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==38
   assert hashlib.sha256(bytes(uu.mem_read(utf_output,76))).hexdigest()==APIO['output_sha256'];calls.append('CB7824:OUTPUT_RETURN_38')
  elif r==0xcb7834:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==38 and int.from_bytes(uu.mem_read(c.dw_entry_sp-1768,8),'little')==37
   calls.append('CB7834:SET_STATUS_ZERO')
  elif r==0xcfd4e8:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==0 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1784,8),'little')==utf_output and int.from_bytes(uu.mem_read(c.dw_entry_sp-1776,8),'little')==38 and int.from_bytes(uu.mem_read(c.dw_entry_sp-1768,8),'little')==37 and int.from_bytes(uu.mem_read(c.dw_entry_sp-1760,1),'little')==1
   assert hashlib.sha256(bytes(uu.mem_read(utf_output,76))).hexdigest()==APIO['output_sha256']
   calls.append('CB76B0:COMPLETE_RETURN')
  elif r==0xcfd514:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_W3),uu.reg_read(UC_ARM64_REG_W4),uu.reg_read(UC_ARM64_REG_W5),uu.reg_read(UC_ARM64_REG_W6),uu.reg_read(UC_ARM64_REG_SP),True)
   want=(c.dw_entry_sp-1664,c.dw_entry_sp-1600,utf_output,0,128,384,1,c.dw_entry_sp-1856,True);eq(got,want)
   bad=[]
   for k in range(7):
    x=list(got);x[k]=(x[k]+(8 if k<3 else 1))&0xffffffffffffffff;bad.append((tuple(x),want))
   x=list(got);x[7]+=16;bad.append((tuple(x),want));x=list(got);x[8]=False;bad.append((tuple(x),want));neg+=reject(eq,bad)
   assert bytes(uu.mem_read(n.base+r,4))==EC.PE.get_data(r,4)
   calls.append('CFD514:CFD570_CALL')
  elif r==0xcfd570:
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856 and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfd518
   cfd570_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL}
   calls.append('CFD570:ENTRY_WITH_JOINED_LOWIO')
  elif r==0xcfd5b0:
   got=(uu.reg_read(UC_ARM64_REG_W0),uu.reg_read(UC_ARM64_REG_W1),uu.reg_read(UC_ARM64_REG_W2),uu.reg_read(UC_ARM64_REG_X8),uu.reg_read(UC_ARM64_REG_SP),True)
   want=(0,128,384,c.dw_entry_sp-2096+0x40,c.dw_entry_sp-2096,True);eq(got,want)
   neg+=reject(eq,[((1,*got[1:]),want),((got[0],127,*got[2:]),want),((got[0],got[1],385,*got[3:]),want),((got[0],got[1],got[2],got[3]+8,got[4],True),want),((got[0],got[1],got[2],got[3],got[4]+16,True),want),((*got[:5],False),want)])
   calls.append('CFD5B0:CFD0B0_PARSER_CALL')
  elif r==0xcfd0b0:
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096 and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfd5b4
   calls.append('CFD0B0:ENTRY')
  elif r==0xcfd5b4:
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096
   calls.append('CFD0B0:RETURN')
  elif r==0xcfd5e8:
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096
   assert int.from_bytes(uu.mem_read(n.base+0x16a2a90,8),'little')==low_ptr and int.from_bytes(uu.mem_read(n.base+0x16a2e90,4),'little')==64
   assert bytes(uu.mem_read(low_ptr,64*72))==before_lowio
   calls.append('CFD5E8:CC08E8_CALL')
  elif r==0xcc08e8:
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096 and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfd5ec
   calls.append('CC08E8:ENTRY_JOINED_STARTUP_TABLE')
  elif r==0xcfd5ec:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==0 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096
   assert low_depths[low_global7]==0 and low_depths[low_record0]==1 and len(lowio_api_events)==3
   assert int.from_bytes(uu.mem_read(n.base+0x16a2a90,8),'little')==low_ptr and int.from_bytes(uu.mem_read(n.base+0x16a2e90,4),'little')==64
   assert bytes(uu.mem_read(low_ptr+56,1))==b'\x01' and int.from_bytes(uu.mem_read(low_ptr+40,8),'little')==0xffffffffffffffff
   calls.append('CC08E8:RETURN_INDEX0')
  elif r==0xcfd658:
   sec=uu.reg_read(UC_ARM64_REG_X3);iat=int.from_bytes(uu.mem_read(n.base+0xf7e3b8,8),'little')
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_W1),uu.reg_read(UC_ARM64_REG_W2),sec,uu.reg_read(UC_ARM64_REG_W4),uu.reg_read(UC_ARM64_REG_W5),uu.reg_read(UC_ARM64_REG_X6),uu.reg_read(UC_ARM64_REG_X8),True)
   want=(utf_output,0x80000000,1,c.dw_entry_sp-2000,3,128,0,createfile_target,True);eq(got,want)
   assert iat==createfile_target and bytes(uu.mem_read(sec,24))==struct.pack('<QQII',24,0,1,0)
   assert hashlib.sha256(bytes(uu.mem_read(utf_output,76))).hexdigest()==APIO['output_sha256']
   calls.append('CFD658:CREATEFILEW_CALL_SOURCE_EXACT')
  elif r==0xcfd65c:
   assert uu.reg_read(UC_ARM64_REG_X0)==0xffffffffffffffff and createfile_calls==1
   calls.append('CFD65C:CREATEFILEW_RETURN_INVALID_HANDLE')
  elif r==0xcfd678:
   assert uu.reg_read(UC_ARM64_REG_X23)==0xffffffffffffffff
   calls.append('CFD678:INVALID_HANDLE_FAILURE_BRANCH')
  elif r==0xcfd6fc:
   iat=int.from_bytes(uu.mem_read(n.base+0xf7e468,8),'little');assert iat==getlasterror_target and uu.reg_read(UC_ARM64_REG_X8)==getlasterror_target and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096
   calls.append('CFD6FC:GETLASTERROR_CALL_SOURCE_EXACT')
  elif r==0xcfd700:
   assert getlasterror_calls==1 and (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==3 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096
   assert uu.reg_read(UC_ARM64_REG_X18)==teb and int.from_bytes(uu.mem_read(thread_ptr+32,8),'little')==0
   ey_state['stack_before']=bytes(uu.mem_read(n.stack,65536));ey_state['stack_model']=bytearray(ey_state['stack_before'])
   calls.append('CFD700:CAEC20_CALL_ERROR3')
  elif r==0xcaec20:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==3 and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfd704 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096 and uu.reg_read(UC_ARM64_REG_X18)==teb
   calls.append('CAEC20:ENTRY_ERROR3')
  elif r==0xcb41d0:
   lr=uu.reg_read(UC_ARM64_REG_LR);spv=uu.reg_read(UC_ARM64_REG_SP);assert uu.reg_read(UC_ARM64_REG_X18)==teb
   if lr in (n.base+0xcaec38,n.base+0xcaec60): assert spv==c.dw_entry_sp-2128 and thread_calls<2
   else: assert lr==n.base+0xcaed08 and spv==c.dw_entry_sp-2112 and thread_calls==2
   thread_calls+=1;calls.append('CB41D0:ENTRY_'+str(thread_calls))
  elif r==0xcba180:
   assert uu.reg_read(UC_ARM64_REG_W0)==slot and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcb4210 and int.from_bytes(uu.mem_read(n.base+0x1b60018,8),'little')==getter
   calls.append('CBA180:FLS_DISPATCH_'+str(thread_calls))
  elif r==0xcb4210:
   assert uu.reg_read(UC_ARM64_REG_X0)==thread_ptr and thread_getter_entries==thread_calls and uu.reg_read(UC_ARM64_REG_X18)==teb
   thread_getter_returns+=1;calls.append('NATIVE_FLS_GETTER:RETURN_'+str(thread_getter_returns))
  elif r==0xcaec38:
   assert uu.reg_read(UC_ARM64_REG_X0)==thread_ptr and thread_getter_returns==1;calls.append('CAEC38:THREAD_OWNER_1')
  elif r==0xcaeb48:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==3 and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcaec58;calls.append('CAEB48:MAP_ERROR3')
  elif r==0xcaec58:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==2;calls.append('CAEC58:CRT_ERROR2')
  elif r==0xcaec60:
   assert uu.reg_read(UC_ARM64_REG_X0)==thread_ptr and thread_getter_returns==2;calls.append('CAEC60:THREAD_OWNER_2')
  elif r==0xcfd704:
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096 and uu.reg_read(UC_ARM64_REG_X0)==thread_ptr
   assert int.from_bytes(uu.mem_read(thread_ptr+36,4),'little')==3 and int.from_bytes(uu.mem_read(thread_ptr+32,4),'little')==2
   assert hashlib.sha256(bytes(uu.mem_read(utf_output,76))).hexdigest()==APIO['output_sha256']
   calls.append('CFD704:CAEC20_RETURN_THREADPTR_OS3_CRT2')
  elif r==0xcfd5dc:
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096 and thread_calls==2 and thread_getter_returns==2
   assert int.from_bytes(uu.mem_read(thread_ptr+32,4),'little')==2 and hashlib.sha256(bytes(uu.mem_read(utf_output,76))).hexdigest()==APIO['output_sha256']
   calls.append('CFD5DC:CAECF8_CALL_CURRENT_CRT2')
  elif r==0xcaecf8:
   lr=uu.reg_read(UC_ARM64_REG_LR);sp=uu.reg_read(UC_ARM64_REG_SP)
   if lr==n.base+0xcfd5e0:
    assert sp==c.dw_entry_sp-2096
    calls.append('CAECF8:ENTRY_CURRENT_THREAD')
   else:
    want=(n.base+0xced33c,c.dw_entry_sp-1488,thread_ptr,3,2)
    got=(lr,sp,thread_ptr,int.from_bytes(uu.mem_read(thread_ptr+36,4),'little'),int.from_bytes(uu.mem_read(thread_ptr+32,4),'little'));eq(got,want)
    neg+=reject(eq,[((got[0]+4,*got[1:]),want),((got[0],got[1]+16,*got[2:]),want),((got[0],got[1],got[2]+16,got[3],got[4]),want),((got[0],got[1],got[2],4,got[4]),want),((got[0],got[1],got[2],got[3],3),want)])
    assert not selected_lock_held and owner['released'] and not owner['live'] and low_depths=={low_global7:0,low_record0:0}
    assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1448,8),'little')==0 and len(fi_writes)==1
    calls.append('CAECF8:ENTRY_OUTER_CURRENT_THREAD_CRT2');stop['hit']=True;uu.emu_stop()
  elif r==0xcaed08:
   assert uu.reg_read(UC_ARM64_REG_X0)==thread_ptr and thread_getter_returns==3 and thread_calls==3
   calls.append('CAED08:THREAD_OWNER_3')
  elif r==0xcaed24:
   assert uu.reg_read(UC_ARM64_REG_X0)==thread_ptr+32 and int.from_bytes(uu.mem_read(thread_ptr+32,4),'little')==2
   calls.append('CAED24:RETURN_CRT_ERROR_POINTER')
  elif r==0xcfd5e0:
   assert uu.reg_read(UC_ARM64_REG_X0)==thread_ptr+32 and int.from_bytes(uu.mem_read(thread_ptr+32,4),'little')==2
   calls.append('CFD5E0:LOAD_CRT_ERROR2')
  elif r==0xcfd5e4:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==2 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096
   calls.append('CFD5E4:BRANCH_ERROR_RETURN')
  elif r==0xcfd980:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==2 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-2096 and cfd570_saved is not None
   calls.append('CFD980:ERROR_EPILOGUE')
  elif r==0xcfd518:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==2 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856 and cfd570_saved is not None
   assert all(uu.reg_read(reg)==v for reg,v in cfd570_saved.items())
   assert thread_calls==thread_getter_entries==thread_getter_returns==3 and int.from_bytes(uu.mem_read(thread_ptr+32,4),'little')==2
   assert uu.reg_read(UC_ARM64_REG_X19)==utf_output and owner['live'] and not owner['released']
   owner_sha=hashlib.sha256(bytes(uu.mem_read(utf_output,76))).hexdigest();assert owner_sha==APIO['output_sha256']
   good_cleanup=(1,utf_output,76,owner_sha,utf_output,APIO['output_sha256'],False);validate_current_cleanup(*good_cleanup)
   neg+=reject(validate_current_cleanup,[(0,*good_cleanup[1:]),(1,utf_output+2,*good_cleanup[2:]),(1,utf_output,74,*good_cleanup[3:]),(1,utf_output,76,'0'*64,*good_cleanup[4:]),(1,utf_output,76,owner_sha,utf_output,APIO['output_sha256'],True)])
   calls.append('CFD518:CFD570_COMPLETE_RETURN_CRT2_OWNER76_LIVE')
  elif r==0xcfd51c:
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856 and uu.reg_read(UC_ARM64_REG_X19)==utf_output and owner['live']
   calls.append('CFD51C:CURRENT_OWNER_FLAG_READ')
  elif r==0xcfd520:
   assert (uu.reg_read(UC_ARM64_REG_W8)&0xff)==1 and owner['live'];calls.append('CFD520:OWNER_FLAG_ONE_TAKE_CLEANUP')
  elif r==0xcfd524:
   assert uu.reg_read(UC_ARM64_REG_X19)==utf_output and owner['live'];calls.append('CFD524:SELECT_CURRENT_76_OWNER')
  elif r==0xcfd528:
   assert uu.reg_read(UC_ARM64_REG_X0)==utf_output and owner['live'];calls.append('CFD528:CB1650_CALL_CURRENT_76')
  elif r==0xcb1650:
   assert uu.reg_read(UC_ARM64_REG_X0)==utf_output and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfd52c and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856 and owner['live'];calls.append('CB1650:ENTRY_CURRENT_76')
  elif r==0xcb1654:
   at=c.dw_entry_sp-1872;fa_pending[at,8]=uu.reg_read(UC_ARM64_REG_X19)&0xffffffffffffffff
  elif r==0xcb1658:
   at=c.dw_entry_sp-1888;fa_pending[at,8]=uu.reg_read(UC_ARM64_REG_X29)&0xffffffffffffffff;fa_pending[at+8,8]=uu.reg_read(UC_ARM64_REG_X30)&0xffffffffffffffff
  elif r==0xcb1660:
   assert uu.reg_read(UC_ARM64_REG_X0)==utf_output and owner['live'];calls.append('CB1660:NONNULL_OWNER')
  elif r==0xcb167c:
   assert uu.reg_read(UC_ARM64_REG_X0)==heap_handle and (uu.reg_read(UC_ARM64_REG_W1)&0xffffffff)==0 and uu.reg_read(UC_ARM64_REG_X2)==utf_output and uu.reg_read(UC_ARM64_REG_X8)==heap_free_target and owner['live'];calls.append('CB167C:HEAPFREE_CALL_EXACT_CURRENT_76')
  elif r==0xcb1680:
   assert heap_free_calls==1 and (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==1 and owner['released'] and not owner['live'];calls.append('CB1680:HEAPFREE_SUCCESS')
  elif r==0xcb16a0:
   assert owner['released'] and heap_free_calls==1;calls.append('CB16A0:FREE_WRAPPER_SUCCESS_EPILOGUE')
  elif r==0xcfd52c:
   assert owner['released'] and heap_free_calls==1 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856
   assert (uu.reg_read(UC_ARM64_REG_W20)&0xffffffff)==2 and uu.reg_read(UC_ARM64_REG_X19)==utf_output
   calls.append('CFD52C:CURRENT_76_OWNER_RELEASED_BEGIN_PARENT_EPILOGUE')
  elif r==0xcfcc9c:
   got=(uu.reg_read(UC_ARM64_REG_W0)&0xffffffff,uu.reg_read(UC_ARM64_REG_SP),r);want=(2,c.dw_entry_sp-1680,0xcfcc9c);eq(got,want)
   neg+=reject(eq,[((1,got[1],got[2]),want),((3,got[1],got[2]),want),((got[0],got[1]+16,got[2]),want),((got[0],got[1],got[2]+4),want)])
   assert owner['released'] and not owner['live'] and heap_free_calls==1 and cfd_saved is not None
   assert all(uu.reg_read(reg)==v for reg,v in cfd_saved.items())
   assert uu.reg_read(UC_ARM64_REG_X29)==c.dw_entry_sp-1680 and uu.reg_read(UC_ARM64_REG_X19)==c.dw_entry_sp-1600
   calls.append('CFCC9C:CFD410_COMPLETE_RETURN_CRT2')
  elif r==0xcfcca0:
   at=c.dw_entry_sp-1660;assert uu.reg_read(UC_ARM64_REG_X29)==c.dw_entry_sp-1680 and (uu.reg_read(UC_ARM64_REG_W20)&0xffffffff)==2
   fc_pending[at,4]=2;calls.append('CFCCA0:STORE_RETURN2_LOCAL')
  elif r==0xcfcca4:
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1664,4),'little')==1;calls.append('CFCCA4:LOAD_CLEANUP_FLAG1')
  elif r==0xcfcca8:
   assert (uu.reg_read(UC_ARM64_REG_W8)&0xffffffff)==1 and (uu.reg_read(UC_ARM64_REG_W20)&0xffffffff)==2;calls.append('CFCCA8:FLAG1_ENTER_CLEANUP')
  elif r==0xcfccac:
   assert (uu.reg_read(UC_ARM64_REG_W20)&0xffffffff)==2;calls.append('CFCCAC:RETURN2_ENTER_ERROR_CLEANUP')
  elif r==0xcfccb0:
   assert uu.reg_read(UC_ARM64_REG_X19)==c.dw_entry_sp-1600 and int.from_bytes(uu.mem_read(c.dw_entry_sp-1600,4),'little')==0;calls.append('CFCCB0:LOAD_INDEX0')
  elif r==0xcfccc8:
   assert (uu.reg_read(UC_ARM64_REG_X11)&0xffffffffffffffff)==0 and (uu.reg_read(UC_ARM64_REG_X10)&0xffffffffffffffff)==0;calls.append('CFCCC8:LOAD_LOWIO_BLOCK0')
  elif r==0xcfccd0:
   assert uu.reg_read(UC_ARM64_REG_X9)==low_record0 and int.from_bytes(uu.mem_read(low_record0+56,1),'little')==0;calls.append('CFCCD0:READ_RECORD0_ACTIVE_ZERO')
  elif r==0xcfccd8:
   assert (uu.reg_read(UC_ARM64_REG_W8)&0xff)==0 and uu.reg_read(UC_ARM64_REG_X9)==low_record0;calls.append('CFCCD8:CLEAR_RECORD0_ACTIVE_IDEMPOTENT')
  elif r==0xcfccdc:
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1600,4),'little')==0 and low_depths[low_record0]==1;calls.append('CFCCDC:LOAD_INDEX0_FOR_RELEASE')
  elif r==0xcfcce0:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==0 and low_depths[low_record0]==1;calls.append('CFCCE0:CC08C0_RELEASE_CALL_INDEX0')
  elif r==0xcc08c0:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==0 and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfcce4 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1680;calls.append('CC08C0:ENTRY_INDEX0')
  elif r==0xcc08e4:
   assert uu.reg_read(UC_ARM64_REG_X0)==low_record0 and uu.reg_read(UC_ARM64_REG_X8)==c.apis['LeaveCriticalSection'] and low_depths[low_record0]==1;calls.append('CC08E4:TAIL_LEAVE_RECORD0')
  elif r==0xcfcce4:
   assert low_depths[low_record0]==0 and len(lowio_api_events)==4 and (uu.reg_read(UC_ARM64_REG_W20)&0xffffffff)==2
   assert owner['released'] and not owner['live'];calls.append('CFCCE4:RECORD0_LOCK_RELEASED')
  elif r==0xcfcce8:
   got=(uu.reg_read(UC_ARM64_REG_X19),uu.reg_read(UC_ARM64_REG_W21)&0xffffffff,uu.reg_read(UC_ARM64_REG_SP),int.from_bytes(uu.mem_read(c.dw_entry_sp-1600,4),'little'),uu.reg_read(UC_ARM64_REG_W20)&0xffffffff)
   want=(c.dw_entry_sp-1600,0xffffffff,c.dw_entry_sp-1680,0,2);eq(got,want)
   neg+=reject(eq,[((got[0]+4,*got[1:]),want),((got[0],0,*got[2:]),want),((got[0],got[1],got[2]+16,*got[3:]),want),((got[0],got[1],got[2],1,got[4]),want),((got[0],got[1],got[2],got[3],1),want)])
   fd_pending[c.dw_entry_sp-1600,4]=0xffffffff;calls.append('CFCCE8:RESTORE_RESULT_MINUS1')
  elif r==0xcfccec:
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1600,4),'little')==0xffffffff and (uu.reg_read(UC_ARM64_REG_W20)&0xffffffff)==2;calls.append('CFCCEC:RESTORE_DONE_RETURN2')
  elif r==0xcfccf0:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==2 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1680;calls.append('CFCCF0:BRANCH_CFCC18_EPILOGUE')
  elif r==0xcfcc4c:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==2 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1680 and cfcc_saved is not None;calls.append('CFCC4C:CFCC18_EPILOGUE')
  elif r==0xcfa9c0:
   got=(uu.reg_read(UC_ARM64_REG_W0)&0xffffffff,uu.reg_read(UC_ARM64_REG_SP),r);want=(2,c.dw_entry_sp-1616,0xcfa9c0);eq(got,want)
   neg+=reject(eq,[((1,got[1],got[2]),want),((3,got[1],got[2]),want),((got[0],got[1]+16,got[2]),want),((got[0],got[1],got[2]+4),want)])
   assert all(uu.reg_read(reg)==v for reg,v in cfcc_saved.items()) and low_depths=={low_global7:0,low_record0:0}
   assert owner['released'] and not owner['live'];calls.append('CFA9C0:CFCC18_COMPLETE_RETURN2_BRANCH_NONZERO')
  elif r==0xcfa99c:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==2 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1616
   calls.append('CFA99C:ERROR_BRANCH_TARGET')
  elif r==0xcfa9a0:
   assert uu.reg_read(UC_ARM64_REG_X0)==0 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1616
   calls.append('CFA9A0:ZERO_RETURN_BRANCH_EPILOGUE')
  elif r==0xcfa9f8:
   assert uu.reg_read(UC_ARM64_REG_X0)==0 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1616
   assert owner['released'] and not owner['live'] and selected_lock_held and low_depths=={low_global7:0,low_record0:0}
   calls.append('CFA9F8:CFA968_EPILOGUE')
  elif r==0xced178:
   assert uu.reg_read(UC_ARM64_REG_X0)==0 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1552
   assert owner['released'] and not owner['live'] and selected_lock_held and low_depths=={low_global7:0,low_record0:0}
   calls.append('CED178:CFA968_RETURN_ZERO')
  elif r==0xced17c:
   assert uu.reg_read(UC_ARM64_REG_X19)==0 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1552
   calls.append('CED17C:STORE_ZERO_RESULT')
  elif r==0xced180:
   assert uu.reg_read(UC_ARM64_REG_X19)==0 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1552
   calls.append('CED180:ZERO_RESULT_BRANCH_CLEANUP')
  elif r==0xced184:
   assert uu.reg_read(UC_ARM64_REG_X19)==0 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1552
   calls.append('CED184:LOAD_SELECTED_FOR_CLEANUP')
  elif r==0xced188:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_SP),r);want=(selected,c.dw_entry_sp-1552,0xced188);eq(got,want)
   neg+=reject(eq,[((selected+8,got[1],got[2]),want),((selected,got[1]+16,got[2]),want),((selected,got[1],got[2]+4),want)])
   assert owner['released'] and not owner['live'] and selected_lock_held and low_depths=={low_global7:0,low_record0:0}
   assert bytes(uu.mem_read(selected,88))==before_selected
   calls.append('CED188:CC60E0_SELECTED_CLEANUP_CALL')
  elif r==0xcc60e0:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_LR));want=(selected,c.dw_entry_sp-1552,n.base+0xced18c);eq(got,want)
   neg+=reject(eq,[((selected+8,got[1],got[2]),want),((selected,got[1]+16,got[2]),want),((selected,got[1],got[2]+4),want)])
   assert selected_lock_held and bytes(uu.mem_read(selected,88))==before_selected
   calls.append('CC60E0:ENTRY_SELECTED_EXACT')
  elif r==0x12d0:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_W1)&0xffffffff,uu.reg_read(UC_ARM64_REG_LR));want=(selected+20,0,n.base+0xced18c);eq(got,want)
   neg+=reject(eq,[((got[0]+4,got[1],got[2]),want),((got[0],1,got[2]),want),((got[0],got[1],got[2]+4),want)])
   calls.append('CC60E0:TAIL_ATOMIC_EXCHANGE_ZERO')
  elif r==0x12d8:
   got=uu.reg_read(UC_ARM64_REG_W16)&0xffffffff;assert got==0x80000000
   calls.append('ATOMIC_EXCHANGE:SOURCE_RUNTIME_FLAG_80000000')
  elif r==0x12e8:
   assert (uu.reg_read(UC_ARM64_REG_W16)&0xffffffff)==0x80000000 and uu.reg_read(UC_ARM64_REG_X0)==selected+20
   calls.append('ATOMIC_EXCHANGE:FALLBACK_LDAXR')
  elif r==0x12ec:
   assert (uu.reg_read(UC_ARM64_REG_W2)&0xffffffff)==0x2000 and (uu.reg_read(UC_ARM64_REG_W1)&0xffffffff)==0
   calls.append('ATOMIC_EXCHANGE:FALLBACK_STLXR_ZERO')
  elif r==0x12f4:
   assert (uu.reg_read(UC_ARM64_REG_W16)&0xffffffff)==0 and int.from_bytes(uu.mem_read(selected+20,4),'little')==0
   calls.append('ATOMIC_EXCHANGE:STORE_SUCCESS')
  elif r==0x12f8:
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==0x2000
   calls.append('ATOMIC_EXCHANGE:RETURN_OLD_2000')
  elif r==0xced18c:
   expected=bytearray(before_selected);expected[20:24]=bytes(4)
   assert (uu.reg_read(UC_ARM64_REG_W0)&0xffffffff)==0x2000 and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1552
   assert bytes(uu.mem_read(selected,88))==bytes(expected) and bytes(uu.mem_read(selected+48,40))==before_selected[48:88]
   assert selected_lock_held and owner['released'] and low_depths=={low_global7:0,low_record0:0}
   calls.append('CED18C:CC60E0_RETURN_CLAIM_CLEARED_LOCK_HELD')
  elif r==0xced190:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_SP),r);want=(selected,c.dw_entry_sp-1552,0xced190);eq(got,want)
   neg+=reject(eq,[((selected+8,got[1],got[2]),want),((selected,got[1]+16,got[2]),want),((selected,got[1],got[2]+4),want)])
   assert selected_lock_held and int.from_bytes(uu.mem_read(selected+20,4),'little')==0
   calls.append('CED190:CB3480_SELECTED_LOCK_RELEASE_CALL')
  elif r==0xcb3480:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_LR));want=(selected,c.dw_entry_sp-1552,n.base+0xced194);eq(got,want)
   neg+=reject(eq,[((selected+8,got[1],got[2]),want),((selected,got[1]+16,got[2]),want),((selected,got[1],got[2]+4),want)])
   assert selected_lock_held;calls.append('CB3480:ENTRY_SELECTED_LOCK_HELD')
  elif r==0xcb3484:
   calls.append('CB3484:LOAD_LEAVECRITICALSECTION_IAT')
  elif r==0xcb3488:
   assert uu.reg_read(UC_ARM64_REG_X8)==c.apis['LeaveCriticalSection'];calls.append('CB3488:LEAVECRITICALSECTION_TARGET_EXACT')
  elif r==0xcb348c:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X8),uu.reg_read(UC_ARM64_REG_LR));want=(selected+48,c.apis['LeaveCriticalSection'],n.base+0xced194);eq(got,want)
   neg+=reject(eq,[((got[0]+8,got[1],got[2]),want),((got[0],got[1]+8,got[2]),want),((got[0],got[1],got[2]+4),want)])
   assert selected_lock_held;calls.append('CB348C:TAIL_LEAVE_SELECTED_PLUS48')
  elif r==0xced194:
   got=(uu.reg_read(UC_ARM64_REG_X19),uu.reg_read(UC_ARM64_REG_SP),r);want=(0,c.dw_entry_sp-1552,0xced194);eq(got,want)
   neg+=reject(eq,[((1,got[1],got[2]),want),((got[0],got[1]+16,got[2]),want),((got[0],got[1],got[2]+4),want)])
   assert not selected_lock_held and owner['released'] and not owner['live'] and low_depths=={low_global7:0,low_record0:0}
   assert int.from_bytes(uu.mem_read(selected+20,4),'little')==0
   calls.append('CED194:SELECTED_LOCK_RELEASED_OUTER_RETURN_FRONTIER')
  elif r==0xced198:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X19),uu.reg_read(UC_ARM64_REG_SP),r);want=(0,0,c.dw_entry_sp-1552,0xced198);eq(got,want)
   neg+=reject(eq,[((1,got[1],got[2],got[3]),want),((got[0],1,got[2],got[3]),want),((got[0],got[1],got[2]+16,got[3]),want),((got[0],got[1],got[2],got[3]+4),want)])
   calls.append('CED198:ZERO_BRANCH_CED110')
  elif r==0xced110:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_X30));want=(0,c.dw_entry_sp-1552,n.base+0xced194);eq(got,want)
   neg+=reject(eq,[((1,got[1],got[2]),want),((got[0],got[1]+16,got[2]),want),((got[0],got[1],got[2]+4),want)])
   calls.append('CED110:EPILOGUE_ENTRY_ZERO')
  elif r==0xced120:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_X30));want=(0,c.dw_entry_sp-1488,n.base+0xced330);eq(got,want)
   neg+=reject(eq,[((1,got[1],got[2]),want),((got[0],got[1]+16,got[2]),want),((got[0],got[1],got[2]+4),want),((got[0],got[1],n.base+0xced334),want)])
   assert not selected_lock_held and owner['released'] and low_depths=={low_global7:0,low_record0:0}
   calls.append('CED120:RET_TO_CED330_EXACT')
  elif r==0xced330:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_X19),r);want=(0,c.dw_entry_sp-1488,c.dw_entry_sp-1448,0xced330);eq(got,want)
   neg+=reject(eq,[((1,got[1],got[2],got[3]),want),((got[0],got[1]+16,got[2],got[3]),want),((got[0],got[1],got[2]+8,got[3]),want),((got[0],got[1],got[2],got[3]+4),want)])
   assert not selected_lock_held and owner['released'] and not owner['live'] and low_depths=={low_global7:0,low_record0:0}
   calls.append('CED330:CED0D8_ZERO_RETURN_CALLER_FRONTIER')
  elif r==0xced334:
   assert uu.reg_read(UC_ARM64_REG_X0)==0 and int.from_bytes(uu.mem_read(c.dw_entry_sp-1448,8),'little')==0 and len(fi_writes)==1
   calls.append('CED334:ZERO_RESULT_BRANCH_TO_CAECF8')
  elif r==0xced338:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_SP),int.from_bytes(uu.mem_read(thread_ptr+36,4),'little'),int.from_bytes(uu.mem_read(thread_ptr+32,4),'little'));want=(0,c.dw_entry_sp-1488,3,2);eq(got,want)
   neg+=reject(eq,[((1,*got[1:]),want),((got[0],got[1]+16,got[2],got[3]),want),((got[0],got[1],4,got[3]),want),((got[0],got[1],got[2],3),want)])
   assert not selected_lock_held and owner['released'] and not owner['live'] and low_depths=={low_global7:0,low_record0:0}
   calls.append('CED338:CAECF8_CALL_SAME_THREAD_CRT2')

 def memread(uu,a,at,width,value,_):
  nonlocal neg
  r0=uu.reg_read(UC_ARM64_REG_PC)-n.base
  if not selected_lock_held and selected<=at<selected+88:
   raise AssertionError(('selected object read after lock release',hex(r0),hex(at),width))
  if r0==0xced184:
   got=(r0,at,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xced184,uu.reg_read(UC_ARM64_REG_X29)+0x10,8,selected);eq(got,want)
   neg+=reject(eq,[((r0,at+8,width,got[3]),want),((r0,at,4,got[3]&0xffffffff),want),((r0,at,width,selected+8),want)])
  elif r0==0x12d4:
   got=(r0,at,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0x12d4,runtime_atomic_flag,4,0x80000000);eq(got,want)
   neg+=reject(eq,[((r0+4,at,width,got[3]),want),((r0,at+4,width,got[3]),want),((r0,at,8,got[3]),want),((r0,at,width,0),want)]);ff_reads.append(got)
  elif r0==0x12e8:
   got=(r0,at,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0x12e8,selected+20,4,0x2000);eq(got,want)
   neg+=reject(eq,[((r0+4,at,width,got[3]),want),((r0,at+4,width,got[3]),want),((r0,at,8,got[3]),want),((r0,at,width,0),want)]);ff_reads.append(got)
  elif r0==0xced18c:
   got=(r0,at,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xced18c,uu.reg_read(UC_ARM64_REG_X29)+0x10,8,selected);eq(got,want)
   neg+=reject(eq,[((r0,at+8,width,got[3]),want),((r0,at,4,got[3]&0xffffffff),want),((r0,at,width,selected+8),want)]);ff_reads.append(got)
  elif r0==0xcb3484:
   got=(r0,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcb3484,0xf7e0c0,8,c.apis['LeaveCriticalSection']);eq(got,want)
   neg+=reject(eq,[((r0+4,got[1],width,got[3]),want),((r0,got[1]+8,width,got[3]),want),((r0,got[1],4,got[3]&0xffffffff),want),((r0,got[1],width,got[3]+8),want)]);ff_reads.append(got)
  if owner['released']: assert at+width<=utf_output or at>=utf_output+76,('original read of retired current 76-byte owner',hex(uu.reg_read(UC_ARM64_REG_PC)-n.base),hex(at),width)
  pcv=uu.reg_read(UC_ARM64_REG_PC);r=pcv-n.base
  if getter<=pcv<getter+0x80:
   allowed={(teb+0x17c8,8),(fls_data+8*cv_case.chunk,8),(fls_slab+8*cv_case.index,8)}
   assert (at,width) in allowed,('unowned native FLS getter read',hex(pcv),hex(at),width)
   native_getter_reads.append((pcv-getter,at,width));return
  if r==0xcfcca4:
   got=(r,at-c.dw_entry_sp,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcfcca4,-1664,4,1);eq(got,want);fc_reads.append(('cleanup_flag',)+got)
  elif r in (0xcfccb0,0xcfccdc):
   got=(r,at-c.dw_entry_sp,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(r,-1600,4,0);eq(got,want);fc_reads.append(('index0',)+got)
  elif r in (0xcfccc8,0xcc08d0):
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(r,0x16a2a90,8,low_ptr);eq(got,want);fc_reads.append(('lowio_block0',)+got)
  elif r==0xcfccd0:
   got=(r,at-low_record0,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcfccd0,56,1,0);eq(got,want);fc_reads.append(('active0',)+got)
  elif r==0xcc08e0:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcc08e0,0xf7e0c0,8,c.apis['LeaveCriticalSection']);eq(got,want);fc_reads.append(('leave_iat',)+got)
  elif at==n.base+GLOBAL_RVA:
   got=(r,at,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcfa2f4,n.base+GLOBAL_RVA,4,0);eq(got,want)
   neg+=reject(eq,[((r+4,at,width,0),want),((r,at+4,width,0),want),((r,at,8,0),want),((r,at,width,1),want),((r,at,width,0xffffffff),want)])
   reads.append(('global',r))
  elif n.base+MODE_RVA<=at<n.base+MODE_RVA+2:
   assert bytes(uu.mem_read(at,width))==bytes(u.mem_read(at,width))
   mode_reads.append((r,at-(n.base+MODE_RVA),width))
  elif r==0xcb6548:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcb6548,0x16a2a84,4,0);eq(got,want)
   neg+=reject(eq,[((r+4,got[1],width,0),want),((r,got[1]+4,width,0),want),((r,got[1],8,0),want),((r,got[1],width,1),want)])
   en_reads.append(got)
  elif r==0xcb6558:
   k=len([x for x in en_reads if x[0]==0xcb6558]); expected=[(0xcb6558,0x16072d8,8,n.base+0x1607180),(0xcb6558,0x16072e0,8,n.base+0x1607650)][k]
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]^8),expected)])
   en_reads.append(got)
  elif r==0xcb9f78:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcb9f78,0x1b60000,8,callback_target);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]+8),expected)])
   callback_reads.append(got)
  elif r==0xf5d434:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xf5d434,0xf7e7b8,8,n.base+0x1a8c0);eq(got,expected)
   cfg_reads.append(got)
  elif r==0xcb8dd0:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcb8dd0,0xf7e2e8,8,os_query_target);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]+8),expected)])
   conversion_iat_reads.append(got)
  elif r==0xcfd6f8:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcfd6f8,0xf7e468,8,getlasterror_target);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]+8),expected)])
   heap_reads.append(('GetLastError_IAT',)+got)
  elif r==0xcfd51c:
   got=(r,at-c.dw_entry_sp,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcfd51c,-1760,1,1);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+1,width,got[3]),expected),((r,got[1],2,got[3]),expected),((r,got[1],width,0),expected)])
   heap_reads.append(('owner_flag',)+got)
  elif r==0xcb166c:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcb166c,0x16a3240,8,heap_handle);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]+8),expected)])
   heap_reads.append(('HeapFree_heap',)+got)
  elif r==0xcb1674:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcb1674,0xf7e278,8,heap_free_target);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]+8),expected)])
   heap_reads.append(('HeapFree_IAT',)+got)
  elif r==0xcb16e8:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcb16e8,0x16a3240,8,heap_handle);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]+8),expected)])
   heap_reads.append(got)
  elif r==0xcb16f0:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcb16f0,0xf7e280,8,heap_alloc_target);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]+8),expected)])
   heap_reads.append(got)
  elif r==0xcfd46c:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little')); expected=(0xcfd46c,0x160718c,4,0);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,0),expected),((r,got[1]+4,width,0),expected),((r,got[1],8,0),expected),((r,got[1],width,1),expected),((r,got[1],width,0xfde9),expected)])
   assert NATIVE['selected_field_value_u32']==got[3] and NATIVE['first_pointer_target_RVA']=='0x1607180'
   pointed_reads.append(got)

 def memwrite(uu,a,at,width,value,_):
  nonlocal neg
  r=uu.reg_read(UC_ARM64_REG_PC)-n.base;value&=(1<<(8*width))-1
  if r==0xced17c:
   got=(r,at,width,value);want=(0xced17c,uu.reg_read(UC_ARM64_REG_X29)+0x18,8,0);eq(got,want)
   neg+=reject(eq,[((r,at+8,width,value),want),((r,at,4,value),want),((r,at,width,1),want)])
   return
  if r==0xced330:
   got=(r,at,width,value);want=(0xced330,c.dw_entry_sp-1448,8,0);eq(got,want)
   neg+=reject(eq,[((r+4,at,width,value),want),((r,at+8,width,value),want),((r,at,4,value),want),((r,at,width,1),want)])
   assert ey_state['stack_model'] is not None
   off=at-n.stack;ey_state['stack_model'][off:off+width]=value.to_bytes(width,'little')
   fi_writes.append(got);return
  if in_ey_source(r):
   key=(at,width);assert key in ey_pending,('unexpected EY write',hex(r),hex(at),width,value,ey_pending)
   expected=ey_pending.pop(key);assert value==expected,(hex(r),hex(at),width,value,expected)
   if n.stack<=at and at+width<=n.stack+65536:
    assert ey_state['stack_model'] is not None;off=at-n.stack;ey_state['stack_model'][off:off+width]=value.to_bytes(width,'little')
   elif thread_page<=at and at+width<=thread_page+0x1000:
    off=at-thread_page;expected_thread[off:off+width]=value.to_bytes(width,'little')
   else:raise AssertionError(('EY write escaped owned stack/thread',hex(r),hex(at),width))
   ey_writes.append((r,at,width,value));return
  if (at,width) in fa_pending:
   expected=fa_pending.pop((at,width));assert value==expected,(hex(r),hex(at),width,value,expected)
   assert n.stack<=at and at+width<=n.stack+65536 and ey_state['stack_model'] is not None
   off=at-n.stack;ey_state['stack_model'][off:off+width]=value.to_bytes(width,'little');fa_writes.append((r,at,width,value));return
  if (at,width) in fc_pending:
   expected=fc_pending.pop((at,width));assert value==expected,(hex(r),hex(at),width,value,expected)
   assert n.stack<=at and at+width<=n.stack+65536 and ey_state['stack_model'] is not None
   off=at-n.stack;ey_state['stack_model'][off:off+width]=value.to_bytes(width,'little');fc_writes.append((r,at,width,value));return
  if (at,width) in fd_pending:
   expected=fd_pending.pop((at,width));assert value==expected,(hex(r),hex(at),width,value,expected)
   assert n.stack<=at and at+width<=n.stack+65536 and ey_state['stack_model'] is not None
   off=at-n.stack;ey_state['stack_model'][off:off+width]=value.to_bytes(width,'little');fd_writes.append((r,at,width,value));return
  if selected<=at and at+width<=selected+48:
   expected_ff=[
    (0xcc60e0,selected,8,0),(0xcc60e0,selected+8,8,0),(0xcc60e8,selected+16,4,0),
    (0xcc60f0,selected+24,8,0xffffffff),(0xcc60f4,selected+32,4,0),(0xcc60f8,selected+40,8,0),
    (0x12ec,selected+20,4,0)]
   got=(r,at,width,value);want=expected_ff[len(ff_writes)];eq(got,want)
   neg+=reject(eq,[((r+4,at,width,value),want),((r,at+1,width,value),want),((r,at,width+1,value),want),((r,at,width,value^1),want)])
   ff_writes.append(got);return
  if low_ptr<=at<low_ptr+64*72:
   expected=[(0xcc0a14,low_ptr+56,1,1),(0xcc0a20,low_ptr+40,8,0xffffffffffffffff),(0xcfd6f0,low_ptr+56,1,0),(0xcfccd8,low_ptr+56,1,0)][len(lowio_writes)]
   got=(r,at,width,value);eq(got,expected)
   neg+=reject(eq,[((r+4,at,width,value),expected),((r,at+1,width,value),expected),((r,at,width+1,value),expected),((r,at,width,value^1),expected)])
   lowio_writes.append(got);return
  assert n.stack<=at and at+width<=n.stack+65536,(hex(r),hex(at),width)
  rel=at-c.dw_entry_sp
  if r in (0xcfa9a8,0xcfcc30,0xcfcc64,0xcfcc78):
   got=(r,rel,width,value)
   want=expected_keywrites[len(keywrites)]
   eq(got,want)
   neg+=reject(eq,[((r+4,rel,width,value),want),((r,rel+4,width,value),want),((r,rel,width+1,value),want),((r,rel,width,value^1),want),((r,rel,width,0x55 & ((1<<(8*width))-1)),want)])
   keywrites.append(got)
  elif r in (0xcfd430,0xcfd438,0xcfd440,0xcfd448,0xcb6534,0xcb655c):
   got=(r,rel,width,value);want=expected_en_writes[len(en_writes)];eq(got,want)
   neg+=reject(eq,[((r+4,rel,width,value),want),((r,rel+4,width,value),want),((r,rel,width+1,value),want),((r,rel,width,value^1),want)])
   en_writes.append(got)

 hs=[u.hook_add(UC_HOOK_CODE,code),u.hook_add(UC_HOOK_MEM_READ,memread),u.hook_add(UC_HOOK_MEM_WRITE,memwrite)]
 try:u.emu_start(n.base+0xced150,n.end,count=6000)
 finally:
  for h in hs:u.hook_del(h)

 assert stop['hit']
 expected_calls=['CED174:CFA968','CFA98C:CFA2E0','CFA9BC:CFD550','CFD550:TAIL_CFCC18','CFCC18:VALIDATION_PREFIX','CFCC98:CFD410','CFD410:ENTRY_RETURN_LINK_CFCC9C','CFD460:CB6520','CB6520:RETURN','CFD46C:NATIVE_QUALIFIED_SELECTED_FIELD_READ','CFD470:ZERO_FIELD_COMPARE','CFD498:CB9F68_CALL','CB9F68:ENTRY_POPULATED_SLOT','CB9FAC:CFG_CHECK','CFG:NOP_RETURN','NATIVE_CALLBACK:RETURN_1','CB9FB4:CALLBACK_RETURN_1','CB9F68:RETURN_NATIVE_1','CFD4C0:NATIVE_RESULT_ONE_BRANCH','CFD4D4:SELECT_MODE_ZERO','CFD4E4:CB76B0_CALL','CB76B0:ENTRY_NONEMPTY_SOURCE','CB76FC:NONEMPTY_INPUT','CB776C:CONVERSION_QUERY_SETUP','CB7784:CB8D88_QUERY_CALL','CB8D88:ENTRY_MODE_ZERO_QUERY','CB8DCC:MULTIBYTE_QUERY_ARGS_PRESERVED','CB8DD0:MULTIBYTETOWIDECHAR_IAT_READ_QUERY','CB8DD4:MULTIBYTETOWIDECHAR_TAILCALL_QUERY','ORIGINAL_API_CONTRACT:QUERY_RETURN_38','CB7788:QUERY_RETURN_38','CB77B0:QUERY_NONZERO_CAPACITY_COMPARE','CB77BC:NEEDS_OWNED_ALLOCATION','CB77D0:COLD_ALLOCATION_FLAG_ZERO','CB77D8:CB16C0_ALLOCATOR_CALL_76','CB16C0:ENTRY_76','OWNED_HEAPALLOC:RETURN_76','CB16C0:HEAPALLOC_RETURN','CB16C0:RETURN_OWNED_76','CB7820:CB8D88_OUTPUT_CALL','CB8D88:ENTRY_MODE_ZERO_OUTPUT','CB8DCC:MULTIBYTE_OUTPUT_ARGS_PRESERVED','CB8DD0:MULTIBYTETOWIDECHAR_IAT_READ_OUTPUT','CB8DD4:MULTIBYTETOWIDECHAR_TAILCALL_OUTPUT','ORIGINAL_API_CONTRACT:OUTPUT_RETURN_38','CB7824:OUTPUT_RETURN_38','CB7834:SET_STATUS_ZERO','CB76B0:COMPLETE_RETURN','CFD514:CFD570_CALL','CFD570:ENTRY_WITH_JOINED_LOWIO','CFD5B0:CFD0B0_PARSER_CALL','CFD0B0:ENTRY','CFD0B0:RETURN','CFD5E8:CC08E8_CALL','CC08E8:ENTRY_JOINED_STARTUP_TABLE','LOWIO_ENTERCRITICALSECTION_GLOBAL7','LOWIO_ENTERCRITICALSECTION_RECORD0','LOWIO_LEAVECRITICALSECTION_GLOBAL7','CC08E8:RETURN_INDEX0','CFD658:CREATEFILEW_CALL_SOURCE_EXACT','WINDOWS_OS_CONTRACT:CREATEFILEW_INVALID_HANDLE_ERROR_PATH_NOT_FOUND','CFD65C:CREATEFILEW_RETURN_INVALID_HANDLE','CFD678:INVALID_HANDLE_FAILURE_BRANCH','CFD6FC:GETLASTERROR_CALL_SOURCE_EXACT','WINDOWS_OS_CONTRACT:GETLASTERROR_RETURN_3','CFD700:CAEC20_CALL_ERROR3','CAEC20:ENTRY_ERROR3','CB41D0:ENTRY_1','CBA180:FLS_DISPATCH_1','NATIVE_FLS_GETTER:ENTRY','NATIVE_FLS_GETTER:RETURN_1','CAEC38:THREAD_OWNER_1','CAEB48:MAP_ERROR3','CAEC58:CRT_ERROR2','CB41D0:ENTRY_2','CBA180:FLS_DISPATCH_2','NATIVE_FLS_GETTER:ENTRY','NATIVE_FLS_GETTER:RETURN_2','CAEC60:THREAD_OWNER_2','CFD704:CAEC20_RETURN_THREADPTR_OS3_CRT2','CFD5DC:CAECF8_CALL_CURRENT_CRT2','CAECF8:ENTRY_CURRENT_THREAD','CB41D0:ENTRY_3','CBA180:FLS_DISPATCH_3','NATIVE_FLS_GETTER:ENTRY','NATIVE_FLS_GETTER:RETURN_3','CAED08:THREAD_OWNER_3','CAED24:RETURN_CRT_ERROR_POINTER','CFD5E0:LOAD_CRT_ERROR2','CFD5E4:BRANCH_ERROR_RETURN','CFD980:ERROR_EPILOGUE','CFD518:CFD570_COMPLETE_RETURN_CRT2_OWNER76_LIVE','CFD51C:CURRENT_OWNER_FLAG_READ','CFD520:OWNER_FLAG_ONE_TAKE_CLEANUP','CFD524:SELECT_CURRENT_76_OWNER','CFD528:CB1650_CALL_CURRENT_76','CB1650:ENTRY_CURRENT_76','CB1660:NONNULL_OWNER','CB167C:HEAPFREE_CALL_EXACT_CURRENT_76','OWNED_HEAPFREE:RETURN_SUCCESS_CURRENT_76','CB1680:HEAPFREE_SUCCESS','CB16A0:FREE_WRAPPER_SUCCESS_EPILOGUE','CFD52C:CURRENT_76_OWNER_RELEASED_BEGIN_PARENT_EPILOGUE','CFCC9C:CFD410_COMPLETE_RETURN_CRT2','CFCCA0:STORE_RETURN2_LOCAL','CFCCA4:LOAD_CLEANUP_FLAG1','CFCCA8:FLAG1_ENTER_CLEANUP','CFCCAC:RETURN2_ENTER_ERROR_CLEANUP','CFCCB0:LOAD_INDEX0','CFCCC8:LOAD_LOWIO_BLOCK0','CFCCD0:READ_RECORD0_ACTIVE_ZERO','CFCCD8:CLEAR_RECORD0_ACTIVE_IDEMPOTENT','CFCCDC:LOAD_INDEX0_FOR_RELEASE','CFCCE0:CC08C0_RELEASE_CALL_INDEX0','CC08C0:ENTRY_INDEX0','CC08E4:TAIL_LEAVE_RECORD0','LOWIO_LEAVECRITICALSECTION_RECORD0','CFCCE4:RECORD0_LOCK_RELEASED','CFCCE8:RESTORE_RESULT_MINUS1','CFCCEC:RESTORE_DONE_RETURN2','CFCCF0:BRANCH_CFCC18_EPILOGUE','CFCC4C:CFCC18_EPILOGUE','CFA9C0:CFCC18_COMPLETE_RETURN2_BRANCH_NONZERO','CFA99C:ERROR_BRANCH_TARGET','CFA9A0:ZERO_RETURN_BRANCH_EPILOGUE','CFA9F8:CFA968_EPILOGUE','CED178:CFA968_RETURN_ZERO','CED17C:STORE_ZERO_RESULT','CED180:ZERO_RESULT_BRANCH_CLEANUP','CED184:LOAD_SELECTED_FOR_CLEANUP','CED188:CC60E0_SELECTED_CLEANUP_CALL','CC60E0:ENTRY_SELECTED_EXACT','CC60E0:TAIL_ATOMIC_EXCHANGE_ZERO','ATOMIC_EXCHANGE:SOURCE_RUNTIME_FLAG_80000000','ATOMIC_EXCHANGE:FALLBACK_LDAXR','ATOMIC_EXCHANGE:FALLBACK_STLXR_ZERO','ATOMIC_EXCHANGE:STORE_SUCCESS','ATOMIC_EXCHANGE:RETURN_OLD_2000','CED18C:CC60E0_RETURN_CLAIM_CLEARED_LOCK_HELD','CED190:CB3480_SELECTED_LOCK_RELEASE_CALL','CB3480:ENTRY_SELECTED_LOCK_HELD','CB3484:LOAD_LEAVECRITICALSECTION_IAT','CB3488:LEAVECRITICALSECTION_TARGET_EXACT','CB348C:TAIL_LEAVE_SELECTED_PLUS48','SELECTED_LEAVECRITICALSECTION_LOCK_RELEASED','CED194:SELECTED_LOCK_RELEASED_OUTER_RETURN_FRONTIER','CED198:ZERO_BRANCH_CED110','CED110:EPILOGUE_ENTRY_ZERO','CED120:RET_TO_CED330_EXACT','CED330:CED0D8_ZERO_RETURN_CALLER_FRONTIER','CED334:ZERO_RESULT_BRANCH_TO_CAECF8','CED338:CAECF8_CALL_SAME_THREAD_CRT2','CAECF8:ENTRY_OUTER_CURRENT_THREAD_CRT2']
 assert calls==expected_calls,(len(calls),[(i,a,b) for i,(a,b) in enumerate(zip(calls,expected_calls)) if a!=b],calls[len(expected_calls):],expected_calls[len(calls):])
 assert reads==[('global',0xcfa2f4)]
 assert mode_reads==[(0xcfa300,0,1),(0xcfa360,1,1),(0xcfa4d4,1,1),(0xcfa4ec,1,1)]
 assert keywrites==expected_keywrites and en_writes==expected_en_writes
 assert en_reads==[(0xcb6548,0x16a2a84,4,0),(0xcb6558,0x16072d8,8,n.base+0x1607180),(0xcb6558,0x16072e0,8,n.base+0x1607650)]
 assert pointed_reads==[(0xcfd46c,0x160718c,4,0)]
 assert callback_reads==[(0xcb9f78,0x1b60000,8,callback_target)] and cfg_reads==[(0xf5d434,0xf7e7b8,8,n.base+0x1a8c0)]
 assert callback_invocations==callback_returns==1 and os_query_calls==os_output_calls==heap_calls==heap_free_calls==createfile_calls==getlasterror_calls==1 and owner=={'live':False,'released':True}
 assert conversion_iat_reads==[(0xcb8dd0,0xf7e2e8,8,os_query_target)]*2
 assert heap_reads==[(0xcb16e8,0x16a3240,8,heap_handle),(0xcb16f0,0xf7e280,8,heap_alloc_target),('GetLastError_IAT',0xcfd6f8,0xf7e468,8,getlasterror_target),('owner_flag',0xcfd51c,-1760,1,1),('HeapFree_heap',0xcb166c,0x16a3240,8,heap_handle),('HeapFree_IAT',0xcb1674,0xf7e278,8,heap_free_target)]
 assert hashlib.sha256(bytes(u.mem_read(n.base+0x16072d8,16))).hexdigest()==AUTH['0x16072d8']['file_initial_sha256']
 assert bytes(u.mem_read(n.base,EC.PE.OPTIONAL_HEADER.SizeOfImage))==before_image
 expected_selected=bytearray(before_selected);expected_selected[20:24]=bytes(4)
 assert bytes(u.mem_read(selected,88))==bytes(expected_selected) and bytes(u.mem_read(selected+48,40))==before_selected[48:88]
 assert bytes(u.mem_read(c.dw_entry_sp-1392,640))==before_output
 expected_heap=bytearray(before_owned_heap);wide=before_output[:38].decode('utf-8').encode('utf-16-le');assert len(wide)==76 and hashlib.sha256(wide).hexdigest()==APIO['output_sha256']
 off=utf_output-owned_heap;expected_heap[off:off+76]=wide
 assert bytes(u.mem_read(owned_heap,owned_heap_size))==expected_heap
 expected_lowio=bytearray(before_lowio);expected_lowio[56]=0
 assert bytes(u.mem_read(low_ptr,64*72))==bytes(expected_lowio)
 assert lowio_writes==[(0xcc0a14,low_ptr+56,1,1),(0xcc0a20,low_ptr+40,8,0xffffffffffffffff),(0xcfd6f0,low_ptr+56,1,0),(0xcfccd8,low_ptr+56,1,0)]
 assert lowio_api_events==[('EnterCriticalSection',low_global7,n.base+0xcc090c,c.dw_entry_sp-2192),('EnterCriticalSection',low_record0,n.base+0xcc09cc,c.dw_entry_sp-2192),('LeaveCriticalSection',low_global7,n.base+0xcc0978,c.dw_entry_sp-2192),('LeaveCriticalSection',low_record0,n.base+0xcfcce4,c.dw_entry_sp-1680),('LeaveCriticalSection',selected+48,n.base+0xced194,c.dw_entry_sp-1552)]
 assert low_depths=={low_global7:0,low_record0:0}
 assert int.from_bytes(u.mem_read(n.base+0x16a2a90,8),'little')==low_ptr and int.from_bytes(u.mem_read(n.base+0x16a2e90,4),'little')==64
 assert bytes(u.mem_read(utf_output-32,32))==b'\xa9'*32 and bytes(u.mem_read(utf_output+76,32))==b'\xa9'*32
 assert int.from_bytes(u.mem_read(c.dw_entry_sp-1784,8),'little')==utf_output
 assert int.from_bytes(u.mem_read(c.dw_entry_sp-1776,8),'little')==38
 assert int.from_bytes(u.mem_read(c.dw_entry_sp-1768,8),'little')==37
 assert int.from_bytes(u.mem_read(c.dw_entry_sp-1760,1),'little')==1
 assert int.from_bytes(u.mem_read(n.base+GLOBAL_RVA,4),'little')==0
 assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcaecf8
 assert not ey_pending and not fa_pending and not fc_pending and not fd_pending and len(fa_writes)==3 and len(fc_writes)==1 and len(fd_writes)==1 and thread_getter_entries==thread_getter_returns==thread_calls==3
 assert ey_state['stack_before'] is not None and bytes(u.mem_read(n.stack,65536))==bytes(ey_state['stack_model'])
 assert bytes(u.mem_read(thread_page,0x1000))==bytes(expected_thread)
 assert bytes(u.mem_read(teb,8192))==before_teb and bytes(u.mem_read(fls_data,8192))==before_fls_data and bytes(u.mem_read(fls_slab,8192))==before_fls_slab
 assert int.from_bytes(u.mem_read(thread_ptr+36,4),'little')==3 and int.from_bytes(u.mem_read(thread_ptr+32,4),'little')==2
 assert len(native_getter_reads)==9 and native_getter_reads[:3]==native_getter_reads[3:6]==native_getter_reads[6:9]
 assert ff_reads==[(0x12d4,runtime_atomic_flag,4,0x80000000),(0x12e8,selected+20,4,0x2000),(0xced18c,c.dw_entry_sp-1536,8,selected),(0xcb3484,0xf7e0c0,8,c.apis['LeaveCriticalSection'])]
 assert len(ff_writes)==7 and ff_writes[-1]==(0x12ec,selected+20,4,0)
 assert int.from_bytes(u.mem_read(runtime_atomic_flag,4),'little')==0x80000000
 assert not selected_lock_held and not c.ec_lock_held
 return {
  'selected_placement_bias':sel_bias,'selected_owned_offset':selected-0x93000000,'owned_UTF16_offset':utf_output-owned_heap,
  'CFA9BC_CFD550_arguments_exact':True,'CFD550_register_reshape_exact':True,'CFCC18_validation_prefix_qualified':True,
  'CFCC98_CFD410_arguments_exact':True,'CFD410_executed':True,'CB6520_return_qualified':True,
  'pointed_object_field_read_executed':True,'native_front_selected_field_authority_joined':True,
  'selected_field_zero_branch_taken':True,'native_callback_cache_slot_read_qualified':True,'native_callback_return_one_qualified':True,
  'CB76B0_nonempty_source_branch_qualified':True,'CB8D88_mode_zero_dispatch_qualified':True,'MultiByteToWideChar_query_arguments_qualified':True,
  'exact_original_API_query_return_qualified':True,'exact_original_API_output_return_qualified':True,'exact_query_return_characters':38,'exact_output_return_characters':38,
  'derived_UTF16_allocation_bytes':76,'owned_process_heap_handle_read_qualified':True,'owned_HeapAlloc_contract_executed':True,'original_CB16C0_allocator_executed':True,'original_CB16C0_allocator_return_qualified':True,
  'complete_CB76B0_return_qualified':True,'converted_UTF16_output_exact':True,'converted_UTF16_output_sha256':APIO['output_sha256'],
  'selected_object_unchanged_before_CC60E0':True,'selected_object_cleanup_mutation_exact':True,'selected_object_claim_cleared':True,'formatted_output_unchanged':True,'selected_object_lock_retained_held_before_release':True,'global_index8_lock_released':True,
  'post_conversion_parent_resume_qualified':True,'startup_lowIO_lifetime_join_qualified':True,'startup_lowIO_pointer_owned_offset':low_ptr-boot.own,'startup_lowIO_count':64,'startup_lowIO_block_sha256':low_sha,'startup_lowIO_state_unchanged_to_CFD570_entry':True,'CFD570_call_arguments_qualified':True,'CFD570_executed':True,'CFD0B0_parser_return_qualified':True,'CC08E8_executed':True,'CC08E8_return_index':0,'joined_lowIO_record0_selected_under_owned_fixture':True,'native_lowIO_record_selection_qualified':False,'lowIO_global7_lock_released':True,'lowIO_record0_lock_retained_held':True,'CreateFileW_arguments_qualified':True,'CreateFileW_executed_under_same_boot_exact_OS_contract':True,'CreateFileW_invalid_handle_qualified':True,'CreateFileW_last_error_authority':3,'exact_source_callsite_breakpoint_observed':False,'invalid_handle_failure_branch_qualified':True,'lowIO_record_active_cleared_on_failure':True,'GetLastError_executed':True,'GetLastError_return_qualified':True,'GetLastError_return_u32':3,'thread_slot_source_producer_joined':True,'thread_slot_owned_fixture':slot,'thread_owner_pointer':hex(thread_ptr),'thread_owner_bytes':968,'thread_owner_sha256_before_error':thread_sha,'thread_owner_matches_current_CRT_next_allocation':True,'thread_producer_invalid_API_requests_rejected':cv_detail['invalid_API_requests_rejected_before_effect'],'native_FlsGetValue2_original_instructions_executed':True,'native_FlsGetValue2_instruction_visits':native_getter_instructions,'native_FlsGetValue2_reads':len(native_getter_reads),'EZ_original_source_instruction_visits':ey_source_visits,'CAEC20_executed':True,'CAEC20_error3_to_thread_OS3_CRT2_qualified':True,'CAECF8_executed':True,'CAECF8_returned_current_thread_CRT_error_pointer':True,'CFD570_complete_error_return_qualified':True,'CFD570_return_u32':2,'current_UTF16_owner_bytes':76,'current_UTF16_owner_flag_u8':1,'current_UTF16_owner_pointer_selected_exact':True,'current_UTF16_owner_released':True,'parent_cleanup_executed':True,'original_CB1650_executed':True,'owned_HeapFree_contract_executed':True,'HeapFree_success_return_u32':1,'older_74byte_cleanup_geometry_reused':False,'old_74byte_geometry_negative_rejected':True,'no_original_reads_of_released_current_owner':True,'CFD410_complete_return_qualified':True,'CFD410_return_u32':2,'caller_resume_executed':True,'caller_cleanup_flag_u32':1,'caller_index_u32':0,'caller_return_store_u32':2,'lowIO_record0_active_clear_qualified':True,'lowIO_record0_lock_released':True,'CC08C0_executed':True,'CFCC18_complete_error_return_qualified':True,'CFCC18_return_u32':2,'outer_caller_resume_executed':True,'CFA9C0_nonzero_branch_target_RVA':'0xcfa99c','CFA968_complete_error_return_qualified':True,'CFA968_return_u64':0,'outer_zero_result_cleanup_branch_taken':True,'selected_cleanup_pointer_exact':True,'CC60E0_executed':True,'CC60E0_claim_old_u32':0x2000,'CC60E0_claim_new_u32':0,'source_runtime_atomic_flag_joined_u32':0x80000000,'selected_object_lock_retained_held_after_CC60E0':True,'CB3480_executed':True,'selected_object_lock_release_executed':True,'selected_object_lock_released':True,'CED0D8_complete_return_qualified':True,'CED0D8_return_u64':0,'CED0D8_return_target_RVA':'0xced330','outer_result_pointer_SP_relative':-1448,'outer_result_store_executed':True,'outer_result_store_value_u64':0,'outer_zero_branch_qualified':True,'same_thread_error_authority_rejoined':True,'same_thread_CRT_error_u32':2,'next_source_RVA':'0xcaecf8','FD_exact_stack_store_chunks':len(fd_writes),'FC_exact_stack_store_chunks':len(fc_writes),'FC_exact_reads':len(fc_reads),'FA_exact_stack_store_chunks':len(fa_writes),'EZ_exact_source_store_chunks':len(ey_writes),'rejected_altered_contracts':neg
 }

def main():
 rows=[one_case(x) for x in (0,1,40,1230)]
 for r in rows:print(json.dumps(r),flush=True)
 assert len(rows)==4 and len({x['rejected_altered_contracts'] for x in rows})==1,[x['rejected_altered_contracts'] for x in rows]
 result={
  'experiment':'E011FI','status':'PASS_CED330_ZERO_STORE_BRANCH_TO_CAECF8_FRONTIER','base_commit':'4c159a6c',
  'inherited_E011FH_result_sha256':hashlib.sha256(FH_RESULT.read_bytes()).hexdigest(),
  'inherited_E011FG_result_sha256':hashlib.sha256(FG_RESULT.read_bytes()).hexdigest(),
  'inherited_E011FF_result_sha256':hashlib.sha256(FF_RESULT.read_bytes()).hexdigest(),
  'inherited_E011FE_result_sha256':hashlib.sha256(FE_RESULT.read_bytes()).hexdigest(),
  'inherited_E011FC_result_sha256':hashlib.sha256(FC_RESULT.read_bytes()).hexdigest(),
  'inherited_E011EJ_result_sha256':hashlib.sha256(EJ_RESULT.read_bytes()).hexdigest(),
  'inherited_E011EJ_source_safe_sha256':hashlib.sha256(EJ_SOURCE.read_bytes()).hexdigest(),
  'inherited_E011FB_result_sha256':hashlib.sha256(FB_RESULT.read_bytes()).hexdigest(),
  'inherited_E011FA_result_sha256':hashlib.sha256(FA_RESULT.read_bytes()).hexdigest(),
  'inherited_E011EZ_result_sha256':hashlib.sha256(EZ_RESULT.read_bytes()).hexdigest(),
  'inherited_E011EY_result_sha256':hashlib.sha256(EY_RESULT.read_bytes()).hexdigest(),
  'inherited_E011EX_result_sha256':hashlib.sha256((ROOT/'experiments/E004-front-ir-vd55g0/e011ex-exact-getlasterror-caec20-frontier/RESULT.json').read_bytes()).hexdigest(),
  'inherited_E011CV_result_sha256':hashlib.sha256(CV_RESULT.read_bytes()).hexdigest(),
  'inherited_E011CV_source_sha256':hashlib.sha256(CV_PATH.read_bytes()).hexdigest(),
  'inherited_E011CW_result_sha256':hashlib.sha256(CW_RESULT.read_bytes()).hexdigest(),
  'inherited_E011CW_code_authority_sha256':hashlib.sha256(CW_AUTH.read_bytes()).hexdigest(),
  'pins':PINS,'case_count':4,'thread_slot_fixture_axis':[1,16,37,63],
  'thread_slot_source_producer_joined':True,'thread_owner_bytes':968,'thread_owner_matches_current_CRT_next_allocation':True,
  'source_qualified_state_join_not_native_startup_replay':True,
  'native_FlsGetValue2_original_instructions_executed':True,'native_FlsGetValue2_total_instruction_visits':sum(x['native_FlsGetValue2_instruction_visits'] for x in rows),'native_FlsGetValue2_total_reads':sum(x['native_FlsGetValue2_reads'] for x in rows),
  'CAEC20_executed':True,'CAEC20_error3_to_thread_OS3_CRT2_qualified':True,'CAECF8_executed':True,'CAECF8_returned_current_thread_CRT_error_pointer':True,
  'thread_OS_error_offset':36,'thread_CRT_error_offset':32,'thread_OS_error_u32':3,'thread_CRT_error_u32':2,
  'CFD570_complete_error_return_qualified':True,'CFD570_return_u32':2,
  'EZ_original_source_instruction_visits':sum(x['EZ_original_source_instruction_visits'] for x in rows),'EZ_exact_source_store_chunks':sum(x['EZ_exact_source_store_chunks'] for x in rows),
  'thread_producer_invalid_API_requests_rejected':sum(x['thread_producer_invalid_API_requests_rejected'] for x in rows),
  'current_UTF16_owner_bytes':76,'current_UTF16_owner_flag_u8':1,'current_UTF16_owner_pointer_selected_exact':True,'current_UTF16_owner_released':True,'CFA968_complete_error_return_qualified':True,'CFA968_return_u64':0,'outer_zero_result_cleanup_branch_taken':True,'selected_cleanup_pointer_exact':True,'selected_object_unchanged_before_CC60E0':True,'selected_object_cleanup_mutation_exact':True,'selected_object_claim_cleared':True,'selected_object_lock_retained_held_before_release':True,'CC60E0_executed':True,'CC60E0_claim_old_u32':0x2000,'CC60E0_claim_new_u32':0,'source_runtime_atomic_flag_joined_u32':0x80000000,'selected_object_lock_retained_held_after_CC60E0':True,'CB3480_executed':True,'selected_object_lock_release_executed':True,'selected_object_lock_released':True,'CED0D8_complete_return_qualified':True,'CED0D8_return_u64':0,'CED0D8_return_target_RVA':'0xced330','outer_result_pointer_SP_relative':-1448,'outer_result_store_executed':True,'outer_result_store_value_u64':0,'outer_zero_branch_qualified':True,'same_thread_error_authority_rejoined':True,'same_thread_CRT_error_u32':2,'caller_cleanup_flag_u32':1,'caller_index_u32':0,'caller_return_store_u32':2,'lowIO_record0_active_clear_qualified':True,'lowIO_record0_lock_released':True,'CC08C0_executed':True,'CFCC18_complete_error_return_qualified':True,'CFCC18_return_u32':2,'outer_caller_resume_executed':True,'CFA9C0_nonzero_branch_target_RVA':'0xcfa99c','CFA968_complete_error_return_qualified':True,'CFA968_return_u64':0,'parent_cleanup_executed':True,'original_CB1650_executed':True,'owned_HeapFree_contract_executed':True,'HeapFree_success_return_u32':1,'old_74byte_geometry_negative_rejected':True,'no_original_reads_of_released_current_owner':True,'CFD410_complete_return_qualified':True,'CFD410_return_u32':2,'caller_resume_executed':True,
  'older_E011CW_UTF16_owner_bytes':74,'older_E011CW_cleanup_geometry_reused':False,
  'next_source_RVA':'0xcaecf8','next_return_target_RVA':'0xced33c','next_expected_CRT_error_u32':2,
  'live_Windows_loader_full_CRT_TLS_locale_concurrency_qualified':False,'original_Windows_FlsAlloc_or_FlsSetValue_executed':False,
  'native_mutex_bytes_or_concurrency_qualified':False,'rejected_altered_contracts':sum(x['rejected_altered_contracts'] for x in rows),
  'new_front_camera_starts':0,'new_rear_camera_starts':0,'new_reboots':0,'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='details'},sort_keys=True),flush=True)
if __name__=='__main__':main()
