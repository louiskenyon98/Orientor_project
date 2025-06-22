# Database Migrations with Alembic

This directory contains database migrations for all microservices using Alembic.

## Setup

1. Install Alembic:
```bash
pip install alembic asyncpg
```

2. Configure database URLs in environment variables or `alembic.ini`

## Creating Migrations

Each service has its own database, specify which one:

```bash
# Create migration for career service
alembic revision --autogenerate -m "Add career tables" -x db=career

# Create migration for skills service
alembic revision --autogenerate -m "Add skills tables" -x db=skills

# Create migration for user service
alembic revision --autogenerate -m "Add user tables" -x db=user

# Create migration for assessment service
alembic revision --autogenerate -m "Add assessment tables" -x db=assessment

# Create migration for matching service
alembic revision --autogenerate -m "Add matching tables" -x db=matching
```

## Running Migrations

```bash
# Upgrade career database to latest
alembic upgrade head -x db=career

# Upgrade all databases
for db in career skills user assessment matching; do
    alembic upgrade head -x db=$db
done

# Downgrade career database by one revision
alembic downgrade -1 -x db=career
```

## Migration History

```bash
# Show migration history for career database
alembic history -x db=career

# Show current revision for skills database
alembic current -x db=skills
```

## Environment Variables

Set these for each service:
- `CAREER_DATABASE_URL`
- `SKILLS_DATABASE_URL`
- `USER_DATABASE_URL`
- `ASSESSMENT_DATABASE_URL`
- `MATCHING_DATABASE_URL`

## Best Practices

1. Always review auto-generated migrations
2. Test migrations on a development database first
3. Keep migrations small and focused
4. Add meaningful descriptions
5. Never edit migrations that have been applied to production