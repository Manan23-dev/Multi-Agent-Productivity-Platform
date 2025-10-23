# FlowAgent Deployment Troubleshooting Guide

## 🚀 Quick Fix for Vercel Deployment

### Option 1: Simplified Deployment (Recommended)

1. **Use the simplified vercel.json** (already configured)
2. **Deploy only the frontend first**:
   - Go to [Vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Configure:
     - **Framework**: Create React App
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `build`
   - Click "Deploy"

### Option 2: Full Stack Deployment

If you want both frontend and API:

1. **Update vercel.json** to:
```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/build",
  "installCommand": "cd frontend && npm install",
  "functions": {
    "api/**/*.js": {
      "runtime": "nodejs18.x"
    }
  }
}
```

2. **Deploy with API routes**:
   - Framework: Other
   - Root Directory: `.` (root)
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/build`

## 🔧 Common Issues & Solutions

### Issue 1: Build Command Failed
**Error**: `Build Command failed`
**Solution**: 
- Make sure `frontend/package.json` exists
- Check that all dependencies are in `package.json`
- Try: `cd frontend && npm install && npm run build`

### Issue 2: Functions Property Conflict
**Error**: `The functions property cannot be used in conjunction with the builds property`
**Solution**: Use the simplified vercel.json above

### Issue 3: Module Not Found
**Error**: `Cannot find module`
**Solution**: 
- Check that all imports are correct
- Make sure dependencies are installed
- Verify file paths are correct

### Issue 4: TypeScript Errors
**Error**: `TypeScript compilation failed`
**Solution**: 
- Run `npm run build` locally first
- Fix any TypeScript errors
- Commit and push changes

## 🧪 Test Locally First

Before deploying, test locally:

```bash
# Test frontend build
cd frontend
npm install
npm run build

# Test API files
cd ../api
node -c health.js
node -c status.js
```

## 📋 Deployment Checklist

- [ ] Frontend builds successfully (`npm run build`)
- [ ] All API files have valid syntax
- [ ] vercel.json is properly configured
- [ ] All dependencies are in package.json
- [ ] No TypeScript errors
- [ ] Git repository is up to date

## 🆘 Still Having Issues?

1. **Check Vercel logs** in the deployment dashboard
2. **Try deploying just the frontend** first
3. **Use Vercel CLI**: `npx vercel --prod`
4. **Check GitHub repository** is properly connected

## 🎯 Minimal Working Configuration

For a basic deployment that should work:

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/build"
}
```

This will deploy only the frontend, which is often sufficient for testing.
