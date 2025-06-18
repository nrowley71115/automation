import os
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict
from openai import OpenAI  # Updated import

# Load environment variables (create a .env file with OPENAI_API_KEY=your_key)
load_dotenv()

# OpenAI model options
OPENAI_MODELS = {
    "GPT4_MINI": "gpt-4o-mini",
    "GPT4O": "gpt-4o",
    "GPT4_1": "gpt-4-1106-preview",           # GPT-4.1
    "GPT4_1_MINI": "gpt-4-1106-vision-preview" # GPT-4.1 mini (vision, also works for text)
}

# Current Model
CURRENT_MODEL = OPENAI_MODELS["GPT4_1"]

# Configure OpenAI API with new client format
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define budget categories
BUDGET_CATEGORIES = {
    "Incoming": ["venmo", "eastman", "work", "cash", "payment"],
    "Spending": [
        "rent", "utilities", "elec", "wifi", "debt payment", 
        "insurance", "car", "renters", "dr. apt", "gas", "maint",
        "groceries", "gym", "shopping", "eating out", "food", "drink",
        "alcohol", "going out", "gifts", "movies", "entertainment", "subscriptions"
    ],
    "Investments": ["vanguard", "roth ira", "robinhood", "coinbase", "ally bank"],
    "Unknown": []
}

def read_transactions(file_path):
    """Read transactions from CSV file and standardize format."""
    transactions = []
    account_name = os.path.basename(file_path).split('_')[0]  # Extract account name from filename
    
    with open(file_path, 'r', encoding='utf-8') as file:
        # Read the first line to detect format
        first_line = file.readline().strip()
        file.seek(0)  # Reset file pointer
        
        reader = csv.DictReader(file)
        
        # Detect if this is a debit account format (Chase)
        is_debit_format = 'Details,Posting Date,Description,Amount,Type,Balance' in first_line
        
        for row in reader:
            # Standardize transaction format based on CSV type
            if is_debit_format:
                # Handle Chase debit account format
                transaction = {
                    'Transaction Date': row.get('Posting Date', ''),
                    'Description': row.get('Description', ''),
                    'Amount': row.get('Amount', '0.0'),
                    'Category': '', # Default empty category
                    'Type': row.get('Type', ''),
                    'Balance': row.get('Balance', '0.0'),
                    'Account': account_name  # Add account info
                }
            else:
                # Use original format (for credit accounts)
                transaction = row.copy()  # Make a copy to not modify the original
                transaction['Account'] = account_name  # Add account info
                
            transactions.append(transaction)
            
    print(f"Read {len(transactions)} transactions from {os.path.basename(file_path)}")
    print(f"Format detected: {'Chase Debit' if is_debit_format else 'Credit Account'}")
    
    return transactions

def categorize_transaction(transaction, model=CURRENT_MODEL):
    """Use OpenAI to categorize a transaction."""
    description = transaction['Description']
    
    # Get amount and handle potential formatting differences
    amount_str = transaction['Amount']
    try:
        # For debit accounts, positive numbers are credits and negative are debits
        amount = float(amount_str)
    except ValueError:
        # Handle cases where amount might have currency symbols or commas
        amount_str = amount_str.replace('$', '').replace(',', '')
        amount = float(amount_str)
    
    transaction_type = transaction.get('Type', '')
    category = transaction.get('Category', '')
    
    # Enhance prompt with transaction type for debit accounts
    prompt = f"""
    Based on the transaction description, amount, and existing category (if any), 
    classify this transaction into one of the following budget categories:
    
    - Incoming: venmo, eastman (work), or cash
    - Spending: rent, utilities (elec, wifi), debt payment, insurance (car, renters, dr. apt), 
      car (gas, maint), groceries, gym, shopping, eating out, alcohol/going out, gifts, 
      movies, or subscriptions
    - Investments: vanguard roth IRA, robinhood, coinbase, or ally bank
    - Unknown: if it doesn't match any above
    
    Transaction Information:
    - Description: {description}
    - Amount: ${amount}
    - Existing Category: {category}
    - Transaction Type: {transaction_type}
    
    For debit accounts: ACH_CREDIT and QUICKPAY_CREDIT are typically incoming transactions,
    while ACH_DEBIT and LOAN_PMT are typically spending or investments.

    'SAMSCLUB' and 'SAMS SCAN-N-GO' are usually groceries even though the category is labeled as 'shopping'. 'SAMSCLUB' is car (gas, maint) when the cateogry is gas. 'D J*WSJ' and 'CHE*CHEGG STUDY' is a subscription.
    
    Return only the budget category (Incoming, Spending, Investments, or Unknown) 
    followed by a colon and the specific subcategory.
    Example: "Spending: groceries" or "Incoming: eastman"
    """

    try:
        # API call with correct format
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a financial categorization assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Get content directly using the correct attribute path
        categorization = response.choices[0].message.content.strip()
        
        # Extract main category and subcategory
        parts = categorization.split(':', 1)
        main_category = parts[0].strip()
        subcategory = parts[1].strip() if len(parts) > 1 else "general"
        
        print(f"API Response: '{categorization}' → {main_category}: {subcategory}")
        return main_category, subcategory
    
    except Exception as e:
        print(f"Error categorizing transaction: {str(e)}")
        return "Unknown", "error"

