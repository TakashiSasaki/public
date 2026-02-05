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