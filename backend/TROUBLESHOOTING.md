# Troubleshooting Guide

This guide helps you resolve common issues with the application setup, particularly related to database and Redis connections.

## Pydantic Validation Errors

### Error: "Extra inputs are not permitted"

This error occurs when your .env file contains variables that are not defined in your Settings model.

**Example error:**
```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
REDIS_USERNAME
  Extra inputs are not permitted [type=extra_forbidden, input_value='default', input_type=str]
REDIS_PASSWORD
  Extra inputs are not permitted [type=extra_forbidden, input_value='your_password', input_type=str]
```

**Solution:**

1. Make sure all environment variables in your .env file are defined in the Settings class in app/config.py.
2. The application has been updated to include REDIS_USERNAME and REDIS_PASSWORD in the Settings model.
3. If you add new environment variables, make sure to add them to the Settings class as well.

## PostgreSQL Enum Type Errors

### Error: "no schema has been selected to create in"

This error occurs when trying to create a PostgreSQL enum type without specifying a schema.

**Example error:**
```
Warning: Could not create enum type: (sqlalchemy.dialects.postgresql.asyncpg.Error) <class 'asyncpg.exceptions.InvalidSchemaNameError'>: no schema has been selected to create in
[SQL: CREATE TYPE coursestatus AS ENUM ('DRAFT', 'ACTIVE', 'ARCHIVED')]
```

**Solution:**

1. The application has been updated to use String columns with enum validation instead of PostgreSQL ENUM types.
2. If you need to use PostgreSQL ENUM types, make sure to:
   - Set the search_path explicitly before creating the enum type
   - Use PL/pgSQL to check if the enum type already exists before creating it
   - Handle the transaction properly to avoid transaction aborts

## DateTime Errors

### Error: "can't subtract offset-naive and offset-aware datetimes"

This error occurs when mixing timezone-aware and timezone-naive datetime objects in database operations.

**Example error:**
```
(sqlalchemy.dialects.postgresql.asyncpg.Error) <class 'asyncpg.exceptions.DataError'>: invalid input for query argument $2: datetime.datetime(2025, 3, 10, 16, 23, 1... (can't subtract offset-naive and offset-aware datetimes)
```

**Solution:**

1. Always use timezone-aware datetimes consistently throughout your application.
2. Use `datetime.now(UTC)` instead of `datetime.now()` to create timezone-aware datetimes.
3. When working with PostgreSQL, use `DateTime(timezone=True)` in your SQLAlchemy models.
4. For direct SQL queries, convert datetimes to strings using `strftime('%Y-%m-%d %H:%M:%S')`.

## Database Connection Issues

### Error: "no schema has been selected to create in"

This error occurs when PostgreSQL cannot determine which schema to use when creating database objects like tables or enum types.

**Solution:**

1. Ensure your database URL includes the proper schema information.
2. The application has been updated to explicitly set the schema to "public" in the database connection.
3. Run the database connection test script to verify:

```bash
python scripts/test_db_connection.py
```

### Error: "relation does not exist"

This error occurs when the application tries to access a table that hasn't been created yet.

**Solution:**

1. Make sure the database initialization process completes successfully.
2. Check if you have the necessary permissions to create tables in the database.
3. If using a cloud database service like Neon, ensure your user has the proper permissions.

## Redis Connection Issues

### Error: "Authentication required"

This error occurs when Redis requires a password, but none was provided in the connection.

**Solution:**

1. Get the correct Redis password from your Redis provider (Redis Cloud dashboard).
2. Add the password to your `.env` file:

```
REDIS_PASSWORD=your_redis_password_here
```

3. Run the Redis connection test script to verify:

```bash
python scripts/test_redis_connection.py
```

## General Troubleshooting Steps

If you're still experiencing issues, follow these general troubleshooting steps:

1. **Check your .env file**: Make sure all required environment variables are set correctly.

2. **Test connections individually**:
   - Database: `python scripts/test_db_connection.py`
   - Redis: `python scripts/test_redis_connection.py`

3. **Restart the application**:
   - Use the provided restart script: `./restart.sh`

4. **Check logs**:
   - Look for specific error messages in the application logs.

5. **Verify credentials**:
   - Double-check all usernames, passwords, and connection strings.

## Getting Redis Password for Redis Cloud

If you're using Redis Cloud and don't know your password:

1. Log in to your Redis Cloud dashboard.
2. Navigate to your database.
3. Look for the "Security" or "Access Control" section.
4. Find your password or generate a new one.

Alternatively, you might find the password in the Redis URL. The format is typically:
```
redis://username:password@host:port
```

You can extract it using the Redis connection test script:
```bash
python scripts/test_redis_connection.py
``` 