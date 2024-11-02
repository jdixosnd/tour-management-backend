# Tour Operator Management System

A comprehensive web application built using Django to manage tour operator data, packages, hotels, destinations, transportation, and other logistics required for seamless tour operations.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
- [Application Structure](#application-structure)
- [Admin Configuration](#admin-configuration)
- [Models Overview](#models-overview)
- [APIs](#apis)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This project is designed to streamline and simplify the operations of tour operators by providing a web interface to manage tour packages, clients, hotels, car rentals, sightseeing events, and itineraries. The application allows tour operators to create, update, and manage various entities related to their business.

## Features

1. **Tour Operator Management**: CRUD operations for managing tour operators and their data.
2. **User Management**: Role-based access control for `Manager` and `User`.
3. **Hotel, Room, and Amenity Management**: Easily manage hotel details, room availability, and amenities.
4. **Destination and Sightseeing Management**: Manage destinations, cities, sightseeing events, and more.
5. **Car Dealer and Transportation Management**: Track car dealers, car types, and manage transportation for tours.
6. **Package Management**: Create and manage tour packages, including pricing, inclusions, and exclusions.
7. **Dynamic Itinerary Generation**: Add custom itineraries for each package.
8. **Django Admin Customization**: Custom admin views for all models with search, filter, and list display features.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Django 3.x or higher
- MySQL database (or alternative database supported by Django)
- Docker (optional, if you want to run the app in containers)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/tour-operator-management.git
   cd tour-operator-management

2. **Create a virtual environment**:
   ```python3 -m venv venv

source venv/bin/activate
3. **Install dependencies**:
    ```pip install -r requirements.txt

4. **Environment Variables: Create a .env file in the project root with the following content**:
    ```DATABASE_NAME=your_db_name
    DATABASE_USER=your_db_user
    DATABASE_PASSWORD=your_db_password
    DATABASE_HOST=127.0.0.1
    SECRET_KEY=your_secret_key

