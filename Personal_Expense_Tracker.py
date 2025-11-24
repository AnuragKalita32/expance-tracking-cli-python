import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_FILE = Path("expenses.json")


def load_expenses(filepath: Path = DATA_FILE) -> List[Dict[str, Any]]:
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, IOError):
        print("Warning: Could not read JSON file or file is corrupted. Starting with empty ledger.")
        return []


def save_expenses(expenses: List[Dict[str, Any]], filepath: Path = DATA_FILE) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(expenses, f, indent=2, ensure_ascii=False)
    except IOError:
        print("Error: Unable to save expenses.")


def make_expense(amount: float, category: str, note: str = "", date_iso: Optional[str] = None) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "amount": round(amount, 2),
        "category": category.strip(),
        "note": note.strip(),
        "date": date_iso or datetime.now().isoformat(timespec="seconds")
    }


def add_expense_interactive(expenses: List[Dict[str, Any]]) -> None:
    while True:
        amt_str = input("Enter amount (numbers only, e.g. 250.50): ").strip()
        try:
            amount = float(amt_str)
            break
        except ValueError:
            print("Invalid amount. Try again.")

    category = input("Enter category (e.g. Food, Travel, Bills): ").strip() or "Uncategorized"
    note = input("Optional note: ").strip()
    date_input = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()
    date_iso = None
    if date_input:
        try:
            # store as ISO (YYYY-MM-DDT00:00:00)
            parsed = datetime.fromisoformat(date_input)
            date_iso = parsed.isoformat(timespec="seconds")
        except ValueError:
            # try parse YYYY-MM-DD only
            try:
                parsed = datetime.strptime(date_input, "%Y-%m-%d")
                date_iso = parsed.isoformat(timespec="seconds")
            except ValueError:
                print("Invalid date format. Using current date/time.")
                date_iso = None

    expense = make_expense(amount, category, note, date_iso)
    expenses.append(expense)
    save_expenses(expenses)
    print("Expense added!\n")


def print_expense(exp: Dict[str, Any]) -> None:
    print(f"ID: {exp['id']}")
    print(f"Date: {exp['date']}")
    print(f"Category: {exp['category']}")
    print(f"Amount: {exp['amount']}")
    if exp.get("note"):
        print(f"Note: {exp['note']}")
    print("-" * 40)


def view_all_expenses(expenses: List[Dict[str, Any]]) -> None:
    if not expenses:
        print("No expenses found.")
        return
    # sort by date descending
    sorted_exp = sorted(expenses, key=lambda x: x.get("date", ""), reverse=True)
    for exp in sorted_exp:
        print_expense(exp)


def get_total_spending(expenses: List[Dict[str, Any]]) -> float:
    return sum(float(e.get("amount", 0)) for e in expenses)


def spending_by_category(expenses: List[Dict[str, Any]]) -> Dict[str, float]:
    summary: Dict[str, float] = {}
    for e in expenses:
        cat = e.get("category", "Uncategorized")
        summary[cat] = summary.get(cat, 0.0) + float(e.get("amount", 0.0))
    return {k: round(v, 2) for k, v in summary.items()}


def view_totals(expenses: List[Dict[str, Any]]) -> None:
    total = get_total_spending(expenses)
    print(f"Total spending: {round(total,2)}")
    by_cat = spending_by_category(expenses)
    print("\nSpending by category:")
    if not by_cat:
        print("  No category data.")
    else:
        for cat, amt in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {amt}")


def delete_expense(expenses: List[Dict[str, Any]]) -> None:
    eid = input("Enter the ID of the expense to delete: ").strip()
    before = len(expenses)
    expenses[:] = [e for e in expenses if e.get("id") != eid]
    if len(expenses) < before:
        save_expenses(expenses)
        print("Expense deleted.")
    else:
        print("ID not found. No changes made.")


def search_expenses(expenses: List[Dict[str, Any]]) -> None:
    keyword = input("Enter search keyword (category/note/date fragment): ").strip().lower()
    results = [
        e for e in expenses
        if keyword in e.get("category", "").lower()
        or keyword in e.get("note", "").lower()
        or keyword in e.get("date", "").lower()
    ]
    if not results:
        print("No matching expenses found.")
        return
    for e in sorted(results, key=lambda x: x.get("date", ""), reverse=True):
        print_expense(e)


def menu() -> None:
    expenses = load_expenses()
    choices = {
        "1": ("Add an expense", lambda: add_expense_interactive(expenses)),
        "2": ("View all expenses", lambda: view_all_expenses(expenses)),
        "3": ("View totals & category summary", lambda: view_totals(expenses)),
        "4": ("Search expenses", lambda: search_expenses(expenses)),
        "5": ("Delete an expense (by ID)", lambda: delete_expense(expenses)),
        "6": ("Export expenses to JSON file (save)", lambda: save_expenses(expenses)),
        "0": ("Exit", None)
    }

    while True:
        print("\nPersonal Expense Tracker")
        print("-" * 25)
        for key, (desc, _) in choices.items():
            print(f"{key}. {desc}")
        choice = input("Choose an option: ").strip()
        action = choices.get(choice)
        if not action:
            print("Invalid choice. Try again.")
            continue
        if choice == "0":
            print("Goodbye!")
            break
        # call action
        _, func = action
        if func:
            func()


if __name__ == "__main__":
    menu()
