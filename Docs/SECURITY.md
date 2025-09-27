# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting Security Vulnerabilities

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them responsibly through one of the following channels:

1. **Email**: Send details to `security@yourdomain.com` (if applicable)
2. **GitHub Security Advisory**: Use [GitHub's security advisory feature](https://github.com/sanjanb/ocr-automation-pipeline/security/advisories/new)
3. **Private Issue**: Create a private security issue (if your repository supports it)

### What to Include

When reporting a security vulnerability, please include:

- **Type of issue** (e.g., buffer overflow, SQL injection, XSS, etc.)
- **Full paths** of source files related to the manifestation of the issue
- **Location** of the affected source code (tag/branch/commit or direct URL)
- **Special configuration** required to reproduce the issue
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact** of the issue, including how an attacker might exploit it

### Response Timeline

- **Acknowledgment**: We'll acknowledge receipt within 48 hours
- **Initial Assessment**: We'll provide an initial assessment within 5 business days
- **Regular Updates**: We'll send updates every 5 business days until resolved
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

## Security Measures

### Current Security Features

#### API Security

- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: Protection against DoS attacks
- **CORS Configuration**: Restricted cross-origin requests
- **File Upload Limits**: Maximum file size restrictions
- **Content Type Validation**: Only allowed file types accepted

#### Data Security

- **No Data Persistence**: Documents are not stored after processing
- **Memory Cleanup**: Processed images cleared from memory
- **Environment Variables**: Sensitive data stored in environment variables
- **API Key Protection**: Gemini API keys secured via environment configuration

#### Infrastructure Security

- **Docker Security**: Non-root user in containers
- **Dependency Scanning**: Automated vulnerability scanning with safety
- **CI/CD Security**: Secure secrets management in GitHub Actions
- **HTTPS Enforcement**: Production deployments should use HTTPS

### Recommended Security Practices

#### For Deployment

1. **Use HTTPS**: Always deploy behind HTTPS in production
2. **Environment Variables**: Never commit API keys to version control
3. **Network Security**: Use firewalls and network restrictions
4. **Regular Updates**: Keep dependencies updated
5. **Monitoring**: Implement logging and monitoring
6. **Access Control**: Restrict API access as needed

#### For Development

1. **Secure Development**: Follow OWASP guidelines
2. **Code Review**: All changes should be reviewed
3. **Dependency Management**: Regularly audit dependencies
4. **Secret Scanning**: Use tools to prevent secret commits
5. **Static Analysis**: Run security linters (bandit)

## Known Security Considerations

### File Upload Security

- **File Type Validation**: Only specific image formats allowed
- **File Size Limits**: 10MB maximum to prevent DoS
- **Content Scanning**: Files are validated before processing
- **Memory Management**: Files processed in memory, not saved

### API Security

- **Rate Limiting**: Prevents abuse and DoS attacks
- **Input Sanitization**: All inputs validated before processing
- **Error Handling**: Secure error messages (no sensitive data exposure)
- **CORS Policy**: Configurable origin restrictions

### Third-Party Dependencies

- **Gemini API**: Uses official Google AI SDK
- **Dependency Monitoring**: Automated vulnerability scanning
- **Regular Updates**: Dependencies updated regularly
- **License Compliance**: All dependencies vetted for licensing

## Vulnerability Disclosure

### Our Commitment

- We take security seriously and appreciate responsible disclosure
- We'll work with you to understand and resolve issues quickly
- We'll credit researchers who report vulnerabilities responsibly
- We'll provide updates on our progress toward resolution

### Safe Harbor

We support safe harbor for security researchers who:

- Make a good faith effort to avoid privacy violations and data destruction
- Report vulnerabilities promptly and allow reasonable time for fixes
- Avoid social engineering, DoS, or physical attacks
- Don't access or modify data beyond what's necessary to demonstrate the vulnerability

## Security Updates

### Update Process

1. **Critical Vulnerabilities**: Immediate patch release
2. **High Severity**: Patch within 1 week
3. **Medium/Low Severity**: Next scheduled release
4. **Security Advisories**: Published for all security fixes

### Notification Channels

- **GitHub Releases**: Security fixes noted in release notes
- **Security Advisories**: GitHub security advisory system
- **Changelog**: All security fixes documented
- **README**: Major security updates mentioned

## Security Checklist for Contributors

Before contributing, ensure:

- [ ] No hardcoded secrets or credentials
- [ ] Input validation for all user inputs
- [ ] Proper error handling (no sensitive data in errors)
- [ ] Dependencies are up-to-date and secure
- [ ] Code follows security best practices
- [ ] Tests include security scenarios
- [ ] Documentation updated for security implications

## Security Tools and Scanning

### Automated Security Checks

- **bandit**: Python security linter
- **safety**: Dependency vulnerability scanner
- **GitHub Dependabot**: Automated dependency updates
- **GitHub Advanced Security**: Code scanning (if available)

### Manual Security Review

- Regular security audits of critical components
- Penetration testing for major releases
- Code review with security focus
- Dependency license and security review

## Contact Information

For security-related questions or concerns:

- **Security Email**: security@yourdomain.com (if applicable)
- **General Contact**: Open a private issue or discussion
- **Urgent Issues**: Use GitHub security advisory for immediate attention

## Acknowledgments

We thank the security research community for helping keep our project safe:

- [List of security researchers who helped]
- [Bug bounty program information if applicable]

---

**Last Updated**: September 26, 2025
**Policy Version**: 1.0

This policy is subject to updates. Please check back regularly for the latest version.
