import json
from pathlib import Path

import duckdb
import pandas as pd

DATASETS_DIR = Path(__file__).parent.parent / "datasets"
DB_PATH = Path(__file__).parent / "challenge.duckdb"

_conn: duckdb.DuckDBPyConnection | None = None


def get_connection() -> duckdb.DuckDBPyConnection:
    global _conn
    if _conn is None:
        _conn = duckdb.connect(str(DB_PATH))
    return _conn


def initialize_db() -> None:
    """Load CSVs and JSON into DuckDB tables. Skipped if tables already exist."""
    conn = get_connection()

    existing = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
    required = {"users", "cards", "transactions", "mcc_codes"}
    if required.issubset(existing):
        return

    if "users" not in existing:
        conn.execute(
            f"CREATE TABLE users AS SELECT * FROM read_csv_auto('{(DATASETS_DIR / 'users_data.csv').as_posix()}')"
        )
        print("  Loaded: users")

    if "cards" not in existing:
        conn.execute(
            f"CREATE TABLE cards AS SELECT * FROM read_csv_auto('{(DATASETS_DIR / 'cards_data.csv').as_posix()}')"
        )
        print("  Loaded: cards")

    if "transactions" not in existing:
        conn.execute(
            f"CREATE TABLE transactions AS SELECT * FROM read_csv_auto('{(DATASETS_DIR / 'transactions_data.csv').as_posix()}')"
        )
        print("  Loaded: transactions")

    if "mcc_codes" not in existing:
        with open(DATASETS_DIR / "mcc_codes.json") as f:
            raw = json.load(f)
        mcc_df = pd.DataFrame(
            list(raw.items()), columns=["mcc_code", "description"]
        )
        conn.register("mcc_df", mcc_df)
        conn.execute("CREATE TABLE mcc_codes AS SELECT * FROM mcc_df")
        conn.unregister("mcc_df")
        print("  Loaded: mcc_codes")


def query(sql: str) -> pd.DataFrame:
    """Execute a SELECT statement and return results as a DataFrame.

    Args:
        sql: A SQL SELECT statement to run against the database.

    Returns:
        A pandas DataFrame containing the query results.

    Example:
        df = query("SELECT * FROM users LIMIT 5")
    """
    return get_connection().execute(sql).df()


def execute(sql: str) -> None:
    """Execute a DDL or DML statement such as CREATE TABLE, ALTER TABLE, or UPDATE.

    Use this for statements that modify the schema or data rather than reading it.

    Args:
        sql: A SQL DDL or DML statement to execute.

    Examples:
        execute("CREATE TABLE summary AS SELECT client_id, COUNT(*) AS txn_count FROM transactions GROUP BY client_id")
        execute("ALTER TABLE users ADD COLUMN full_name VARCHAR")
        execute("ALTER TABLE transactions RENAME COLUMN amount TO transaction_amount")
    """
    get_connection().execute(sql)


def main():
    print("Initializing database...")
    initialize_db()
    print("\nDatabase ready.")
    print("Available tables: users, cards, transactions, mcc_codes\n")

    counts = query("""
        SELECT 'users'        AS table_name, COUNT(*) AS row_count FROM users
        UNION ALL
        SELECT 'cards',       COUNT(*) FROM cards
        UNION ALL
        SELECT 'transactions',COUNT(*) FROM transactions
        UNION ALL
        SELECT 'mcc_codes',   COUNT(*) FROM mcc_codes
    """)
    print(counts.to_string(index=False))
    print("\n Example Question Result:\n")
    ### Questions to answer: 
    # Example Question: What city is the merchant associated with transaction 7485074 located in? 
    location = query("""
    select merchant_city 
    from transactions
    where id = 7485074
    """)
    print(location.to_string(index=False))

    print("\nQuestion 1 Result:\n")
    '''
    Question 1: Which year was user ID 1752 born in? 
    '''
    ### Your Code Goes Here ###

    '''
    Question 2: Create a new column in the transactions table 
    called "merchant_location" which shows the full merchant location 
    in the format of "City, State, ZIP". Ensure to backfill this 
    column for all existing records. Then return the merchant_location 
    for merchant ID 20519 and transaction ID 7581366.
    '''
    print("\nQuestion 2 Result:\n")
    ### Your Code Goes Here ###

    print("\nQuestion 3 Result:\n")
    '''
    Question 3: What is the credit limit of the card used in transaction ID 7879552? 
    '''
    ### Your Code Goes Here ###


    print("\nQuestion 4 Result:\n")

    ''''
    Question 4: A team member from the fraud detection department is curious 
    about the transaction activity for client ID 1098.  They would like 
    to know which year this client had the highest amount of Debit Card spending. 
    They would like this to be returned with the following information: 

    GENDER, CURRENT_AGE, ADDRESS, TRANSACTION_YEAR, ANNUAL_SPEND
    '''

    ### Your Code Goes Here ###

    print("\nQuestion 5 Result:\n")
    '''
    Based on the data you've seen in the database, what is one interesting 
    insight you can find by writing a SQL query?

    Here are some examples of insights you could look for:
    - Which merchant category code (MCC) has the highest average transaction amount?
    - What is the distribution of transaction amounts for each card type?
    - Are there any seasonal trends in transaction activity (e.g., higher spending in certain months)?
    - Which clients have the highest total transaction amounts, and what are their demographics?
    '''

    ### Your Code Goes Here ###

    print("\nBonus Question Result:\n")

    '''
    NOTE: THIS QUESTION IS OPTIONAL AND NOT REQUIRED FOR A COMPLETE SUBMISSION.

    Create an API integration with the Nominatim Reverse Geocoding API (https://nominatim.org/release-docs/latest/api/Reverse/)
    which takes a user's latitude and longitude and returns additional details about their location. Take 
    this data and transform it in a way where you can store it in a new table in the database. 
    Then, write a SQL query using the new table which shows the top 5 states by total 
    debit and credit card spending each year.
    '''

    ### Your Code Goes Here ###

if __name__ == "__main__":
    main()
