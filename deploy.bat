@echo off
chcp 65001 > nul

:: 1. 메시지 확인
if "%~1"=="" (
    echo ❌ 에러: 커밋 메시지가 없습니다.
    echo 사용법: .\deploy.bat "커밋 메시지"
    exit /b
)

echo ==========================================
echo 📦 Git Auto Push 시작...
echo 📝 메시지: %~1
echo ==========================================

:: 2. 스테이징
git add .

:: 3. 커밋
git commit -m "%~1"

:: 4. 푸시
echo 🚀 GitHub로 업로드 중...
git push origin main

echo ==========================================
echo ✅ 배포 완료!