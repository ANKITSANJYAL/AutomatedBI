# AutomatedBI - AI-Powered Business Intelligence Dashboard

A automated business intelligence platform that transforms raw CSV data into professional, interactive dashboards using AI agents and best practices in data visualization.

## 🚀 Features

### Core Capabilities
- **Smart Data Upload**: Automatic validation and quality analysis
- **AI-Powered Analysis**: Domain recognition using CrewAI and Gemini AI
- **Professional Dashboards**: Interactive, responsive charts with best practices
- **Data Quality Reports**: Comprehensive profiling and quality metrics
- **Business Insights**: Domain-specific KPIs and recommendations

### Technical Features
- **Production-Ready**: Docker containerization with proper error handling
- **Real-time Processing**: Live progress tracking with WebSocket-like updates
- **Interactive Charts**: Zoomable, filterable, and touchable visualizations
- **Professional UI**: Modern, responsive design with Tailwind CSS
- **Scalable Architecture**: Microservices with PostgreSQL and Redis

##  Architecture

```
Frontend (React)          Backend (Flask)           AI Layer (CrewAI)
├── Upload Interface  →   ├── File Processing   →   ├── Data Quality Agent
├── Progress Tracking →   ├── API Endpoints     →   ├── Domain Expert Agent
├── Dashboard Display →   ├── Database Layer    →   ├── KPI Strategist Agent
└── Export Features   →   └── Background Tasks →   └── Dashboard Designer Agent
```

## Prerequisites

Before setting up the project, ensure you have:

1. **Docker & Docker Compose** installed
2. **Gemini API Key** from Google AI Studio
3. **PostgreSQL** credentials (or use Docker setup)
4. **Node.js 18+** and **Python 3.11+** (for development)


## Quickstart (Clone & Run)

```bash
git clone <repository-url>
cd AutomatedBI
cp .env.example .env  # Edit .env with your Gemini API key and DB credentials
docker-compose up --build
# Frontend: http://localhost:3000  |  Backend: http://localhost:5001
```

---

##  Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AutomatedBI
```

### 2. Environment Configuration
Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

**Edit the `.env` file with your configuration:**

```env
# Database Configuration
POSTGRES_DB=automated_bi
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_strong_password

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_super_secret_key_here

# AI Configuration - GET THIS FROM GOOGLE AI STUDIO
GEMINI_API_KEY=your_gemini_api_key_here

# File Upload Configuration
MAX_UPLOAD_SIZE=50MB
UPLOAD_FOLDER=uploads

# Logging
LOG_LEVEL=INFO
```

### 3. Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file as `GEMINI_API_KEY`

### 4. Start the Application

**Using Docker (Recommended):**
```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

**For Development (Local):**

Backend setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up database
flask init-db

