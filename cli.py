# cli.py
"""
Command Line Interface for Knowledge Representation Engine
Provides administrative and utility commands
"""

import asyncio
import click
import json
import csv
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import DatabaseManager
from core.llm_manager import LLMManager
from core.representations import RepresentationEngine
from core.utils import FileUtils, HashUtils, CacheUtils
from config.settings import Settings, ConfigManager

class KnowledgeRepCLI:
    """CLI interface for Knowledge Representation Engine"""
    
    def __init__(self):
        self.settings = Settings()
        self.db_manager = DatabaseManager()
        self.config_manager = ConfigManager()
        
    async def initialize(self):
        """Initialize CLI components"""
        await self.db_manager.initialize()

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """Knowledge Representation Engine CLI"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['cli'] = KnowledgeRepCLI()

@cli.group()
def db():
    """Database management commands"""
    pass

@db.command()
@click.pass_context
def init(ctx):
    """Initialize the database"""
    click.echo("🗄️ Initializing database...")
    
    async def _init():
        await ctx.obj['cli'].initialize()
        click.echo("✅ Database initialized successfully!")
    
    asyncio.run(_init())

@db.command()
@click.option('--limit', '-l', default=10, help='Number of records to show')
@click.pass_context
def stats(ctx, limit):
    """Show database statistics"""
    click.echo("📊 Database Statistics")
    click.echo("=" * 30)
    
    async def _stats():
        cli_obj = ctx.obj['cli']
        await cli_obj.initialize()
        
        stats = await cli_obj.db_manager.get_system_stats()
        
        click.echo(f"Total Conversations: {stats.get('total_conversations', 0)}")
        click.echo(f"Total Sessions: {stats.get('total_sessions', 0)}")
        click.echo(f"Today's Conversations: {stats.get('todays_conversations', 0)}")
        
        token_usage = stats.get('token_usage', {})
        if token_usage:
            click.echo(f"Total Tokens: {token_usage.get('total_tokens', 0):,}")
            click.echo(f"Average Tokens: {token_usage.get('avg_tokens', 0):.1f}")
            click.echo(f"Estimated Cost: ${token_usage.get('total_cost', 0):.4f}")
        
        # Show popular modes
        popular_modes = stats.get('popular_modes', [])
        if popular_modes:
            click.echo("\n🎯 Popular Representation Modes:")
            for mode in popular_modes[:limit]:
                click.echo(f"  {mode['representation_mode']}: {mode['count']} uses")
    
    asyncio.run(_stats())

@db.command()
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'csv']), default='json',
              help='Output format')
@click.pass_context
def export(ctx, output, output_format):
    """Export conversations data"""
    click.echo(f"📤 Exporting conversations as {output_format.upper()}...")
    
    async def _export():
        cli_obj = ctx.obj['cli']
        await cli_obj.initialize()
        
        # Get conversations
        conversations = await cli_obj.db_manager.get_conversations(page=1, limit=10000)
        data = conversations.get('conversations', [])
        
        if not data:
            click.echo("⚠️ No conversations found to export")
            return
        
        # Generate output filename if not provided
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"conversations_export_{timestamp}.{output_format}"
        else:
            output_file = output
        
        # Export data
        if output_format == 'json':
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif output_format == 'csv':
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False)
        
        click.echo(f"✅ Exported {len(data)} conversations to {output_file}")
    
    asyncio.run(_export())

@db.command()
@click.option('--days', '-d', default=30, help='Delete data older than N days')
@click.option('--confirm', is_flag=True, help='Confirm deletion without prompt')
@click.pass_context
def cleanup(ctx, days, confirm):
    """Clean up old conversation data"""
    click.echo(f"🧹 Cleaning up data older than {days} days...")
    
    if not confirm:
        if not click.confirm('Are you sure you want to delete old data?'):
            click.echo("❌ Cleanup cancelled")
            return
    
    async def _cleanup():
        cli_obj = ctx.obj['cli']
        await cli_obj.initialize()
        
        # This would implement cleanup logic
        # For now, just show what would be cleaned
        cutoff_date = datetime.now() - timedelta(days=days)
        click.echo(f"Would delete conversations older than {cutoff_date}")
        click.echo("✅ Cleanup completed (simulated)")
    
    asyncio.run(_cleanup())

@db.command()
@click.argument('query')
@click.option('--limit', '-l', default=100, help='Maximum number of results')
@click.pass_context
def query(ctx, query, limit):
    """Execute SQL query on database"""
    click.echo(f"🔍 Executing query: {query[:50]}...")
    
    # Security check - only allow SELECT
    if not query.strip().upper().startswith('SELECT'):
        click.echo("❌ Only SELECT queries are allowed for security")
        return
    
    async def _query():
        cli_obj = ctx.obj['cli']
        await cli_obj.initialize()
        
        try:
            results = await cli_obj.db_manager.execute_query(f"{query} LIMIT {limit}")
            
            if results:
                # Display results in table format
                if len(results) > 0:
                    headers = list(results[0].keys())
                    click.echo(f"\n📋 Results ({len(results)} rows):")
                    click.echo("-" * 60)
                    
                    # Print headers
                    header_line = " | ".join(f"{h[:15]:15}" for h in headers)
                    click.echo(header_line)
                    click.echo("-" * len(header_line))
                    
                    # Print data
                    for row in results[:20]:  # Limit display to 20 rows
                        row_line = " | ".join(f"{str(row[h])[:15]:15}" for h in headers)
                        click.echo(row_line)
                    
                    if len(results) > 20:
                        click.echo(f"... and {len(results) - 20} more rows")
                else:
                    click.echo("📋 No results found")
            else:
                click.echo("📋 Query executed successfully (no results)")
                
        except Exception as e:
            click.echo(f"❌ Query failed: {e}")
    
    asyncio.run(_query())

@cli.group()
def config():
    """Configuration management commands"""
    pass

@config.command()
@click.pass_context
def show(ctx):
    """Show current configuration"""
    click.echo("⚙️ Current Configuration")
    click.echo("=" * 30)
    
    config_dict = ctx.obj['cli'].config_manager.get_config_dict()
    
    def print_config(obj, prefix=""):
        for key, value in obj.items():
            if isinstance(value, dict):
                click.echo(f"{prefix}{key}:")
                print_config(value, prefix + "  ")
            else:
                # Mask sensitive values
                if any(sensitive in key.lower() for sensitive in ['key', 'password', 'secret']):
                    if value:
                        value = '*' * len(str(value))
                    else:
                        value = 'NOT SET'
                click.echo(f"{prefix}{key}: {value}")
    
    print_config(config_dict)

@config.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def set(ctx, key, value):
    """Set configuration value"""
    click.echo(f"⚙️ Setting {key} = {value}")
    
    success = ctx.obj['cli'].config_manager.set(key, value)
    
    if success:
        click.echo("✅ Configuration updated")
    else:
        click.echo("❌ Failed to update configuration")

@config.command()
@click.argument('key')
@click.pass_context
def get(ctx, key):
    """Get configuration value"""
    value = ctx.obj['cli'].config_manager.get(key)
    
    if value is not None:
        # Mask sensitive values
        if any(sensitive in key.lower() for sensitive in ['key', 'password', 'secret']):
            if value:
                value = '*' * len(str(value))
        click.echo(f"{key}: {value}")
    else:
        click.echo(f"❌ Configuration key '{key}' not found")

@config.command()
@click.option('--confirm', is_flag=True, help='Confirm reset without prompt')
@click.pass_context
def reset(ctx, confirm):
    """Reset configuration to defaults"""
    if not confirm:
        if not click.confirm('Are you sure you want to reset all configuration to defaults?'):
            click.echo("❌ Reset cancelled")
            return
    
    success = ctx.obj['cli'].config_manager.reset_to_defaults()
    
    if success:
        click.echo("✅ Configuration reset to defaults")
    else:
        click.echo("❌ Failed to reset configuration")

@cli.group()
def test():
    """Testing and validation commands"""
    pass

@test.command()
@click.pass_context
def llm(ctx):
    """Test LLM connection and response"""
    click.echo("🤖 Testing LLM connection...")
    
    async def _test_llm():
        try:
            llm_manager = LLMManager()
            await llm_manager.initialize()
            
            # Test basic response
            response = await llm_manager.generate_response(
                query="Say 'Hello' if you can hear me.",
                representation_mode="plain_text"
            )
            
            click.echo("✅ LLM connection successful!")
            click.echo(f"Model: {response.model}")
            click.echo(f"Response: {response.content[:100]}...")
            click.echo(f"Tokens used: {response.usage['total_tokens']}")
            click.echo(f"Response time: {response.response_time:.2f}s")
            
        except Exception as e:
            click.echo(f"❌ LLM test failed: {e}")
            if ctx.obj['verbose']:
                import traceback
                click.echo(traceback.format_exc())
    
    asyncio.run(_test_llm())

@test.command()
@click.pass_context
def representations(ctx):
    """Test representation generation"""
    click.echo("🎨 Testing representation modes...")
    
    async def _test_representations():
        engine = RepresentationEngine()
        test_content = "Artificial Intelligence is a broad field that includes Machine Learning and Deep Learning."
        
        modes = ["plain_text", "color_coded", "knowledge_graph", "summary"]
        
        for mode in modes:
            try:
                result = await engine.generate_representation(test_content, mode)
                click.echo(f"✅ {mode}: OK")
                if ctx.obj['verbose']:
                    click.echo(f"   Content keys: {list(result.content.keys())}")
            except Exception as e:
                click.echo(f"❌ {mode}: {e}")
    
    asyncio.run(_test_representations())

@test.command()
@click.pass_context
def health(ctx):
    """Run comprehensive health check"""
    click.echo("🏥 Running health check...")
    
    async def _health_check():
        cli_obj = ctx.obj['cli']
        
        checks = []
        
        # Database check
        try:
            await cli_obj.initialize()
            db_health = await cli_obj.db_manager.health_check()
            checks.append(("Database", "✅" if db_health else "❌"))
        except Exception as e:
            checks.append(("Database", f"❌ {e}"))
        
        # LLM check
        try:
            llm_manager = LLMManager()
            await llm_manager.initialize()
            llm_health = await llm_manager.health_check()
            checks.append(("LLM Service", "✅" if llm_health else "❌"))
        except Exception as e:
            checks.append(("LLM Service", f"❌ {e}"))
        
        # File system check
        try:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            test_file = data_dir / "health_test.tmp"
            test_file.write_text("test")
            test_file.unlink()
            checks.append(("File System", "✅"))
        except Exception as e:
            checks.append(("File System", f"❌ {e}"))
        
        # Configuration check
        try:
            env_file = Path(".env")
            if env_file.exists():
                checks.append(("Configuration", "✅"))
            else:
                checks.append(("Configuration", "⚠️ .env file missing"))
        except Exception as e:
            checks.append(("Configuration", f"❌ {e}"))
        
        # Display results
        click.echo("\n📋 Health Check Results:")
        click.echo("-" * 30)
        for component, status in checks:
            click.echo(f"{component:15}: {status}")
        
        # Overall status
        failures = sum(1 for _, status in checks if status.startswith("❌"))
        if failures == 0:
            click.echo("\n🎉 All systems healthy!")
        else:
            click.echo(f"\n⚠️ {failures} system(s) need attention")
    
    asyncio.run(_health_check())

@cli.group()
def analyze():
    """Data analysis commands"""
    pass

@analyze.command()
@click.option('--days', '-d', default=7, help='Number of days to analyze')
@click.pass_context
def usage(ctx, days):
    """Analyze usage patterns"""
    click.echo(f"📈 Analyzing usage patterns for last {days} days...")
    
    async def _analyze_usage():
        cli_obj = ctx.obj['cli']
        await cli_obj.initialize()
        
        # Get conversations from last N days
        query = f"""
        SELECT 
            date(timestamp) as date,
            representation_mode,
            COUNT(*) as count,
            AVG(processing_time) as avg_time,
            SUM(json_extract(token_usage, '$.total_tokens')) as total_tokens
        FROM conversations 
        WHERE timestamp >= datetime('now', '-{days} days')
        GROUP BY date(timestamp), representation_mode
        ORDER BY date DESC, count DESC
        """
        
        try:
            results = await cli_obj.db_manager.execute_query(query)
            
            if results:
                click.echo(f"\n📊 Usage Analysis ({len(results)} records):")
                click.echo("-" * 80)
                click.echo(f"{'Date':12} {'Mode':20} {'Count':8} {'Avg Time':10} {'Tokens':10}")
                click.echo("-" * 80)
                
                for row in results:
                    click.echo(f"{row['date']:12} {row['representation_mode']:20} {row['count']:8} {row['avg_time']:.2f}s     {row['total_tokens'] or 0:8}")
                    
            else:
                click.echo("📊 No usage data found for the specified period")
                
        except Exception as e:
            click.echo(f"❌ Analysis failed: {e}")
    
    asyncio.run(_analyze_usage())

@analyze.command()
@click.pass_context
def performance(ctx):
    """Analyze performance metrics"""
    click.echo("⚡ Analyzing performance metrics...")
    
    async def _analyze_performance():
        cli_obj = ctx.obj['cli']
        await cli_obj.initialize()
        
        query = """
        SELECT 
            representation_mode,
            COUNT(*) as total_requests,
            AVG(processing_time) as avg_time,
            MIN(processing_time) as min_time,
            MAX(processing_time) as max_time,
            AVG(json_extract(token_usage, '$.total_tokens')) as avg_tokens
        FROM conversations 
        WHERE processing_time IS NOT NULL
        GROUP BY representation_mode
        ORDER BY avg_time DESC
        """
        
        try:
            results = await cli_obj.db_manager.execute_query(query)
            
            if results:
                click.echo("\n⚡ Performance Analysis:")
                click.echo("-" * 90)
                click.echo(f"{'Mode':20} {'Requests':10} {'Avg Time':10} {'Min Time':10} {'Max Time':10} {'Avg Tokens':12}")
                click.echo("-" * 90)
                
                for row in results:
                    click.echo(f"{row['representation_mode']:20} {row['total_requests']:10} {row['avg_time']:.2f}s     {row['min_time']:.2f}s     {row['max_time']:.2f}s     {row['avg_tokens']:.0f}")
                    
            else:
                click.echo("⚡ No performance data found")
                
        except Exception as e:
            click.echo(f"❌ Performance analysis failed: {e}")
    
    asyncio.run(_analyze_performance())

@cli.group()
def backup():
    """Backup and restore commands"""
    pass

@backup.command()
@click.option('--output', '-o', help='Backup file path')
@click.pass_context
def create(ctx, output):
    """Create system backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = output or f"backup_{timestamp}.tar.gz"
    
    click.echo(f"💾 Creating backup: {backup_file}")
    
    try:
        import subprocess
        
        subprocess.run([
            "tar", "-czf", backup_file,
            "data", ".env", "logs"
        ], check=True)
        
        click.echo(f"✅ Backup created successfully: {backup_file}")
        
        # Show backup info
        backup_path = Path(backup_file)
        if backup_path.exists():
            size = backup_path.stat().st_size
            click.echo(f"📁 Backup size: {size:,} bytes")
            
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Backup failed: {e}")
    except Exception as e:
        click.echo(f"❌ Backup error: {e}")

