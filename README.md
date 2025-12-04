# Expense Tracker

A comprehensive web application for tracking personal expenses, managing budgets, and analyzing spending patterns.

##  Features

- **User Authentication**
  - Secure signup and login
  - Password reset functionality
  - User profile management

- **Expense Management**
  - Add, edit, and delete expenses
  - Categorize expenses
  - Add notes and attachments

- **Budget Tracking**
  - Set monthly budgets
  - Track spending against budgets
  - Visual budget reports

- **Reports & Analytics**
  - Expense trends
  - Category-wise spending
  - Export reports (CSV/PDF)

##  Tech Stack

### Backend
- **Framework**: Django 4.2
- **Database**: SQLite (Development), PostgreSQL (Production-ready)
- **Authentication**: Django's built-in auth system
- **API**: Django REST Framework (if applicable)

### Frontend
- **HTML5** with Django Templates
- **CSS3** with Bootstrap 5
- **JavaScript** for interactive elements
- **Chart.js** for data visualization

### Development Tools
- **Version Control**: Git
- **Package Manager**: pip
- **Virtual Environment**: venv

##  Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git (for version control)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker
   ```

2. **Set up a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (admin account)
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/


##  Configuration

1. **Environment Variables**
   Create a `.env` file in the project root with:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

2. **Database**
   - By default, SQLite is used for development
   - For production, configure PostgreSQL in `settings.py`

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


##  Acknowledgments

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [Font Awesome](https://fontawesome.com/)