# Start backend
python app.py
```

Frontend setup:
```bash
cd frontend
npm install
npm start
```


##  Dashboard Tabs Explained

The AutomatedBI dashboard provides two main tabs, each designed for a specific type of user and analysis:

### 1. Data Quality Tab ("ML Engineering Dashboard")
**Audience:** Data scientists, ML engineers, analysts

- **ML Readiness Score:** Visual gauge and breakdown of your dataset's suitability for machine learning, including missing data, duplicates, outliers, and more.
- **Critical Issues:** Highlights any major data quality problems that could impact analysis or modeling.
- **Dataset Overview:** Quick stats on rows, columns, missing data, and memory usage.
- **ML Engineer Recommendations:** Actionable suggestions for improving data quality and ML-readiness.
- **Preprocessing Tab:** Column-by-column missing value and outlier strategies, recommended preprocessing pipeline, and transformation steps.
- **Modeling Tab:** AI-recommended ML models, validation strategies, and performance considerations based on your data.
- **Feature Engineering Tab:** Encoding and scaling requirements, plus opportunities for new features (datetime, text, interactions, binning).
- **Data Profile Tab:** Data types, missing percentages, unique values, and a sample data preview for transparency and auditability.

### 2. Business Insights Tab
**Audience:** Business users, executives, product managers

- **Domain-Specific KPIs:** Automatically selected and calculated key performance indicators relevant to your data's business context.
- **Intelligent Visualizations:** Interactive charts (bar, donut, histogram, box, scatter, treemap, gauge, KPI cards) chosen by AI agents for best insight delivery.
- **AI-Generated Insights:** Natural language summaries and recommendations based on detected trends, anomalies, and business logic.
- **Export & Sharing:** Download or share your dashboard and insights for reporting or collaboration.

---

---

##  What Makes This Project Special?

- **Intelligent Chart Selection:** Backend AI agents (CrewAI, Gemini) analyze your data and select the best chart types (bar, donut, histogram, box, scatter, treemap, gauge, KPI cards) based on data cardinality and business context.
- **Professional, Responsive UI:** Modern React + Tailwind dashboard with mobile-first, executive-grade design. All charts are styled for business use and adapt to any screen size.
- **Data Quality & Insights:** Automated profiling, ML-readiness scoring, and actionable recommendations for both business and ML users.
- **End-to-End Automation:** Upload any CSV/Excel, get a ready-to-use dashboard in minutes—no manual setup required.
- **Production-Ready:** Dockerized, robust error handling, scalable microservices, and clean codebase.

---

### 1. Upload Your Data
- Navigate to the homepage
- Upload a CSV or Excel file (max 50MB)
- Supported formats: `.csv`, `.xlsx`, `.xls`

### 2. AI Processing
Watch the real-time processing steps:
- **File Upload** - Data validation and storage
- **Quality Analysis** - Comprehensive data profiling
- **Domain Classification** - AI identifies business context
- **KPI Recommendation** - Suggests relevant metrics
- **Dashboard Design** - Creates optimal layout
- **Completion** - Interactive dashboard ready

### 3. Explore Your Dashboard

**Data Quality Tab:**
- Overall quality score and metrics
- Missing values analysis
- Data type distributions
- Column-by-column statistics
- Sample data preview

**Business Insights Tab:**
- Domain-specific KPIs
- Interactive visualizations
- AI-generated insights
- Export capabilities

##  Configuration

### File Upload Limits
- Maximum file size: 50MB
- Supported formats: CSV, Excel (.xlsx, .xls)
- Automatic encoding detection

### AI Processing
- Uses CrewAI multi-agent system
- Powered by Google's Gemini AI
- Domain detection for 6+ business areas
- Automatic KPI and chart recommendations

### Database
- PostgreSQL with JSONB for flexible data storage
- Automatic cleanup of old datasets (30 days)
- Optimized indexes for performance

##  Production Deployment

### Docker Production Setup
```bash
# Set production environment
export FLASK_ENV=production

# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production
```env
FLASK_ENV=production
SECRET_KEY=your_very_secure_production_key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GEMINI_API_KEY=your_production_gemini_key
```

### Security Considerations
- Use strong, unique passwords
- Implement SSL/TLS certificates
- Configure firewall rules
- Regular security updates
- Monitor API usage limits

## 🧪 Development

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Database migrations
flask db upgrade

# Start development server
python app.py
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Code Quality
- **Backend**: Black formatting, Flake8 linting
- **Frontend**: ESLint, Prettier formatting
- **Testing**: Pytest for backend, Jest for frontend

## 📁 Project Structure

```
AutomatedBI/
├── backend/
│   ├── app/
│   │   ├── agents/          # CrewAI agents
│   │   ├── api/             # Flask API endpoints
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   ├── sql/                 # Database schema
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   └── services/        # API services
│   └── package.json
├── docker-compose.yml       # Development setup
└── README.md
```

##  API Documentation

### Upload Endpoints
- `POST /api/upload` - Upload CSV/Excel file
- `GET /api/upload/status/{id}` - Get processing status
- `GET /api/upload/progress/{id}` - Get detailed progress

### Analysis Endpoints
- `GET /api/analysis/{id}` - Get complete analysis
- `GET /api/analysis/{id}/quality` - Get quality report
- `GET /api/analysis/{id}/insights` - Get business insights

### Dashboard Endpoints
- `GET /api/dashboard/{id}` - Get dashboard structure
- `GET /api/dashboard/{id}/kpis` - Get KPI values
- `POST /api/dashboard/{id}/chart-data` - Get chart data

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

##  License

This project is licensed under the MIT License.

### Common Issues

**"Import errors when starting backend"**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment: `source venv/bin/activate`

**"Frontend won't start"**
- Clear node modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (requires 18+)

**"Database connection failed"**
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists: `createdb automated_bi`

**"AI processing fails"**
- Verify Gemini API key is valid
- Check API quota and limits
- Ensure internet connectivity

### Getting Help
- Open an issue on GitHub
- Check the documentation
- Review the logs: `docker-compose logs`

## 🔄 Updates

To update the application:
```bash
git pull origin main
docker-compose down
docker-compose up --build
```

---

**Built with ❤️ using Flask, React, CrewAI, and Gemini AI**