def format_amount(amount):
    """Format the amount with $ sign and appropriate color indicator."""
    try:
        amount_float = float(amount)
        if amount_float > 0:
            return f"+${abs(amount_float):.2f}"
        else:
            return f"-${abs(amount_float):.2f}"
    except:
        return amount

def process_multiple_files(file_paths):
    """Process multiple transaction files and combine results."""
    all_transactions = []
    for file_path in file_paths:
        transactions = read_transactions(file_path)
        all_transactions.extend(transactions)
    
    # Sort all transactions by date
    try:
        all_transactions.sort(key=lambda x: datetime.strptime(x['Transaction Date'], '%m/%d/%Y'))
    except:
        print("Warning: Could not sort all transactions by date. Continuing with unsorted data.")
    
    categorized = defaultdict(lambda: defaultdict(list))
    
    print(f"\nProcessing {len(all_transactions)} total transactions across {len(file_paths)} files...")
    
    for i, transaction in enumerate(all_transactions):
        print(f"Processing transaction {i+1}/{len(all_transactions)}: {transaction['Description']} ({transaction['Account']})")
        
        # Handle transactions with known amount format
        amount = transaction['Amount']
        date = transaction['Transaction Date']
        description = transaction['Description']
        account = transaction['Account']
        original_category = transaction.get('Category', '')  # Get original category if available
        
        # Use OpenAI to categorize
        main_category, subcategory = categorize_transaction(transaction)
        
        # Store transaction
        categorized[main_category][subcategory].append({
            'date': date,
            'description': description,
            'amount': amount,
            'account': account,
            'original_category': original_category  # Store the original category
        })
    
    return categorized

def display_results(categorized):
    """Display the categorized results."""
    print("\n===== TRANSACTION SUMMARY =====\n")
    
    for main_category, subcategories in categorized.items():
        print(f"\n== {main_category} ==")
        main_category_total = 0
        
        for subcategory, transactions in subcategories.items():
            subcategory_total = sum(float(t['amount']) for t in transactions)
            main_category_total += subcategory_total
            
            print(f"\n{subcategory.upper()} (${abs(subcategory_total):.2f})")
            
            for t in transactions:
                formatted_amount = format_amount(t['amount'])
                print(f"  {t['date']} | {t['account']} | {t['description']} | {formatted_amount}")
        
        print(f"\nTotal {main_category}: ${abs(main_category_total):.2f}")
    
    # Calculate overall total
    total = sum(
        sum(float(t['amount']) for t in transactions)
        for subcategories in categorized.values()
        for transactions in subcategories.values()
    )
    
    print(f"\n===== OVERALL TOTAL: {format_amount(total)} =====")

