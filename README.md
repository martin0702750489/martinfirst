# Hospital Management System

A comprehensive hospital management system built with FastAPI (Python) backend and React (JavaScript) frontend. This system provides role-based access control for patients, doctors, nurses, and administrators to manage hospital operations efficiently.

## Features

### 🏥 Core Functionality
- **Patient Management**: Registration, profiles, medical history
- **Doctor Management**: Profiles, specializations, schedules, availability
- **Appointment Scheduling**: Booking, calendar view, conflict detection
- **Medical Records**: Secure patient records, diagnoses, treatments
- **Dashboard**: Role-specific dashboards with statistics and quick actions

### 👤 Role-Based Access Control
- **Admin**: Full system access, user management
- **Doctor**: Patient records, appointments, medical records
- **Nurse**: Patient care, appointment assistance
- **Patient**: Personal appointments, medical history
- **Receptionist**: Appointment scheduling, patient registration

### 🛡️ Security Features
- JWT token authentication
- Role-based permissions
- Secure password hashing
- API request validation

### 🎨 Modern UI/UX
- Material-UI design system
- Responsive mobile-first design
- Intuitive navigation
- Real-time updates

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **JWT**: Authentication tokens
- **Pydantic**: Data validation
- **Alembic**: Database migrations

### Frontend
- **React 18**: Modern UI library
- **Material-UI**: Component library
- **React Router**: Navigation
- **Axios**: HTTP client
- **React Hook Form**: Form management

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **PostgreSQL**: Database service

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hospital-management-system
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env file with your configurations
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Demo Credentials

#### Admin Access
- Username: `admin`
- Password: `admin123`

#### Doctor Access
- Username: `doctor1`
- Password: `doctor123`

#### Patient Access
- Username: `patient1`
- Password: `patient123`

## Development Setup

### Backend Development

1. **Setup Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database setup**
   ```bash
   # Start PostgreSQL
   docker run -d --name postgres \
     -e POSTGRES_DB=hospital_db \
     -e POSTGRES_USER=hospital_user \
     -e POSTGRES_PASSWORD=hospital_pass \
     -p 5432:5432 postgres:15
   ```

3. **Run the backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Development

1. **Setup Node.js environment**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the frontend**
   ```bash
   npm start
   ```

## API Documentation

The FastAPI backend automatically generates interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key API Endpoints

#### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user

#### Patients
- `GET /patients` - List patients
- `POST /patients` - Create patient
- `GET /patients/{id}` - Get patient details
- `PUT /patients/{id}` - Update patient

#### Doctors
- `GET /doctors` - List doctors
- `POST /doctors` - Create doctor
- `GET /doctors/{id}` - Get doctor details
- `PUT /doctors/{id}` - Update doctor

#### Appointments
- `GET /appointments` - List appointments
- `POST /appointments` - Create appointment
- `PUT /appointments/{id}` - Update appointment
- `DELETE /appointments/{id}` - Cancel appointment

#### Medical Records
- `GET /medical-records` - List medical records
- `POST /medical-records` - Create medical record
- `GET /medical-records/{id}` - Get medical record
- `PUT /medical-records/{id}` - Update medical record

## Database Schema

### Core Tables
- **users**: User authentication and basic info
- **patients**: Patient-specific information
- **doctors**: Doctor profiles and availability
- **appointments**: Appointment scheduling
- **medical_records**: Patient medical history
- **departments**: Hospital departments

### Key Relationships
- Users have roles (patient, doctor, admin, etc.)
- Patients and Doctors are linked to Users
- Appointments link Patients and Doctors
- Medical Records track patient-doctor interactions

## Security Considerations

- All API endpoints require authentication (except login/register)
- Role-based access control ensures users only access permitted data
- Passwords are hashed using bcrypt
- JWT tokens have configurable expiration
- Database queries use SQLAlchemy ORM to prevent SQL injection

## Deployment

### Production Deployment

1. **Update environment variables**
   ```bash
   # Set production values in .env
   SECRET_KEY=your-strong-secret-key
   DATABASE_URL=postgresql://user:pass@host:port/db
   ```

2. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://hospital_user:hospital_pass@localhost:5432/hospital_db` |
| `SECRET_KEY` | JWT signing key | `your-secret-key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation at `/docs`

## Roadmap

### Phase 1 (Current)
- ✅ Basic authentication
- ✅ User roles and permissions
- ✅ Core database models
- ✅ REST API endpoints
- ✅ Basic frontend structure

### Phase 2 (Planned)
- 🔄 Complete frontend pages
- 🔄 Advanced appointment scheduling
- 🔄 Medical records management
- 🔄 Reporting and analytics
- 🔄 Email notifications

### Phase 3 (Future)
- 📱 Mobile app
- 🔔 Real-time notifications
- 📊 Advanced analytics
- 🏥 Multi-hospital support
- 🔗 Integration with medical devices
