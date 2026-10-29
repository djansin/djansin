"""Database Models for Kasejyan App.

This module defines the database schema using Django's ORM. Models represent
the core data structures of your application and encapsulate business logic,
validation rules, and relationships between data entities.

Model Design Guidelines:
    - Each model maps to a single database table
    - Field definitions determine column types and constraints
    - Relationships (ForeignKey, ManyToMany) define data associations
    - Meta class configures table behavior (ordering, permissions)
    - __str__() provides human-readable representation

Note:
    - Define all models before creating migrations
    - Use appropriate field types and constraints
    - Add docstrings to model classes for documentation
    - Keep business logic in models when it relates to data
"""

from django.db import models
