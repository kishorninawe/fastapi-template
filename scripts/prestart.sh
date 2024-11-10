#! /usr/bin/env bash

# Let the DB start
python -c "from app.backend_pre_start import main; main();"

# Run migrations
alembic upgrade head

# Create initial data in DB
python -c "from app.initial_data import main; main();"