# start.py
"""
Startup script for Knowledge Representation Engine
Provides easy commands to run the application in different modes
"""

import os
import sys
import time
import argparse
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional
import json

class ApplicationStarter:
    """Application startup manager"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.data_path = self.project_root / "data"
        
    def start_development(self, host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
        """Start the application in development mode"""
        print("🚀 Starting Knowledge Representation Engine (Development Mode)")
        print(f"📍 URL: http://{host}:{port}")
        print("🔧 Features: Hot reload, Debug mode, Detailed logging")
        print("-" * 60)
        print("Root Directory:", self.project_root)
        
        # Check if virtual environment exists
        if not self._check_venv():
            print("❌ Virtual environment not found. Please run 'python deploy.py --action setup' first.")
            return False
        
        # Check environment file
        if not self._check_env_file():
            return False
        else:
            print("✅ Environment file found and valid")
        # Get Python path
        python_path = self._get_python_path()
        if not python_path.exists():
            print(f"❌ Python executable not found at {python_path}. Please check your virtual environment setup.")
            return False
        print(f"✅ Using Python executable: {python_path}")
        
        # Start the application
        cmd = [
            str(python_path), "-m", "uvicorn", "main:app",
            "--host", host,
            "--port", str(port),
            "--reload",
            "--log-level", "debug"
        ]
        
        # Open browser after a delay
        if open_browser:
            import threading
            def open_browser_delayed():
                time.sleep(2)  # Wait for server to start
                try:
                    webbrowser.open(f"http://{host}:{port}")
                    print(f"🌐 Opened browser at http://{host}:{port}")
                except Exception as e:
                    print(f"⚠️ Could not open browser: {e}")
            
            threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        try:
            print("🎯 Starting server...")
            print("Command:", " ".join(cmd))
            print("Working Directory:", self.project_root)
            # Run the command in the project root directory
            subprocess.run(cmd, cwd=self.project_root)
            return True
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
            return True
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def start_production(self, host: str = "0.0.0.0", port: int = 8000, workers: int = 4):
        """Start the application in production mode"""
        print("🚀 Starting Knowledge Representation Engine (Production Mode)")
        print(f"📍 URL: http://{host}:{port}")
        print(f"👥 Workers: {workers}")
        print("🔒 Features: Optimized performance, Security enabled")
        print("-" * 60)
        
        if not self._check_venv():
            print("❌ Virtual environment not found. Please run setup first.")
            return False
        
        if not self._check_env_file():
            return False
        
        python_path = self._get_python_path()
        
        cmd = [
            str(python_path), "-m", "uvicorn", "main:app",
            "--host", host,
            "--port", str(port),
            "--workers", str(workers),
            "--log-level", "info"
        ]
        
        try:
            print("🎯 Starting production server...")
            subprocess.run(cmd, cwd=self.project_root)
            return True
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
            return True
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def start_docker(self):
        """Start the application using Docker"""
        print("🐳 Starting Knowledge Representation Engine (Docker)")
        print("-" * 60)
        
        # Check if Docker is available
        if not self._check_docker():
            return False
        
        # Check if .env file exists
        if not self._check_env_file():
            return False
        
        try:
            # Build and run Docker container
            print("🔨 Building Docker image...")
            subprocess.run([
                "docker", "build", "-t", "knowledge-repr-engine", "."
            ], check=True, cwd=self.project_root)
            
            print("🚀 Starting Docker container...")
            subprocess.run([
                "docker", "run", "-p", "8000:8000",
                "--env-file", ".env",
                "-v", f"{self.data_path}:/app/data",
                "knowledge-repr-engine"
            ], cwd=self.project_root)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker startup failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n👋 Docker container stopped by user")
            return True
    
    def start_docker_compose(self):
        """Start the application using Docker Compose"""
        print("🐳 Starting Knowledge Representation Engine (Docker Compose)")
        print("🔧 Features: Multi-service setup, Redis cache, Nginx proxy")
        print("-" * 60)
        
        if not self._check_docker_compose():
            return False
        
        if not self._check_env_file():
            return False
        
        try:
            print("🚀 Starting services with Docker Compose...")
            subprocess.run([
                "docker-compose", "up", "--build"
            ], cwd=self.project_root)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker Compose startup failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n👋 Docker Compose stopped by user")
            return True
    
    def quick_setup(self):
        """Quick setup for first-time users"""
        print("⚡ Quick Setup for Knowledge Representation Engine")
        print("=" * 60)
        
        # Check Python version
        if not self._check_python_version():
            return False
        
        # Run deployment setup
        print("📦 Setting up environment...")
        deploy_script = self.project_root / "deploy.py"
        
        if deploy_script.exists():
            try:
                subprocess.run([
                    sys.executable, str(deploy_script), "--action", "setup"
                ], check=True, cwd=self.project_root)
                print("✅ Environment setup completed!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Setup failed: {e}")
                return False
        else:
            print("⚠️ Deploy script not found, running basic setup...")
            if not self._basic_setup():
                return False
        
        # Create .env file if it doesn't exist
        if not self._setup_env_file():
            return False
        
        print("\n🎉 Quick setup completed!")
        print("📝 Next steps:")
        print("   1. Edit .env file with your Azure OpenAI credentials")
        print("   2. Run: python start.py --mode dev")
        
        return True
    
    def _check_venv(self) -> bool:
        """Check if virtual environment exists"""
        return self.venv_path.exists()
    
    def _check_env_file(self) -> bool:
        """Check if .env file exists and has required variables"""
        env_file = self.project_root / ".env"
        
        if not env_file.exists():
            print("❌ .env file not found!")
            print("📝 Please create .env file with your Azure OpenAI credentials")
            print("💡 You can copy .env.template to .env and edit it")
            return False
        
        # Check for required variables
        with open(env_file, 'r') as f:
            content = f.read()
        # view keys in .env file
        print(f"📂 .env file found at: {env_file}")
        
        required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
        missing_vars = []
        
        # Check if required variables are set
        # content is a string containing the content of the .env file in key=value format
        content = content.replace("\r\n", "\n")  # Normalize line endings
        content = content.replace("\r", "\n")  # Normalize line endings
        content = content.strip()  # Remove leading/trailing whitespace
        content = content.replace(" ", "")  # Remove all spaces for easier checking
        content = content.replace("\n", "")  # Remove newlines for easier checking
        content = content.replace("\t", "")  # Remove tabs for easier checking
        content = content.replace("\r", "")  # Remove carriage returns for easier checking

        # Check if each required variable is present
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required environment variables in .env file:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n📝 Please edit .env file and add your Azure OpenAI credentials")
            return False
        
        return True
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            subprocess.run(["docker", "--version"], 
                         check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker not found!")
            print("📝 Please install Docker to use Docker mode")
            print("🔗 https://docs.docker.com/get-docker/")
            return False
    
    def _check_docker_compose(self) -> bool:
        """Check if Docker Compose is available"""
        try:
            subprocess.run(["docker-compose", "--version"], 
                         check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker Compose not found!")
            print("📝 Please install Docker Compose to use compose mode")
            print("🔗 https://docs.docker.com/compose/install/")
            return False
    
    def _check_python_version(self) -> bool:
        """Check Python version"""
        if sys.version_info < (3, 8):
            print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} detected")
            print("📝 Python 3.8+ is required")
            return False
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
        return True
    
    def _basic_setup(self) -> bool:
        """Basic setup without deploy script"""
        try:
            # Create virtual environment
            if not self.venv_path.exists():
                print("🐍 Creating virtual environment...")
                subprocess.run([
                    sys.executable, "-m", "venv", str(self.venv_path)
                ], check=True)
            
            # Install requirements
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                print("📦 Installing dependencies...")
                pip_path = self._get_pip_path()
                subprocess.run([
                    str(pip_path), "install", "-r", str(requirements_file)
                ], check=True)
            
            # Create directories
            self.data_path.mkdir(exist_ok=True)
            (self.project_root / "logs").mkdir(exist_ok=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Basic setup failed: {e}")
            return False
    
    def _setup_env_file(self) -> bool:
        """Set up .env file from template"""
        env_file = self.project_root / ".env"
        env_template = self.project_root / ".env.template"
        
        if env_file.exists():
            return True
        
        if env_template.exists():
            print("📋 Creating .env from template...")
            import shutil
            shutil.copy2(env_template, env_file)
            print("✅ .env file created")
            print("📝 Please edit .env file with your Azure OpenAI credentials")
            return True
        else:
            print("⚠️ .env.template not found, creating basic .env file...")
            basic_env = """# Basic .env configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-nano
