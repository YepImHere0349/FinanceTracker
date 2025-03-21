import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class FinanceTracker:
    def __init__(self):
        self.transactions = []
        self.categories = set(["Food", "Transportation", "Entertainment", "Utilities", "Salary", "Other"])
        self.balance = 0
        self.load_data()


        self.root = tk.Tk()
        self.root.title("Finance Tracker")
        self.root.geometry("1000x1000")  


        app_title_label = tk.Label(self.root, text=self.root.title(), font=("Serif", 40))
        app_title_label.pack(pady=20)


    def load_data(self):
        try:
            with open('transactions.json', 'r') as file:
                data = json.load(file)
                self.transactions = data['transactions']
                self.balance = data['balance']
                self.categories = set(data['categories'])
        except FileNotFoundError:
            self.transactions = []
            self.balance = 0
            self.categories = set(["Food", "Transportation", "Entertainment", "Utilities", "Salary", "Other"])


    def save_data(self):
        data = {
            'transactions': self.transactions,
            'balance': self.balance,
            'categories': list(self.categories)
        }
        with open('transactions.json', 'w') as file:
            json.dump(data, file)


    def add_transaction(self, amount, category, date, transaction_type, source):
        # First check if amount contains any non-numeric characters (except decimal point)
        if any(c.isalpha() or (not c.isdigit() and c != '.') for c in str(amount)):
            messagebox.showerror(title="Error", message="Numbers only.")
            return False

        try:
            amount = float(amount)
            if amount <= 0:
                messagebox.showerror(title="Error", message="Amount must be greater than zero.")
                return False

            # Check decimal places
            if '.' in str(amount) and len(str(amount).split('.')[-1]) > 2:
                messagebox.showerror(title="Error", message="Amount cannot have more than 2 decimal places")
                return False

        except ValueError:
            messagebox.showerror(title="Error", message="Invalid amount format.")
            return False

        if category not in self.categories:
            messagebox.showerror(f"Error: Category '{category}' is not valid.")
            return False

        if transaction_type not in ['Income', 'Expense']:
            messagebox.showerror(title="Error:", message="Transaction type must be 'Income' or 'Expense'.")
            return False

        # Validate and format date
        formatted_date = self.format_date(date)

        transaction = {
            'amount': amount,
            'category': category,
            'date': formatted_date,  # Use the formatted date
            'type': transaction_type,
            'source': source
        }

        transaction['index'] = len(self.transactions) 
        self.transactions.append(transaction)

        if transaction_type == 'Income':
            self.balance += amount
        elif transaction_type == 'Expense':
            self.balance -= amount

        self.save_data()
        return True
        
    def view_balance(self):
        print(f"Current Balance: ${self.balance:.2f}")


    def generate_summary(self, start_date, end_date):
        income = 0
        expenses = 0
        category_expenses = {category: 0 for category in self.categories}

        try:
            filtered_transactions = self.filter_transactions(start_date=start_date, end_date=end_date)

            for transaction in filtered_transactions:
                if transaction['type'] == 'Income':
                    income += transaction['amount']
                else:  # Expense
                    expenses += transaction['amount']
                    category_expenses[transaction['category']] += transaction['amount']

            summary_text = f"Summary from {start_date.date()} to {end_date.date()}: \n"
            summary_text += f"Total Income: ${income:.2f} \n"
            summary_text += f"Total Expenses: ${expenses:.2f} \n"
            summary_text += "Expenses by Category: \n"

            for category, amount in category_expenses.items():
                summary_text += f"  {category}: ${amount:.2f} \n"

            summary_text += f"Net Balance: ${income - expenses:.2f} \n"

            return summary_text

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating summary: {e}")
            return ""
            
    def format_date(self, date_string):
        try:
            # Split the date into components
            year, month, day = date_string.split('-')

            # Validate year is 4 digits
            if len(year) != 4:
                messagebox.showerror(title="Error", message="Year must be 4 digits (YYYY)")
                return None

            # Convert to datetime object to validate the date
            date_obj = datetime.strptime(date_string, "%Y-%m-%d")

            # Check if date is in the future
            if date_obj.date() > datetime.now().date():
                messagebox.showerror(title="Error", message="Date must be within the time")
                return None

            # Format back to ensure YYYY-MM-DD with leading zeros
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            # Only show error if it's not already handled by the above conditions
            if '-' not in date_string:
                messagebox.showerror(title="Error", message="Invalid date format. Please use YYYY-MM-DD.")
            return None

    def update_transaction(self, index, new_amount=None, new_category=None, new_date=None, new_type=None):
        try:
            index = int(index)
            if index < 0 or index >= len(self.transactions):
                messagebox.showerror(title="Error", message="Invalid transaction index.")
                return False

            transaction = self.transactions[index]

            if new_amount is not None:
                # Check for non-numeric characters first
                if any(c.isalpha() or (not c.isdigit() and c != '.') for c in str(new_amount)):
                    messagebox.showerror(title="Error", message="Numbers only.")
                    return False

                try:
                    new_amount = float(new_amount)
                    if new_amount <= 0:
                        messagebox.showerror(title="Error", message="Amount must be greater than zero.")
                        return False

                    # Check decimal places
                    if '.' in str(new_amount) and len(str(new_amount).split('.')[-1]) > 2:
                        messagebox.showerror(title="Error", message="Amount cannot have more than 2 decimal places")
                        return False

                    transaction['amount'] = new_amount
                except ValueError:
                    messagebox.showerror(title="Error", message="Invalid amount format.")
                    return False

            if new_category is not None:
                if new_category not in self.categories:
                    messagebox.showerror(title="Error", message="Invalid category selected.")
                    return False
                transaction['category'] = new_category

            if new_date is not None:
                formatted_date = self.format_date(new_date)
                transaction['date'] = formatted_date

            if new_type is not None:
                if new_type not in ['Income', 'Expense']:
                    messagebox.showerror(title="Error", message="Transaction type must be 'Income' or 'Expense'.")
                    return False
                transaction['type'] = new_type

            self.save_data()
            return True

        except ValueError:
            messagebox.showerror(title="Error", message="Invalid index format.")
            return False

    def delete_transaction(self, index):
        if index < 0 or index >= len(self.transactions):
            messagebox.showerror(title="Error", message="Invalid transaction index.")
            return
        del self.transactions[index]
        self.save_data()


    def add_category(self, category_name):
        if category_name in self.categories:
            messagebox.showerror(f"Error: Category '{category_name}' already exists.")
        else:
            self.categories.add(category_name)
            self.save_data()


    def remove_category(self, category_name):
        if category_name not in self.categories:
            messagebox.showerror(f"Error: Category '{category_name}' does not exist.")
        else:
            self.categories.remove(category_name)
            self.save_data()


    def get_weekly_summary(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=1)

        try:
            # Create report window with date range in title
            weekly_report_window = tk.Toplevel(self.root)
            weekly_report_window.title(f"Weekly Report     {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            weekly_report_window.geometry("1000x1000")

            # Initialize tracking variables
            total_income = 0
            total_expenses = 0
            income_by_category = {category: 0.00 for category in self.categories}
            expenses_by_category = {category: 0.00 for category in self.categories}

            # Process transactions
            for transaction in self.transactions:
                transaction_date = datetime.strptime(transaction['date'], "%Y-%m-%d")
                if start_date <= transaction_date <= end_date:
                    if transaction['type'] == 'Income':
                        total_income += transaction['amount']
                        income_by_category[transaction['category']] += transaction['amount']
                    else:  # Expense
                        total_expenses += transaction['amount']
                        expenses_by_category[transaction['category']] += transaction['amount']

            # Create frame for the report
            frame = tk.Frame(weekly_report_window)
            frame.pack(fill='both', expand=True)

            # Create Treeview with style
            style = ttk.Style()
            style.configure("Bold.Treeview", font=('Helvetica', 10, 'bold'))

            tree = ttk.Treeview(frame, columns=("Category", "Amount"), show="headings", style="Bold.Treeview")
            tree.heading("Category", text="Category")
            tree.heading("Amount", text="Amount")

            # Add summary section with bold text
            tree.insert("", tk.END, values=("WEEKLY SUMMARY", ""))
            tree.insert("", tk.END, values=("TOTAL INCOME", f"${total_income:.2f}"))
            tree.insert("", tk.END, values=("TOTAL EXPENSES", f"${total_expenses:.2f}"))
            tree.insert("", tk.END, values=("NET BALANCE", f"${total_income - total_expenses:.2f}"))
            tree.insert("", tk.END, values=("", ""))

            # Add income breakdown with bold header
            tree.insert("", tk.END, values=("INCOME BREAKDOWN", ""))
            for category in sorted(self.categories):
                tree.insert("", tk.END, values=(category, f"${income_by_category[category]:.2f}"))
            tree.insert("", tk.END, values=("", ""))

            # Add expense breakdown with bold header
            tree.insert("", tk.END, values=("EXPENSE BREAKDOWN", ""))
            for category in sorted(self.categories):
                tree.insert("", tk.END, values=(category, f"${expenses_by_category[category]:.2f}"))

            # Add horizontal scrollbar
            hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            hsb.pack(side='bottom', fill='x')

            # Configure the Treeview to use scrollbar
            tree.configure(xscrollcommand=hsb.set)
            tree.pack(fill='both', expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


    def get_monthly_summary(self):
        end_date = datetime.now()
        start_date = end_date.replace(day=1)  # First day of current month

        try:
            # Create report window with date range in title
            monthly_report_window = tk.Toplevel(self.root)
            monthly_report_window.title(f"Monthly Report     {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            monthly_report_window.geometry("1000x1000")

            # Initialize tracking variables
            total_income = 0
            total_expenses = 0
            income_by_category = {category: 0.00 for category in self.categories}
            expenses_by_category = {category: 0.00 for category in self.categories}

            # Process transactions
            for transaction in self.transactions:
                transaction_date = datetime.strptime(transaction['date'], "%Y-%m-%d")
                if start_date <= transaction_date <= end_date:
                    if transaction['type'] == 'Income':
                        total_income += transaction['amount']
                        income_by_category[transaction['category']] += transaction['amount']
                    else:  # Expense
                        total_expenses += transaction['amount']
                        expenses_by_category[transaction['category']] += transaction['amount']

            # Create frame for the report
            frame = tk.Frame(monthly_report_window)
            frame.pack(fill='both', expand=True)

            # Create Treeview with style
            style = ttk.Style()
            style.configure("Bold.Treeview", font=('Helvetica', 10, 'bold'))

            tree = ttk.Treeview(frame, columns=("Category", "Amount"), show="headings", style="Bold.Treeview")
            tree.heading("Category", text="Category")
            tree.heading("Amount", text="Amount")

            # Add summary section with bold text
            tree.insert("", tk.END, values=("MONTHLY SUMMARY", ""))
            tree.insert("", tk.END, values=("TOTAL INCOME", f"${total_income:.2f}"))
            tree.insert("", tk.END, values=("TOTAL EXPENSES", f"${total_expenses:.2f}"))
            tree.insert("", tk.END, values=("NET BALANCE", f"${total_income - total_expenses:.2f}"))
            tree.insert("", tk.END, values=("", ""))

            # Add income breakdown with bold header
            tree.insert("", tk.END, values=("INCOME BREAKDOWN", ""))
            for category in sorted(self.categories):
                tree.insert("", tk.END, values=(category, f"${income_by_category[category]:.2f}"))
            tree.insert("", tk.END, values=("", ""))

            # Add expense breakdown with bold header
            tree.insert("", tk.END, values=("EXPENSE BREAKDOWN", ""))
            for category in sorted(self.categories):
                tree.insert("", tk.END, values=(category, f"${expenses_by_category[category]:.2f}"))

            # Add horizontal scrollbar
            hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            hsb.pack(side='bottom', fill='x')

            # Configure the Treeview to use scrollbar
            tree.configure(xscrollcommand=hsb.set)
            tree.pack(fill='both', expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")



    def add_transaction_gui(self):
        def submit_transaction():
            amount = amount_entry.get()
            category = category_var.get()
            date = date_entry.get()
            transaction_type = type_var.get()
            source = source_entry.get()

            if not all([amount, category, date, transaction_type, source]):
                messagebox.showerror(title="Error", message="Please fill in all fields.")
                return

            # If add_transaction returns True, then show success message and close window
            if self.add_transaction(amount, category, date, transaction_type, source):
                messagebox.showinfo(title="Success", message="Transaction added successfully.")
                add_transaction_window.destroy()

        add_transaction_window = tk.Toplevel(self.root)
        add_transaction_window.title("Add Transaction")
        add_transaction_window.geometry("1000x1000")

        amount_label = tk.Label(add_transaction_window, text="Amount:")
        amount_label.grid(row=0, column=0, padx=5, pady=5)

        amount_entry = tk.Entry(add_transaction_window)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)

        category_label = tk.Label(add_transaction_window, text="Category:")
        category_label.grid(row=1, column=0, padx=5, pady=5)

        category_var = tk.StringVar(add_transaction_window)
        category_var.set("")

        category_dropdown = ttk.Combobox(
            add_transaction_window,
            textvariable=category_var,
            values=list(self.categories),
            state="readonly"
        )
        category_dropdown.grid(row=1, column=1, padx=5, pady=5)

        date_label = tk.Label(add_transaction_window, text="Date (YYYY-MM-DD):")
        date_label.grid(row=2, column=0, padx=5, pady=5)

        date_entry = tk.Entry(add_transaction_window)
        date_entry.grid(row=2, column=1, padx=5, pady=5)

        type_label = tk.Label(add_transaction_window, text="Type:")
        type_label.grid(row=3, column=0, padx=5, pady=5)

        type_var = tk.StringVar(add_transaction_window)
        type_var.set("")

        type_dropdown = ttk.Combobox(
            add_transaction_window,
            textvariable=type_var,
            values=["Income", "Expense"],
            state="readonly"
        )
        type_dropdown.grid(row=3, column=1, padx=5, pady=5)

        source_label = tk.Label(add_transaction_window, text="Source:")
        source_label.grid(row=4, column=0, padx=5, pady=5)

        source_entry = tk.Entry(add_transaction_window)
        source_entry.grid(row=4, column=1, padx=5, pady=5)

        index_label = tk.Label(add_transaction_window, text=f"Transaction Index: {len(self.transactions)}")
        index_label.grid(row=5, column=0, padx=5, pady=5)

        submit_button = tk.Button(add_transaction_window, text="Submit", command=submit_transaction)
        submit_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    
    def view_balance_gui(self):
        balance_window = tk.Toplevel(self.root)
        balance_window.title("Current Balance")
        balance_window.geometry("1000x1000")

        # Create frame for the display
        frame = tk.Frame(balance_window)
        frame.pack(fill='both', expand=True)

        # Create Treeview with style
        style = ttk.Style()
        style.configure("Bold.Treeview", font=('Helvetica', 10, 'bold'))

        tree = ttk.Treeview(frame, columns=("Item", "Amount"), show="headings", style="Bold.Treeview")
        tree.heading("Item", text="Item")
        tree.heading("Amount", text="Amount")

        # Insert balance with bold formatting
        tree.insert("", tk.END, values=("Current Balance", f"${self.balance:.2f}"))

        tree.pack(fill='both', expand=True)


    def generate_summary_gui(self):
        def submit_summary():
            start_date = start_date_entry.get()
            end_date = end_date_entry.get()

            if not start_date or not end_date:
                messagebox.showerror(title="Error", message="Please fill in both start and end dates.")
                return

            start_formatted_date = self.format_date(start_date)
            end_formatted_date = self.format_date(end_date)

            if not start_formatted_date or not end_formatted_date:
                return

            start_date_obj = datetime.strptime(start_formatted_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_formatted_date, "%Y-%m-%d")

            # Check if start date is older than end date
            if start_date_obj >= end_date_obj:
                messagebox.showerror(title="Error", message="Start date must be older than end date.")
                return

            summary_text = self.generate_summary(start_date_obj, end_date_obj)
            summary_window = tk.Toplevel(self.root)
            summary_window.title("Summary")
            summary_window.geometry("1000x1000") 

            summary_label = tk.Label(summary_window, text=f"Summary from {start_date_obj.date()} to {end_date_obj.date()}:")
            summary_label.pack()

            # Create Treeview to display transactions
            tree = ttk.Treeview(summary_window, columns=("Amount", "Category", "Date", "Type", "Source"), show="headings")
            tree.heading("Amount", text="Amount")
            tree.heading("Category", text="Category")
            tree.heading("Date", text="Date")
            tree.heading("Type", text="Type")
            tree.heading("Source", text="Source")

            filtered_transactions = self.filter_transactions(start_date=start_date_obj, end_date=end_date_obj)
            for transaction in filtered_transactions:
                tree.insert("", tk.END, values=(
                    transaction['amount'],
                    transaction['category'],
                    transaction['date'],
                    transaction['type'],
                    transaction['source']
                ))

            tree.pack()
            summary_window.mainloop()

        summary_window = tk.Toplevel(self.root)
        summary_window.title("Choose Dates")
        summary_window.geometry("1000x1000")

        start_date_label = tk.Label(summary_window, text="Start Date (YYYY-MM-DD):")
        start_date_label.grid(row=0, column=0, padx=5, pady=5)

        start_date_entry = tk.Entry(summary_window)
        start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        end_date_label = tk.Label(summary_window, text="End Date (YYYY-MM-DD):")
        end_date_label.grid(row=1, column=0, padx=5, pady=5)

        end_date_entry = tk.Entry(summary_window)
        end_date_entry.grid(row=1, column=1, padx=5, pady=5)

        submit_button = tk.Button(summary_window, text="Submit", command=submit_summary)
        submit_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)




    def update_transaction_gui(self):
        def update_transaction():
            index = index_entry.get()
            new_amount = amount_entry.get()
            new_category = category_var.get()
            new_date = date_entry.get()
            new_type = type_var.get()

            if not all([index, new_amount, new_category, new_date, new_type]):
                messagebox.showerror(title="Error", message="Please fill out all fields.")
                return

            # First validate the date before proceeding with update
            formatted_date = self.format_date(new_date)
            if not formatted_date:
                return  # format_date will handle the error message

            if self.update_transaction(index, new_amount, new_category, new_date, new_type):
                messagebox.showinfo(title="Success", message="Transaction updated successfully.")
                update_transaction_window.destroy()

        update_transaction_window = tk.Toplevel(self.root)
        update_transaction_window.title("Update Transaction")
        update_transaction_window.geometry("1000x1000")

        index_label = tk.Label(update_transaction_window, text="Transaction Index:")
        index_label.grid(row=0, column=0, padx=5, pady=5)

        index_entry = tk.Entry(update_transaction_window)
        index_entry.grid(row=0, column=1, padx=5, pady=5)

        amount_label = tk.Label(update_transaction_window, text="New Amount:")
        amount_label.grid(row=1, column=0, padx=5, pady=5)

        amount_entry = tk.Entry(update_transaction_window)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)

        category_label = tk.Label(update_transaction_window, text="New Category:")
        category_label.grid(row=2, column=0, padx=5, pady=5)

        category_var = tk.StringVar(update_transaction_window)
        category_var.set("")

        category_dropdown = ttk.Combobox(
            update_transaction_window,
            textvariable=category_var,
            values=list(self.categories),
            state="readonly"
        )
        category_dropdown.grid(row=2, column=1, padx=5, pady=5)

        date_label = tk.Label(update_transaction_window, text="New Date (YYYY-MM-DD):")
        date_label.grid(row=3, column=0, padx=5, pady=5)

        date_entry = tk.Entry(update_transaction_window)
        date_entry.grid(row=3, column=1, padx=5, pady=5)

        type_label = tk.Label(update_transaction_window, text="New Type:")
        type_label.grid(row=4, column=0, padx=5, pady=5)

        type_var = tk.StringVar(update_transaction_window)
        type_var.set("")

        type_dropdown = ttk.Combobox(
            update_transaction_window,
            textvariable=type_var,
            values=["Income", "Expense"],
            state="readonly"
        )
        type_dropdown.grid(row=4, column=1, padx=5, pady=5)

        submit_button = tk.Button(update_transaction_window, text="Submit", command=update_transaction)
        submit_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def delete_transaction(self, index):
        try:
            index = int(index)
            # Check if index exists in current transactions
            if not any(t['index'] == index for t in self.transactions):
                return False

            # Find and delete the transaction with matching index
            for i, transaction in enumerate(self.transactions):
                if transaction['index'] == index:
                    deleted_transaction = self.transactions.pop(i)

                    # Update the balance based on the deleted transaction
                    if deleted_transaction['type'] == 'Income':
                        self.balance -= deleted_transaction['amount']
                    else:  # Expense
                        self.balance += deleted_transaction['amount']

                    self.save_data()
                    return True

            return False

        except ValueError:
            return False

    def delete_transaction_gui(self):
            def delete_transaction():
                try:
                    index = index_entry.get()
                    if index.strip() == "":
                        messagebox.showerror(title="Error", message="Please enter a transaction index.")
                        return

                    index = int(index)
                    if not any(t['index'] == index for t in self.transactions):
                        messagebox.showerror(title="Error", message="This transaction index does not exist.")
                        return

                    success = self.delete_transaction(index)
                    if success:
                        messagebox.showinfo(title="Success", message=f"Transaction {index} deleted successfully.")
                        delete_transaction_window.destroy()
                    else:
                        messagebox.showerror(title="Error", message="Transaction could not be deleted.")

                except ValueError:
                    messagebox.showerror(title="Error", message="Please enter a valid number for the index.")

            delete_transaction_window = tk.Toplevel(self.root)
            delete_transaction_window.title("Delete Transaction")
            delete_transaction_window.geometry("1000x1000")

            index_label = tk.Label(delete_transaction_window, text="Transaction Index:")
            index_label.grid(row=0, column=0, padx=5, pady=5)
            index_entry = tk.Entry(delete_transaction_window)
            index_entry.grid(row=0, column=1, padx=5, pady=5)

            submit_button = tk.Button(delete_transaction_window, text="Delete", command=delete_transaction)
            submit_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)


    def search_transactions_gui(self):
        def search_transactions():
            category = category_var.get() if category_var.get() != "" else None
            transaction_type = type_var.get() if type_var.get() != "" else None

            try:
                start_date_obj = None
                end_date_obj = None

                if start_date_entry.get().strip():
                    start_date_obj = datetime.strptime(start_date_entry.get().strip(), "%Y-%m-%d")

                if end_date_entry.get().strip():
                    end_date_obj = datetime.strptime(end_date_entry.get().strip(), "%Y-%m-%d")

                if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
                    messagebox.showerror("Error", "Start date must be before end date")
                    return

                filtered_transactions = self.filter_transactions(
                    category=category,
                    transaction_type=transaction_type,
                    start_date=start_date_obj,
                    end_date=end_date_obj
                )

                results_window = tk.Toplevel(self.root)
                results_window.title("Search Results")
                results_window.geometry("1000x1000")

                tree = ttk.Treeview(results_window, columns=("Amount", "Category", "Date", "Type", "Source"), show="headings")
                tree.heading("Amount", text="Amount")
                tree.heading("Category", text="Category")
                tree.heading("Date", text="Date")
                tree.heading("Type", text="Type")
                tree.heading("Source", text="Source")

                for transaction in filtered_transactions:
                    tree.insert("", tk.END, values=(
                        transaction['amount'],
                        transaction['category'],
                        transaction['date'],
                        transaction['type'],
                        transaction['source']
                    ))

                tree.pack()

            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return

        search_transactions_window = tk.Toplevel(self.root)
        search_transactions_window.title("Search Transactions")
        search_transactions_window.geometry("1000x1000")

        category_label = tk.Label(search_transactions_window, text="Category:")
        category_label.grid(row=0, column=0, padx=5, pady=5)

        category_var = tk.StringVar(search_transactions_window)
        category_var.set("")

        category_dropdown = ttk.Combobox(
            search_transactions_window,
            textvariable=category_var,
            values=list(self.categories),
            state="readonly"
        )
        category_dropdown.grid(row=0, column=1, padx=5, pady=5)

        type_label = tk.Label(search_transactions_window, text="Type:")
        type_label.grid(row=1, column=0, padx=5, pady=5)

        type_var = tk.StringVar(search_transactions_window)
        type_var.set("")

        type_dropdown = ttk.Combobox(
            search_transactions_window,
            textvariable=type_var,
            values=["Income", "Expense"],
            state="readonly"
        )
        type_dropdown.grid(row=1, column=1, padx=5, pady=5)

        start_date_label = tk.Label(search_transactions_window, text="Start Date (YYYY-MM-DD):")
        start_date_label.grid(row=2, column=0, padx=5, pady=5)

        start_date_entry = tk.Entry(search_transactions_window)
        start_date_entry.grid(row=2, column=1, padx=5, pady=5)

        end_date_label = tk.Label(search_transactions_window, text="End Date (YYYY-MM-DD):")
        end_date_label.grid(row=3, column=0, padx=5, pady=5)

        end_date_entry = tk.Entry(search_transactions_window)
        end_date_entry.grid(row=3, column=1, padx=5, pady=5)

        submit_button = tk.Button(search_transactions_window, text="Search", command=search_transactions)
        submit_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        


    def add_category_gui(self):
        def submit_category():
            category_name = category_entry.get()
            if not category_name:
                messagebox.showerror(title="Error", message="Please enter a category name.")
                return
            self.add_category(category_name)
            messagebox.showinfo(title="Success", message="Category added successfully.")
            add_category_window.destroy()


        add_category_window = tk.Toplevel(self.root)
        add_category_window.title("Add Category")
        add_category_window.geometry("1000x1000")


        category_label = tk.Label(add_category_window, text="Category Name:")
        category_label.grid(row=0, column=0, padx=5, pady=5)
        category_entry = tk.Entry(add_category_window)
        category_entry.grid(row=0, column=1, padx=5, pady=5)


        submit_button = tk.Button(add_category_window, text="Submit", command=submit_category)
        submit_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)


    def remove_category_gui(self):
        def remove_category():
            category_name = category_var.get()
            if not category_name:
                messagebox.showerror(title="Error", message="Please select a category to remove.")
                return
            self.remove_category(category_name)
            messagebox.showinfo(title="Success", message="Category removed successfully.")
            remove_category_window.destroy()


        remove_category_window = tk.Toplevel(self.root)
        remove_category_window.title("Remove Category")
        remove_category_window.geometry("1000x1000")


        category_label = tk.Label(remove_category_window, text="Category:")
        category_label.grid(row=0, column=0, padx=5, pady=5)
        category_var = tk.StringVar(remove_category_window)
        category_var.set("")
        category_dropdown = ttk.Combobox(
            remove_category_window,
            textvariable=category_var,
            values=list(self.categories),
            state="readonly"
        )
        category_dropdown.grid(row=0, column=1, padx=5, pady=5)


        submit_button = tk.Button(remove_category_window, text="Remove", command=remove_category)
        submit_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)


    def transaction_maintenance_menu(self):
        transaction_maintenance_window = tk.Toplevel(self.root)
        transaction_maintenance_window.title("Transaction Maintenance")
        transaction_maintenance_window.geometry("1000x1000")


        add_button = tk.Button(transaction_maintenance_window, text="Add Transaction", command=self.add_transaction_gui)
        add_button.pack(pady=5)


        delete_button = tk.Button(transaction_maintenance_window, text="Delete Transaction", command=self.delete_transaction_gui)
        delete_button.pack(pady=5)


        modify_button = tk.Button(transaction_maintenance_window, text="Update Transaction", command=self.update_transaction_gui)
        modify_button.pack(pady=5)




    def reports_menu(self):
        reports_window = tk.Toplevel(self.root)
        reports_window.title("Reports")
        reports_window.geometry("1000x1000")


        summary_button = tk.Button(reports_window, text="Choose Dates", command=self.generate_summary_gui)
        summary_button.pack(pady=5)


        weekly_button = tk.Button(reports_window, text="Weekly Report", command=self.get_weekly_summary)
        weekly_button.pack(pady=5)


        monthly_button = tk.Button(reports_window, text="Monthly Report", command=self.get_monthly_summary)
        monthly_button.pack(pady=5)


        current_balance_button = tk.Button(reports_window, text="Current Balance", command=self.view_balance_gui)
        current_balance_button.pack(pady=5)


    def category_maintenance_menu(self):
        category_maintenance_window = tk.Toplevel(self.root)
        category_maintenance_window.title("Category Maintenance")
        category_maintenance_window.geometry("1000x1000")


        add_button = tk.Button(category_maintenance_window, text="Add Category", command=self.add_category_gui)
        add_button.pack(pady=5)


        remove_button = tk.Button(category_maintenance_window, text="Remove Category", command=self.remove_category_gui)
        remove_button.pack(pady=5)

    def filter_transactions(self, category=None, transaction_type=None, start_date=None, end_date=None):
        filtered = self.transactions.copy()

        if category:
            filtered = [t for t in filtered if t['category'] == category]

        if transaction_type:
            filtered = [t for t in filtered if t['type'] == transaction_type]

        if start_date:
            filtered = [t for t in filtered if t['date'] and datetime.strptime(t['date'], "%Y-%m-%d") >= start_date]

        if end_date:
            filtered = [t for t in filtered if t['date'] and datetime.strptime(t['date'], "%Y-%m-%d") <= end_date]

        return filtered


    def run(self):
        # Create a menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)


        # Create the "File" menu
        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="App", menu=filemenu)
        filemenu.add_command(label="Exit", command=self.root.quit)


        # Create the "Transactions" menu
        transactions_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Transactions", menu=transactions_menu)
        transactions_menu.add_command(label="Transaction Maintenance", command=self.transaction_maintenance_menu)
        transactions_menu.add_command(label="Search Transactions", command=self.search_transactions_gui) #Directly call search_transactions_gui


        # Create the "Reports" menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Choose Dates", command=self.generate_summary_gui)
        reports_menu.add_command(label="Weekly Report", command=self.get_weekly_summary)
        reports_menu.add_command(label="Monthly Report", command=self.get_monthly_summary)
        reports_menu.add_command(label="Current Balance", command=self.view_balance_gui)


        # Create the "Categories" menu
        categories_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Categories", menu=categories_menu)
        categories_menu.add_command(label="Category Maintenance", command=self.category_maintenance_menu)


        self.root.mainloop()



if __name__ == '__main__':
    app = FinanceTracker()
    app.run()


