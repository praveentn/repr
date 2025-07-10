# deploy.py
"""
Deployment script for Knowledge Representation Engine
Handles environment setup, database initialization, and deployment tasks
"""

import os
import sys
import subprocess
import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """Manages deployment tasks for the Knowledge Representation Engine"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.data_path = self.project_root / "data"
        self.logs_path = self.project_root / "logs"
        
        # Environment-specific configurations
        self.configs = {
            "development": {
                "debug": True,
                "workers": 1,
                "reload": True,
                "log_level": "debug",
                "port": 8000
            },
            "staging": {
                "debug": False,
                "workers": 2,
                "reload": False,
                "log_level": "info",
                "port": 8000
            },
            "production": {
                "debug": False,
                "workers": 4,
                "reload": False,
                "log_level": "warning",
                "port": 8000
            }
        }
    
    def setup_environment(self) -> bool:
        """Set up the deployment environment"""
        logger.info(f"🚀 Setting up {self.environment} environment...")
        
        try:
            # Create required directories
            self._create_directories()
            
            # Set up Python virtual environment
            if not self.venv_path.exists():
                self._create_virtual_environment()
            
            # Install dependencies
            self._install_dependencies()
            
            # Initialize database
            self._initialize_database()
            
            # Set up configuration
            self._setup_configuration()
            
            # Run health checks
            if self._run_health_checks():
                logger.info("✅ Environment setup completed successfully!")
                return True
            else:
                logger.error("❌ Environment setup failed health checks")
                return False
                
        except Exception as e:
            logger.error(f"❌ Environment setup failed: {e}")
            return False
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.data_path,
            self.data_path / "backups",
            self.data_path / "exports", 
            self.data_path / "uploads",
            self.logs_path,
            Path("static"),
            Path("templates")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
    
    def _create_virtual_environment(self):
        """Create Python virtual environment"""
        logger.info("🐍 Creating Python virtual environment...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True)
            logger.info("✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to create virtual environment: {e}")
    
    def _install_dependencies(self):
        """Install Python dependencies"""
        logger.info("📦 Installing dependencies...")
        
        pip_path = self._get_pip_path()
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            logger.warning("⚠️ requirements.txt not found")
            return
        
        try:
            subprocess.run([
                str(pip_path), "install", "-r", str(requirements_file)
            ], check=True)
            logger.info("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to install dependencies: {e}")
    
    def _initialize_database(self):
        """Initialize the SQLite database"""
        logger.info("🗄️ Initializing database...")
        
        python_path = self._get_python_path()
        
        init_script = """
import asyncio
from core.database import DatabaseManager

