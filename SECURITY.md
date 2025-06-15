# Security Guidelines - NYC Public Health MVP

## 🔐 API Key Security

### ⚠️ CRITICAL: Never Commit API Keys to Git

This project uses external APIs that require API keys. **NEVER** hardcode API keys in your source code.

### ✅ Secure API Key Management

#### For Local Development:
1. **Create a .env file** (not committed to git):
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to .env**:
   ```
   OPENROUTER_API_KEY=your_actual_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

3. **Load environment variables** in your code:
   ```python
   import os
   API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
   ```

#### For Production Deployment:

##### Heroku:
```bash
heroku config:set OPENROUTER_API_KEY=your_api_key_here
heroku config:set SECRET_KEY=your_secret_key_here
```

##### Other Platforms:
- Set environment variables in your hosting platform's dashboard
- Never include API keys in deployment files

### 🛡️ Security Checklist

- [ ] API keys stored in environment variables only
- [ ] .env file added to .gitignore
- [ ] No hardcoded secrets in source code
- [ ] Production environment variables configured
- [ ] Old/exposed API keys revoked and replaced

### 🚨 If You Accidentally Commit an API Key:

1. **Immediately revoke the exposed key** in your API provider dashboard
2. **Generate a new API key**
3. **Remove the key from git history**:
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch filename_with_key.py' \
   --prune-empty --tag-name-filter cat -- --all
   ```
4. **Force push to update remote repository**:
   ```bash
   git push origin --force --all
   ```

### 📞 Reporting Security Issues

If you discover a security vulnerability, please report it privately to the repository maintainer.

## 🔒 Additional Security Measures

### Authentication
- Default admin credentials should be changed immediately
- Use strong passwords for production deployments
- Consider implementing 2FA for production systems

### Database Security
- SQLite database contains no sensitive personal information
- All data is aggregated and anonymized
- Regular backups recommended for production

### Network Security
- Use HTTPS in production
- Configure proper CORS settings
- Implement rate limiting for API endpoints

## 📚 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Environment Variable Security](https://12factor.net/config)
