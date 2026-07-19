# Contributing to ConfidentialRAG

Thank you for your interest in contributing to ConfidentialRAG! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/confidential-rag.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `make test`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions.

**Quick setup:**
```bash
./scripts/setup-all.sh
make start
```

## Code Style

### Python
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Maximum line length: 100 characters
- Use async/await for I/O operations
- Format code with `black`
- Lint with `flake8`

### TypeScript/Compact
- Follow Compact best practices
- Comment complex ZK circuits
- Use meaningful variable names
- Document proof requirements

### Shell Scripts
- Use bash with `set -euo pipefail`
- Add color-coded output for user feedback
- Include error handling and rollback logic
- Test on both Linux and macOS

## Testing

All contributions should include tests:

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Contract Tests
```bash
cd contracts
compact test ConfidentialRAG.compact
```

### End-to-End Tests
```bash
python demo/test-e2e.py
```

## Pull Request Guidelines

1. **Title**: Use descriptive title with conventional commit format
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Test additions/changes
   - `chore:` - Build/config changes

2. **Description**: Include:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Screenshots (if applicable)

3. **Tests**: All PRs must include tests

4. **Documentation**: Update relevant documentation

5. **Commits**:
   - Keep commits focused and atomic
   - Write clear commit messages
   - Reference issues when applicable

## Code Review Process

1. Automated checks must pass (tests, linting)
2. At least one maintainer approval required
3. Address all review comments
4. Squash commits before merging

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the problem
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - OS and version
   - Python/Node.js version
   - Docker version
   - Midnight CLI version
6. **Logs**: Relevant error logs or screenshots

## Feature Requests

Feature requests are welcome! Please include:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: What alternatives have you considered?
4. **Additional Context**: Any other relevant information

## Areas for Contribution

### High Priority
- [ ] Real Midnight SDK integration (replace placeholders)
- [ ] RAGAS evaluation implementation
- [ ] Production deployment guides (AWS/GCP/Azure)
- [ ] Advanced ZK circuits (cross-encoder proofs)
- [ ] Performance benchmarking

### Medium Priority
- [ ] Additional retrieval strategies (HyDE, multi-query)
- [ ] Document versioning
- [ ] Access control and permissions
- [ ] Query cost tracking
- [ ] Reputation system

### Good First Issues
- [ ] Improve error messages
- [ ] Add more demo datasets
- [ ] Write additional tests
- [ ] Improve documentation
- [ ] Fix UI/UX issues

## Security

If you discover a security vulnerability, please email security@example.com instead of opening a public issue.

## Community

- Join the [Midnight Discord](https://discord.gg/midnightnetwork)
- Use the #mlh-hackers channel for questions
- Follow [@MidnightNtwrk](https://twitter.com/MidnightNtwrk) on Twitter

## License

By contributing to ConfidentialRAG, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue with the `question` label if you need help!

Thank you for contributing! 🎉
