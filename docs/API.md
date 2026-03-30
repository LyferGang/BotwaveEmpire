# Botwave API Documentation

## Base URL

```
https://api.botwave.app/v1
```

## Authentication

All requests require an API key in the header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents_available": ["business", "plumbing", "intelligence"]
}
```

### List Agents

```http
GET /agents
```

**Response:**
```json
{
  "agents": [
    {
      "name": "business",
      "description": "Financial audits and business analytics"
    },
    {
      "name": "plumbing",
      "description": "Service business automation"
    },
    {
      "name": "intelligence",
      "description": "LLM-powered analysis"
    }
  ]
}
```

### Run Agent

```http
POST /agents/{agent_name}/run
Content-Type: application/json

{
  "action": "audit",
  "data": {
    "audit_type": "financial"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Audit completed",
  "data": {
    "audit_type": "financial",
    "findings": []
  }
}
```

### Agent Health

```http
GET /agents/{agent_name}/health
```

## Error Responses

```json
{
  "status": "error",
  "message": "Agent not found",
  "code": 404
}
```

## Rate Limits

- Starter: 500 requests/month
- Professional: 5,000 requests/month
- Enterprise: Unlimited
