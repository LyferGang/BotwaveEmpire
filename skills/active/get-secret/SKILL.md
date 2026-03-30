---
name: get-secret
description: Retrieve secrets from the vault securely
version: 1.0.0
author: Botwave Empire
---

# Get Secret Skill

Retrieves secrets from the secure vault.

## Usage

```
/get-secret <secret_name>
```

## Implementation

The skill reads from environment variables or the secrets vault.

## Security

- Never log secret values
- Mask output in chat
- Require authentication
