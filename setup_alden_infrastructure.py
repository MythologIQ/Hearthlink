#!/usr/bin/env python3
"""
Hearthlink Infrastructure Setup Script
Installs dependencies, starts databases, and launches real Alden backend
"""

import os
import sys
import subprocess
import time
import json
import logging
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hearthlink_setup")

class HearthlinkSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        
    def run_command(self, command, cwd=None, capture_output=False):
        """Run shell command with logging"""
        logger.info(f"🔧 Running: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info(f"✅ Command succeeded: {command}")
                return result
            else:
                logger.warning(f"⚠️ Command failed with code {result.returncode}: {command}")
                if capture_output and result.stderr:
                    logger.warning(f"Error output: {result.stderr}")
                return result
        except Exception as e:
            logger.error(f"❌ Command execution failed: {command} - {e}")
            return None
    
    def check_prerequisites(self):
        """Check if required tools are installed"""
        logger.info("🔍 Checking prerequisites...")
        
        prerequisites = {
            "python3": "python3 --version",
            "docker": "docker --version",
            "docker-compose": "docker-compose --version",
            "node": "node --version",
            "npm": "npm --version"
        }
        
        missing = []
        for tool, command in prerequisites.items():
            result = self.run_command(command, capture_output=True)
            if not result or result.returncode != 0:
                missing.append(tool)
            else:
                logger.info(f"✅ {tool}: {result.stdout.strip()}")
        
        if missing:
            logger.error(f"❌ Missing prerequisites: {', '.join(missing)}")
            logger.info("Please install missing tools and try again")
            return False
        
        logger.info("✅ All prerequisites satisfied")
        return True
    
    def setup_python_environment(self):
        """Setup Python virtual environment and install dependencies"""
        logger.info("🐍 Setting up Python environment...")
        
        # Create virtual environment if it doesn't exist
        if not self.venv_path.exists():
            logger.info("Creating Python virtual environment...")
            result = self.run_command(f"python3 -m venv {self.venv_path}")
            if not result or result.returncode != 0:
                logger.error("❌ Failed to create virtual environment")
                return False
        
        # Activate virtual environment and install dependencies
        if os.name == 'nt':  # Windows
            pip_cmd = f"{self.venv_path}\\Scripts\\pip"
            python_cmd = f"{self.venv_path}\\Scripts\\python"
        else:  # Unix/Linux/Mac
            pip_cmd = f"{self.venv_path}/bin/pip"
            python_cmd = f"{self.venv_path}/bin/python"
        
        # Upgrade pip
        self.run_command(f"{pip_cmd} install --upgrade pip")
        
        # Install requirements
        requirements_files = ["requirements_full.txt", "requirements.txt"]
        requirements_file = None
        
        for req_file in requirements_files:
            if (self.project_root / req_file).exists():
                requirements_file = req_file
                break
        
        if requirements_file:
            logger.info(f"Installing Python dependencies from {requirements_file}...")
            result = self.run_command(f"{pip_cmd} install -r {requirements_file}")
            if not result or result.returncode != 0:
                logger.warning(f"⚠️ Some packages may have failed to install")
        else:
            logger.warning("⚠️ No requirements file found, installing basic dependencies")
            basic_packages = [
                "fastapi>=0.104.0",
                "uvicorn[standard]>=0.24.0",
                "psycopg2-binary>=2.9.0",
                "redis>=5.0.0",
                "qdrant-client>=1.6.0",
                "sentence-transformers>=2.2.0",
                "python-dotenv>=1.0.0",
                "requests>=2.31.0"
            ]
            for package in basic_packages:
                self.run_command(f"{pip_cmd} install {package}")
        
        logger.info("✅ Python environment setup complete")
        return True
    
    def setup_environment_file(self):
        """Create .env file if it doesn't exist"""
        logger.info("📝 Setting up environment configuration...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.production"
        
        if not env_file.exists():
            if env_example.exists():
                logger.info("Copying .env.production to .env...")
                import shutil
                shutil.copy(env_example, env_file)
            else:
                logger.info("Creating default .env file...")
                env_content = """# Hearthlink Environment Configuration

# Database Configuration
POSTGRES_PASSWORD=hearthlink_secure_2025
REDIS_PASSWORD=hearthlink_redis_2025
NEO4J_PASSWORD=hearthlink_neo4j_2025

# Database URLs
DATABASE_URL=postgresql://alden:hearthlink_secure_2025@localhost:5432/hearthlink
REDIS_URL=redis://:hearthlink_redis_2025@localhost:6379/0
QDRANT_URL=http://localhost:6333

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080
REACT_APP_HEARTHLINK_API=http://localhost:8080/api

# LLM Configuration
LLM_BACKEND=claude_code
CLAUDE_CODE_ENABLED=true
LOCAL_LLM_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434

# Security
ENCRYPTION_KEY=hearthlink_default_key_change_in_production
JWT_SECRET=change_this_in_production
SESSION_SECRET=change_this_in_production

# Development
DEBUG=true
LOG_LEVEL=INFO
DEVELOPMENT_MODE=true
"""
                with open(env_file, 'w') as f:
                    f.write(env_content)
        
        logger.info("✅ Environment configuration ready")
        return True
    
    def start_databases(self):
        """Start database services using Docker Compose"""
        logger.info("🐳 Starting database services...")
        
        # Check if docker-compose.yml exists
        compose_file = self.project_root / "docker-compose.yml"
        if not compose_file.exists():
            logger.error("❌ docker-compose.yml not found")
            return False
        
        # Start services
        logger.info("Starting PostgreSQL, Redis, Qdrant, and Neo4j...")
        result = self.run_command("docker-compose up -d", capture_output=True)
        
        if not result or result.returncode != 0:
            logger.error("❌ Failed to start database services")
            if result and result.stderr:
                logger.error(f"Error: {result.stderr}")
            return False
        
        # Wait for services to be ready
        logger.info("⏳ Waiting for databases to initialize...")
        time.sleep(10)
        
        # Check service health
        services = ["postgres", "redis", "qdrant"]
        for service in services:
            for attempt in range(30):  # 30 attempts, 2 seconds each = 1 minute
                result = self.run_command(
                    f"docker-compose exec -T {service} echo 'healthy'", 
                    capture_output=True
                )
                if result and result.returncode == 0:
                    logger.info(f"✅ {service} is ready")
                    break
                time.sleep(2)
            else:
                logger.warning(f"⚠️ {service} may not be fully ready")
        
        logger.info("✅ Database services started")
        return True
    
    def test_database_connections(self):
        """Test database connections"""
        logger.info("🔌 Testing database connections...")
        
        try:
            # Test PostgreSQL
            import psycopg2
            conn = psycopg2.connect(
                "postgresql://alden:hearthlink_secure_2025@localhost:5432/hearthlink"
            )
            conn.close()
            logger.info("✅ PostgreSQL connection successful")
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL connection failed: {e}")
        
        try:
            # Test Redis
            import redis
            r = redis.Redis(host='localhost', port=6379, password='hearthlink_redis_2025')
            r.ping()
            logger.info("✅ Redis connection successful")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
        
        try:
            # Test Qdrant
            from qdrant_client import QdrantClient
            client = QdrantClient(url="http://localhost:6333")
            client.get_collections()
            logger.info("✅ Qdrant connection successful")
        except Exception as e:
            logger.warning(f"⚠️ Qdrant connection failed: {e}")
        
        return True
    
    def start_alden_backend(self):
        """Start the real Alden backend server"""
        logger.info("🚀 Starting Alden backend server...")
        
        backend_file = self.project_root / "src" / "backend" / "alden_backend_real.py"
        if not backend_file.exists():
            logger.error("❌ Alden backend file not found")
            return False
        
        # Use virtual environment Python
        if os.name == 'nt':  # Windows
            python_cmd = f"{self.venv_path}\\Scripts\\python"
        else:  # Unix/Linux/Mac
            python_cmd = f"{self.venv_path}/bin/python"
        
        logger.info("Starting Alden backend on http://localhost:8080")
        logger.info("Press Ctrl+C to stop the server")
        
        # Start the server (this will block)
        result = self.run_command(f"{python_cmd} {backend_file}")
        return True
    
    def run_frontend_setup(self):
        """Setup and start React frontend"""
        logger.info("⚛️ Setting up React frontend...")
        
        # Install npm dependencies
        if (self.project_root / "package.json").exists():
            logger.info("Installing Node.js dependencies...")
            result = self.run_command("npm install")
            if not result or result.returncode != 0:
                logger.warning("⚠️ npm install may have failed")
        
        logger.info("✅ Frontend setup complete")
        logger.info("To start the frontend, run: npm run dev")
        return True
    
    def full_setup(self):
        """Run complete setup process"""
        logger.info("🚀 Starting Hearthlink Infrastructure Setup")
        logger.info("=" * 60)
        
        steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Setting up Python environment", self.setup_python_environment),
            ("Setting up environment file", self.setup_environment_file),
            ("Starting database services", self.start_databases),
            ("Testing database connections", self.test_database_connections),
            ("Setting up frontend", self.run_frontend_setup),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 {step_name}...")
            try:
                if not step_func():
                    logger.error(f"❌ Failed: {step_name}")
                    return False
            except KeyboardInterrupt:
                logger.info("\n⚠️ Setup interrupted by user")
                return False
            except Exception as e:
                logger.error(f"❌ Error in {step_name}: {e}")
                return False
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Hearthlink Infrastructure Setup Complete!")
        logger.info("\nNext steps:")
        logger.info("1. Start Alden backend: python src/backend/alden_backend_real.py")
        logger.info("2. Start frontend: npm run dev")
        logger.info("3. Open http://localhost:3000 in your browser")
        logger.info("\nDatabase services are running in Docker containers")
        logger.info("Use 'docker-compose down' to stop services")
        
        return True

def main():
    setup = HearthlinkSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "backend":
            setup.start_alden_backend()
        elif command == "databases":
            setup.start_databases()
        elif command == "test":
            setup.test_database_connections()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: backend, databases, test")
    else:
        setup.full_setup()

if __name__ == "__main__":
    main()