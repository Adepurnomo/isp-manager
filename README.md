# ISP Manager - Production-Ready ISP Management System

A complete, production-ready ISP (Internet Service Provider) Management System built with Python Flask, MariaDB, and modern cloud-native architecture for Rocky Linux 9.

## Features

### Core Management
- **Multi-tenant Architecture**: Complete tenant isolation with secure data access
- **Customer Management**: Full lifecycle management from signup to suspension
- **Billing System**: Automated invoice generation, payment processing, and accounting
- **Automatic Suspension**: Scheduler-based service suspension for overdue payments
- **Audit Logging**: Complete audit trail of all system operations

### Network Management
- **Mikrotik RouterOS Integration**: PPP, Hotspot, Queue management
- **FreeRADIUS Integration**: User authentication and accounting
- **VPN Management**: Support for PPTP, L2TP/IPSec, SSTP, OpenVPN, WireGuard
- **Network Monitoring**: Real-time device metrics and historical data

### Payment Processing
- **Multi-Gateway Support**: Midtrans, Xendit, Tripay integrations
- **Webhook Handling**: Secure callback processing and verification
- **Automatic Settlement**: Invoice reconciliation on payment receipt

### Customer Communication
- **WhatsApp Notifications**: Integration for service notifications
- **Notification Templates**: Configurable message templates for various events
- **Notification Logging**: Complete notification history tracking

### Portal & Access
- **Customer Portal**: Self-service portal with invoice management
- **Role-Based Access Control**: Super Admin, Tenant Admin, Billing, NOC, Customer Service
- **JWT Authentication**: Secure token-based authentication with refresh tokens

## Technology Stack

- **Backend**: Python 3.12+, Flask
- **Database**: MariaDB 11.x (InnoDB, Foreign Keys, Transactions)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Scheduling**: APScheduler
- **Server**: Gunicorn with Nginx reverse proxy
- **API Documentation**: OpenAPI/Swagger

## Project Structure

```
isp-manager/
├── backend/                          # Backend Flask application
│   ├── app/
│   │   ├── __init__.py              # Flask app initialization
│   │   ├── config.py                # Configuration management
│   │   ├── models/                  # SQLAlchemy models
│   │   ├── routes/                  # API endpoints
│   │   ├── services/                # Business logic
│   │   ├── middleware/              # Middleware (tenant, auth, etc)
│   │   ├── utils/                   # Utility functions
│   │   └── integrations/            # External integrations
│   ├── migrations/                  # Database migrations
│   ├── tests/                       # Test suite
│   ├── requirements.txt             # Python dependencies
│   ├── wsgi.py                      # Gunicorn entry point
│   └── docker-compose.yml           # Docker development environment
├── customer-portal/                 # Customer portal (React/Vue)
│   ├── src/
│   ├── public/
│   └── package.json
├── installer/                       # Rocky Linux installation script
│   └── install.sh
├── docs/                            # Documentation
│   ├── API.md
│   ├── INSTALLATION.md
│   ├── DEPLOYMENT.md
│   ├── DATABASE_ERD.md
│   └── ENV_VARIABLES.md
└── docker-compose.yml              # Production docker compose

```

## Installation

### Quick Start (Development)

```bash
# Clone repository
git clone https://github.com/yourusername/isp-manager.git
cd isp-manager

# Using Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec backend flask db upgrade

# Create admin user
docker-compose exec backend flask create-admin
```

### Production Installation (Rocky Linux 9)

```bash
chmod +x installer/install.sh
./installer/install.sh
```

See [INSTALLATION.md](docs/INSTALLATION.md) for detailed instructions.

## API Documentation

API documentation is available at `/api/docs` when the application is running.

Endpoints are organized by resource:
- `/api/v1/auth` - Authentication endpoints
- `/api/v1/customers` - Customer management
- `/api/v1/invoices` - Billing and invoicing
- `/api/v1/payments` - Payment processing
- `/api/v1/services` - Service packages
- `/api/v1/routers` - Router management
- `/api/v1/vpn` - VPN management
- `/api/v1/notifications` - Notification management
- `/api/v1/audit-logs` - Audit logging

## Environment Variables

Create `.env` file in the root directory. See [ENV_VARIABLES.md](docs/ENV_VARIABLES.md) for complete list.

```env
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/isp_manager
ENVIRONMENT=development

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

# Payment Gateways
MIDTRANS_SERVER_KEY=your-midtrans-key
XENDIT_API_KEY=your-xendit-key
TRIPAY_API_KEY=your-tripay-key

# WhatsApp
WHATSAPP_API_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER=+62xxxxx

# Mikrotik
MIKROTIK_HOST=192.168.1.1
MIKROTIK_USERNAME=admin
MIKROTIK_PASSWORD=password

# FreeRADIUS
RADIUS_HOST=192.168.1.1
RADIUS_PORT=1812
RADIUS_SECRET=shared-secret
```

## Database Schema

The system uses a comprehensive database schema with the following main entities:

- **tenants** - Multi-tenant organization data
- **users** - System users with roles and permissions
- **customers** - ISP customers
- **service_packages** - Service offerings
- **invoices** - Billing documents
- **payments** - Payment records
- **routers** - Network routers (Mikrotik)
- **radius_users** - RADIUS authentication users
- **vpn_servers** & **vpn_users** - VPN management
- **network_devices** & **device_metrics** - Network monitoring
- **audit_logs** - System audit trail
- **notifications** - User notifications

See [DATABASE_ERD.md](docs/DATABASE_ERD.md) for complete schema diagram.

## Authentication

The system implements JWT-based authentication with the following roles:

1. **Super Admin** - Full system access
2. **Tenant Admin** - Tenant-level management
3. **Billing** - Invoice and payment management
4. **NOC** - Network operations center
5. **Customer Service** - Customer support

## Multi-Tenant Architecture

All data queries are automatically filtered by tenant. The system enforces:
- Tenant middleware authentication
- Tenant-based row filtering
- Tenant ownership validation
- Cross-tenant access prevention

## API Response Format

All API responses follow a consistent format:

```json
{
  "status": "success",
  "message": "Operation completed",
  "data": {},
  "timestamp": "2025-01-01T12:00:00Z"
}
```

Error responses:

```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## Development

### Running Tests

```bash
cd backend
pytest
```

### Code Style

Uses `black`, `flake8`, and `isort`:

```bash
black app/
flake8 app/
isort app/
```

### Database Migrations

Create migration:
```bash
flask db migrate -m "Description"
```

Apply migration:
```bash
flask db upgrade
```

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment guidelines.

## License

Proprietary - All Rights Reserved

## Support

For support issues, please contact support@ispmanager.local

## Contributing

Please follow the contributing guidelines in CONTRIBUTING.md
