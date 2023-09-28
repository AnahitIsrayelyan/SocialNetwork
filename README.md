# SocialNetwork


## Overview

This is a simple social networking application built using Flask. Users can register, log in, post messages, follow other users, and view a stream of posts from users they follow. Below, you'll find instructions on how to run the project, its structure, and the technologies used.

## Technologies Used

- Flask: A micro web framework for Python.
- Peewee: A lightweight ORM for database operations.
- Flask-Bcrypt: Used for hashing passwords securely.
- Flask-Login: Handles user authentication and session management.
- Flask-WTF: Integrates WTForms for form handling and validation.

## How to Run

1. Clone this GitHub repository:
  git clone <repository-url>

2. Install the required Python packages:
  pip install -r requirements.txt

3. Set up the database:

- The project uses an SQLite database named `social.db`. You can create it by running the following command:

  ```
  python run.py
  ```

4. Run the application:
  python run.py


The application will be available at `http://localhost:8080`.

## Project Structure

- `app.py`: The main application file that defines routes and handles requests.
- `forms.py`: Contains form classes for user registration, login, posting, and searching.
- `models.py`: Defines database models for users, posts, and relationships.
- `run.py`: Initializes the database, creates a test user, and starts the Flask application.
- `templates/`: Directory containing HTML templates for rendering web pages.
- `static/`: Directory for static files like CSS and JavaScript (not included in your code snippet).

## Usage

1. Register: Create an account with a unique username and email.
2. Login: Authenticate with your registered email and password.
3. Post: Share thoughts by creating new posts.
4. Follow: Connect with other users by following their profiles.
5. Explore: View a stream of posts from users you follow on the home page.
6. Search: Look for users by their usernames using the search feature.
7. Following: See posts from users you follow on the "Following" page.


