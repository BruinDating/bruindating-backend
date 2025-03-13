# Bruin Dating Backend

Bruin Dating is a web application designed and built for students at UCLA. Through the application you are able to connect with your fellow bruins, and make friendships and maybe even meet the love of your life. This repository only contains the details for the backend of the application. The frontend is located here: [https://github.com/BruinDating/bruindating-frontend](https://github.com/BruinDating/bruindating-frontend)

## Getting started

### Required Technologies

- Python (v3.12 +)
- PostgreSQL
- pip (Python package manager)
### Installation
#### Entire shell prompt

```bash
git clone https://github.com/BruinDating/bruindating-backend.git
cd bruindating-backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python manage.py runserver
```

#### Step by step

1. **Clone the repository**

Note: if you have not already done so, it is recommended that before cloning this repository you create a parent folder that will hold both the frontend and the backend for this application. 

```bash
git clone https://github.com/BruinDating/bruindating-backend.git
cd bruindating-backend
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the development server**

```bash
python manage.py runserver
```

The backend server is located at [http://localhost:8000](http://localhost:8000)

## Features

### User Authentication

An important feature of Bruin Dating is that only students at UCLA are able to access it. To do this users will be required to use their UCLA email to sign up for Bruin Dating. Users will also be required to use DUO Mobile authentication to verify that it is you who is logging in or signing up. 

### How to meet people

After you fill out the questionnaire an algorithm is used to show you the profile of a potential match and you will be able to swipe left or right (ignore or like). When both of you give each other a like you will unlock the ability to message each other with the built in chat feature. 

## Technology Stack

- [Django](https://www.djangoproject.com/) - Web framework for Python
- [PostgreSQL](https://www.postgresql.org/) - Relational database
- [Django Rest Framework](https://www.django-rest-framework.org/) - API framework for Django

## Learn More

To learn more about Django, take a look at the following resources:

- [Django Documentation](https://docs.djangoproject.com/en/stable/) - Comprehensive guide to Django
- [Django Rest Framework](https://www.django-rest-framework.org/) - Learn about building APIs with Django
