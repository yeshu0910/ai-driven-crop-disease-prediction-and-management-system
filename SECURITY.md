# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public issue for security vulnerabilities
2. Email security concerns to: security@example.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge receipt within 3 business days and provide a detailed response within 10 business days.

## Security Measures

- All dependencies are audited regularly
- Static analysis with Bandit and Semgrep
- Secret scanning with Gitleaks
- Pre-commit hooks prevent secret commits
- Security scans run in CI/CD pipeline

## Data Protection

- Farmer data collected with explicit consent
- End-to-end encryption for data transmission
- Images processed securely with automatic deletion
- Compliance with data protection regulations
