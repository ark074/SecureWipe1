# SecureWipe Windows Agent

## Build Backend
```powershell
cd backend
cargo build --release
```
Binary will be at `backend\target\release\securewipe.exe`.

## Create Test Disk
```powershell
cd agent\windows
./create_vhdx.ps1 -Path E:\test_disk.vhdx -SizeGB 1
```

## Install as Service
```powershell
./install_service.ps1
```

## Run Manually
```powershell
backend\target\release\securewipe.exe
```

## Notes
- Requires PowerShell with Hyper-V module enabled for VHDX management.
- Always test on virtual disks before using on real hardware!
