# AI-Powered Budget Transaction Categorizer

An intelligent budget tracking tool that uses ChatGPT to automatically categorize Chase bank transactions into predefined budget categories, making manual budget tracking faster and more organized.

## Overview

This tool is designed for hands-on budget trackers who want to maintain detailed control over their finances while reducing manual categorization time. Instead of manually categorizing every transaction when inputting into Excel budget trackers, this tool uses OpenAI's ChatGPT API to intelligently categorize transactions based on your custom budget categories.

## How It Works

1. **Download CSV files** from Chase's built-in CSV downloader (both checking and credit card accounts)
2. **AI Categorization** - ChatGPT analyzes each transaction and categorizes it based on:
   - Transaction description
   - Amount
   - Transaction type
   - Your predefined budget categories
3. **Excel Integration** - Outputs organized data with Excel formulas for easy import
4. **Manual Review** - You can still see every line item and manually adjust as needed

## Features

- **Multi-Account Support**: Handles both Chase checking and credit card CSV formats
- **Custom Categories**: Easily modify budget categories in the code
- **AI-Powered**: Uses ChatGPT for intelligent transaction categorization
- **Excel Formulas**: Automatically generates sum formulas for each subcategory
- **Detailed Output**: Preserves all transaction details while adding categorization
- **Virtual Environment**: Isolated Python environment for clean dependency management

## Setup

### Prerequisites
- Python 3.7+
- OpenAI API key
- Chase bank account with CSV download capability

### Installation

1. Clone this repository:
```bash
git clone [your-repo-url]
cd budget-automation
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

## Usage

### Step 1: Download Chase CSV Files
1. Log into your Chase account
2. Navigate to account statements
3. Download CSV files for your checking and credit card accounts
4. Place CSV files in the `accounts/` directory

### Step 2: Run the Categorizer
```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Run the main script
python budget.py
```

### Step 3: Select Files and Process
- The script will list all CSV files in the `accounts/` directory
- Choose which files to process (or select 'all')
- AI will categorize each transaction
- Results are saved to `outputs/` directory

## Budget Categories

The tool comes with predefined categories that you can customize:

- **Incoming**: venmo, eastman, work, cash, slb_payroll, cameron_payroll
- **Spending**: rent, utilities, insurance, groceries, gym, shopping, eating out, etc.
- **Investments**: vanguard, roth ira, robinhood, coinbase, ally bank
- **Unknown**: Uncategorized transactions

### Customizing Categories
Edit the `BUDGET_CATEGORIES` dictionary in `budget.py`:

```python
BUDGET_CATEGORIES = {
    "Incoming": ["your", "income", "sources"],
    "Spending": ["your", "expense", "categories"],
    "Investments": ["your", "investment", "accounts"],
    "Unknown": []
}
```

## Output Format

The tool generates a detailed CSV file with:
- Original transaction data
- AI-assigned categories
- Excel formulas for easy summation
- Organized by main category and subcategory

## Utilities

### Format Numbers Tool
`format_numbers.py` - Converts negative numbers to Excel sum formulas and copies to clipboard.

```bash
python format_numbers.py
```

## Why This Approach?

**Before**: Manually categorizing 100+ transactions each month when inputting to Excel
**After**: AI categorizes everything, you review and manually input organized data

This tool doesn't replace your existing budget tracking workflow—it enhances it by:
- Reducing categorization time by 80%+
- Maintaining full transaction visibility
- Providing Excel-ready formulas
- Allowing manual adjustments and overrides

## API Usage

The tool uses OpenAI's ChatGPT API with configurable models:
- GPT-4 (default)
- GPT-4 Mini
- GPT-4 Vision

Costs are typically under $1-2 per month for personal use with 100-200 transactions.

## Security

- API keys stored in `.env` file (excluded from git)
- Personal financial data never committed to repository
- CSV files automatically ignored by git

## Contributing

Feel free to submit issues and enhancement requests! This tool is designed to be customizable for different banks, categories, and workflows.

## License

MIT License - See LICENSE file for details.
