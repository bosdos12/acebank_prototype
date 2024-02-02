import tkinter as tk
from tkinter import messagebox
import pyautogui
import requests
import json

# Utils
def entry_enter(event):
    pyautogui.press('tab')

BUSINESS_BANK_NUMBER = "0077234724"

class MainApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.title("ADAK POS")
        self.geometry("500x300")
        self.resizable(False, False)

        adakposlabel = tk.Label(self, text="ADAK POS", font=("Arial", 24))
        adakposlabel.place(x=10, y=10)


        totalpricelabel = tk.Label(self, text="Total Price: ", font=("Arial", 24))
        totalpricelabel.place(x=10, y=50)

        self.totalprice_entry = tk.Entry(self, font=("Arial", 24), width=6)
        self.totalprice_entry.place(x=200, y=50)



        cardnumberlabel = tk.Label(self, text="Card Number: ", font=("Arial", 12))
        cardnumberlabel.place(x=10, y=150)
        self.cardnumber_entry = tk.Entry(self, font=("Arial", 12), show="*")
        self.cardnumber_entry.place(x=200, y=150)


        cardcvvlabel = tk.Label(self, text="Card CVV: ", font=("Arial", 12))
        cardcvvlabel.place(x=10, y=180)
        self.cardcvv_entry = tk.Entry(self, font=("Arial", 12), width=4, show="*")
        self.cardcvv_entry.place(x=200, y=180)


        self.totalprice_entry.bind("<Return>", entry_enter)
        self.cardnumber_entry.bind("<Return>", entry_enter)
        self.cardcvv_entry.bind("<Return>", self.run_transaction)


    def run_transaction(self, event):
        # try:
        price_total = int(self.totalprice_entry.get())


        cardnumber = self.cardnumber_entry.get()
        cardcvv = self.cardcvv_entry.get()

        if len(cardnumber) > 0 and len(cardcvv) > 0:
            
            transaction_request = requests.post("http://127.0.0.1:5000/post_transaction", json={
                "payer_card_number": cardnumber,
                "payer_cvv": cardcvv,
                "beneficiary_card_number": BUSINESS_BANK_NUMBER,
                "amount": price_total
            }).json()

            if (transaction_request["action_success"]):
                messagebox.showinfo("Success", "Payment Successfull")
                self.totalprice_entry.delete(0, tk.END)
                self.cardnumber_entry.delete(0, tk.END)
                self.cardcvv_entry.delete(0, tk.END)

            else:
                messagebox.showerror("Error", transaction_request["action_message"])


        else:
            messagebox.showwarning("Warning", "Card details must be entered.")    
        # except:
        #     messagebox.showwarning("Warning", "Please enter a total price.")
        



if __name__ == "__main__":
    print("wtf")
    app = MainApp()
    app.mainloop()
