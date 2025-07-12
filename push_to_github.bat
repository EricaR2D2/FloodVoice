@echo off
echo Pushing NYC Public Health MVP updates to GitHub...
echo.

echo Switching to bugfix branch...
git checkout bugfix 2>nul || git checkout -b bugfix

echo Adding all changes...
git add .

echo Committing changes...
git commit -m "Polish: Demo readiness improvements for Wednesday presentation

- Added data freshness verification with visual indicators
- Improved loading state with overlay and animations
- Standardized error handling with custom error pages

These polish improvements enhance the demo experience without adding new features."

echo Pushing to GitHub bugfix branch...
git push origin bugfix

echo.
echo ✅ Code pushed to GitHub!
echo 🔗 Branch: bugfix
echo 🔗 Share this link: https://github.com/EricaR2D2/PublicHealthMVP/tree/bugfix
echo.
pause

