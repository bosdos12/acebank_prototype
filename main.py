from flask import Flask, request, jsonify
import json
import sys
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============================================================================
# UTIL's

def read_accounts():
    with open("accounts.json", "r") as _read_accounts:
        accounts = json.load(_read_accounts)
    _read_accounts.close()

    return accounts

def write_accounts(value):
    with open("accounts.json", "w") as _write_accounts:
        json.dump(value, _write_accounts, indent=4)
    _write_accounts.close()



# Message: Custom message explaining action; Value: Amount of money processed; Action: in, out.
# NOTE: its an internal system call, no need to validate if account exists.
def add_history(card_number, message, value, action):
    accounts = read_accounts()

    for account in accounts:
        if account["card_number"] == card_number:
            account["history"].append({
                "message": message,
                "value": value,
                "action": action
            })
            break

    write_accounts(accounts)

# Authenticates user by making sure there is a user with the card number given
# and making sure the card number and the cvv are matching.
def user_exists(card_number):
    print("USER EXISTS FUNCTION")
    accounts = read_accounts()
    user_exists = False
    for account in accounts:
        print(account)
        print(account["card_number"])
        if account["card_number"] == card_number:
            print("USER EXISTS")
            user_exists = True
            break
        
    print(card_number)
    print(user_exists)
    return user_exists

def authenticate_user(card_number, cvv):
    print("USER EXISTS FUNCTION")
    accounts = read_accounts()
    user_exists = False
    valid_cvv = False
    for account in accounts:
        print(account)
        print(account["card_number"])
        if account["card_number"] == card_number:
            print("USER EXISTS")
            user_exists = True

            if (account["cvv"] == cvv):
                valid_cvv = True

            break
        
    print(card_number)
    print(user_exists)
    return [user_exists, valid_cvv]

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
def transaction(payer_card_number, payer_cvv, beneficiary_card_number, amount):
    accounts = read_accounts()

    payer_found = user_exists(payer_card_number)
    beneficiary_found = user_exists(beneficiary_card_number)

    action_success = False
    funds_exist = False
    valid_payer_cvv = False
    action_message = ""

    # Verifying both the accounts exist

    print(f"Payer Found: {payer_found}")
    print(f"Beneficiary Found: {beneficiary_found}")

        
            
    if payer_found and beneficiary_found:
        for account in accounts:
            if (account["card_number"] == payer_card_number):
                if (account["cvv"] == payer_cvv):
                    valid_payer_cvv = True
                    if (account["balance"] >= amount):
                        account["balance"] -= amount
                        funds_exist = True


            if (account["card_number"] == beneficiary_card_number):
                if valid_payer_cvv:
                    if funds_exist:
                        account["balance"] += amount
                        action_success = True
                    else:
                        action_message = f"Transaction failed due to the payer not having enough funds."
                else:
                    action_message = f"Transaction failed due to payers CVV not being correct or entered."

        if action_success:
            write_accounts(accounts)
            action_message = f"Successfully transferred {amount} from payer({payer_card_number}) to beneficiary({beneficiary_card_number})"
            add_history(beneficiary_card_number, action_message, value=amount, action="in")
            add_history(payer_card_number, action_message, value=amount, action="out")


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
@app.post('/post_transaction')
def post_transaction():
    # Get JSON data from the request body
    data = request.get_json()
    print(data)
    # Check if 'username' and 'password' are present in the JSON data
    if 'payer_card_number' not in data or 'payer_cvv' not in data or "beneficiary_card_number" not in data or "amount" not in data:
        return jsonify({'action_message': 'Missing payer_card_number or payer_cvv or beneficiary_card_number or amount', "action_success": False}), 400

    # Extract username and password from the JSON data
    payer_card_number = data["payer_card_number"]
    payer_cvv = data["payer_cvv"]
    beneficiary_card_number = data["beneficiary_card_number"]
    amount = data["amount"]

    transaction_output = transaction(payer_card_number, payer_cvv, beneficiary_card_number, amount)
    return jsonify(transaction_output) # action_message: string, action_success: boolean


@app.post("/post_login")
def post_login():
    data = request.get_json()
    print(data)

    auth_user_res = authenticate_user(data["cardnumber"], data["cvv"])

    print(auth_user_res)

    if (auth_user_res[0] and auth_user_res[1]):
        return jsonify({"action_success": True})
    elif (not(auth_user_res[0]) and not(auth_user_res[1])):
        return jsonify({"action_success": False, "action_message": "User doesnt exist."})
    elif (auth_user_res[0] and not(auth_user_res[1])):
        return jsonify({"action_success": False, "action_message": "User exists, invalid cvv."})


# Account Data
@app.post("/account_data")
def account_data():
    data = request.get_json()    

    auth_user_res = authenticate_user(data["cardnumber"], data["cvv"])

    print(auth_user_res)

    if (auth_user_res[0] and auth_user_res[1]):
        accounts = read_accounts()

        current_account = False

        for account in accounts:
            if account["card_number"] == data["cardnumber"]:
                current_account = account
                break


        return jsonify({"action_success": True, "balance": account["balance"], "history": account["history"]})

    
    elif (not(auth_user_res[0]) and not(auth_user_res[1])):
        return jsonify({"action_success": False, "action_message": "User doesnt exist."})
    elif (auth_user_res[0] and not(auth_user_res[1])):
        return jsonify({"action_success": False, "action_message": "User exists, invalid cvv."})


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
                payer_card_number = input("Payer Card Number: ")
                payer_cvv = input("Payer CVV: ")
                beneficiary_card_number = input("Beneficiary Card Number: ")
                amount = int(input("Amount of money to transfer: "))
                print(transaction(payer_card_number, payer_cvv, beneficiary_card_number, amount))
            except:
                print("Please enter valid values.")