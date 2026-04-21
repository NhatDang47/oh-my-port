# Build script for Windows
# Run this in PowerShell from the project root:
#   .\build_windows.ps1

Write-Host "🚀 Building oh-my-port for Windows..." -ForegroundColor Cyan

# Activate uv environment and run PyInstaller
uv run pyinstaller oh-my-port.spec --distpath dist/windows --workpath build/windows --noconfirm

if ($LASTEXITCODE -eq 0) {
    $exe = "dist\windows\oh-my-port.exe"
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host "   Output: $exe" -ForegroundColor Yellow
    $size = (Get-Item $exe).Length / 1MB
    Write-Host ("   Size:   {0:N1} MB" -f $size) -ForegroundColor Yellow
} else {
    Write-Host "❌ Build failed. Check the output above for errors." -ForegroundColor Red
    exit 1
}
