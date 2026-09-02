# Importing necessary modules
import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

# Connecting to Database
connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
    'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT)'
)

# Insert initial data if table empty
cursor.execute("SELECT COUNT(*) FROM Library")
if cursor.fetchone()[0] == 0:
    sample_books = [
        ('The Great Gatsby', 'BK001', 'F. Scott Fitzgerald', 'Available', 'N/A'),
        ('To Kill a Mockingbird', 'BK002', 'Harper Lee', 'Issued', 'C1001'),
        ('1984', 'BK003', 'George Orwell', 'Available', 'N/A'),
        ('The Hobbit', 'BK004', 'J.R.R. Tolkien', 'Issued', 'C1002'),
        ('Pride and Prejudice', 'BK005', 'Jane Austen', 'Available', 'N/A'),
    ]
    cursor.executemany("INSERT INTO Library VALUES (?, ?, ?, ?, ?)", sample_books)
    connector.commit()

# Tooltip helper
class CreateToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # ms
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
    def enter(self, event=None):
        self.schedule()
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1,
                      wraplength = self.wraplength)
        label.pack(ipadx=1)
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

# Functions
def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?')
    if not Cid:
        mb.showerror('Issuer ID cannot be zero!', 'Can\'t keep Issuer ID empty, it must have a value')
    else:
        return Cid

def display_records():
    clear_fields()
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM Library ORDER BY BK_NAME")
    data = cursor.fetchall()
    count = 0
    for record in data:
        if count % 2 == 0:
            tree.insert('', END, values=record, tags=('evenrow',))
        else:
            tree.insert('', END, values=record, tags=('oddrow',))
        count += 1

def clear_fields():
    bk_status.set('Available')
    for var in [bk_name, bk_id, author_name, card_id]:
        var.set('')
    bk_id_entry.config(state='normal')
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass

def add_record():
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    else:
        card_id.set('N/A')
    surety = mb.askyesno('Are you sure?',
                'Are you sure this is the data you want to enter?\nPlease note that Book ID cannot be changed later.')
    if surety:
        try:
            connector.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get()))
            connector.commit()
            display_records()
            mb.showinfo('Record added', 'The new record was successfully added.')
        except sqlite3.IntegrityError:
            mb.showerror('Book ID already exists!',
                         'The Book ID you entered is already in the database. Please use a unique ID.')

def view_record():
    if not tree.focus():
        mb.showerror('Select a row!', 'Please select a row to view its details.')
        return
    selected = tree.focus()
    values = tree.item(selected)['values']
    bk_id.set(values[1])
    bk_name.set(values[0])
    author_name.set(values[2])
    bk_status.set(values[3])
    card_id.set(values[4])

def update_record():
    def update():
        if bk_status.get() == 'Issued':
            card_id.set(issuer_card())
        else:
            card_id.set('N/A')
        cursor.execute('UPDATE Library SET BK_NAME=?, BK_STATUS=?, AUTHOR_NAME=?, CARD_ID=? WHERE BK_ID=?',
                       (bk_name.get(), bk_status.get(), author_name.get(), card_id.get(), bk_id.get()))
        connector.commit()
        display_records()
        edit_btn.destroy()
        bk_id_entry.config(state='normal')
        clear.config(state='normal')
    view_record()
    bk_id_entry.config(state='disable')
    clear.config(state='disable')
    edit_btn = Button(left_frame, text='Update Record', font=btn_font, bg=btn_hlb_bg, width=20, command=update)
    edit_btn.place(x=50, y=375)

def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item to delete.')
        return
    current_item = tree.focus()
    values = tree.item(current_item)['values']
    cursor.execute('DELETE FROM Library WHERE BK_ID=?', (values[1],))
    connector.commit()
    display_records()
    mb.showinfo('Done', 'Record deleted successfully.')

def delete_inventory():
    if mb.askyesno('Are you sure?', 'Delete the entire inventory? This cannot be undone.'):
        cursor.execute('DELETE FROM Library')
        connector.commit()
        display_records()

def change_availability():
    if not tree.selection():
        mb.showerror('Error!', 'Please select a book.')
        return
    current_item = tree.focus()
    values = tree.item(current_item)['values']
    BK_id = values[1]
    BK_status = values[3]
    if BK_status == 'Issued':
        surety = mb.askyesno('Confirm Return', 'Has the book been returned?')
        if surety:
            cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=? WHERE BK_ID=?', ('Available', 'N/A', BK_id))
            connector.commit()
    else:
        cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=? WHERE BK_ID=?', ('Issued', issuer_card(), BK_id))
        connector.commit()
    display_records()

