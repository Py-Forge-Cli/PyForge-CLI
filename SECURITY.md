# Security Policy

## Supported Versions

We actively support the following versions of PyForge CLI with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in PyForge CLI, please report it responsibly.

### How to Report

**Please do NOT create a public GitHub issue for security vulnerabilities.**

Instead, please:

1. **Email us directly**: Send details to dd.santosh@gmail.com
2. **Include**: 
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. **Subject line**: Use "SECURITY: PyForge CLI - [Brief Description]"

### What to Expect

- **Acknowledgment**: We'll acknowledge receipt within 48 hours
- **Investigation**: We'll investigate and assess the vulnerability
- **Timeline**: We aim to provide an initial response within 5 business days
- **Updates**: We'll keep you informed of our progress
- **Credit**: We'll credit you in the security advisory (if desired)

### Security Considerations

PyForge CLI processes various file formats which may contain:

#### Potential Security Risks

1. **File Processing**
   - Malicious PDF files with embedded content
   - Excel files with macros or external references
   - Access databases with malicious queries
   - DBF files with encoding exploits

2. **Path Traversal**
   - Output file paths could potentially be manipulated
   - Temporary file handling

3. **Memory Issues**
   - Large file processing could lead to DoS
   - Memory exhaustion attacks

4. **Dependencies**
   - Third-party library vulnerabilities
   - Supply chain security

#### Security Best Practices

When using PyForge CLI:

1. **Input Validation**
   - Only process files from trusted sources
   - Validate file extensions and content
   - Use sandboxed environments for untrusted files

2. **Output Security**
   - Verify output file paths
   - Set appropriate file permissions
   - Monitor disk space usage

3. **Environment Security**
   - Keep PyForge CLI updated
   - Monitor for dependency vulnerabilities
   - Use virtual environments

### Security Features

PyForge CLI implements several security measures:

1. **Input Validation**
   - File type verification
   - Size limits and validation
   - Path sanitization

2. **Safe Defaults**
   - No execution of embedded code
   - Safe temporary file handling
   - Controlled output locations

3. **Error Handling**
   - No sensitive information in error messages
   - Graceful failure for malformed files
   - Proper cleanup of temporary resources

### Dependency Security

We regularly:

- Monitor dependencies for known vulnerabilities
- Update dependencies to secure versions
- Use automated security scanning tools
- Pin dependency versions for reproducibility

### Disclosure Policy

When we receive a security report:

1. **Assessment**: We'll assess the severity and impact
2. **Fix Development**: We'll develop and test a fix
3. **Coordinated Disclosure**: We'll coordinate release timing with the reporter
4. **Public Disclosure**: We'll publish a security advisory after the fix is released

### Security Updates

Security updates will be:

- Released as patch versions (e.g., 0.2.1 → 0.2.2)
- Announced in our changelog
- Published as GitHub security advisories
- Communicated through appropriate channels

## Contact

For security-related inquiries:

- **Email**: dd.santosh@gmail.com
- **Subject**: "SECURITY: PyForge CLI - [Your Topic]"
- **PGP**: Available upon request

Please allow up to 48 hours for initial response.

## Thanks

We appreciate security researchers and users who help keep PyForge CLI secure. Responsible disclosure helps protect all users of the project.