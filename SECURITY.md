# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

TaskFlow takes security issues seriously. We appreciate your efforts to responsibly disclose your findings.

To report a security vulnerability, please follow these steps:

1. **DO NOT** create a public GitHub issue for the vulnerability.
2. Email kiaranhurley@gmail.com with a detailed description of the vulnerability.
3. Include steps to reproduce the vulnerability if possible.
4. We will acknowledge receipt of your vulnerability report as soon as possible and send you regular updates about our progress.

## What to Expect

- An acknowledgment of your report within 48 hours.
- An assessment of the security issue and its impact.
- An explanation of how we plan to address the issue.
- Notification when the issue has been resolved.

## Security Best Practices for Contributors

If you're contributing to TaskFlow, please follow these security best practices:

1. **Never** commit sensitive information (API keys, credentials, personal data) to the repository.
2. Keep dependencies up to date.
3. Follow secure coding practices:
   - Validate all user inputs
   - Use parameterized queries for database operations
   - Sanitize data before display
   - Implement proper authentication and authorization
4. Write tests that verify security controls.

## Security Features

TaskFlow implements the following security features:

- Input validation and sanitization
- CSRF protection
- Secure password handling
- Session management
- Role-based access control

Thank you for helping keep TaskFlow and its users safe! 