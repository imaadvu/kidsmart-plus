from core.db import SessionLocal
from core.etl import ingest_all_sources


def main():
    with SessionLocal() as db:
        ingest_all_sources(db)


if __name__ == "__main__":
    main()

