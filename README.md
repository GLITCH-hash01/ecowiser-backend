# Ecowiser

## Overview
Ecowiser is a multi-tenant platform designed to manage users, projects, billings, and resources. It provides APIs for authentication, tenant management, project handling, billing, and media processing. The platform is built using Django, Celery, and PostgreSQL, with AWS S3 for media storage.

---

## Features
- **Authentication**: JWT-based authentication.
- **Multi-Tenant Architecture**: Each tenant has its own users, projects, subscriptions, and invoices.
- **Media Management**: Upload and process media files using Celery tasks.
- **Billing**: Subscription tiers and automated invoice generation.
- **Comprehensive Documentation**: All details consolidated into this README.

---

## Project Structure
```
Ecowiser/
├── ecowiser/                # Core Django project files
├── users/                   # User management app
├── tenants/                 # Tenant management app
├── projects/                # Project management app
├── billings/                # Billing and subscription app
├── resources/               # Media and resource management app
├── utils/                   # Shared utilities
├── staticfiles/             # Static files
├── media/                   # Media files
├── nginx/                   # Nginx configuration
├── Dockerfile.dev           # Dockerfile for development
├── Dockerfile.prod          # Dockerfile for production
├── docker-compose.dev.yml   # Docker Compose for development
├── docker-compose.prod.yml  # Docker Compose for production
├── requirements.txt         # Python dependencies
├── .env.dev                 # Environment variables for development
└── README.md                # Project overview and documentation
```

---

## Setup Instructions

### Prerequisites
- Python 3.12
- Docker and Docker Compose
- PostgreSQL
- AWS S3 bucket for media storage

### Local Development Setup
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd Ecowiser
   ```

2. Create a `.env.dev` file based on the provided template and update the values.

3. Build and start the development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. Apply migrations:
   ```bash
   docker exec backend python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker exec backend python manage.py createsuperuser
   ```

6. Access the application at `http://localhost:8000`.

---

## Environment Setup

### .env File Configuration
The `.env` file is used to store environment variables required for the project. Below is a list of all the variables that need to be included:

#### Database Configuration
- **`DB_USER`**: The username for the PostgreSQL database.
- **`DB_PASSWORD`**: The password for the PostgreSQL database.
- **`DB_HOST`**: The host address for the PostgreSQL database (e.g., `localhost` or `host.docker.internal` for Docker).
- **`DB_PORT`**: The port number for the PostgreSQL database (default: `5432`).

#### Django Configuration
- **`DJANGO_SECRET_KEY`**: The secret key for the Django application. This should be a long, random string.

#### AWS S3 Configuration
- **`AWS_ACCESS_KEY_ID`**: The access key ID for AWS S3.
- **`AWS_SECRET_ACCESS_KEY`**: The secret access key for AWS S3.
- **`AWS_STORAGE_BUCKET_NAME`**: The name of the S3 bucket where media files will be stored.
- **`AWS_S3_REGION_NAME`**: The AWS region where the S3 bucket is located.
- **`AWS_S3_CUSTOM_DOMAIN`**: The custom domain for accessing the S3 bucket (e.g., `bucket-name.s3.amazonaws.com`).

#### Email Configuration
- **`EMAIL_HOST_USER`**: The email address used for sending emails.
- **`EMAIL_HOST_PASSWORD`**: The password for the email account.
- **`EMAIL_BACKEND`**: The email backend to use (e.g., `django.core.mail.backends.smtp.EmailBackend`).
- **`EMAIL_HOST`**: The SMTP host for the email service (e.g., `smtp.gmail.com`).
- **`EMAIL_PORT`**: The port number for the SMTP service (default: `587`).
- **`EMAIL_USE_TLS`**: Whether to use TLS for email communication (default: `True`).
- **`DEFAULT_FROM_EMAIL`**: The default email address for outgoing emails (e.g., `Ecowiser <email@example.com>`).

---

## API Documentation


## Routes

### Authentication
- **Login**: `POST /users/login/` - Authenticate user and retrieve tokens.
- **Refresh Token**: `POST /users/login/refresh/` - Refresh access token.
- **Verify Token**: `POST /users/login/verify/` - Verify token validity.

### Users
- **Create User**: `POST /users/sign-up/` - Register a new user.
- **Retrieve User**: `GET /users/<id>/` - Get user details.
- **Self User Operations**: `GET, PUT, DELETE /users/self/` - Manage own user account.

### Tenants
- **Create Tenant**: `POST /tenants/` - Add a new tenant.
- **Retrieve Tenant**: `GET /tenants/<id>/` - Get tenant details.
- **Update Tenant**: `PUT /tenants/<id>/` - Modify tenant information.
- **Delete Tenant**: `DELETE /tenants/<id>/` - Remove a tenant.

### Projects
- **Create Project**: `POST /projects/` - Add a new project.
- **Retrieve Project**: `GET /projects/<id>/` - Get project details.
- **Update Project**: `PUT /projects/<id>/` - Modify project information.
- **Delete Project**: `DELETE /projects/<id>/` - Remove a project.

### Billings
- **Create Subscription**: `POST /billings/subscriptions/` - Subscribe to a plan.
- **Retrieve Subscription**: `GET /billings/subscriptions/<id>/` - Get subscription details.
- **Create Invoice**: `POST /billings/invoices/` - Generate an invoice.
- **Retrieve Invoice**: `GET /billings/invoices/<id>/` - Get invoice details.

### Resources
- **Upload Media**: `POST /resources/media/` - Upload media files.
- **Delete Media**: `DELETE /resources/media/<id>/` - Remove media files.
- **Handle CSV**: `POST /resources/csv/` - Process CSV files.

For detailed examples and additional information, refer to the [Postman Collection](Ecowise.postman_collection.json).

---

## Deployment

### Production Setup
1. Update the `.env` file with production values.
2. Build and start the production environment:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build
   ```
3. Apply migrations:
   ```bash
   docker exec backend python manage.py migrate
   ```


---

## Troubleshooting

### Common Issues
- **Database connection errors**: Verify `.env` values and database accessibility.
- **AWS S3 upload errors**: Check AWS credentials and bucket permissions.
- **Docker build issues**: Ensure Docker is installed and running.


