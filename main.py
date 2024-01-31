from flask import Flask
import json
import sys
import datetime


app = Flask(__name__)


# ============================================================================
# UTIL's

def read_accounts():
    with open("accounts.json", "r") as _read_accounts:
        accounts = json.load(_read_accounts)
    _read_accounts.close()

    return accounts

def write_accounts(value):
    with open("accounts.json", "w") as _write_accounts:
        json.dump(value, _write_accounts)
    _write_accounts.close()

# Message: Custom message explaining action; Value: Amount of money processed; Action: in, out.
# NOTE: its an internal system call, no need to validate if account exists.
def add_history(card_number, message, value, action):
    accounts = read_accounts()

    for account in accounts:
        account["history"].append({
            "message": message,
            "value": value,
            "action": action
        })

    write_accounts(accounts)


# ============================================================================
# ADMIN functions

# create user
def create_user(sysargv):

    accounts = read_accounts()

    try:

        account_exists = False
        for account in accounts:
            if account["card_number"] == sysargv[4]:
                account_exists = True
                break

        if account_exists:
            print("The card number is already used by another account. Please use another card number.")
        else:
            newAccount = dict(
                username = sysargv[2].replace(" ", ""),
                cvv = sysargv[3],
                card_number = sysargv[4],
                balance = 0,
                history = []
            )

            accounts = read_accounts()
            accounts.append(newAccount)
            write_accounts(accounts)

            print(f"User {newAccount['username']} created successfully.")

    except:
        print("Please enter a name, cvv and card number.")


# ============================================================================
# Banking

# deposit
def deposit(card_number, amount):
    accounts = read_accounts()

    account_exists = False
    action_success = False
    for account in accounts:
        if account["card_number"] == card_number:
            account["balance"] += amount
            account_exists = True
            action_success = True
            print(f"Successfully deposited {amount} to {account['username']}")
            break

    if account_exists:
        if action_success:
            write_accounts(accounts)
            add_history(card_number, "Deposit to bank", amount, "in")
    else:
        print(f"Failed to deposit. Card number {card_number} doesn't exist")

# withdraw
def withdraw(card_number, amount):
    accounts = read_accounts()
    
    account_exists = False
    action_success = False
    for account in accounts:
        if account["card_number"] == card_number:
            if account["balance"] >= amount:
                account["balance"] -= amount
                action_success = True
                print(f"Successfully withdrew {amount} from {account['username']}")
            else:
                print(f"There isnt {amount} in the account. Failed to withdraw.")
            account_exists = True
            break


    if account_exists:
        if action_success:
            write_accounts(accounts)
            add_history(card_number, "Withdrawal from bank", amount, "out")
    else:
        print(f"Failed to withdraw. Card number {card_number} doesn't exist")
    
# transaction
def transaction(payer_card_number, beneficiary_card_number, amount):
    accounts = read_accounts()

    payer_found = False
    beneficiary_found = False

    action_success = False
    funds_exist = False
    action_message = ""

    # Verifying both the accounts exist
    for account in accounts:
        if (account["card_number"] == payer_card_number):
            payer_found = True
            if (account["balance"] >= amount):
                account["balance"] -= amount
                funds_exist = True


        if (account["card_number"] == beneficiary_card_number):
            beneficiary_found = True
            if funds_exist:
                account["balance"] += amount
                action_success = True
        
        if payer_found and beneficiary_found:
            break
            
    if payer_found and beneficiary_found:
        if action_success:
            action_message = f"Successfully transferred {amount} from payer({payer_card_number}) to beneficiary({beneficiary_card_number})"
        else:
            action_message = f"Transaction failed due to the payer not having enough funds."

    else:
        if not(payer_found) and not(beneficiary_found):
            action_message = f"The payer({payer_card_number}) and beneficiary({beneficiary_card_number}) accounts don't exist."
        elif payer_found and not(beneficiary_found):
            action_message = f"The beneficiary({beneficiary_card_number}) account doesn't exist."
        elif not(payer_found) and beneficiary_found:
            action_message = f"The payer({payer_card_number}) account doesn't exist."


    return {
        "action_message": action_message,
        "action_success": action_success
    }

# ============================================================================
# APIS

# Transaction
# @Flask.post("/api/transaction")
# def post_transaction():
#     return ""

# E-commerce



if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 2:
        app.run(debug=True)
    else:
        if (sys.argv[1] == "create_user"):
            create_user(sys.argv)
        elif (sys.argv[1] == "deposit"):
            try:
                amount = int(sys.argv[2])
                card_number = str(sys.argv[3])
                deposit(card_number, amount)
            except:
                print("Error depositing to user. Make sure amount and card number has been entered.")
        elif (sys.argv[1] == "withdraw"):
            try:
                amount = int(sys.argv[2])
                card_number = str(sys.argv[3])
                withdraw(card_number, amount)
            except:
                print("Error withdrawing from user. Make sure amount and card number has been entered.")
        elif (sys.argv[1] == "transaction"):
            try:
                payer_card_number = int(input("Payer Card Number: "))
                beneficiary_card_number = int(input("Beneficiary Card Number: "))
                amount = int(input("Amount of money to transfer: "))
                print(transaction(payer_card_number, beneficiary_card_number, amount))
            except:
                print("Please enter asdafdsvalid values.")