#!/usr/bin/env python
"""
Script to create PostgreSQL database for the crowdfunding platform
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the crowdfunding_db database if it doesn't exist"""
    
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'port': '5432',
        'user': 'postgres',
        'password': '0000'
    }
    
    try:
        # Connect to PostgreSQL server (not to a specific database)
        print("Connecting to PostgreSQL server...")
        connection = psycopg2.connect(**db_params)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'crowdfunding_db'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create the database
            print("Creating crowdfunding_db database...")
            cursor.execute('CREATE DATABASE crowdfunding_db')
            print("Database 'crowdfunding_db' created successfully!")
        else:
            print("Database 'crowdfunding_db' already exists.")
        
        cursor.close()
        connection.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    create_database()