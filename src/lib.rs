use windows::{
    core::*,
    Win32::Foundation::*,
    Win32::UI::Shell::*,
    Win32::System::Com::*,
};

// 1. あなたの拡張機能専用の UUID を定義
// ※ guidgen.exe 等で生成した独自のものに差し替えるのが理想です
pub const CLSID_MY_FOLDER: GUID = GUID::from_u128(0x550e8400_e29b_41d4_a716_446655440000);

// 2. 仮想フォルダの実体となる構造体
#[implement(IShellFolder, IPersistFolder)]
struct MyVirtualFolder;

// 3. IShellFolder インターフェースの実装
// エクスプローラーがフォルダの中身や名前を問い合わせる窓口です
impl IShellFolder_Impl for MyVirtualFolder {
    fn ParseDisplayName(&self, _: HWND, _: &IBindCtx, _: &PCWSTR, _: *mut u32, _: *mut *mut ITEMIDLIST, _: *mut u32) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn EnumObjects(&self, _: HWND, _: SHCONTF) -> Result<IEnumIDList> {
        // 空の列挙子を返すか、E_NOTIMPL を返すと「空のフォルダ」になります
        Err(E_NOTIMPL.into())
    }

    fn BindToObject(&self, _: *const ITEMIDLIST, _: &IBindCtx, _: &GUID, _: *mut *mut std::ffi::c_void) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn CompareIDs(&self, _: LPARAM, _: *const ITEMIDLIST, _: *const ITEMIDLIST) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn CreateViewObject(&self, _: HWND, _: &GUID, _: *mut *mut std::ffi::c_void) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn GetAttributesOf(&self, _: u32, _: *const *const ITEMIDLIST, rgf_inout: *mut u32) -> Result<()> {
        unsafe { *rgf_inout = 0; }
        Ok(())
    }

    fn GetUIObjectOf(&self, _: HWND, _: u32, _: *const *const ITEMIDLIST, _: &GUID, _: *mut u32, _: *mut *mut std::ffi::c_void) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn GetDisplayNameOf(&self, _: *const ITEMIDLIST, _: SHGDNF) -> Result<STRRET> {
        Err(E_NOTIMPL.into())
    }

    fn SetNameOf(&self, _: HWND, _: *const ITEMIDLIST, _: &PCWSTR, _: u32) -> Result<*mut ITEMIDLIST> {
        Err(E_NOTIMPL.into())
    }
}

// 4. IPersistFolder の実装
// フォルダがどこに配置されているかを管理するために必要です
impl IPersistFolder_Impl for MyVirtualFolder {
    fn GetClassID(&self) -> Result<GUID> {
        Ok(CLSID_MY_FOLDER)
    }

    fn Initialize(&self, _pidl: *const ITEMIDLIST) -> Result<()> {
        Ok(())
    }
}

use std::sync::Once;
use windows::Win32::System::SystemServices::DLL_PROCESS_ATTACH;

// --- クラスファクトリの実装 ---
// Windowsが「MyVirtualFolderのインスタンスを作ってくれ」と頼むための仲介役です
#[implement(IClassFactory)]
struct MyClassFactory;

impl IClassFactory_Impl for MyClassFactory {
    fn CreateInstance(&self, punkouter: Option<&IUnknown>, riid: *const GUID, ppvobject: *mut *mut std::ffi::c_void) -> Result<()> {
        if punkouter.is_some() {
            return Err(CLASS_E_NOAGGREGATION.into());
        }
        let folder = MyVirtualFolder;
        unsafe { folder.cast(riid, ppvobject) }
    }

    fn LockServer(&self, _flock: BOOL) -> Result<()> {
        Ok(())
    }
}

// --- Windows OS から直接呼ばれる公開関数 ---

// DLLがロードされた時の処理（必要に応じて）
#[no_mangle]
extern "system" fn DllMain(_: HINSTANCE, dw_reason: u32, _: *const std::ffi::c_void) -> bool {
    if dw_reason == DLL_PROCESS_ATTACH {
        // 初期化が必要ならここに書く
    }
    true
}

// WindowsがこのDLLに「CLSIDに対応するオブジェクトをくれ」と頼む関数
#[no_mangle]
extern "system" fn DllGetClassObject(rclsid: *const GUID, riid: *const GUID, ppv: *mut *mut std::ffi::c_void) -> HRESULT {
    unsafe {
        if *rclsid == CLSID_MY_FOLDER {
            let factory = MyClassFactory;
            factory.cast(riid, ppv)
        } else {
            CLASS_E_CLASSNOTAVAILABLE.into()
        }
    }
}

// DLLをメモリから解放していいか確認する関数
#[no_mangle]
extern "system" fn DllCanUnloadNow() -> HRESULT {
    S_FALSE // 簡略化のため常にロード状態を維持（デバッグ中はS_OKにするのが一般的）
}