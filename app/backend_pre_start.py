import logging

from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    session = SessionLocal()

    try:
        session.execute(text("SELECT 1"))

        # Execute the query to create pgcrypto if not exists
        session.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
        session.commit()

        # Execute the query to check if pgcrypto exists
        query = "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') AS pgcrypto_exists;"
        result = session.execute(text(query)).fetchone()
        pgcrypto_exists = result[0] if result else False
        logger.info(f"pgcrypto extension exists: {pgcrypto_exists}")
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        # Close the session
        session.close()


def main() -> None:
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
