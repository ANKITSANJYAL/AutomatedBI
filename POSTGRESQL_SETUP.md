# PostgreSQL Setup Guide for AutomatedBI

This guide will help you set up PostgreSQL for the AutomatedBI project.

## Option 1: Using Docker (Recommended for Development)

The easiest way is to use the provided Docker setup which includes PostgreSQL:

```bash
# Clone the project
git clone <your-repo>
cd AutomatedBI

# Copy environment file
cp .env.example .env

# Edit .env file with your settings
nano .env

# Start all services including PostgreSQL
docker-compose up --build
```

The Docker setup automatically:
- Creates PostgreSQL container
- Sets up the database with proper schema
- Runs initialization scripts
- Connects all services

## Option 2: Local PostgreSQL Installation

### macOS Installation

**Using Homebrew:**
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Create a database user
createuser --interactive --pwprompt automated_bi_user

# Create the database
createdb -O automated_bi_user automated_bi
```

**Using PostgreSQL.app:**
1. Download from https://postgresapp.com/
2. Install and start the app
3. Create database via GUI or command line

### Ubuntu/Debian Installation

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user
sudo -u postgres psql

# Inside PostgreSQL shell:
CREATE USER automated_bi_user WITH PASSWORD 'your_password';
CREATE DATABASE automated_bi OWNER automated_bi_user;
GRANT ALL PRIVILEGES ON DATABASE automated_bi TO automated_bi_user;
\q
```

### Windows Installation

1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run installer and follow the setup wizard
3. Remember the password you set for the postgres user
4. Open pgAdmin or command line tool
5. Create database and user:

```sql
CREATE USER automated_bi_user WITH PASSWORD 'your_password';
CREATE DATABASE automated_bi OWNER automated_bi_user;
GRANT ALL PRIVILEGES ON DATABASE automated_bi TO automated_bi_user;
```

## Configuration

### Environment Variables

Edit your `.env` file with the database configuration:

```env
# Database Configuration
POSTGRES_DB=automated_bi
POSTGRES_USER=automated_bi_user
POSTGRES_PASSWORD=your_strong_password
DATABASE_URL=postgresql://automated_bi_user:your_password@localhost:5432/automated_bi

# For Docker setup (if using local PostgreSQL instead)
# DATABASE_URL=postgresql://automated_bi_user:your_password@localhost:5432/automated_bi
```

### Initialize Database Schema

The application will automatically create the required tables when you first run it. The SQL initialization script is in `backend/sql/init.sql`.

**Manual initialization (if needed):**
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

## Verification

### Test Database Connection

Create a test script `test_db.py`:

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host="localhost",
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    print("✅ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

Run the test:
```bash
python test_db.py
```

### Check Tables

Connect to your database and verify tables are created:

```bash
# Connect to database
psql -U automated_bi_user -d automated_bi

# List tables
\dt

# You should see:
# dataset_analysis
# data_points
```

## Troubleshooting

### Common Issues

**"Connection refused"**
- Ensure PostgreSQL service is running
- Check if port 5432 is available
- Verify host and port in connection string

**"Password authentication failed"**
- Double-check username and password in .env
- Ensure user has proper permissions
- Try connecting with psql first

**"Database does not exist"**
- Create the database: `createdb automated_bi`
- Check database name in .env file

**"Permission denied"**
- Grant proper permissions to user
- Ensure user owns the database

### Commands Reference

**Start/Stop PostgreSQL:**
```bash
# macOS (Homebrew)
brew services start postgresql
brew services stop postgresql

# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl stop postgresql

# Windows (as Administrator)
net start postgresql-x64-13
net stop postgresql-x64-13
```

**Database Operations:**
```bash
# Connect to database
psql -U automated_bi_user -d automated_bi

# List databases
\l

# List tables
\dt

# Describe table
\d dataset_analysis

# Exit
\q
```

**Backup/Restore:**
```bash
# Backup
pg_dump -U automated_bi_user automated_bi > backup.sql

# Restore
psql -U automated_bi_user automated_bi < backup.sql
```

## Production Deployment

For production, consider:

1. **Use managed PostgreSQL services:**
   - AWS RDS
   - Google Cloud SQL
   - Azure Database for PostgreSQL
   - DigitalOcean Managed Databases

2. **Security settings:**
   - Use strong passwords
   - Enable SSL connections
   - Configure firewall rules
   - Regular backups

3. **Performance optimization:**
   - Proper indexing (already included in init.sql)
   - Connection pooling
   - Regular VACUUM operations

Example production DATABASE_URL:
```env
DATABASE_URL=postgresql://user:pass@your-db-host:5432/automated_bi?sslmode=require
```

## Next Steps

After setting up PostgreSQL:

1. Configure your `.env` file with database credentials
2. Get your Gemini API key from Google AI Studio
3. Start the application:
   ```bash
   # Docker method
   docker-compose up --build
   
   # Or local development
   cd backend && python app.py
   cd frontend && npm start
   ```

Your AutomatedBI application should now be ready to use!
