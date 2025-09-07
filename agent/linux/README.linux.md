# SecureWipe Linux Agent

## Build Backend
```bash
cd backend
cargo build --release
```
Binary will be at `backend/target/release/securewipe`.

## Create Loopback Test Disk
```bash
cd scripts
./create_loopback.sh
```

## Run Wipe
```bash
./backend/target/release/securewipe
```

## Notes
- Run as root if wiping block devices.
- Always test on loopback before using on real disks!
