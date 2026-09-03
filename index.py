import requests
import urllib.request as urllib2
from bs4 import BeautifulSoup
from tkinter import messagebox, Tk, Label, Button, filedialog
from TowerPy import main


def get_date():
    try:
        r = requests.get('https://www.calendardate.com/todays.html')
        soup = BeautifulSoup(r.text, 'html.parser')

        date_str = soup.find_all(id='tprg')[6].get_text()
        todays_date = date_str.replace('-', '')
        todays_date = todays_date.replace(' ', '')

        return todays_date
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get the date: {e}")
        return None


def connection_check():
    try:
        urllib2.urlopen('https://google.com.co', timeout=1)
        return True
    except urllib2.URLError:
        return False


def show_main_interface():
    # Create main interface
    main_window = Tk()
    main_window.title("TowerPy Interface")

    Label(main_window, text="Enjoy free version").pack(pady=10)
    Label(main_window, text='Current results path: "c:\\U\\I\\TowerPy\\Results"').pack()
    Label(main_window, text='Current ATP solver: "C:\\ATPSolvers\\PyTP Solver.bat"').pack()
    Label(main_window, text='Earthing Data Excel: C:\\U\\I\\T\\Earthing_Data\\Earthing Data.xlsx').pack()

    Button(main_window, text="Load .atp File", command=lambda: filedialog.askopenfilename(filetypes=[("ATP files", "*.atp")])).pack(pady=5)
    Button(main_window, text="Choose Results Path", command=lambda: filedialog.askdirectory()).pack(pady=5)
    Button(main_window, text="Choose ATP Solver", command=lambda: filedialog.askopenfilename(filetypes=[("Batch files", "*.bat")])).pack(pady=5)
    Button(main_window, text="Choose Earthing Data Excel File", command=lambda: filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])).pack(pady=5)
    Button(main_window, text="Exit", command=main_window.destroy).pack(pady=10)

    main_window.mainloop()


def main_program():
    if connection_check():
        tlimit = 20500720
        current_date = get_date()

        if current_date:
            try:
                current_date = int(current_date)
                if current_date <= tlimit:
                    print('Enjoy free version')
                    show_main_interface()
                else:
                    messagebox.showinfo("Info", "Your program has expired")
            except ValueError as ve:
                messagebox.showerror("Error", f"Invalid date format: {ve}")
        else:
            messagebox.showinfo("Error", "Could not retrieve the current date")
    else:
        messagebox.showinfo("Error", "Check your internet connection")


if __name__ == "__main__":
    try:
        main_program()
    except Exception as e:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")
        root.destroy()
