import json
from datetime import datetime
import serial
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
import pandas as pd

# Set up the serial connection for RFID reader
try:
    ser = serial.Serial('COM5', 9600, timeout=1)
except serial.SerialException:
    ser = None
    print("Warning: Could not connect to RFID reader on COM5")

user_list = {
    'Demo Member': '00 00 00 00'
}

class Library:
    def check_overdue_books(self):
        overdue_users = []
        today = datetime.now()
        
        for transaction in self.transactions:
            if transaction['return_date'] is None:
                borrow_date = datetime.strptime(transaction['borrow_date'], '%Y-%m-%d %H:%M:%S.%f')
                days_overdue = (today - borrow_date).days
                
                if days_overdue > 30:
                    for name, uid in user_list.items():
                        if uid == transaction['member_uid']:
                            overdue_users.append(name)
                            break
                            
        return overdue_users

    def __init__(self):
        self.books = self.load_books()
        self.transactions = self.load_transactions()

    def load_books(self):
        try:
            with open('books.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def load_transactions(self):
        try:
            with open('transactions.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_books(self):
        with open('books.json', 'w') as f:
            json.dump(self.books, f)

    def save_transactions(self):
        with open('transactions.json', 'w') as f:
            json.dump(self.transactions, f)

    def add_book(self, title, author, isbn, sn):
        book = {
            'title': title,
            'author': author,
            'isbn': isbn,
            'available': True,
            'sn': sn
        }
        self.books.append(book)
        self.save_books()
        return f'Book "{title}" added successfully!'
    def search_book(query, self):
        query = query.lower()
        results = []
        for book in self.books:
            if (query in book['title'].lower() or
               query in book['author'].lower() or
               query in book['isbn'].lower()
                ):
                results.append(book)
        return results
            

    def view_books(self):
        sorted_books = sorted(self.books, key=lambda book: book['title'].lower())
        return sorted_books

    def borrow_book(self, member_uid, book_index):
        if book_index < 0 or book_index >= len(self.books):
            return "Invalid book index."

        sorted_books = sorted(self.books, key=lambda book: book['title'].lower())
        book = sorted_books[book_index]
        if not book['available']:
            return f'Sorry, "{book["title"]}" is currently not available.'

        transaction = {
            'member_uid': member_uid,
            'book_title': book['title'],
            'borrow_date': str(datetime.now()),
            'return_date': None
        }
        for b in self.books:
            if b['title'] == book['title']:
                b['available'] = False
                break
        self.transactions.append(transaction)
        self.save_books()
        self.save_transactions()
        for k, v in user_list.items():
            if v == member_uid:
                name = k
        return f'Book "{book["title"]}" borrowed by {name}.'

    def return_book(self, member_uid, book_title):
        return_date = str(datetime.now())
        for transaction in self.transactions:
            if (transaction['book_title'] == book_title and 
                transaction['member_uid'] == member_uid and 
                transaction['return_date'] is None):
                
                transaction['return_date'] = return_date
                for b in self.books:
                    if b['title'] == book_title:
                        b['available'] = True
                        break
                self.save_books()
                self.save_transactions()
                for k, v in user_list.items():
                    if v == member_uid:
                        name = k
                        return f'Book "{book_title}" returned by {name}.'
        return f'No active transaction found for "{book_title}".'

    def remove_book(self, book_index):
        if book_index < 0 or book_index >= len(self.books):
            return "Invalid book index."

        removed_book = self.books.pop(book_index)
        self.save_books()
        return f'Book "{removed_book["title"]}" removed successfully!'

    def history(self):
        history_list = []
        for transaction in self.transactions:
            return_date = transaction['return_date'] if transaction['return_date'] else "Not Returned"
            for k, v in user_list.items():
                if v == transaction['member_uid']:
                    name = k
            history_list.append(f"{transaction['book_title']} borrowed by {name} on {transaction['borrow_date']} and returned on {return_date}.")
        return history_list
    
    def export_data(self):
        # Prepare data for export
        books_data = pd.DataFrame(self.books)
        transactions_data = pd.DataFrame(self.transactions)
        users_data = pd.DataFrame(list(user_list.items()), columns=['Name', 'UID'])

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        with pd.ExcelWriter('library_data.xlsx', engine='openpyxl') as writer:
            books_data.to_excel(writer, sheet_name='Books', index=False)
            transactions_data.to_excel(writer, sheet_name='Transactions', index=False)
            users_data.to_excel(writer, sheet_name='Users', index=False)

        return "Data exported successfully to 'library_data.xlsx'."

class LibraryApp:
    def __init__(self, root):
        self.library = Library()
        self.root = root
        self.root.title("Library Management System")
        
        self.member_uid = ''
        
        self.create_widgets()

    def create_widgets(self):
        
        tk.Label(self.root, text="Library Management System", font=("Arial", 24)).grid(row=1, column=0, columnspan=2, pady=20)

        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Create buttons with grid layout
        button_width = 10  # Set a fixed width for buttons
        button_height = 5  # Set a fixed height for buttons

        tk.Button(self.root, text="View Books", command=self.view_books, font=("Arial", 14), bg="#4CAF50", fg="white", width=button_width, height=button_height).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="Add Book (Admin only)", command=self.add_book, font=("Arial", 14), bg="#2196F3", fg="white", width=button_width, height=button_height).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="Borrow Book", command=self.borrow_book, font=("Arial", 14), bg="#FFC107", fg="black", width=button_width, height=button_height).grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="Return Book", command=self.return_book, font=("Arial", 14), bg="#FF5722", fg="white", width=button_width, height=button_height).grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="Remove Book (Admin only)", command=self.remove_book, font=("Arial", 14), bg="#9C27B0", fg="white", width=button_width, height=button_height).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="View History (Admin only)", command=self.view_history, font=("Arial", 14), bg="#3F51B5", fg="white", width=button_width, height=button_height).grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="View User List (Admin only)", command=self.view_user_list, font=("Arial", 14), bg="#FF9800", fg="white", width=button_width, height=button_height).grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="Add User (Admin only)", command=self.add_user, font=("Arial", 14), bg="#8BC34A", fg="white", width=button_width, height=button_height).grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="Remove User (Admin only)", command=self.remove_user, font=("Arial", 14), bg="#FF5722", fg="white", width=button_width, height=button_height).grid(row=6, column=0, padx=5, pady=5, sticky="ew")  # New button added
        tk.Button(self.root, text="Apply Fines (Admin only)", command=self.apply_fines, font=("Arial", 14), bg="#607D8B", fg="white", width=button_width, height=button_height).grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="Exit", command=self.root.quit, font=("Arial", 14), bg="#F44336", fg="white", width=10, height=5).grid(row=7, column=0, columnspan=1, padx=5, pady=5, sticky="ew")
        tk.Button(self.root, text="Export Data (Admin only)", command=self.export_data, font=("Arial", 14), bg="#FF9800", fg="white", width=button_width, height=button_height).grid(row=7, column=1, padx=5, pady=5, sticky="ew")

    def export_data(self):
        if not self.access():
            messagebox.showwarning("Access Denied", "You do not have permission to export data.")
            return
        
        message = self.library.export_data()
        messagebox.showinfo("Export Data", message)

    def toggle_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def end_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

    def read_rfid(self):
        if ser and ser.in_waiting > 0:
            uid = ser.readline().decode('utf-8').strip()
            return uid
        return None

    def access(self):
        # Bypass RFID check for testing
        return True

    def view_books(self):
        books = self.library.view_books()
        book_list = "\n".join([f"{i + 1}. {book['title']} by {book['author']} (ISBN: {book['isbn']}) - {'Available' if book['available'] else 'Not Available'}" for i, book in enumerate(books)])
        messagebox.showinfo("Available Books", book_list if book_list else "No books available.")

    def add_book(self):
        if not self.access():
            messagebox.showwarning("Access Denied", "You do not have permission to add books.")
            return
        
        title = simpledialog.askstring("Input", "Enter book title:")
        if not title:
            return
            
        author = simpledialog.askstring("Input", "Enter book author:")
        if not author:
            return
            
        isbn = simpledialog.askstring("Input", "Enter book ISBN:")
        if not isbn:
            return
            
        sn = simpledialog.askstring("Input", "Is the book a part of a series? (Enter series name or leave blank):")
        
        message = self.library.add_book(title, author, isbn, sn)
        messagebox.showinfo("Add Book", message)

        

    def borrow_book(self):
        self.member_uid = self.read_rfid()
        if not self.member_uid:
            messagebox.showwarning("Error", "No RFID tag detected")
            return
            
        name = ""
        for k, v in user_list.items():
            if v == self.member_uid:
                name = k
                break
        book_index = simpledialog.askinteger("Input", "Enter the book index to borrow:") - 1
        message = self.library.borrow_book(self.member_uid, book_index)
        messagebox.showinfo("Borrow Book", message)

    def return_book(self):
        self.member_uid = self.read_rfid()
        name = ""
        for k, v in user_list.items():
            if v == self.member_uid:
                name = k
        book_title = simpledialog.askstring("Input", "Enter the title of the book to return:")
        message = self.library.return_book(self.member_uid, book_title)
        messagebox.showinfo("Return Book", message)

    def remove_book(self):
        if not self.access():
            messagebox.showwarning("Access Denied", "You do not have permission to remove books.")
            return
        
        book_index = simpledialog.askinteger("Input", "Enter the book index to remove:") - 1
        message = self.library.remove_book(book_index)
        messagebox.showinfo("Remove Book", message)

    def view_history(self):
        if not self.access():
            messagebox.showwarning("Access Denied", "You do not have permission to view history.")
            return
        
        history = self.library.history()
        history_list = "\n".join(history) if history else "No transaction history available."
        messagebox.showinfo("Transaction History", history_list)

    def view_user_list(self):
        if not self.access():
            messagebox.showwarning("Access Denied", "You do not have permission to view user list.")
            return
        
        user_list_str = "\n".join([f"{name}: {uid}" for name, uid in user_list.items()])
        messagebox.showinfo("User List", user_list_str)

    def apply_fines(self):
        if not self.access():
            messagebox.showwarning("Access Denied", "You do not have permission to apply fines.")
            return
            
        overdue_users = self.library.check_overdue_books()
        if not overdue_users:
            messagebox.showinfo("Fines", "No users have overdue books.")
            return
            
        for user in overdue_users:
            for name in user_list:
                if name == user:
                    user_list[name] += " (FINE)"
                    break
                    
        with open('users.json', 'w') as f:
            json.dump(user_list, f)
            
        messagebox.showinfo("Fines Applied", f"Fines applied to {len(overdue_users)} users.")

    def remove_user(self):
        if not self.access():
            messagebox.showwarning("Access Denied", "You do not have permission to remove users.")
            return
            
        name = simpledialog.askstring("Input", "Enter user name to remove:")
        if not name or name not in user_list:
            messagebox.showwarning("Error", "User not found.")
            return
            
        del user_list[name]
        
        # Save to JSON file
        with open('users.json', 'w') as f:
            json.dump(user_list, f)
        
        messagebox.showinfo("Success", f"User {name} removed successfully!")
        
    def add_user(self):
        if not self.access():
            messagebox.showwarning("Access Denied", "You do not have permission to add users.")
            return
            
        name = simpledialog.askstring("Input", "Enter user name:")
        if not name:
            return
            
        uid = simpledialog.askstring("Input", "Enter user UID:")
        if not uid:
            return
            
        # Add to in-memory dictionary
        user_list[name] = uid
        
        # Save to JSON file
        try:
            with open('users.json', 'w') as f:
                json.dump(user_list, f)
            messagebox.showinfo("Success", f"User {name} added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

