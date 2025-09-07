# Install SecureWipe backend as a Windows service
$exePath = "C:\securewipe\backend\target\release\securewipe.exe"
New-Service -Name "SecureWipeService" -BinaryPathName $exePath -DisplayName "SecureWipe Data Erasure" -StartupType Automatic
Start-Service -Name "SecureWipeService"
Write-Host "SecureWipe service installed and started."