# GUI Variables
lf_bg = '#dbeeff'
rtf_bg = '#aed6f1'
rbf_bg = '#85c1e9'
btn_hlb_bg = '#2980b9'
lbl_font = ('Segoe UI', 12)
entry_font = ('Segoe UI', 11)
btn_font = ('Segoe UI', 12)

# Main Window
root = Tk()
root.title('Library Management System')
root.geometry('1020x540')
root.resizable(True, True)


Label(root, text='📚 LIBRARY MANAGEMENT SYSTEM 📚', font=("Segoe UI", 18, 'bold'),
      bg=btn_hlb_bg, fg='white', pady=10).pack(side=TOP, fill=X)

# StringVars
bk_status = StringVar(value='Available')
bk_name = StringVar()
bk_id = StringVar()
author_name = StringVar()
card_id = StringVar()

# Frames
left_frame = Frame(root, bg=lf_bg)
left_frame.place(x=0, y=55, relwidth=0.3, relheight=0.9)
RT_frame = Frame(root, bg=rtf_bg)
RT_frame.place(relx=0.3, y=55, relheight=0.18, relwidth=0.7)
RB_frame = Frame(root, bg=rbf_bg)
RB_frame.place(relx=0.3, rely=0.25, relheight=0.7, relwidth=0.7)

# Left Frame
Label(left_frame, text='Book Name', bg=lf_bg, font=lbl_font).place(x=90, y=15)
Entry(left_frame, width=25, font=entry_font, textvariable=bk_name).place(x=45, y=40)
Label(left_frame, text='Book ID', bg=lf_bg, font=lbl_font).place(x=110, y=75)
bk_id_entry = Entry(left_frame, width=25, font=entry_font, textvariable=bk_id)
bk_id_entry.place(x=45, y=100)
Label(left_frame, text='Author Name', bg=lf_bg, font=lbl_font).place(x=90, y=135)
Entry(left_frame, width=25, font=entry_font, textvariable=author_name).place(x=45, y=160)
Label(left_frame, text='Status', bg=lf_bg, font=lbl_font).place(x=125, y=195)
OptionMenu(left_frame, bk_status, 'Available', 'Issued').place(x=90, y=220)

submit = Button(left_frame, text='Add new record', font=btn_font, bg=btn_hlb_bg, fg='white', width=20, command=add_record)
submit.place(x=50, y=270)
clear = Button(left_frame, text='Clear fields', font=btn_font, bg=btn_hlb_bg, fg='white', width=20, command=clear_fields)
clear.place(x=50, y=320)

CreateToolTip(submit, "Add a new book to the database")
CreateToolTip(clear, "Clear all input fields")

# Right Top Frame
Button(RT_frame, text='Delete record', font=btn_font, bg=btn_hlb_bg, fg='white', width=15, command=remove_record).place(x=10, y=25)
Button(RT_frame, text='Delete all', font=btn_font, bg=btn_hlb_bg, fg='white', width=15, command=delete_inventory).place(x=180, y=25)
Button(RT_frame, text='Update book', font=btn_font, bg=btn_hlb_bg, fg='white', width=15, command=update_record).place(x=350, y=25)
Button(RT_frame, text='Change Availability', font=btn_font, bg=btn_hlb_bg, fg='white', width=18, command=change_availability).place(x=520, y=25)

# Right Bottom Frame
Label(RB_frame, text='BOOK INVENTORY', bg=rbf_bg, font=("Segoe UI", 14, 'bold')).pack(side=TOP, fill=X)

tree = ttk.Treeview(RB_frame, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID'), show='headings')
tree.heading('Book Name', text='Book Name')
tree.heading('Book ID', text='Book ID')
tree.heading('Author', text='Author')
tree.heading('Status', text='Status')
tree.heading('Issuer Card ID', text='Issuer Card ID')

tree.column('Book Name', width=220, anchor='center')
tree.column('Book ID', width=90, anchor='center')
tree.column('Author', width=150, anchor='center')
tree.column('Status', width=100, anchor='center')
tree.column('Issuer Card ID', width=100, anchor='center')

tree.pack(fill=BOTH, expand=1)
tree.bind("<Double-1>", lambda e: view_record())

# Treeview styles
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
    background="#f0f0f0",
    foreground="black",
    rowheight=25,
    fieldbackground="#f0f0f0",
    font=('Segoe UI', 11))
style.map('Treeview', background=[('selected', '#3498db')])

tree.tag_configure('oddrow', background="lightblue")
tree.tag_configure('evenrow', background="white")

display_records()

root.mainloop()
