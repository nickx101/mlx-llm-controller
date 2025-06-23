# Contributing to MLX LLM Controller

Thank you for your interest in contributing to the MLX LLM Controller! This document provides guidelines for contributing to this project.

## 🤝 Code of Conduct

This project follows a simple code of conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Prioritize the community and project goals

## 🚀 Getting Started

### Prerequisites
- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.9 or higher
- Git
- Basic understanding of MLX and language models

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/mlx-llm-controller.git
   cd mlx-llm-controller
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Run Tests**
   ```bash
   python test_system.py
   python test_api.py
   ```

4. **Start Development Server**
   ```bash
   python start_mlx_frontend.py
   ```

## 📝 Development Guidelines

### Code Style
- Follow Python PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and under 50 lines when possible
- Use type hints where appropriate

### Project Structure
```
mlx-llm-controller/
├── backend/           # Core MLX integration
├── frontend/          # Web interface
├── scripts/           # Utility scripts
├── tests/            # Test files
└── docs/             # Documentation
```

### Logging
All components should use structured logging:
```python
import logging
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.info("Information message")
logger.warning("Warning message") 
logger.error("Error message")
```

### Error Handling
- Always handle exceptions gracefully
- Provide meaningful error messages
- Use custom exception classes when appropriate
- Log errors with context information

## 🧪 Testing

### Running Tests
```bash
# Full system test
python test_system.py

# API functionality
python test_api.py

# Comprehensive validation
python final_test.py

# Specific component tests
python -m pytest tests/ -v
```

### Writing Tests
- Write tests for all new functionality
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies when appropriate

Example test structure:
```python
def test_parameter_validation():
    """Test that parameter validation works correctly"""
    params = GenerationParams(temperature=0.7)
    assert params.validate() == True
    
    invalid_params = GenerationParams(temperature=3.0)
    assert invalid_params.validate() == False
```

## 🔧 Making Changes

### Branch Naming
Use descriptive branch names:
- `feature/add-new-model-support`
- `bugfix/fix-memory-leak`
- `improvement/optimize-gpu-usage`
- `docs/update-installation-guide`

### Commit Messages
Write clear, descriptive commit messages:
```
feat: add support for Gemma 2 models

- Add Gemma 2 to model list
- Update download script for new model format
- Add validation for Gemma-specific parameters

Fixes #123
```

Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `perf:` - Performance improvements

### Pull Request Process

1. **Before Submitting**
   - Ensure all tests pass
   - Update documentation if needed
   - Check code style with linting tools
   - Test on actual Apple Silicon hardware

2. **PR Description Template**
   ```markdown
   ## Summary
   Brief description of changes

   ## Changes Made
   - Detailed list of changes
   - Why these changes were necessary

   ## Testing
   - How you tested the changes
   - Any new test cases added

   ## Documentation
   - Documentation updates made
   - Any breaking changes

   ## Checklist
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] Code follows style guidelines
   - [ ] No breaking changes (or clearly documented)
   ```

## 🎯 Areas for Contribution

### High Priority
- **Model Support**: Add support for new MLX-compatible models
- **Performance**: GPU optimization improvements
- **Testing**: Comprehensive test coverage
- **Documentation**: Usage examples and tutorials

### Medium Priority
- **UI/UX**: Frontend improvements and mobile support
- **API**: Additional REST endpoints
- **Monitoring**: Better memory and performance monitoring
- **Integration**: MCP (Model Context Protocol) enhancements

### Low Priority
- **Features**: Additional parameter controls
- **Tools**: Development and debugging tools
- **Examples**: More usage examples and demos

## 📚 Specific Contribution Areas

### Adding New Models

1. **Update Model List**
   ```python
   # In backend/api_server.py
   common_models = [
       "existing-models...",
       "new-model-name"  # Add here
   ]
   ```

2. **Test Model Compatibility**
   ```bash
   python scripts/test_model_availability.py "new-model-name"
   python scripts/download_model.py "new-model-name"
   ```

3. **Update Documentation**
   - Add model to README.md
   - Update any relevant docs

### GPU Optimization Improvements

1. **Understand Current Implementation**
   - Review `scripts/optimize_mlx_gpu.py`
   - Test current performance benchmarks

2. **Implement Improvements**
   - Add new optimization techniques
   - Ensure backward compatibility
   - Test on different Apple Silicon chips

3. **Benchmark and Validate**
   - Measure performance improvements
   - Test memory usage patterns
   - Validate stability under load

### Frontend Enhancements

1. **Setup Development Environment**
   ```bash
   cd frontend/
   # Test current interface
   python3 -m http.server 3000
   ```

2. **Make Changes**
   - Update HTML/CSS/JavaScript
   - Test responsive design
   - Ensure accessibility

3. **Test Across Browsers**
   - Safari (primary target)
   - Chrome, Firefox
   - Mobile Safari

### MCP Integration

1. **Review MCP Specification**
   - Study [Model Context Protocol](https://github.com/modelcontextprotocol)
   - Understand integration patterns

2. **Implement MCP Features**
   - Extend `mcp_integration.py`
   - Add new MCP methods
   - Test with MCP clients

## 🐛 Reporting Issues

### Bug Reports
Include:
- **System Information**: macOS version, chip type, RAM
- **Steps to Reproduce**: Detailed steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error logs
- **Screenshots**: If applicable

### Feature Requests
Include:
- **Use Case**: Why this feature is needed
- **Proposed Solution**: How it might work
- **Alternatives**: Other approaches considered
- **Additional Context**: Any relevant information

## 📖 Documentation

### Types of Documentation
- **README**: Project overview and quick start
- **API Documentation**: Endpoint specifications
- **User Guides**: How-to guides for specific tasks
- **Developer Docs**: Architecture and contribution guides

### Documentation Style
- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep information up to date

## 🏆 Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **CHANGELOG.md**: Release notes
- **GitHub**: Contributor badges
- **Documentation**: Author attribution

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **MCP Community**: For MCP-specific integration questions

## 🎉 Thank You

Every contribution helps make this project better for the entire community. Whether you're fixing a typo, adding a feature, or improving documentation, your efforts are appreciated!

---

**Happy Contributing! 🚀**