# Vercel + Supabase Deployment Guide

## 🆓 100% Free Deployment Stack

- **Frontend**: Vercel (free forever)
- **Backend**: Supabase Edge Functions (free tier)
- **Database**: Supabase PostgreSQL (free tier)
- **Redis**: Upstash Redis (free tier)

## 📋 Prerequisites

1. **Vercel Account**: https://vercel.com (free)
2. **Supabase Account**: https://supabase.com (free)
3. **Upstash Account**: https://upstash.com (free)

## 🚀 Deployment Steps

### Step 1: Deploy Frontend to Vercel

1. Go to [Vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

5. **Environment Variables**:
   ```
   REACT_APP_API_URL=https://your-project.supabase.co/functions/v1
   ```

### Step 2: Setup Supabase Backend

1. Go to [Supabase.com](https://supabase.com)
2. Create new project
3. Go to "Edge Functions"
4. Create new function: `flowagent-api`

### Step 3: Setup Upstash Redis

1. Go to [Upstash.com](https://upstash.com)
2. Create free Redis database
3. Copy connection details

### Step 4: Configure Environment Variables

In Supabase Edge Functions:
```
OPENAI_API_KEY=your_openai_api_key
UPSTASH_REDIS_REST_URL=your_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_upstash_token
SECRET_KEY=your_secret_key
```

## 🔧 Code Changes Needed

1. **Convert FastAPI to Supabase Edge Functions**
2. **Update frontend API calls**
3. **Use Supabase client libraries**

## 💰 Cost Breakdown

- **Vercel**: $0/month (free forever)
- **Supabase**: $0/month (free tier)
- **Upstash**: $0/month (free tier)
- **Total**: $0/month

## 🎯 Benefits

- No trial periods
- No credit card required
- Generous free tiers
- Production-ready
- Global CDN
- Automatic HTTPS
- Easy scaling
