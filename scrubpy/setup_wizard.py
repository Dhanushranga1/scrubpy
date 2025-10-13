#!/usr/bin/env python3
"""
setup_wizard.py - First-time setup wizard for ScrubPy

Guides users through initial configuration including:
- AI model installation (Ollama + Mistral)
- Environment setup
- Feature preferences
"""

import os
import sys
import subprocess
import platform
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from InquirerPy import inquirer
import requests
import time

console = Console()

class ScrubPySetupWizard:
    """Interactive setup wizard for first-time ScrubPy users"""
    
    def __init__(self):
        self.console = console
        self.config = {
            'ai_enabled': False,
            'ollama_installed': False,
            'preferred_models': [],
            'web_interface': True,
            'completed': False
        }
    
    def welcome(self):
        """Display welcome message"""
        welcome_text = """
Welcome to ScrubPy Setup!

This wizard will help you configure ScrubPy for the best experience.
We'll set up AI features, download models, and configure preferences.
        """
        
        self.console.print(Panel(
            welcome_text.strip(),
            title="ScrubPy First-Time Setup",
            title_align="center",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        if not Confirm.ask("Ready to get started?", default=True):
            self.console.print("Setup cancelled. Run 'scrubpy setup' anytime to configure.")
            return False
        return True
    
    def check_system(self):
        """Check system requirements and capabilities"""
        self.console.print("\n[bold cyan]Checking system requirements...[/bold cyan]")
        
        system_info = {
            'os': platform.system(),
            'arch': platform.machine(),
            'python': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'ram_gb': self._get_available_ram(),
            'disk_space_gb': self._get_available_disk_space()
        }
        
        self.console.print(f"OS: {system_info['os']} ({system_info['arch']})")
        self.console.print(f"Python: {system_info['python']}")
        self.console.print(f"RAM: ~{system_info['ram_gb']:.1f} GB available")
        self.console.print(f"Disk: ~{system_info['disk_space_gb']:.1f} GB available")
        
        # Check if AI features can be supported
        can_support_ai = system_info['ram_gb'] >= 4 and system_info['disk_space_gb'] >= 5
        
        if can_support_ai:
            self.console.print("System can support AI features")
        else:
            self.console.print("Limited resources detected - AI features may be slower")
        
        return system_info
    
    def setup_ai_features(self, system_info):
        """Configure AI features and model installation"""
        self.console.print("\n[bold cyan]AI Features Configuration[/bold cyan]")
        
        enable_ai = inquirer.confirm(
            message="Enable AI-powered data analysis features?",
            default=True
        ).execute()
        
        if not enable_ai:
            self.console.print("AI features disabled. You can enable them later with 'scrubpy setup --ai'")
            return
            
        self.config['ai_enabled'] = True
        
        # Check if Ollama is already installed
        ollama_installed = self._check_ollama_installation()
        
        if ollama_installed:
            self.console.print("Ollama already installed")
            self.config['ollama_installed'] = True
        else:
            install_ollama = inquirer.confirm(
                message="Install Ollama for local AI models? (Recommended)",
                default=True
            ).execute()
            
            if install_ollama:
                self._install_ollama(system_info)
        
        if self.config['ollama_installed']:
            self._setup_models(system_info)
    
    def _install_ollama(self, system_info):
        """Install Ollama based on the operating system"""
        self.console.print("\n[bold yellow]Installing Ollama...[/bold yellow]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Installing Ollama...", total=None)
                
                if system_info['os'] == 'Linux' or system_info['os'] == 'Darwin':  # macOS
                    # Download and run Ollama installer
                    result = subprocess.run([
                        'curl', '-fsSL', 'https://ollama.ai/install.sh'
                    ], capture_output=True, text=True, check=True)
                    
                    # Execute the install script
                    subprocess.run(['sh'], input=result.stdout, text=True, check=True)
                    
                elif system_info['os'] == 'Windows':
                    self.console.print("Please download Ollama for Windows from: https://ollama.ai/download")
                    self.console.print("After installation, run this setup again.")
                    return
                
                progress.update(task, completed=True)
                
            self.console.print("Ollama installed successfully!")
            self.config['ollama_installed'] = True
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"Failed to install Ollama: {e}")
            self.console.print("Please install manually from: https://ollama.ai/")
    
    def _setup_models(self, system_info):
        """Download and configure AI models"""
        self.console.print("\n[bold cyan]AI Model Setup[/bold cyan]")
        
        # Recommend models based on system capabilities
        if system_info['ram_gb'] >= 16:
            recommended_models = ['mistral:7b', 'llama3:8b', 'codellama:7b']
            size_warning = ""
        elif system_info['ram_gb'] >= 8:
            recommended_models = ['mistral:7b', 'llama3:8b']
            size_warning = " (Larger models may be slow)"
        else:
            recommended_models = ['mistral:7b']
            size_warning = " (Only smaller models recommended)"
        
        self.console.print(f"Recommended models for your system{size_warning}:")
        
        selected_models = inquirer.checkbox(
            message="Select models to download:",
            choices=[
                {'name': 'mistral:7b (4.1GB) - Fast, general purpose', 'value': 'mistral:7b'},
                {'name': 'llama3:8b (4.7GB) - Meta\'s latest model', 'value': 'llama3:8b'},
                {'name': 'codellama:7b (3.8GB) - Specialized for code', 'value': 'codellama:7b'},
                {'name': 'phi3:mini (2.3GB) - Microsoft\'s compact model', 'value': 'phi3:mini'}
            ],
            default=['mistral:7b']
        ).execute()
        
        if not selected_models:
            self.console.print("No models selected. You can download them later with 'ollama pull <model>'")
            return
        
        # Download selected models
        for model in selected_models:
            self._download_model(model)
        
        self.config['preferred_models'] = selected_models
    
    def _download_model(self, model):
        """Download a specific AI model"""
        self.console.print(f"\n[bold yellow]Downloading {model}...[/bold yellow]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Downloading {model}...", total=None)
                
                # Run ollama pull command
                process = subprocess.Popen(
                    ['ollama', 'pull', model],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Update progress description with download info
                        if 'pulling' in output.lower() or 'downloading' in output.lower():
                            progress.update(task, description=f"Downloading {model}: {output.strip()}")
                
                if process.returncode == 0:
                    progress.update(task, completed=True)
                    self.console.print(f"{model} downloaded successfully!")
                else:
                    self.console.print(f"Failed to download {model}")
                    
        except Exception as e:
            self.console.print(f"Error downloading {model}: {e}")
    
    def setup_preferences(self):
        """Configure user preferences"""
        self.console.print("\n[bold cyan]⚙️  Preferences[/bold cyan]")
        
        # Web interface preference
        enable_web = inquirer.confirm(
            message="Enable web interface by default?",
            default=True
        ).execute()
        
        self.config['web_interface'] = enable_web
        
        # Auto-update preferences
        auto_check_updates = inquirer.confirm(
            message="Check for ScrubPy updates automatically?",
            default=True
        ).execute()
        
        self.config['auto_check_updates'] = auto_check_updates
        
    def save_config(self):
        """Save configuration to user's home directory"""
        import json
        from pathlib import Path
        
        config_dir = Path.home() / '.scrubpy'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'config.json'
        
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        self.console.print(f"\nConfiguration saved to {config_file}")
    
    def completion_summary(self):
        """Show setup completion summary"""
        summary_text = f"""
Setup Complete!

Configuration Summary:
• AI Features: {'Enabled' if self.config['ai_enabled'] else 'Disabled'}
• Ollama: {'Installed' if self.config['ollama_installed'] else 'Not installed'}
• Models: {', '.join(self.config['preferred_models']) if self.config['preferred_models'] else 'None'}
• Web Interface: {'Enabled' if self.config['web_interface'] else 'Disabled'}

Ready to use ScrubPy! Try these commands:
• scrubpy --help          - Show all available commands
• scrubpy web             - Launch web interface
• scrubpy chat            - Start AI chat session
• scrubpy analyze <file>  - Analyze a dataset
        """
        
        self.console.print(Panel(
            summary_text.strip(),
            title="Setup Complete",
            title_align="center",
            border_style="green",
            padding=(1, 2)
        ))
    
    def run(self):
        """Run the complete setup wizard"""
        if not self.welcome():
            return
        
        system_info = self.check_system()
        self.setup_ai_features(system_info)
        self.setup_preferences()
        
        self.config['completed'] = True
        self.save_config()
        self.completion_summary()
    
    # Helper methods
    def _check_ollama_installation(self):
        """Check if Ollama is already installed"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_available_ram(self):
        """Get available RAM in GB (approximate)"""
        try:
            import psutil
            return psutil.virtual_memory().total / (1024**3)
        except ImportError:
            # Fallback estimation
            return 8.0  # Assume 8GB default
    
    def _get_available_disk_space(self):
        """Get available disk space in GB (approximate)"""
        try:
            import psutil
            return psutil.disk_usage('.').free / (1024**3)
        except ImportError:
            # Fallback estimation
            return 50.0  # Assume 50GB available


def run_setup():
    """Main entry point for setup wizard"""
    wizard = ScrubPySetupWizard()
    wizard.run()


if __name__ == '__main__':
    run_setup()