@backup.command()
@click.argument('backup_file')
@click.option('--confirm', is_flag=True, help='Confirm restore without prompt')
@click.pass_context
def restore(ctx, backup_file, confirm):
    """Restore from backup"""
    if not Path(backup_file).exists():
        click.echo(f"❌ Backup file not found: {backup_file}")
        return
    
    if not confirm:
        if not click.confirm(f'Are you sure you want to restore from {backup_file}? This will overwrite current data.'):
            click.echo("❌ Restore cancelled")
            return
    
    click.echo(f"📥 Restoring from backup: {backup_file}")
    
    try:
        import subprocess
        
        subprocess.run([
            "tar", "-xzf", backup_file
        ], check=True)
        
        click.echo("✅ Restore completed successfully")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Restore failed: {e}")
    except Exception as e:
        click.echo(f"❌ Restore error: {e}")

@cli.command()
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'yaml', 'table']), default='table',
              help='Output format')
@click.pass_context
def status(ctx, output_format):
    """Show system status"""
    click.echo("📊 System Status")
    
    async def _status():
        cli_obj = ctx.obj['cli']
        
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "database": {
                "file_exists": Path("data/knowledge_repr.db").exists(),
                "healthy": False
            },
            "configuration": {
                "env_file_exists": Path(".env").exists(),
                "config_valid": False
            },
            "directories": {
                "data": Path("data").exists(),
                "logs": Path("logs").exists(),
                "static": Path("static").exists()
            }
        }
        
        # Test database health
        try:
            await cli_obj.initialize()
            status_data["database"]["healthy"] = await cli_obj.db_manager.health_check()
        except:
            pass
        
        # Test configuration
        try:
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, 'r') as f:
                    content = f.read()
                    status_data["configuration"]["config_valid"] = "AZURE_OPENAI_API_KEY" in content
        except:
            pass
        
        # Output in requested format
        if output_format == 'json':
            click.echo(json.dumps(status_data, indent=2))
        elif output_format == 'yaml':
            try:
                import yaml
                click.echo(yaml.dump(status_data, default_flow_style=False))
            except ImportError:
                click.echo("❌ PyYAML not installed, falling back to JSON")
                click.echo(json.dumps(status_data, indent=2))
        else:  # table format
            def print_status(data, prefix=""):
                for key, value in data.items():
                    if isinstance(value, dict):
                        click.echo(f"{prefix}{key}:")
                        print_status(value, prefix + "  ")
                    else:
                        status_icon = "✅" if value else "❌"
                        click.echo(f"{prefix}{key}: {status_icon}")
            
            print_status(status_data)
    
    asyncio.run(_status())

@cli.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    from config.settings import Settings
    settings = Settings()
    
    click.echo("🧠 Knowledge Representation Engine")
    click.echo(f"Version: {settings.app.version}")
    click.echo(f"Python: {sys.version}")
    click.echo(f"Platform: {sys.platform}")

if __name__ == '__main__':
    cli()
