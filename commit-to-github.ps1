# PowerShell script to commit and push to GitHub
# Run this script from the local-buyer-intelligence directory

Write-Host "Initializing Git repository..." -ForegroundColor Green
git init

Write-Host "`nAdding all files to staging..." -ForegroundColor Green
git add .

Write-Host "`nCreating initial commit..." -ForegroundColor Green
git commit -m "Initial commit: Local Buyer Intelligence Platform foundation

- FastAPI backend with database models and API endpoints
- Next.js frontend with Mapbox integration  
- Intelligence engine for demand scoring
- Data collector templates (Census, Property, Events)
- Docker Compose setup for local development
- Comprehensive documentation"

Write-Host "`n✅ Local repository initialized and committed!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Create a repository on GitHub (https://github.com/new)" -ForegroundColor White
Write-Host "2. Copy the repository URL" -ForegroundColor White
Write-Host "3. Run these commands:" -ForegroundColor White
Write-Host "   git branch -M main" -ForegroundColor Cyan
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host "`nOr see GIT_SETUP.md for detailed instructions." -ForegroundColor White

