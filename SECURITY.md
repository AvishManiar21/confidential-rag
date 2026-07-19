# Security Policy

## Supported Versions

This is a hackathon project. Security updates will be applied to the main branch.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Environment Variables and Secrets

**CRITICAL**: Never commit secrets to version control.

### Required Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```bash
# PostgreSQL - Use a strong password
POSTGRES_USER=raguser
POSTGRES_PASSWORD=<generate-strong-password>
POSTGRES_DB=confidentialrag

# ChromaDB - Generate a secure token
CHROMA_AUTH_TOKEN=<generate-secure-token>

# Application Secret Key - Generate with: openssl rand -hex 32
SECRET_KEY=<generate-secret-key>

# Database URL (uses variables above)
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
CHROMA_URL=http://localhost:8000
OLLAMA_URL=http://localhost:11434

# Midnight Configuration
MIDNIGHT_RPC_URL=http://localhost:8080
MIDNIGHT_CONTRACT_ADDRESS=
MIDNIGHT_PRIVATE_KEY=

# Environment
DEBUG=false
```

### Generating Secure Values

```bash
# PostgreSQL password (32 characters)
openssl rand -base64 32

# ChromaDB auth token (64 characters)
openssl rand -hex 32

# Application secret key (64 characters)
openssl rand -hex 32
```

## Privacy Guarantees

ConfidentialRAG provides the following privacy guarantees through Midnight blockchain:

| Data Type | Storage | Visibility | Protection |
|-----------|---------|------------|------------|
| Document content | ChromaDB (off-chain) | Owner only | Local encryption |
| Document embeddings | Midnight (commitment) | Hidden | ZK proof only |
| User query | Client-side only | User only | Never sent to chain |
| Query embedding | Commitment on-chain | User only | ZK commitment |
| Retrieval results | Off-chain API | User only | Local processing |
| Similarity score | ZK proof on-chain | Threshold met: YES/NO | Zero-knowledge |
| RAGAS metrics | ZK proof on-chain | Above threshold: YES/NO | Zero-knowledge |

## Security Best Practices

### Development

1. **Never commit `.env` files** - Already in `.gitignore`
2. **Use strong passwords** - Minimum 32 characters for production
3. **Rotate secrets regularly** - Especially after suspected exposure
4. **Use HTTPS in production** - TLS/SSL for all API communication
5. **Validate all inputs** - FastAPI Pydantic models handle this

### Deployment

1. **Use environment variables** - Never hardcode credentials
2. **Enable firewall rules** - Restrict database/ChromaDB access
3. **Use Docker secrets** - For production Docker deployments
4. **Enable audit logging** - Monitor all document/query operations
5. **Review CORS settings** - Restrict to trusted domains only

### Midnight Blockchain

1. **Protect private keys** - Never share or commit `MIDNIGHT_PRIVATE_KEY`
2. **Use testnet first** - Test deployments before mainnet
3. **Verify contracts** - Review compiled Compact contracts before deployment
4. **Monitor gas costs** - Set appropriate limits for ZK proof submission

## Threat Model

### In Scope

- Document content privacy (solved: local storage)
- Query privacy (solved: local processing)
- Embedding privacy (solved: ZK commitments)
- Retrieval verification (solved: ZK proofs)

### Out of Scope

- Denial of Service (rate limiting recommended but not implemented)
- Side-channel timing attacks on embeddings
- Physical access to ChromaDB storage
- Compromised client devices

## Reporting a Vulnerability

If you discover a security vulnerability, please email the maintainers directly:

1. **Do not** open a public GitHub issue
2. Email: [Add your security contact email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond within 48 hours.

## Acknowledgments

Security researchers who responsibly disclose vulnerabilities will be acknowledged in this file (with permission).

## Cryptographic Dependencies

This project uses the following cryptographic libraries:

- **hashlib** (Python stdlib) - SHA-256 hashing for commitments
- **secrets** (Python stdlib) - Cryptographically secure random generation
- **Midnight Compact** - Zero-knowledge proof circuits
- **ChromaDB** - Vector database with authentication

Always keep dependencies up to date:
```bash
pip install --upgrade -r requirements.txt
```

## Audit Trail

All document uploads and query operations are logged with:
- Timestamp
- User/session identifier
- Document/query hash
- Success/failure status
- Zero-knowledge proof transaction hash (when applicable)

Logs are stored in PostgreSQL and can be audited for compliance.
