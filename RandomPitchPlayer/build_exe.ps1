# RandomPitchPlayer EXE 빌드 PowerShell 스크립트
# Windows PowerShell에서 실행하는 고급 빌드 스크립트

param(
    [switch]$SkipDependencies,  # 의존성 설치 건너뛰기
    [switch]$AutoRelease,       # 자동으로 릴리즈 모드로 설정
    [switch]$OpenFolder         # 빌드 완료 후 dist 폴더 열기
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "RandomPitchPlayer EXE 빌드 도구" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  관리자 권한으로 실행하는 것을 권장합니다." -ForegroundColor Yellow
    Write-Host ""
}

# Python 설치 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python이 설치되지 않았거나 PATH에 없습니다." -ForegroundColor Red
    exit 1
}

# 1. 의존성 설치
if (-not $SkipDependencies) {
    Write-Host "1단계: 필요한 패키지 설치 중..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        Write-Host "✅ 패키지 설치 완료" -ForegroundColor Green
    } catch {
        Write-Host "❌ 패키지 설치 실패!" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
} else {
    Write-Host "⏭️  의존성 설치 건너뛰기" -ForegroundColor Yellow
    Write-Host ""
}

# 2. 릴리즈 모드 설정
if ($AutoRelease) {
    Write-Host "2단계: 자동 릴리즈 모드 설정 중..." -ForegroundColor Yellow
    try {
        Copy-Item "config_release.py" "config.py" -Force
        Write-Host "✅ 릴리즈 모드로 설정됨" -ForegroundColor Green
    } catch {
        Write-Host "❌ 릴리즈 모드 설정 실패!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "2단계: 빌드 모드 확인 중..." -ForegroundColor Yellow
    $configContent = Get-Content "config.py" -Raw -ErrorAction SilentlyContinue
    if ($configContent -match "RELEASE_MODE = True") {
        Write-Host "✅ 이미 릴리즈 모드로 설정됨" -ForegroundColor Green
    } else {
        Write-Host "⚠️  현재 디버그 모드입니다." -ForegroundColor Yellow
        $response = Read-Host "릴리즈 모드로 변경하시겠습니까? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Copy-Item "config_release.py" "config.py" -Force
            Write-Host "✅ 릴리즈 모드로 변경됨" -ForegroundColor Green
        } else {
            Write-Host "⚠️  디버그 모드로 계속 진행합니다." -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# 3. EXE 빌드
Write-Host "3단계: EXE 파일 빌드 중..." -ForegroundColor Yellow
try {
    python build_exe.py
    Write-Host "✅ EXE 빌드 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ EXE 빌드 실패!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🎉 빌드 완료!" -ForegroundColor Green
Write-Host "📂 dist 폴더를 확인하세요." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# 4. dist 폴더 열기 (옵션)
if ($OpenFolder -and (Test-Path "dist")) {
    Write-Host "📂 dist 폴더를 열고 있습니다..." -ForegroundColor Yellow
    Start-Process "explorer.exe" -ArgumentList "dist"
}

# 빌드 결과 요약
if (Test-Path "dist\RandomPitchPlayer.exe") {
    $exeSize = (Get-Item "dist\RandomPitchPlayer.exe").Length / 1MB
    Write-Host ""
    Write-Host "빌드 결과:" -ForegroundColor Cyan
    Write-Host "- 실행 파일: dist\RandomPitchPlayer.exe" -ForegroundColor White
    Write-Host "- 파일 크기: $($exeSize.ToString('F1')) MB" -ForegroundColor White
    Write-Host "- 빌드 시간: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
}

Write-Host ""
Write-Host "사용법:" -ForegroundColor Cyan
Write-Host "1. dist 폴더의 모든 파일을 압축" -ForegroundColor White
Write-Host "2. 사용자에게 배포" -ForegroundColor White
Write-Host "3. 사용자는 압축 해제 후 RandomPitchPlayer.exe 실행" -ForegroundColor White

Read-Host "`nEnter 키를 눌러 종료"