DEBUG=true
PORT=8000
"""
            with open(env_file, 'w') as f:
                f.write(basic_env)
            print("✅ Basic .env file created")
            return True
    
    def _get_python_path(self) -> Path:
        """Get path to Python executable in virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            return self.venv_path / "bin" / "python"
    
    def _get_pip_path(self) -> Path:
        """Get path to pip executable in virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "pip.exe"
        else:  # Unix-like
            return self.venv_path / "bin" / "pip"
    
    def show_status(self):
        """Show application status"""
        print("📊 Knowledge Representation Engine Status")
        print("=" * 50)
        
        # Check components
        status = {
            "Virtual Environment": "✅" if self._check_venv() else "❌",
            "Environment File": "✅" if (self.project_root / ".env").exists() else "❌",
            "Data Directory": "✅" if self.data_path.exists() else "❌",
            "Database": "✅" if (self.data_path / "knowledge_repr.db").exists() else "⚠️ (will be created)",
            "Docker": "✅" if self._check_docker() else "❌",
            "Docker Compose": "✅" if self._check_docker_compose() else "❌"
        }
        
        for component, status_icon in status.items():
            print(f"{component:20}: {status_icon}")
        
        # Show configuration info
        env_file = self.project_root / ".env"
        if env_file.exists():
            print("\n⚙️ Configuration:")
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        if 'KEY' in key or 'PASSWORD' in key:
                            value = '*' * len(value) if value else 'NOT SET'
                        print(f"   {key}: {value}")
    
    def show_help(self):
        """Show help information"""
        print("🧠 Knowledge Representation Engine - Startup Script")
        print("=" * 60)
        print("\nAvailable commands:")
        print("  --mode dev         Start in development mode (default)")
        print("  --mode prod        Start in production mode")
        print("  --mode docker      Start using Docker")
        print("  --mode compose     Start using Docker Compose")
        print("  --setup           Run quick setup")
        print("  --status          Show application status")
        print("  --help            Show this help message")
        print("\nOptions:")
        print("  --host HOST       Host to bind to (default: 127.0.0.1 for dev, 0.0.0.0 for prod)")
        print("  --port PORT       Port to bind to (default: 8000)")
        print("  --workers N       Number of workers for production mode (default: 4)")
        print("  --no-browser      Don't open browser automatically")
        print("\nExamples:")
        print("  python start.py                    # Development mode")
        print("  python start.py --mode prod        # Production mode")
        print("  python start.py --port 3000        # Custom port")
        print("  python start.py --setup            # First-time setup")
        print("\n🔗 URLs:")
        print("  Main App:     http://localhost:8000")
        print("  Admin Panel:  http://localhost:8000/admin")
        print("  API Docs:     http://localhost:8000/docs")

def main():
    """Main startup script"""
    parser = argparse.ArgumentParser(description="Knowledge Representation Engine Startup")
    parser.add_argument(
        "--mode", 
        choices=["dev", "prod", "docker", "compose"],
        default="dev",
        help="Startup mode"
    )
    parser.add_argument("--host", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers (production)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    parser.add_argument("--setup", action="store_true", help="Run quick setup")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--help-extended", action="store_true", help="Show extended help")
    
    args = parser.parse_args()
    
    starter = ApplicationStarter()
    
    # Handle special commands
    if args.help_extended:
        starter.show_help()
        return
    
    if args.setup:
        success = starter.quick_setup()
        sys.exit(0 if success else 1)
    
    if args.status:
        starter.show_status()
        return
    
    # Determine host
    if args.host:
        host = args.host
    else:
        host = "127.0.0.1" if args.mode == "dev" else "0.0.0.0"
    
    # Start application
    try:
        if args.mode == "dev":
            success = starter.start_development(
                host=host, 
                port=args.port, 
                open_browser=not args.no_browser
            )
        elif args.mode == "prod":
            success = starter.start_production(
                host=host, 
                port=args.port, 
                workers=args.workers
            )
        elif args.mode == "docker":
            success = starter.start_docker()
        elif args.mode == "compose":
            success = starter.start_docker_compose()
        else:
            print(f"❌ Unknown mode: {args.mode}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n👋 Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