def export_to_csv(categorized, file_paths):
    """Export categorized transactions to a CSV file organized by budget category."""
    # Generate output filename based on current date
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"budget_summary_{timestamp}.csv"
    
    # Get the directory of this script and create outputs directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, output_filename)
    
    # Prepare data for CSV, organized by budget category
    csv_data = []
    
    # Add header with files processed
    csv_data.append({
        'Date': 'Files Processed:',
        'Description': ', '.join(os.path.basename(path) for path in file_paths),
        'Amount': '',
        'Account': '',
        'Given Category': '',
        'Main Category': '',
        'Subcategory': ''
    })
    
    # Add blank row
    csv_data.append({
        'Date': '',
        'Description': '',
        'Amount': '',
        'Account': '',
        'Given Category': '',
        'Main Category': '',
        'Subcategory': ''
    })
    
    # Track category and subcategory totals
    for main_category, subcategories in categorized.items():
        main_category_total = 0
        
        for subcategory, transactions in subcategories.items():
            subcategory_total = sum(float(t['amount']) for t in transactions)
            main_category_total += subcategory_total
            
            # Add a header row for each subcategory
            csv_data.append({
                'Date': '',
                'Description': f"== {main_category}: {subcategory} ==",
                'Amount': f"${abs(subcategory_total):.2f}",
                'Account': '',
                'Given Category': '',
                'Main Category': main_category,
                'Subcategory': subcategory
            })
            
            # Add all transactions for this subcategory
            for t in transactions:
                row = {
                    'Date': t['date'],
                    'Description': t['description'],
                    'Amount': t['amount'],
                    'Account': t['account'],
                    'Given Category': t.get('original_category', ''),  # Include original category
                    'Main Category': main_category,
                    'Subcategory': subcategory
                }
                csv_data.append(row)
            
            # Add a blank row after each subcategory
            csv_data.append({
                'Date': '',
                'Description': '',
                'Amount': '',
                'Account': '',
                'Given Category': '',
                'Main Category': '',
                'Subcategory': ''
            })
        
        # Add subtotal for the main category
        csv_data.append({
            'Date': '',
            'Description': f"=== TOTAL {main_category} ===",
            'Amount': f"${abs(main_category_total):.2f}",
            'Account': '',
            'Given Category': '',
            'Main Category': main_category,
            'Subcategory': 'TOTAL'
        })
        
        # Add another blank row after each main category
        csv_data.append({
            'Date': '',
            'Description': '',
            'Amount': '',
            'Account': '',
            'Given Category': '',
            'Main Category': '',
            'Subcategory': ''
        })
    
    # Calculate overall total
    total = sum(
        sum(float(t['amount']) for t in transactions)
        for subcategories in categorized.values()
        for transactions in subcategories.values()
    )
    
    # Add overall total to the end
    csv_data.append({
        'Date': '',
        'Description': '=== OVERALL TOTAL ===',
        'Amount': format_amount(total),
        'Account': '',
        'Given Category': '',
        'Main Category': 'TOTAL',
        'Subcategory': 'TOTAL'
    })
    
    # Write to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'Description', 'Amount', 'Account', 'Given Category', 'Main Category', 'Subcategory']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
    
    print(f"\nCategorized transactions exported to: {output_path}")
    return output_path

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for CSV files in the accounts subdirectory
    accounts_dir = os.path.join(script_dir, "accounts")
    csv_files = [f for f in os.listdir(accounts_dir) if f.endswith('.CSV') or f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the accounts directory.")
        return
    
    # Print currently selected AI model
    print(f"LLM MOODEL: {CURRENT_MODEL}")
    
    # List available files
    print("Available CSV files:")
    for i, file in enumerate(csv_files):
        print(f"{i+1}. {file}")
    
    # Allow multiple file selection
    print("\nSelect files to process (comma-separated numbers, or 'all' for all files):")
    selection = input("> ")
    
    file_paths = []
    if selection.lower() == 'all':
        # Process all files
        file_paths = [os.path.join(accounts_dir, f) for f in csv_files]
    else:
        try:
            # Process selected files
            indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
            for idx in indices:
                if idx < 0 or idx >= len(csv_files):
                    print(f"Warning: Invalid selection {idx+1}, skipping.")
                else:
                    file_paths.append(os.path.join(accounts_dir, csv_files[idx]))
        except ValueError:
            print("Invalid selection format. Please use comma-separated numbers.")
            return
    
    if not file_paths:
        print("No valid files selected.")
        return
    
    print(f"\nProcessing {len(file_paths)} files:")
    for path in file_paths:
        print(f"- {os.path.basename(path)}")
    
    # Process selected files
    categorized = process_multiple_files(file_paths)
    
    # Display results
    display_results(categorized)
    
    # Export to CSV
    output_file = export_to_csv(categorized, file_paths)
    print(f"Data exported to: {output_file}")

if __name__ == "__main__":
    main()
