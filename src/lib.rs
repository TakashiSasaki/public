use windows::{
    core::*,
    Win32::Foundation::*,
    Win32::System::Com::*,
    Win32::UI::Shell::*,
    Win32::UI::Shell::Common::*,
};

pub const CLSID_MY_FOLDER: GUID =
    GUID::from_u128(0x550e8400_e29b_41d4_a716_446655440000);

#[implement(
    windows::Win32::UI::Shell::IShellFolder,
    windows::Win32::System::Com::IPersist,
    windows::Win32::UI::Shell::IPersistFolder
)]
struct MyVirtualFolder;

impl IShellFolder_Impl for MyVirtualFolder_Impl {
    fn ParseDisplayName(
        &self,
        _: HWND,
        _: Option<&IBindCtx>,
        _: &PCWSTR,
        _: *const u32,
        _: *mut *mut ITEMIDLIST,
        _: *mut u32,
    ) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn EnumObjects(
        &self,
        _: HWND,
        _: u32, // ← 重要：windows-rs 0.58 では u32
        ppenumidlist: *mut Option<IEnumIDList>,
    ) -> HRESULT {
        unsafe {
            if !ppenumidlist.is_null() {
                *ppenumidlist = None;
            }
        }
        S_FALSE
    }

    fn BindToObject(
        &self,
        _: *const ITEMIDLIST,
        _: Option<&IBindCtx>,
        _: *const GUID,
        _: *mut *mut core::ffi::c_void,
    ) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn BindToStorage(
        &self,
        _: *const ITEMIDLIST,
        _: Option<&IBindCtx>,
        _: *const GUID,
        _: *mut *mut core::ffi::c_void,
    ) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn CompareIDs(
        &self,
        _: LPARAM,
        _: *const ITEMIDLIST,
        _: *const ITEMIDLIST,
    ) -> HRESULT {
        S_OK
    }

    fn CreateViewObject(
        &self,
        _: HWND,
        _: *const GUID,
        _: *mut *mut core::ffi::c_void,
    ) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn GetAttributesOf(
        &self,
        _: u32,
        _: *const *const ITEMIDLIST,
        rgf_inout: *mut u32,
    ) -> Result<()> {
        unsafe {
            if !rgf_inout.is_null() {
                *rgf_inout = 0;
            }
        }
        Ok(())
    }

    fn GetUIObjectOf(
        &self,
        _: HWND,
        _: u32,
        _: *const *const ITEMIDLIST,
        _: *const GUID,
        _: *const u32,
        _: *mut *mut core::ffi::c_void,
    ) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn GetDisplayNameOf(
        &self,
        _: *const ITEMIDLIST,
        _: SHGDNF,
        _: *mut STRRET,
    ) -> Result<()> {
        Err(E_NOTIMPL.into())
    }

    fn SetNameOf(
        &self,
        _: HWND,
        _: *const ITEMIDLIST,
        _: &PCWSTR,
        _: SHGDNF,
        _: *mut *mut ITEMIDLIST,
    ) -> Result<()> {
        Err(E_NOTIMPL.into())
    }
}

impl IPersist_Impl for MyVirtualFolder_Impl {
    fn GetClassID(&self) -> Result<GUID> {
        Ok(CLSID_MY_FOLDER)
    }
}

impl IPersistFolder_Impl for MyVirtualFolder_Impl {
    fn Initialize(&self, _: *const ITEMIDLIST) -> Result<()> {
        Ok(())
    }
}

#[implement(windows::Win32::System::Com::IClassFactory)]
struct MyClassFactory;

impl IClassFactory_Impl for MyClassFactory_Impl {
    fn CreateInstance(
        &self,
        punkouter: Option<&IUnknown>,
        riid: *const GUID,
        ppvobject: *mut *mut core::ffi::c_void,
    ) -> Result<()> {
        if punkouter.is_some() {
            return Err(CLASS_E_NOAGGREGATION.into());
        }
        if ppvobject.is_null() {
            return Err(E_POINTER.into());
        }

        let folder: IUnknown = MyVirtualFolder.into();
        unsafe { folder.query(riid, ppvobject).ok() }
    }

    fn LockServer(&self, _: BOOL) -> Result<()> {
        Ok(())
    }
}

#[unsafe(no_mangle)]
extern "system" fn DllGetClassObject(
    rclsid: *const GUID,
    riid: *const GUID,
    ppv: *mut *mut core::ffi::c_void,
) -> HRESULT {
    unsafe {
        if !rclsid.is_null() && *rclsid == CLSID_MY_FOLDER {
            let factory: IClassFactory = MyClassFactory.into();
            factory.query(riid, ppv).into()
        } else {
            CLASS_E_CLASSNOTAVAILABLE
        }
    }
}

#[unsafe(no_mangle)]
extern "system" fn DllCanUnloadNow() -> HRESULT {
    S_FALSE
}
