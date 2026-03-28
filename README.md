# Baysal NAC System

Network Access Control (NAC) system built with FreeRADIUS, FastAPI, PostgreSQL and Redis.

## Tech Stack

| Service | Image | Port |
|---------|-------|------|
| FreeRADIUS | freeradius/freeradius-server:latest-3.2 | 1812/1813 UDP |
| FastAPI | python:3.13-slim | 8000 |
| PostgreSQL | postgres:18-alpine | 5432 |
| Redis | redis:8-alpine | 6379 |

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/baysal-nac-system.git
cd baysal-nac-system
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values. The following variables are required:

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_DB | Database name | radius |
| POSTGRES_USER | Database user | radius |
| POSTGRES_PASSWORD | Database password | - |
| POSTGRES_HOST | Database host (do not change) | postgres |
| POSTGRES_PORT | Database port (do not change) | 5432 |
| REDIS_HOST | Redis host (do not change) | redis |
| REDIS_PORT | Redis port (do not change) | 6379 |
| API_PORT | FastAPI port | 8000 |
| RADIUS_SECRET | Shared secret between NAS and FreeRADIUS | - |

> `POSTGRES_HOST`, `POSTGRES_PORT`, `REDIS_HOST`, `REDIS_PORT` are Docker internal addresses — do not change them.

### 3. Start all services

```bash
docker-compose up --build -d
```

All 4 services will start in the correct order based on healthcheck dependencies:
`postgres` → `redis` → `api` → `freeradius`

### 4. Verify services are running

```bash
docker-compose ps
```

All services should show `healthy` status.

---

## Testing

### Authentication (PAP)

```bash
# Admin user — should return Access-Accept with VLAN 10
docker exec -it nac_freeradius radtest admin1 admin123 localhost 0 testing123

# Employee user — should return Access-Accept with VLAN 20
docker exec -it nac_freeradius radtest emp1 emp123 localhost 0 testing123

# Guest user — should return Access-Accept with VLAN 30
docker exec -it nac_freeradius radtest guest1 guest123 localhost 0 testing123

# Wrong password — should return Access-Reject
docker exec -it nac_freeradius radtest admin1 wrongpassword localhost 0 testing123
```

### Accounting

```bash
# Enter the FreeRADIUS container
docker exec -it nac_freeradius bash

# Send Accounting-Start
radclient -x -r 1 127.0.0.1:1813 acct testing123 <<EOF
User-Name = "admin1"
Acct-Status-Type = Start
Acct-Session-Id = "test-session-001"
NAS-IP-Address = 127.0.0.1
EOF

# Send Accounting-Stop
radclient -x -r 1 127.0.0.1:1813 acct testing123 <<EOF
User-Name = "admin1"
Acct-Status-Type = Stop
Acct-Session-Id = "test-session-001"
NAS-IP-Address = 127.0.0.1
Acct-Session-Time = 120
Acct-Input-Octets = 50000
Acct-Output-Octets = 100000
EOF
```

### Verify accounting records

```bash
# Check PostgreSQL — session should appear with start/stop times
docker exec -it nac_postgres psql -U radius -d radius \
  -c "SELECT acctsessionid, username, acctstarttime, acctstoptime, acctsessiontime FROM radacct;"

# Check Redis — active sessions (empty after Stop)
docker exec -it nac_redis redis-cli keys "session:*"
```

### FastAPI endpoints

```bash
# Health check
curl http://localhost:8000/health

# List all users
curl http://localhost:8000/users

# List active sessions
curl http://localhost:8000/sessions/active
```

---

## Project Structure

```
baysal-nac-system/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPI app, lifespan, /health /users /sessions/active
│       ├── db.py            # asyncpg pool and Redis connection
│       ├── models.py        # Pydantic schemas (FreeRADIUS-compatible)
│       └── routes/
│           ├── auth.py      # POST /auth — bcrypt verification + rate limiting
│           ├── authorize.py # POST /authorize — VLAN attribute assignment
│           └── accounting.py# POST /accounting — session Start/Update/Stop
├── freeradius/
│   ├── clients.conf         # NAS definitions and shared secrets
│   ├── mods-enabled/
│   │   ├── rest             # rlm_rest — FastAPI integration
│   │   └── sql              # rlm_sql — PostgreSQL connection
│   └── sites-enabled/
│       └── default          # AAA flow definition
├── postgres/
│   └── init.sql             # Schema and test data
├── .env.example
├── .gitignore
└── docker-compose.yml
```

---

## Test Users

| Username | Password | Group | VLAN |
|----------|----------|-------|------|
| admin1 | admin123 | admin | 10 |
| emp1 | emp123 | employee | 20 |
| guest1 | guest123 | guest | 30 |

---

## Stopping the system

```bash
# Stop services (keep data)
docker-compose down

# Stop services and remove all data
docker-compose down -v
```