async def init_db():
    db_manager = DatabaseManager()
    await db_manager.initialize()
    print("Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(init_db())
"""
        
        try:
            subprocess.run([
                str(python_path), "-c", init_script
            ], cwd=self.project_root, check=True)
            logger.info("✅ Database initialized")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Database initialization warning: {e}")
    
    def _setup_configuration(self):
        """Set up environment configuration"""
        logger.info("⚙️ Setting up configuration...")
        
        env_file = self.project_root / ".env"
        env_template = self.project_root / ".env.template"
        
        # Copy template if .env doesn't exist
        if not env_file.exists() and env_template.exists():
            shutil.copy2(env_template, env_file)
            logger.info("📋 Created .env from template")
        
        # Update environment-specific settings
        self._update_env_file(env_file)
        
        logger.info("✅ Configuration setup completed")
    
    def _update_env_file(self, env_file: Path):
        """Update .env file with environment-specific settings"""
        if not env_file.exists():
            return
        
        config = self.configs.get(self.environment, {})
        
        # Read current .env content
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update specific settings
        updated_lines = []
        settings_updated = set()
        
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                if key in ['DEBUG', 'LOG_LEVEL', 'PORT']:
                    if key == 'DEBUG':
                        updated_lines.append(f"{key}={str(config.get('debug', False)).lower()}\n")
                    elif key == 'LOG_LEVEL':
                        updated_lines.append(f"{key}={config.get('log_level', 'info').upper()}\n")
                    elif key == 'PORT':
                        updated_lines.append(f"{key}={config.get('port', 8000)}\n")
                    settings_updated.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
    
    def _run_health_checks(self) -> bool:
        """Run health checks to verify setup"""
        logger.info("🔍 Running health checks...")
        
        checks = [
            self._check_python_installation,
            self._check_dependencies,
            self._check_database,
            self._check_configuration,
            self._check_file_permissions
        ]
        
        passed = 0
        total = len(checks)
        
        for check in checks:
            try:
                if check():
                    passed += 1
            except Exception as e:
                logger.error(f"Health check failed: {e}")
        
        success_rate = passed / total
        logger.info(f"📊 Health checks: {passed}/{total} passed ({success_rate:.1%})")
        
        return success_rate >= 0.8  # 80% pass rate required
    
    def _check_python_installation(self) -> bool:
        """Check Python installation"""
        python_path = self._get_python_path()
        
        try:
            result = subprocess.run([
                str(python_path), "--version"
            ], capture_output=True, text=True, check=True)
            
            version = result.stdout.strip()
            logger.info(f"✅ Python check: {version}")
            return True
        except Exception as e:
            logger.error(f"❌ Python check failed: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """Check if key dependencies are installed"""
        python_path = self._get_python_path()
        
        key_packages = ["fastapi", "uvicorn", "openai", "aiosqlite", "pydantic"]
        
        for package in key_packages:
            try:
                subprocess.run([
                    str(python_path), "-c", f"import {package}"
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.error(f"❌ Package {package} not found")
                return False
        
        logger.info("✅ Dependencies check passed")
        return True
    
    def _check_database(self) -> bool:
        """Check database connectivity"""
        db_file = self.data_path / "knowledge_repr.db"
        
        if db_file.exists():
            logger.info("✅ Database file exists")
            return True
        else:
            logger.warning("⚠️ Database file not found (will be created on first run)")
            return True
    
    def _check_configuration(self) -> bool:
        """Check configuration files"""
        env_file = self.project_root / ".env"
        
        if not env_file.exists():
            logger.error("❌ .env file not found")
            return False
        
        # Check for required environment variables
        required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your_" in content:
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        logger.info("✅ Configuration check passed")
        return True
    
    def _check_file_permissions(self) -> bool:
        """Check file permissions"""
        test_file = self.data_path / "permission_test.tmp"
        
        try:
            # Test write permission
            with open(test_file, 'w') as f:
                f.write("test")
            
            # Test read permission
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Clean up
            test_file.unlink()
            
            logger.info("✅ File permissions check passed")
            return True
        except Exception as e:
            logger.error(f"❌ File permissions check failed: {e}")
            return False
    
    def deploy(self, service: str = "app") -> bool:
        """Deploy the application"""
        logger.info(f"🚀 Deploying {service} in {self.environment} mode...")
        
        if service == "app":
            return self._deploy_app()
        elif service == "docker":
            return self._deploy_docker()
        elif service == "docker-compose":
            return self._deploy_docker_compose()
        else:
            logger.error(f"❌ Unknown service: {service}")
            return False
    
    def _deploy_app(self) -> bool:
        """Deploy the FastAPI application"""
        python_path = self._get_python_path()
        config = self.configs[self.environment]
        
        cmd = [
            str(python_path), "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", str(config["port"]),
            "--workers", str(config["workers"]),
            "--log-level", config["log_level"]
        ]
        
        if config["reload"]:
            cmd.append("--reload")
        
        logger.info(f"🌟 Starting application: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, cwd=self.project_root)
            return True
        except KeyboardInterrupt:
            logger.info("👋 Application stopped by user")
            return True
        except Exception as e:
            logger.error(f"❌ Application deployment failed: {e}")
            return False
    
    def _deploy_docker(self) -> bool:
        """Deploy using Docker"""
        logger.info("🐳 Deploying with Docker...")
        
        try:
            # Build Docker image
            subprocess.run([
                "docker", "build", "-t", "knowledge-repr-engine", "."
            ], check=True, cwd=self.project_root)
            
            # Run Docker container
            subprocess.run([
                "docker", "run", "-p", "8000:8000",
                "--env-file", ".env",
                "knowledge-repr-engine"
            ], check=True, cwd=self.project_root)
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Docker deployment failed: {e}")
            return False
    
    def _deploy_docker_compose(self) -> bool:
        """Deploy using Docker Compose"""
        logger.info("🐳 Deploying with Docker Compose...")
        
        try:
            subprocess.run([
                "docker-compose", "up", "-d"
            ], check=True, cwd=self.project_root)
            
            logger.info("✅ Docker Compose deployment completed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Docker Compose deployment failed: {e}")
            return False
    
    def backup_data(self) -> bool:
        """Create backup of application data"""
        logger.info("💾 Creating data backup...")
        
        backup_dir = self.data_path / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.tar.gz"
        
        try:
            subprocess.run([
                "tar", "-czf", str(backup_file),
                "-C", str(self.project_root),
                "data", ".env"
            ], check=True)
            
            logger.info(f"✅ Backup created: {backup_file}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def restore_data(self, backup_file: str) -> bool:
        """Restore data from backup"""
        logger.info(f"📥 Restoring data from: {backup_file}")
        
        backup_path = Path(backup_file)
        if not backup_path.exists():
            logger.error(f"❌ Backup file not found: {backup_file}")
            return False
        
        try:
            subprocess.run([
                "tar", "-xzf", str(backup_path),
                "-C", str(self.project_root)
            ], check=True)
            
            logger.info("✅ Data restored successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Restore failed: {e}")
            return False
    
    def _get_python_path(self) -> Path:
        """Get path to Python executable"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            return self.venv_path / "bin" / "python"
    
    def _get_pip_path(self) -> Path:
        """Get path to pip executable"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "pip.exe"
        else:  # Unix-like
            return self.venv_path / "bin" / "pip"
    
    def status(self) -> Dict:
        """Get deployment status"""
        status = {
            "environment": self.environment,
            "project_root": str(self.project_root),
            "venv_exists": self.venv_path.exists(),
            "data_dir_exists": self.data_path.exists(),
            "env_file_exists": (self.project_root / ".env").exists(),
            "database_exists": (self.data_path / "knowledge_repr.db").exists()
        }
        
        return status

def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(description="Knowledge Representation Engine Deployment")
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "staging", "production"],
        default="development",
        help="Deployment environment"
    )
    parser.add_argument(
        "--action", "-a",
        choices=["setup", "deploy", "backup", "restore", "status"],
        default="setup",
        help="Action to perform"
    )
    parser.add_argument(
        "--service", "-s",
        choices=["app", "docker", "docker-compose"],
        default="app",
        help="Service to deploy"
    )
    parser.add_argument(
        "--backup-file", "-b",
        help="Backup file path for restore action"
    )
    
    args = parser.parse_args()
    
    deployment_manager = DeploymentManager(args.environment)
    
    try:
        if args.action == "setup":
            success = deployment_manager.setup_environment()
        elif args.action == "deploy":
            success = deployment_manager.deploy(args.service)
        elif args.action == "backup":
            success = deployment_manager.backup_data()
        elif args.action == "restore":
            if not args.backup_file:
                logger.error("❌ Backup file required for restore action")
                sys.exit(1)
            success = deployment_manager.restore_data(args.backup_file)
        elif args.action == "status":
            status = deployment_manager.status()
            print(json.dumps(status, indent=2))
            success = True
        else:
            logger.error(f"❌ Unknown action: {args.action}")
            success = False
        
        if success:
            logger.info("🎉 Deployment script completed successfully!")
            sys.exit(0)
        else:
            logger.error("💥 Deployment script failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Deployment script interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
