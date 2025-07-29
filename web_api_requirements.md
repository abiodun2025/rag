# Flask Web API for User Management

## Requirements:
- RESTful API endpoints for CRUD operations
- User authentication and authorization
- Database integration (SQLite for simplicity)
- Input validation and error handling
- API documentation with Swagger/OpenAPI
- Unit tests with pytest

## Endpoints:
- GET /users - List all users
- POST /users - Create new user
- GET /users/{id} - Get user by ID
- PUT /users/{id} - Update user
- DELETE /users/{id} - Delete user
- POST /auth/login - User login
- POST /auth/register - User registration

## Features:
- JWT token authentication
- Password hashing
- Input sanitization
- Rate limiting
- CORS support

## Constraints:
- Use Flask and Flask-RESTful
- SQLite database
- JWT for authentication
- Comprehensive error handling
