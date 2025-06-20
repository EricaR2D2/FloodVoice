@echo off
echo Pushing NYC Public Health MVP updates to GitHub...
echo.

echo Adding all changes...
git add .

echo Committing changes...
git commit -m "Fix: Advanced dashboard authentication and map initialization issues

- Added @login_required decorators to all advanced dashboard routes
- Fixed map container double initialization error
- Improved error handling in JavaScript map functions
- Ready for collaborative debugging session"

echo Pushing to GitHub...
git push origin main

echo.
echo ✅ Code pushed to GitHub!
echo 🔗 Share this link: https://github.com/EricaR2D2/PublicHealthMVP
echo.
pause
