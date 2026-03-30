# Botwave Business Setup Guide

Complete deployment guide for Botwave - Professional Business Automation

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/LyferGang/Botwave.git
cd Botwave
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Start services
python plumbing_telegram_bot.py &        # Customer bot
python dashboard/web_app.py &            # Web dashboard
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Customer      │     │   Telegram      │     │   Business      │
│   Portal        │◄────│   Bot           │◄────│   Dashboard     │
│   (Web)         │     │   (Quotes)      │     │   (Internal)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   SQLite Database         │
                    │   - customers             │
                    │   - quotes                │
                    │   - appointments          │
                    └───────────────────────────┘
```

## Component Breakdown

### 1. Telegram Bot (Customer-Facing)
- **File:** `plumbing_telegram_bot.py`
- **Purpose:** Handle customer quotes and scheduling
- **Access:** t.me/[your_bot_name]

**Features:**
- Instant quote generation
- Service scheduling
- Appointment reminders
- Emergency service info

**Setup:**
```bash
# Get token from @BotFather
export TG_PLUMBING_BOT_TOKEN="your_token"
python plumbing_telegram_bot.py
```

### 2. Customer Portal (Web)
- **File:** `website/customer_portal.html`
- **Purpose:** Let customers view quotes and appointments online
- **URL:** http://localhost:5000/website/customer_portal.html

**Features:**
- View active quotes
- See scheduled appointments
- Service history
- Quick contact options

### 3. Business Dashboard (Internal)
- **File:** `dashboard/web_app.py`
- **Purpose:** Manage agents, view stats, process payments
- **URL:** http://localhost:5000

**Features:**
- Real-time agent monitoring
- Stripe payment processing
- Task management
- System statistics

### 4. System Cleanup Tools
- **Files:** `BOTWAVE_CLEANUP.bat`, `BOTWAVE_MAINTENANCE.bat`
- **Purpose:** Keep customer computers optimized

## Database Schema

```sql
-- Customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT UNIQUE,
    phone TEXT,
    name TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quotes table
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT,
    customer_name TEXT,
    phone TEXT,
    service_type TEXT,
    description TEXT,
    price_low REAL,
    price_high REAL,
    estimated_hours INTEGER,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments table
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT,
    customer_name TEXT,
    phone TEXT,
    service_type TEXT,
    scheduled_date TEXT,
    scheduled_time TEXT,
    status TEXT DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Customer Portal API
- `GET /api/customer/stats/<telegram_id>` - Get customer statistics
- `GET /api/customer/quotes/<telegram_id>` - Get customer quotes
- `GET /api/customer/appointments/<telegram_id>` - Get customer appointments

### Payment API
- `POST /api/stripe/create-checkout-session` - Create payment session
- `GET /api/stripe/status` - Check Stripe configuration

### Agent API
- `GET /api/agents` - List all agents
- `GET /api/agents/<name>/health` - Check agent health
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - List all tasks

## Environment Variables

```bash
# Telegram
TG_PLUMBING_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Database
DATABASE_URL=sqlite:///data/plumbing_customers.db

# API
API_HOST=0.0.0.0
API_PORT=5000
API_SECRET_KEY=your_secret_key
```

## Deployment Options

### Option 1: Local Development
```bash
python plumbing_telegram_bot.py &
python dashboard/web_app.py &
```

### Option 2: Docker (Coming Soon)
```bash
docker-compose up -d
```

### Option 3: Production Server
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 dashboard.web_app:app

# Using Nginx reverse proxy
# See deployment/nginx.conf
```

## Customization

### Adding New Services
Edit `plumbing_telegram_bot.py`:
```python
PLUMBING_SERVICES = {
    "your_service": {
        "name": "Service Name",
        "base_price": 199,
        "hours": 2,
        "keywords": ["keyword1", "keyword2"],
        "description": "Service description"
    }
}
```

### Updating Pricing
Modify `LABOR_RATE` in `plumbing_telegram_bot.py`:
```python
LABOR_RATE = 95  # per hour
```

### Branding
Update these files:
- `website/index.html` - Company name
- `website/customer_portal.html` - Colors/logos
- `BOTWAVE_CLEANUP.bat` - Company info

## Testing

```bash
# Test bot
python -c "from plumbing_telegram_bot import *; print('OK')"

# Test dashboard
curl http://localhost:5000/api/agents

# Test database
sqlite3 data/plumbing_customers.db ".tables"
```

## Troubleshooting

### Bot not responding
- Check token is correct
- Ensure webhook is disabled (polling mode)
- Check firewall settings

### Dashboard not loading
- Check port 5000 is free
- Verify Flask is installed
- Check logs: `tail -f logs/dashboard.log`

### Database errors
- Ensure `data/` directory exists
- Check write permissions
- Run: `python -c "import plumbing_telegram_bot; plumbing_telegram_bot.init_database()"`

## Support

- **Documentation:** http://localhost:5000/docs
- **Dashboard:** http://localhost:5000
- **Customer Portal:** http://localhost:5000/website/customer_portal.html

## Next Steps

1. [ ] Get Telegram bot token from @BotFather
2. [ ] Configure Stripe for payments
3. [ ] Customize service prices
4. [ ] Test customer flow
5. [ ] Set up customer computers with cleanup tools
6. [ ] Schedule monthly maintenance

---

**Botwave** - Professional IT Automation
Built for businesses that need reliable, private automation.
