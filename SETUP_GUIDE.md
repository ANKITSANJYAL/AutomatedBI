# Complete Setup Guide for AutomatedBI

## 🚀 Quick Start (Recommended)

**The fastest way to get started is using Docker which handles everything automatically:**

```bash
# 1. Clone/navigate to project directory
cd /Users/ankitsanjyal/Desktop/Projects/AutomatedBI

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env file with your API key
nano .env
# Add your GEMINI_API_KEY (get from https://makersuite.google.com/app/apikey)

# 4. Start everything with Docker
docker-compose up --build
```

**Access your application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- PostgreSQL: localhost:5432

---

## 📋 Prerequisites

### Required Software

1. **Docker & Docker Compose** (Recommended)
   ```bash
   # macOS with Homebrew
   brew install docker docker-compose
   
   # Or download Docker Desktop from https://docker.com
   ```

2. **Alternative: Local Development Setup**
   - Python 3.9+
   - Node.js 16+
   - PostgreSQL 13+

### Required API Keys

1. **Google Gemini API Key** (Required)
   - Visit: https://makersuite.google.com/app/apikey
   - Create new API key
   - Copy the key for your .env file

---

## 🛠️ Setup Methods

### Method 1: Docker Setup (Recommended)

**Benefits:** No local dependencies, consistent environment, automatic database setup

```bash
# Step 1: Prepare environment
cp .env.example .env

# Step 2: Edit .env file
nano .env
# Set: GEMINI_API_KEY=your_actual_api_key_here

# Step 3: Start all services
docker-compose up --build

# Step 4: Wait for startup (about 2-3 minutes)
# You'll see logs from postgres, backend, and frontend

# Step 5: Access the application
open http://localhost:3000
```

**Troubleshooting Docker:**
```bash
# If containers fail to start
docker-compose down
docker-compose up --build

# Check container logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs frontend

# Clean restart
docker-compose down -v
docker-compose up --build
```

### Method 2: Local Development Setup

**Step 1: PostgreSQL Setup**
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL
brew services start postgresql

# Create database and user
createuser --interactive --pwprompt automated_bi_user
# Enter password when prompted

createdb -O automated_bi_user automated_bi
```

**Step 2: Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp ../.env.example .env
# Edit .env with your database credentials and Gemini API key

# Initialize database
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"

# Start backend server
python app.py
```

**Step 3: Frontend Setup**
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Database Configuration
POSTGRES_DB=automated_bi
POSTGRES_USER=automated_bi_user
POSTGRES_PASSWORD=your_strong_password
DATABASE_URL=postgresql://automated_bi_user:your_password@localhost:5432/automated_bi

# AI Configuration (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# For Docker (use postgres as host)
# DATABASE_URL=postgresql://automated_bi_user:your_password@postgres:5432/automated_bi
```

### Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add it to your `.env` file

---

## ✅ Verification Steps

### 1. Test Database Connection
```bash
# Test PostgreSQL connection
python test_db.py
# Should output: ✅ Database connection successful!
```

### 2. Test Backend API
```bash
# Test backend health
curl http://localhost:5000/health
# Should return: {"status": "healthy"}

# Test file upload endpoint
curl http://localhost:5000/api/upload
# Should return API documentation
```

### 3. Test Frontend
- Open http://localhost:3000
- You should see the upload interface
- Try uploading a small CSV file

### 4. Test AI Integration
```bash
# Test Gemini API connection
python -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Hello')
print('✅ Gemini AI connected successfully')
"
```

---

## 🗂️ Project Structure Verification

**Check that all components are present:**

```bash
# Verify backend structure
ls -la backend/app/
# Should show: models/, agents/, services/, utils/, api/

# Verify agents are implemented
ls -la backend/app/agents/
# Should show: data_quality_analyst.py, domain_expert.py, kpi_strategist.py, dashboard_designer.py

# Verify frontend structure
ls -la frontend/src/
# Should show: components/, pages/, services/, App.js

# Verify Docker configuration
ls -la 
# Should show: docker-compose.yml, .env.example
```

---

## 🚨 Common Issues & Solutions

### Issue: "crewai module not found"
**Solution:** Install CrewAI in backend environment
```bash
cd backend
source venv/bin/activate
pip install crewai
```

### Issue: "Database connection failed"
**Solutions:**
1. Check PostgreSQL is running: `brew services list | grep postgres`
2. Verify credentials in .env file
3. Test manual connection: `psql -U automated_bi_user -d automated_bi`

### Issue: "Gemini API key invalid"
**Solutions:**
1. Verify API key is correct in .env
2. Check API key permissions in Google AI Studio
3. Ensure no extra spaces in .env file

### Issue: "Port already in use"
**Solutions:**
```bash
# Find process using port
lsof -i :5000  # For backend
lsof -i :3000  # For frontend

# Kill process
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Issue: "Frontend can't connect to backend"
**Solutions:**
1. Check backend is running on port 5000
2. Verify CORS settings in backend
3. Check network configuration in Docker

---

## 📊 Test Data

**Sample CSV for testing:**
```csv
date,product,sales,region,cost
2023-01-01,Product A,1000,North,700
2023-01-02,Product B,1200,South,800
2023-01-03,Product A,950,East,650
2023-01-04,Product C,1500,West,1000
2023-01-05,Product B,1100,North,750
```

**Expected workflow:**
1. Upload CSV file
2. See processing steps
3. View generated dashboard with:
   - KPI cards
   - Sales trend chart
   - Product breakdown pie chart
   - Regional performance bar chart

---

## 🔄 Development Workflow

### Making Changes

**Backend changes:**
```bash
cd backend
source venv/bin/activate
# Make your changes
python app.py  # Test locally
```

**Frontend changes:**
```bash
cd frontend
# Make your changes
npm start  # Hot reload enabled
```

**Docker rebuild after changes:**
```bash
docker-compose down
docker-compose up --build
```

### Adding New Features

1. **New AI Agent:**
   - Create file in `backend/app/agents/`
   - Follow existing agent patterns
   - Update `analysis_service.py` to use new agent

2. **New API Endpoint:**
   - Add route in `backend/app/api/`
   - Update service layer
   - Test with Postman/curl

3. **New Frontend Component:**
   - Create component in `frontend/src/components/`
   - Add to appropriate page
   - Update routing if needed

---

## 🚀 Production Deployment

### Docker Production Build
```bash
# Build production images
docker-compose -f docker-compose.prod.yml up --build

# Use managed database in production
# Update DATABASE_URL to point to AWS RDS, Google Cloud SQL, etc.
```

### Environment Setup
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Set secure SECRET_KEY
- Enable SSL for database connections
- Use production-grade web server (nginx + gunicorn)

---

## ✅ Final Checklist

Before using the application, verify:

- [ ] Docker is installed and running
- [ ] `.env` file created with valid Gemini API key
- [ ] `docker-compose up --build` completes successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API responds at http://localhost:5000/health
- [ ] Database connection working
- [ ] Can upload CSV file and see processing
- [ ] Dashboard generates with visualizations

**Your AutomatedBI application is now ready! 🎉**

---

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs [service-name]`
2. Verify all environment variables are set
3. Ensure all required services are running
4. Test individual components separately

The application will work correctly once all dependencies are properly configured and running.
