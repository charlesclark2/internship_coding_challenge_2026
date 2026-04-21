import pandas as pd
from pathlib import Path

DATASETS_DIR = Path(__file__).parent.parent / "datasets"
CHUNK_SIZE = 500_000
TARGET_ROWS = 100_000
RANDOM_SEED = 42


def main():
    print("Loading valid user and card IDs...")
    users = pd.read_csv(DATASETS_DIR / "users_data.csv", usecols=["id"])
    cards = pd.read_csv(DATASETS_DIR / "cards_data.csv", usecols=["id"])

    valid_user_ids = set(users["id"])
    valid_card_ids = set(cards["id"])

    print(f"  Users:  {len(valid_user_ids):,}")
    print(f"  Cards:  {len(valid_card_ids):,}")

    print("\nFiltering transactions (this may take a minute)...")
    valid_chunks = []
    total_processed = 0

    for chunk in pd.read_csv(DATASETS_DIR / "transactions_data.csv", chunksize=CHUNK_SIZE):
        mask = (
            chunk["client_id"].isin(valid_user_ids)
            & chunk["card_id"].isin(valid_card_ids)
        )
        valid_chunks.append(chunk[mask])
        total_processed += len(chunk)
        print(f"  Processed {total_processed:,} rows...", end="\r")

    print(f"\nCombining {len(valid_chunks)} chunks...")
    all_valid = pd.concat(valid_chunks, ignore_index=True)
    print(f"Total valid transactions: {len(all_valid):,}")

    if len(all_valid) < TARGET_ROWS:
        raise ValueError(
            f"Only {len(all_valid):,} valid transactions found; need {TARGET_ROWS:,}."
        )

    print(f"\nSampling {TARGET_ROWS:,} rows (seed={RANDOM_SEED})...")
    sampled = all_valid.sample(n=TARGET_ROWS, random_state=RANDOM_SEED)
    sampled = sampled.sort_values("date").reset_index(drop=True)

    output_path = DATASETS_DIR / "transactions_data.csv"
    print(f"Writing to {output_path}...")
    sampled.to_csv(output_path, index=False)
    print(f"Done. {len(sampled):,} transactions saved.")


if __name__ == "__main__":
    main()
