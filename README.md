# TaskFlow

TaskFlow is an open-source task management application designed to help individuals and teams organize their work efficiently.

## Features

- Create, update, and delete tasks
- Organize tasks with priorities and due dates
- Track task progress
- User authentication and authorization
- Team collaboration features

## Screenshots

*Coming soon*

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Setup

1. Clone the repository:
```
git clone https://github.com/kiaranhurley/TaskFlow.git
cd TaskFlow
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```
pip install -r requirements.txt
```

4. Initialize the database
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. Run the application:
```
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLite (for development), PostgreSQL (for production)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **CSS Framework**: Bootstrap 5
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF
- **Testing**: pytest

## Project Structure

```
TaskFlow/
├── app/                   # Application package
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # HTML templates
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── routes.py          # Route definitions
│   └── forms.py           # Form definitions
├── migrations/            # Database migrations
├── tests/                 # Test suite
├── .github/               # GitHub specific files
├── .gitignore             # Git ignore file
├── LICENSE                # MIT License
├── README.md              # This file
├── CONTRIBUTING.md        # Contribution guidelines
├── CODE_OF_CONDUCT.md     # Code of conduct
├── requirements.txt       # Project dependencies
└── app.py                 # Application entry point
```

## Development

### Setting Up Development Environment

Follow the installation steps above to set up your development environment.

### Running Tests

```bash
pytest
```

### Code Style

This project follows the PEP 8 style guide for Python code. We use flake8 for linting:

```bash
flake8 .
```

## API Documentation

*Coming soon*

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Flask documentation and community
- Bootstrap team for the CSS framework
- All our contributors

## Contact

Project Link: [https://github.com/kiaranhurley/TaskFlow](https://github.com/kiaranhurley/TaskFlow)

---

Made with ❤️ by [Your Name]