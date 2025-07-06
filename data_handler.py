# data_handler.py (MODIFIED for email validation)
import pandas as pd
import re # Added for robust email validation

def is_valid_email(email):
    """Basic regex for email validation."""
    if not isinstance(email, str):
        return False
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def load_contacts_from_excel(file_path):
    """
    Loads contact data from an Excel file into a list of dictionaries.
    Assumes columns like 'Name', 'Email'.
    Performs validation for email addresses.
    Returns contacts and a list of issues (e.g., invalid/duplicate emails).
    """
    contacts = []
    issues = []
    seen_emails = set()

    try:
        df = pd.read_excel(file_path)

        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        required_cols = ['name', 'email']
        for col in required_cols:
            if col not in df.columns:
                df[col] = '' 

        for index, row in df.iterrows():
            contact = row.to_dict()
            email = str(contact.get('email', '') or '').strip()
            name = contact.get('name', 'Unnamed Contact').strip()

            contact_issues = []

            if not email:
                contact_issues.append(f"Row {index+2}: Missing email for {name}.")
            elif not is_valid_email(email):
                contact_issues.append(f"Row {index+2}: Invalid email format for '{email}' ({name}).")
            elif email in seen_emails:
                contact_issues.append(f"Row {index+2}: Duplicate email '{email}' for {name}.")
            else:
                seen_emails.add(email)
                contacts.append(contact)
            
            if contact_issues:
                issues.extend(contact_issues)

        return contacts, issues
    except FileNotFoundError:
        issues.append(f"Error: File not found at {file_path}")
        return [], issues
    except Exception as e:
        issues.append(f"Error loading Excel file: {e}")
        return [], issues

if __name__ == '__main__':
    # --- For Testing: Create a dummy Excel file ---
    dummy_data = {
        'Name': ['Alice Smith', 'Bob Johnson', 'Charlie Brown', 'Eve Davis', 'Duplicate Alice'],
        'Email': ['alice@example.com', '', 'charlie@example.com', 'eve@example.com', 'alice@example.com'] # Added duplicate
    }
    dummy_df = pd.DataFrame(dummy_data)
    dummy_df.to_excel('dummy_contacts_email.xlsx', index=False)
    print("Dummy Excel file 'dummy_contacts_email.xlsx' created.")

    # --- For Testing: Load the dummy Excel file ---
    contacts, issues = load_contacts_from_excel('dummy_contacts_email.xlsx')
    print("\nLoaded contacts (valid only):")
    for contact in contacts:
        print(contact)
    
    print("\nIssues found during loading:")
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        print("No issues found.")