param(
  [Parameter(Mandatory = $true)]
  [string]$CustomerId,

  [Parameter(Mandatory = $true)]
  [string]$DeviceId,

  [string]$OutDir = "certs",

  [int]$Days = 30,

  [string]$PfxPassword = "changeit"
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$subject = "CN=$DeviceId, O=$CustomerId, OU=edr-agent-parser"
$cert = New-SelfSignedCertificate `
  -Subject $subject `
  -CertStoreLocation "Cert:\CurrentUser\My" `
  -KeyAlgorithm RSA `
  -KeyLength 2048 `
  -KeyExportPolicy Exportable `
  -KeySpec Signature `
  -HashAlgorithm SHA256 `
  -NotAfter (Get-Date).AddDays($Days)

$cerPath = Join-Path $OutDir "device.cer"
$pfxPath = Join-Path $OutDir "device.pfx"
$securePassword = ConvertTo-SecureString -String $PfxPassword -Force -AsPlainText

Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $securePassword | Out-Null

Write-Output "thumbprint=$($cert.Thumbprint)"
Write-Output "cer=$cerPath"
Write-Output "pfx=$pfxPath"
Write-Output "cert_store=Cert:\CurrentUser\My\$($cert.Thumbprint)"
Write-Output "Do not commit certs/*.pfx or private keys."
