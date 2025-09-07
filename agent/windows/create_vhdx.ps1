# Create and mount a test VHDX file (1GB) for wiping
param(
    [string]$Path = "E:\test_disk.vhdx",
    [int]$SizeGB = 1
)
New-VHD -Path $Path -SizeBytes (${SizeGB}GB) -Dynamic | Mount-VHD -Passthru | Initialize-Disk -PartitionStyle MBR -PassThru | New-Partition -AssignDriveLetter -UseMaximumSize | Format-Volume -FileSystem NTFS -Confirm:$false
Write-Host "VHDX created and mounted at $Path"
