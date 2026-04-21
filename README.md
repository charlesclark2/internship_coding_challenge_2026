# Internship Coding Challenge 2026

## Your Mission

Welcome to Meridian Financial Group — a mid-sized consumer lending and credit card company serving over 2,000 customers across the United States.

You have just joined the Analytics team as a Data Engineering intern. Your manager has handed you access to the company's transaction database and asked you to dig in. The risk and fraud teams have been flagging concerns about unusual spending patterns, high-debt customers, and potential card compromise, but they lack the bandwidth to investigate themselves. Your job is to use SQL to answer a series of analytical questions that will help the business understand its customers, monitor card activity, and surface anything that looks off.

The data you have access to covers real customer profiles, the credit and debit cards they hold, and a full history of card transactions. A separate reference table maps merchant category codes (MCCs) to human-readable business categories so you can make sense of where customers are spending their money.

This challenge is designed to assess your ability to write SQL queries and make targeted changes to a Python script. There are no trick questions — just real analytical problems that a data analyst at a financial firm would face day to day.

---

## Overview

### Datasets

All data lives in the `datasets/` directory:

| File | Description | Rows |
|---|---|---|
| `users_data.csv` | Customer profiles (age, income, credit score, etc.) | 2,000 |
| `cards_data.csv` | Credit/debit card records linked to users | 6,146 |
| `transactions_data.csv` | Card transaction history | 100,000 |
| `mcc_codes.json` | Lookup table mapping MCC codes to merchant category names | 109 |

### How `main.py` works

The entry point for the challenge is `coding_challenge/main.py`. It does three things:

1. **Connects to a local DuckDB database** (`challenge.duckdb`) the first time it runs and loads all four datasets into in-process SQL tables. On subsequent runs it detects the tables already exist and skips loading, so startup is fast.

2. **Exposes a `query()` function** for running SELECT statements. It accepts any SQL string and returns the results as a pandas DataFrame:
   ```python
   df = query("SELECT * FROM users WHERE credit_score > 750")
   print(df)
   ```

3. **Exposes an `execute()` function** for DDL and DML statements — anything that creates or modifies the schema or data rather than reading it:
   ```python
   # Create a derived table
   execute("""
       CREATE TABLE high_value_txns AS
       SELECT * FROM transactions WHERE CAST(REPLACE(amount, '$', '') AS DOUBLE) > 500
   """)

   # Add a column
   execute("ALTER TABLE users ADD COLUMN income_bracket VARCHAR")

   # Rename a column
   execute("ALTER TABLE transactions RENAME COLUMN amount TO transaction_amount")
   ```

The four tables available to you are `users`, `cards`, `transactions`, and `mcc_codes`. All of your work for the challenge should be done inside `main.py`, using these two functions.

---

## Data Dictionary

### `users`

Sourced from `users_data.csv`. One row per customer.

| Column | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier for the customer. Primary key. |
| `current_age` | integer | Customer's current age in years. |
| `retirement_age` | integer | Age at which the customer plans to retire. |
| `birth_year` | integer | Year the customer was born. |
| `birth_month` | integer | Month the customer was born (1–12). |
| `gender` | string | Customer's gender. |
| `address` | string | Street address of the customer's residence. |
| `latitude` | float | Geographic latitude of the customer's residence. |
| `longitude` | float | Geographic longitude of the customer's residence. |
| `per_capita_income` | string | Per capita income for the customer's area (e.g. `$29278`). |
| `yearly_income` | string | Customer's annual household income (e.g. `$59696`). |
| `total_debt` | string | Total outstanding debt across all accounts (e.g. `$127613`). |
| `credit_score` | integer | Customer's credit score. |
| `num_credit_cards` | integer | Total number of credit cards the customer holds. |

---

### `cards`

Sourced from `cards_data.csv`. One row per card. Each customer may have multiple cards.

| Column | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier for the card. Primary key. |
| `client_id` | integer | The customer this card belongs to. Foreign key to `users.id`. |
| `card_brand` | string | Card network (e.g. `Visa`, `Mastercard`, `Amex`). |
| `card_type` | string | Whether the card is `Credit` or `Debit`. |
| `card_number` | integer | Full card number. |
| `expires` | string | Card expiration date in `MM/YYYY` format. |
| `cvv` | integer | Card security code. |
| `has_chip` | string | Whether the card has an EMV chip (`YES` or `NO`). |
| `num_cards_issued` | integer | Number of physical cards issued on this account. |
| `credit_limit` | string | Credit limit on the account (e.g. `$24295`). Debit cards show the account limit. |
| `acct_open_date` | string | Date the account was opened in `MM/YYYY` format. |
| `year_pin_last_changed` | integer | Year the card PIN was last updated. |
| `card_on_dark_web` | string | Whether this card number has appeared in a known dark web data breach (`Yes` or `No`). |

