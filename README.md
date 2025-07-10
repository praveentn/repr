# 🧠 Knowledge Representation Engine

A dynamic, AI-powered web application that transforms information into multiple interactive representations, making complex knowledge more accessible and engaging.

![Knowledge Representation Engine](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 🌟 Features

### 🎨 Multiple Representation Modes
- **📝 Plain Text** - Clean, simple format
- **🎨 Color-Coded** - Tagged sections with legend (facts, assumptions, examples, warnings)
- **🧩 Collapsible Concepts** - Hierarchical, expandable concept trees
- **🧠 Knowledge Graph** - Interactive visual networks of interconnected concepts
- **🧪 Analogical** - Metaphor-based explanations
- **👶 ELI5** - Simplified explanations for beginners
- **👩‍🔬 Expert** - Technical, detailed analysis
- **⏳ Timeline** - Chronological evolution view
- **📦 Summary** - Concise key points
- **📚 Detailed** - Comprehensive deep dives

### 🚀 Core Capabilities
- **AI-Powered Processing** - Azure OpenAI integration with GPT-4
- **Real-time Analytics** - Usage tracking and performance monitoring
- **Multi-format Input** - Text, JSON, file uploads
- **Interactive UI** - Modern, responsive design with animations
- **Admin Dashboard** - Comprehensive system management
- **Export Options** - JSON, CSV, Excel, PDF formats
- **Session Management** - Persistent conversations and preferences
- **Rate Limiting** - Built-in security and performance controls

### 🔧 Technical Features
- **Async Architecture** - High-performance FastAPI backend
- **SQLite Database** - Lightweight, file-based storage
- **Modular Design** - Easy to extend and customize
- **Docker Support** - Containerized deployment
- **Comprehensive Logging** - Structured logging with analytics
- **Security First** - Input sanitization, rate limiting, authentication

## 📁 Project Structure

```
knowledge-representation-engine/
├── 📁 core/
│   ├── auth.py              # Authentication & authorization
│   ├── database.py          # Database management
│   ├── llm_manager.py       # Azure OpenAI integration
│   ├── representations.py   # Representation engine
│   └── utils.py            # Utility functions
├── 📁 models/
│   └── schemas.py          # Pydantic data models
├── 📁 config/
│   └── settings.py         # Configuration management
├── 📁 templates/
│   ├── index.html          # Main application UI
│   └── admin.html          # Admin panel UI
├── 📁 static/
│   ├── css/               # Custom stylesheets
│   ├── js/                # JavaScript modules
│   └── images/            # Static images
├── 📁 data/
│   ├── knowledge_repr.db   # SQLite database
│   ├── backups/           # Database backups
│   ├── exports/           # Exported data
│   └── uploads/           # File uploads
├── 📁 logs/               # Application logs
├── 📁 tests/              # Test suite
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-container setup
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI API access
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/knowledge-representation-engine.git
cd knowledge-representation-engine
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy environment template
copy .env.template .env  # Windows
cp .env.template .env    # Linux/Mac

# Edit .env file with your Azure OpenAI credentials
# Required variables:
# AZURE_OPENAI_API_KEY=your_api_key_here
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### 4. Initialize Database
```bash
# The database will be automatically created on first run
# You can also manually initialize:
python -c "from core.database import DatabaseManager; import asyncio; asyncio.run(DatabaseManager().initialize())"
```

### 5. Run the Application
```bash
# Development mode
uvicorn main:app --reload --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Access the Application
- **Main App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🐳 Docker Deployment

### Quick Docker Run
```bash
# Build and run with Docker
docker build -t knowledge-repr-engine .
docker run -p 8000:8000 --env-file .env knowledge-repr-engine
```

### Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | - | ✅ |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | - | ✅ |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4.1-nano` | ❌ |
| `DATABASE_PATH` | SQLite database path | `data/knowledge_repr.db` | ❌ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `PORT` | Application port | `8000` | ❌ |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` | ❌ |

### LLM Model Parameters

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| `TEMPERATURE` | Response creativity | 0.0-2.0 | `0.7` |
| `MAX_TOKENS` | Maximum response length | 1-4000 | `2000` |
| `TOP_P` | Nucleus sampling | 0.0-1.0 | `1.0` |

## 📊 Usage Examples

### Basic Query Processing
```python
import requests

# Process a query
response = requests.post("http://localhost:8000/api/process", json={
    "query": "Explain quantum computing",
    "representation_mode": "knowledge_graph",
    "user_preferences": {
        "complexity_level": "medium",
        "visual_style": "modern"
    }
})

result = response.json()
print(f"Session ID: {result['session_id']}")
print(f"Processing time: {result['processing_time']}s")
```

### File Upload Processing
```python
import requests

# Upload and process a file
files = {'file': open('document.txt', 'rb')}
response = requests.post("http://localhost:8000/api/upload", files=files)

# Use uploaded content as context
upload_result = response.json()
context = upload_result['content']

# Process with context
response = requests.post("http://localhost:8000/api/process", json={
    "query": "Summarize the key points",
    "context": {"uploaded_content": context},
    "representation_mode": "summary"
})
```

### Admin API Usage
```python
import requests

# Get system statistics
stats = requests.get("http://localhost:8000/api/admin/stats").json()
print(f"Total conversations: {stats['total_conversations']}")

# Get database tables
tables = requests.get("http://localhost:8000/api/admin/tables").json()
print(f"Available tables: {tables['tables']}")

# Execute SQL query
query_result = requests.post("http://localhost:8000/api/admin/query", json={
    "query": "SELECT COUNT(*) as count FROM conversations"
}).json()
```

## 🎨 Representation Modes Guide

### Color-Coded Representation
Organizes content into color-tagged sections:
- **🔵 Blue (Facts)**: Verified information and data
- **🟡 Yellow (Assumptions)**: Hypothetical or uncertain elements
- **🟢 Green (Examples)**: Concrete instances and illustrations
- **🔴 Red (Warnings)**: Risks, cautions, and important notes

### Knowledge Graph
Creates interactive visual networks showing:
- **Nodes**: Concepts, entities, or topics
- **Edges**: Relationships and connections
- **Hierarchies**: Parent-child relationships
- **Clusters**: Related concept groups

### Analogical Mode
Uses creative metaphors and comparisons:
- Real-world analogies for complex concepts
- Familiar examples to explain unfamiliar ideas
- Bridge connections between domains
- Memory aids through story-telling

## 🔐 Security Features

### Input Validation
- Query length limits (10,000 characters)
- File type restrictions
- Content sanitization
- SQL injection prevention

### Rate Limiting
- 60 requests per minute per IP (configurable)
- Burst protection
- Graceful degradation

### Authentication (Optional)
- JWT-based sessions
- Role-based access control
- Admin panel protection
- API key authentication

## 📈 Analytics & Monitoring

### Usage Metrics
- Conversation counts and trends
- Popular representation modes
- Processing time distribution
- Token usage and costs

### Performance Monitoring
- Response time tracking
- Memory and CPU usage
- Database performance
- Error rate monitoring

### Admin Dashboard Features
- Real-time statistics
- Database management
- SQL query executor
- Export capabilities
- System health checks

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_representations.py
pytest tests/test_api.py
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning

## 🚀 Deployment

### Production Checklist
- [ ] Set strong `SECRET_KEY`
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Enable authentication if needed
- [ ] Set up backup strategy
- [ ] Configure monitoring
- [ ] Set appropriate rate limits
- [ ] Review security settings

### Environment-Specific Configurations

#### Development
```env
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_DETAILED_LOGGING=true
```

#### Staging
```env
DEBUG=false
LOG_LEVEL=INFO
ENABLE_ANALYTICS=true
```

#### Production
```env
DEBUG=false
LOG_LEVEL=WARNING
ENABLE_AUTHENTICATION=true
REQUIRE_API_KEY=true
```

## 🔧 Customization

### Adding New Representation Modes

1. **Update Representation Engine** (`core/representations.py`):
```python
async def _generate_custom_mode(self, content: str, preferences: Dict) -> RepresentationResult:
    # Implement your custom representation logic
    return RepresentationResult(
        mode="custom_mode",
        content={"processed_content": content},
        metadata={"custom_info": "value"},
        css_classes=["custom-style"]
    )
```

2. **Add to Available Modes**:
```python
self.available_modes["custom_mode"] = {
    "name": "Custom Mode",
    "description": "Your custom representation",
    "icon": "🎯",
    "category": "custom"
}
```

3. **Update Frontend** (`templates/index.html`):
```html
<div x-show="result?.mode === 'custom_mode'">
    <!-- Custom rendering logic -->
</div>
```

### Custom LLM Prompts
Modify prompts in `core/llm_manager.py`:
```python
self.representation_prompts["custom_mode"] = "Your custom prompt here..."
```

### Database Schema Extensions
Add new tables in `core/database.py`:
```python
await db.execute("""
    CREATE TABLE IF NOT EXISTS custom_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        custom_field TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install dev dependencies: `pip install -r requirements-dev.txt`
4. Make your changes
5. Run tests: `pytest`
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions
- Add tests for new features

### Pull Request Process
1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## 📚 API Documentation

### Interactive API Docs
Visit `/docs` when the application is running for interactive Swagger documentation.

### Key Endpoints

#### POST `/api/process`
Process a query and generate representation.

**Request Body:**
```json
{
  "query": "Your question here",
  "context": {"optional": "context"},
  "representation_mode": "plain_text",
  "user_preferences": {"style": "modern"}
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "original_query": "Your question",
  "llm_response": "AI response",
  "representation": {"formatted": "content"},
  "processing_time": 2.5,
  "token_usage": {"total_tokens": 150}
}
```

#### GET `/api/admin/stats`
Get system statistics (admin only).

#### POST `/api/upload`
Upload files for context processing.

## 🐛 Troubleshooting

### Common Issues

#### "Azure OpenAI API Error"
- Verify API key and endpoint in `.env`
- Check deployment name matches your Azure resource
- Ensure API quota is not exceeded

#### "Database Connection Error"
- Check file permissions in `data/` directory
- Ensure SQLite is properly installed
- Verify database path in configuration

#### "High Memory Usage"
- Reduce `MAX_TOKENS` in configuration
- Enable response caching
- Clean up old conversation data

#### "Slow Response Times"
- Check Azure OpenAI service status
- Monitor system resources
- Consider increasing worker count

### Debug Mode
Enable debug mode for detailed error information:
```env
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_DETAILED_LOGGING=true
```

### Log Analysis
Check logs for errors:
```bash
# View application logs
tail -f logs/app.log

# Check specific error patterns
grep "ERROR" logs/app.log
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Azure OpenAI** for powerful language models
- **FastAPI** for excellent async web framework
- **Tailwind CSS** for beautiful, responsive design
- **Alpine.js** for reactive frontend interactions
- **Vis.js** for knowledge graph visualizations

## 📞 Support

- **Documentation**: Check this README and `/docs` endpoint
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join GitHub Discussions for questions
- **Email**: support@your-domain.com

## 🗺️ Roadmap

### Version 1.1 (Coming Soon)
- [ ] Voice input/output support
- [ ] Real-time collaborative sessions
- [ ] Advanced NLP for entity extraction
- [ ] Custom theme builder
- [ ] Mobile app companion

### Version 1.2 (Future)
- [ ] Multi-language support
- [ ] Plugin architecture
- [ ] Cloud storage integration
- [ ] Advanced analytics dashboard
- [ ] AI model switching

### Version 2.0 (Vision)
- [ ] 3D knowledge visualization
- [ ] AR/VR representation modes
- [ ] Multi-modal input (images, audio)
- [ ] Federated learning capabilities
- [ ] Enterprise SSO integration

---

**Built with ❤️ for knowledge exploration and learning**

*Transform the way you understand and interact with information.*