---

### `transactions`

Sourced from `transactions_data.csv`. One row per transaction.

| Column | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier for the transaction. Primary key. |
| `date` | string | Timestamp of the transaction in `YYYY-MM-DD HH:MM:SS` format. |
| `client_id` | integer | The customer who made the transaction. Foreign key to `users.id`. |
| `card_id` | integer | The card used for the transaction. Foreign key to `cards.id`. |
| `amount` | string | Transaction amount including dollar sign (e.g. `$138.83`). |
| `use_chip` | string | How the card was presented: `Swipe Transaction`, `Chip Transaction`, or `Online Transaction`. |
| `merchant_id` | integer | Unique identifier for the merchant. |
| `merchant_city` | string | City where the merchant is located. |
| `merchant_state` | string | State where the merchant is located (two-letter abbreviation). |
| `zip` | float | ZIP code of the merchant location. |
| `mcc` | integer | Merchant Category Code. Foreign key to `mcc_codes.mcc_code`. |
| `errors` | string | Error code recorded on the transaction, if any. Null for clean transactions. |

---

### `mcc_codes`

Sourced from `mcc_codes.json`. One row per merchant category code. Use this table to join against `transactions.mcc` to get a human-readable category name.

| Column | Type | Description |
|---|---|---|
| `mcc_code` | string | Merchant Category Code (e.g. `5812`). |
| `description` | string | Human-readable category name (e.g. `Eating Places and Restaurants`). |

---

## Instructions

### Completing the challenge

All of your work should be done inside `coding_challenge/main.py`. The file already contains placeholder comments marking where each answer belongs (`### Your Code Goes Here ###`). Each question must be answered using a combination of Python and SQL:

- **Every question requires at least one SQL statement.** Use the `query()` function for SELECT-based answers and the `execute()` function for anything that creates or modifies the schema.
- Print your results clearly so each answer is readable when `uv run main.py` is executed. The existing `print("\nQuestion X Result:\n")` calls are already in place — your output should follow them.
- For Question 2 and any question that requires a schema change, use `execute()` to make the modification before using `query()` to retrieve the result.

If you run into syntax questions or need to look up a specific SQL function, refer to the DuckDB SQL documentation: [duckdb.org/docs/sql/introduction](https://duckdb.org/docs/sql/introduction)

### Use of Generative AI

You are welcome to use generative AI tools (e.g. ChatGPT, GitHub Copilot, Claude) to assist you during this challenge. If you do, you must include a comment at the top of `main.py` listing every tool you used. For example:

```python
# AI Tools Used: GitHub Copilot, ChatGPT (GPT-4)
```

Be aware that using AI does not mean handing off the work entirely. We will ask you to walk through your code and explain your approach during the review, so make sure you understand every query and line of code you submit.

### Branching and submission

1. **Before you start**, create a new branch off of `main`. Your branch name must include your first and last name, for example:
   ```bash
   git checkout -b jane-doe
   ```

2. **Work entirely on your branch.** Do not push directly to `main`.

3. **When you are finished**, push your branch to the remote repository:
   ```bash
   git push origin jane-doe
   ```

4. **Notify us that your submission is ready** by sending an email to both reviewers:
   - Charlie Clark — charles_clark@mgic.com
   - Anton Gurevich — anton_gurevich@mgic.com

   Include your branch name in the email so we can find it quickly.

---

## Local Setup

### Prerequisites

- **Python 3.10 or higher** — download from [python.org](https://www.python.org/downloads/) if needed. Confirm your version with:
  ```bash
  python3 --version
  ```

- **uv** — a fast Python package and project manager. Install it with:
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  Full installation docs: [docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/)

### Steps

1. **Clone the repository** (or extract the provided zip):
   ```bash
   git clone <repository-url>
   cd internship_coding_challenge_2026
   ```

2. **Move into the project directory:**
   ```bash
   cd coding_challenge
   ```

3. **Run the project** — uv will automatically create a virtual environment, install all dependencies, and execute the script:
   ```bash
   uv run main.py
   ```
   On the first run you will see each dataset being loaded into the database. Subsequent runs skip that step and go straight to the output.

That's it. No manual `pip install`, no activating virtual environments — uv handles everything.

### Verifying your setup

A successful first run looks like this:

```
Initializing database...
  Loaded: users
  Loaded: cards
  Loaded: transactions
  Loaded: mcc_codes

Database ready.
Available tables: users, cards, transactions, mcc_codes

  table_name  row_count
       users       2000
       cards       6146
transactions     100000
   mcc_codes        109
```
