from tkinter import *
from tkinter import messagebox
import os
import datetime
import calendar
import json
import tkcalendar
from shutil import rmtree

# Simple menu
class My_Menu(Menu):
    def __init__(self, parent, controller, *args, **kwargs):
        Menu.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        self.employee = Menu(self, tearoff=0)
        self.file = Menu(self, tearoff=0)
        self.archive = Menu(self, tearoff=0)
        self.actions = Menu(self, tearoff=0)
        self.exit = Menu(self, tearoff=0)

        self.show_all = BooleanVar()
        self.show_all.set(False)

        self.add_cascade(label="Harmonogram", menu=self.file)
        self.add_cascade(label="Pracownicy", menu=self.employee)
        self.add_cascade(label="Archiwum", menu=self.archive)
        self.add_cascade(label="Akcje", menu=self.actions)
        self.add_command(label="Wyjście", command = lambda: self.on_exit())

        # Employee menu
        self.employee.add_command(label="Dodaj pracownika", command = self.add_employee)
        self.employee.add_command(label="Zwolnij pracownika", command = self.fire_employee)
        self.employee.add_command(label="Edytuj wymiar urlopu", command = self.edit_holiday)
        self.employee.add_command(label="Edytuj imię i nazwisko", command = self.edit_employee)
        self.employee.add_command(label="Edytuj datę zatrudnienia/zwolnienia", command = self.edit_dates)
        self.employee.add_command(label="Odzwolnij pracowników", command = self.unfire_employee)
        self.employee.add_command(label="Usuń pracownika",underline = 1, command =  self.del_employee, foreground="red")

        #File menu
        self.file.add_command(label="Dodaj harmonogram", command = self.add_schedule)
        self.file.add_command(label="Edytuj harmonogramy", command = self.edit_schedule)
        self.file.add_command(label="Edytuj święta", command = self.add_holiday)

        # Archive menu
        self.archive.add_checkbutton(label="Wyświetlaj zwolnionych pracowników", onvalue=1, offvalue=0, variable=self.show_all, command=self.change_show)

        # actions menu
        self.actions.add_command(label="Przelicz urlopy", command = self.verify_holiday)

    # add an employee and set it to the current employee
    def add_employee(self):

        page = self.controller.get_page("Em_App")

        curr_year = page.month.selected_year.get()

        pop_up = Toplevel(background = self.controller.bg)
        pop_up.iconbitmap(r"./data/ecp.ico")
        pop_up.title("Dodawanie pracownika")
        pop_up.focus_set()
        var = StringVar()

        for i in range(12):
            pop_up.grid_rowconfigure(i, weight = 1)
        for i in range(5):
            pop_up.grid_columnconfigure(i, weight = 1)

        ttk.Label(pop_up, text = "Imię i nazwisko").grid(row = 1, column = 1, sticky=NSEW, pady=5, padx=5)
        ttk.Label(pop_up, text = "Roczny wymiar urlopu: ").grid(row = 3, column = 1, sticky=NSEW, pady=5, padx=5)
        ttk.Label(pop_up, text = "Pozostały urlop z " + str(int(curr_year - 1)) + ":").grid(row = 5, column = 1, sticky=NSEW, pady=5, padx=5)
        ttk.Label(pop_up, text = "Pozostały urlop z " + str(int(curr_year - 2)) + ":").grid(row = 7, column = 1, sticky=NSEW, pady=5, padx=5)
        ttk.Label(pop_up, text = "Data zatrudnienia (dd/mm/rrrr)").grid(row = 9, column = 1, sticky=NSEW, pady=5, padx=5)

        e1 = ttk.Entry(pop_up, justify = "center", width = 20, textvariable = var)  # employee name and surname
        e2 = ttk.Entry(pop_up, justify = "center", width = 20)                      # yearly holiday
        e3 = ttk.Entry(pop_up, justify = "center", width = 20)                      # holiday -1 year
        e4 = ttk.Entry(pop_up, justify = "center", width = 20)                      # holiday -2 year
        e5 = ttk.Entry(pop_up, justify = "center", width = 20)                      # hire date
        

        ok = ttk.Button(pop_up, text = "Zapisz", command = lambda: save())

        e2.insert(END, '26')    # default values
        e3.insert(END, '0')
        e4.insert(END, '0')
        e5.insert(END, datetime.datetime.now().strftime("%d/%m/%Y"))

        e1.grid(row = 1, column = 3, sticky=NSEW, pady=5, padx=5)
        e2.grid(row = 3, column = 3, sticky=NSEW, pady=5, padx=5)
        e3.grid(row = 5, column = 3, sticky=NSEW, pady=5, padx=5)
        e4.grid(row = 7, column = 3, sticky=NSEW, pady=5, padx=5)
        e5.grid(row = 9, column = 3, sticky=NSEW, pady=5, padx=5)
        ok.grid(row = 11, column = 1 ,columnspan = 3, sticky = NSEW)

        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        pop_up.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - pop_up.winfo_width()/2, y + 200))

        def autocapitalize(*arg):
            var.set(var.get().title())

        var.trace("w", autocapitalize)

        pop_up.focus_force()
        e1.focus_set()

        def save():
            answer = e1.get()
            if answer != "":
                os.mkdir('./Pracownicy/' + e1.get())
                with open('./Pracownicy/' + e1.get() + '/' + str(curr_year) + '.json', 'w') as f:
                    to_save = {
                    "yearly_holiday" : e2.get(),
                    str("holiday_left_" + str(curr_year - 1)) : e3.get(),
                    str("holiday_left_" + str(curr_year - 2)) : e4.get(),
                    "holiday" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "worked" : {"1" : {}, "2" : {}, "3" : {}, "4" : {}, "5" : {}, "6" : {}, "7" : {}, "8" : {}, "9" : {}, "10" : {}, "11" : {}, "12" : {}}
                    }
                    json.dump(to_save, f, indent=4, ensure_ascii=False)

                # load yearly summary
                with open("./Roczne podsumowanie/" + str(curr_year) + ".json", "r") as f:
                    x = json.load(f)

                x["employees"][e1.get()] = {
                        "work" : 12 * [0],
                        "holiday" : 12 * [0],
                        "yearly_holiday" : e2.get(),
                        str("holiday_left_" + str(curr_year - 1)) : e3.get(),
                        str("holiday_left_" + str(curr_year - 2)) : e4.get(),
                    }

                # yearly summary file
                with open("./Roczne podsumowanie/" + str(curr_year) + ".json", "w") as f:
                    json.dump(x, f, indent=4, ensure_ascii=False)

                # settings file
                with open('./Pracownicy/' + e1.get() + '/settings.json', 'w') as f:
                    to_save = {
                        "hire_date" : e5.get(),
                        "fire_date" : ''
                    }
                    json.dump(to_save, f, indent=4, ensure_ascii=False)

            page.employee.reload_list()
            page.employee.change_combo()
            page.employee.read_data()
            pop_up.destroy()
            self.controller.focus_set()
            self.controller.set_status("Dodano pracownika "+ e1.get())

    # deletes a file of the employee
    def del_employee(self):
        page = self.controller.get_page("Em_App")
        name = page.employee.name.get()
        
        if len(page.employee.names) == 1:
            messagebox.showerror("Nie możność", "Nie można usunąć jedynego pracownika. \nAby usunąć obecnego pracownika musisz dodać nowego.", parent=self.controller)
        else:
            messagebox.showwarning("Ostrzeżenie", "Usuwając pracownika usunięte zostaną wszystkie jego dane. Po usunięciu nie będzie możliwe odzyskanie danych pracownika", parent=self.controller)

            answer = messagebox.askyesno("Usun pracownika", str("Usunąć pracownika: \n" + name), parent=self.controller)
            if answer:
                for file in os.listdir("./Roczne podsumowanie/"):
                    if str(file).endswith('.json'):
                        with open("./Roczne podsumowanie/"+ str(file), "r") as f:
                            x = json.load(f)
                        with open("./Roczne podsumowanie/"+ str(file), "w") as f:
                            try:
                                x["employees"].pop(name)
                            # if employee doesnt exist in summary
                            except KeyError:
                                pass
                            json.dump(x, f, indent=4, ensure_ascii=False)

                rmtree('./Pracownicy/' + name, ignore_errors=True)

                page = self.controller.get_page("Em_App")
                page.employee.reload_list()
                page.employee.change_combo()
                page.employee.read_data()
                self.controller.set_status(f"Trwale usunięto pracownika {name}")
 

    # add an _ on the begining of the file
    def fire_employee(self):
        page = self.controller.get_page("Em_App")
        curr_empl = str(page.employee.name_box.get())
        if curr_empl.startswith("[Z]"):
            messagebox.showerror("Nie możność", "Nie można zwolnić zwolnionego pracownika", parent=self.controller)
            return

        self.fire_date = ""

        def save():
            global fire_date_
            os.rename("./Pracownicy/" + curr_empl, "./Pracownicy/_" + curr_empl)

            for file in os.listdir("./Roczne podsumowanie/"):
                if str(file).endswith('.json'):
                    with open("./Roczne podsumowanie/"+ str(file), "r") as f:
                        x = json.load(f)
                    with open("./Roczne podsumowanie/"+ str(file), "w") as f:
                        try:
                            x["employees"][str('_' + curr_empl)] = x["employees"].pop(curr_empl)
                        # if employee doesnt exist in summary
                        except KeyError:
                            pass
                        json.dump(x, f, indent=4, ensure_ascii=False)

            with open('./Pracownicy/_' + curr_empl + "/settings.json", "r") as f:
                settings = json.load(f)
            settings["fire_date"] = self.fire_date
            with open('./Pracownicy/_' + curr_empl + "/settings.json", "w") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            
            page.employee.reload_list()
            page.employee.name_box.current(0)
            page.employee.change_combo()
            page.employee.read_data()
            top.destroy()
            self.controller.focus_set()
            self.controller.set_status(f"Zwolniono pracownika {curr_empl} z datą {self.fire_date}")

        def color_day(e):  
            global fire_date_        
            date_patterns = ['%m/%d/%y', "%d.%m.%Y"]
            for pattern in date_patterns:
                try:
                    x_date = datetime.datetime.strptime(cal.get_date(), pattern).date()
                except:
                    pass
            self.fire_date = str(x_date.strftime("%d/%m/%Y"))



        answer = messagebox.askyesno("Zwolnij pracownika", str("Zwolnić pracownika: \n" + curr_empl))
        if answer:

            messagebox.showinfo("Zwalnianie pracownika", "Wybierz teraz datę zwolnienia pracownika")

            top = Toplevel(background = self.controller.bg)
            top.title("Data zwolnienia")
            top.focus_set()
            cal = tkcalendar.Calendar(top, selectmode='day')
            cal.bind("<<CalendarSelected>>", color_day)
            cal.pack(fill=BOTH, expand=True)
            ok = ttk.Button(top, text="Zapisz", command = lambda: save())
            ok.pack(fill=X, expand=True)
            x = self.controller.winfo_x()
            y = self.controller.winfo_y()
            top.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - top.winfo_width()/2, y + 200))
        

    # add a working schedule for current month
    def add_schedule(self):

        # save button function
        def save():

            # json dict for rota
            to_save = {
            "default":False,
            "employees":[],
            "days":{},
            "days_off":[],     
            }

            #get current employee
            page = self.controller.get_page("Em_App")
            curr_employee = page.employee.name.get()
            empl_list = [multi_select.get(i) for i in multi_select.curselection()]

            d = page.month.get_date()
            date = datetime.datetime(day = 1, month = d[0], year = d[1]) 
            lenght = calendar.monthrange(date.year, date.month)[1] + 1     

            for day in range(1, lenght):
                to_save["days"][day] = entries[day].get()
                if labels[day].cget("background") == "red":
                    to_save["days_off"].append(day)
            
            # add current employee to employees
            for empl in empl_list:
                to_save["employees"].append(empl)

            # load an existing rota to a dict
            with open("./Harmonogramy/" + str(page.month.get_date()[1]) + "/" + str(page.month.get_date()[0]) + ".json", "r") as f:
                data = json.load(f)

            # pop the current employee from custom_rota
            if curr_employee in data["custom_rota"]:
                for empl in empl_list:
                    try:
                        data["custom_rota"].remove(empl)
                    except ValueError:
                        pass

            # check if current employee is in any rota
            # or if any rota matches current employee's rota
            is_same = False
            for rota in data["harmonograms"]:
                if rota["default"] != True:
                    if to_save["days_off"] == rota["days_off"]:
                        if to_save["days"] == rota["days"]:
                            for empl in empl_list:
                                rota["employees"].append(empl)
                                data["custom_rota"].append(empl)
                            is_same = True
                            break
            if is_same == False:
                data["harmonograms"].append(to_save)
                for empl in empl_list:
                    data["custom_rota"].append(empl)

            with open("./Harmonogramy/" + str(page.month.get_date()[1]) + "/" + str(page.month.get_date()[0]) + ".json", "w") as f:
                json.dump(data, f, indent=4)


            pop_up.destroy()
            self.controller.focus_set()
            self.controller.set_status("Dodano harmonogram dla " + ",".join([a for a in empl_list]))

        # colorize the tile when clicked on
        def color(row):
            if labels[row].cget("background") == "red":
                labels[row].configure(background = "SystemButtonFace")
                entries[row].delete(0, 10)
            else:
                labels[row].configure(background = "red")
                entries[row].delete(0, 10)

        # pop_up settings
        page = self.controller.get_page("Em_App")

        pop_up = Toplevel(background = self.controller.bg)
        pop_up.iconbitmap(r"./data/ecp.ico")
        pop_up.title("Dodawanie harmonogramu")
        pop_up.focus_set()

        pop_up.grid_columnconfigure(0, weight = 1)
        pop_up.grid_columnconfigure(3, weight = 1)

        date = datetime.datetime(day = 1, month = page.month.get_date()[0], year = page.month.get_date()[1])


        ttk.Label(pop_up, text = str(page.month.selected_month.get()) + "/" + str(page.month.selected_year.get()), font = "Arial 8 bold").grid(row = 0, column = 1, sticky = N, columnspan = 2)
        multi_select = Listbox(pop_up, selectmode=MULTIPLE, height= len(page.employee.names), justify=CENTER)
        for name in page.employee.names:
            multi_select.insert(END, name)
        multi_select.grid(column = 3, row = 2, rowspan = (len(page.employee.names) + 4))
        ttk.Label(pop_up, text="Dla kogo:").grid(row=1, column=3)

        ttk.Button(pop_up, text = "Zapisz", command = save).grid(row = 40, column = 1, columnspan = 3, sticky = NSEW)
        labels = {}
        entries = {}

        # generate table
        for row in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
            entries[row] = ttk.Entry(pop_up, width = 12)
            entries[row].grid(row=row, column = 2)
        
        the_day = datetime.datetime.weekday(date)
        for day in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
            def make_lambda(x):
                    return lambda ev: color(x)
            if (the_day) == 5 or (the_day) == 6:
                labels[day] = Label(pop_up, text=day, background="red")
            else:
               labels[day] = Label(pop_up, text=day)
               entries[day].insert(0, "7-15")
            
            labels[day].grid(row=day, column=1)
            labels[day].bind("<Button-1>", make_lambda(day))
            date += datetime.timedelta(days = 1)
            the_day = datetime.datetime.weekday(date)

        pop_up.focus_force()
        entries[1].focus_set()
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        pop_up.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - pop_up.winfo_width()/2, y + 10))

    # edit employee's holiday
    def edit_holiday(self):

        page = self.controller.get_page("Em_App")
        date = page.month.get_date()

        with open("./Pracownicy/"+ page.employee.name.get() + "/" + str(date[1]) + ".json", "r") as f:
            data = json.load(f)
        
        pop_up = Toplevel(background = self.controller.bg)
        pop_up.iconbitmap(r"./data/ecp.ico")
        pop_up.title("Edytowanie pracownika")
        pop_up.focus_set()

        for i in range(6):
            pop_up.grid_rowconfigure(i, weight = 1)
        for i in range(3):
            pop_up.grid_columnconfigure(i, weight = 1)

        ttk.Label(pop_up, text = "Aktualne wartości", font = "Arial 8 bold").grid(row = 0, column = 0, pady=5, padx=5)
        ttk.Label(pop_up, text = "Nowe wartości", font = "Arial 8 bold").grid(row = 0, column = 2, pady=5, padx=5)
        ttk.Label(pop_up, text = "Roczny wymiar urlopu: " + str(data["yearly_holiday"])).grid(row = 1, column = 0, pady=5, padx=5)
        ttk.Label(pop_up, text = "Urlop 1 rok wstecz: " + str(data[str("holiday_left_") + str(date[1] - 1)])).grid(row = 2, column = 0, pady=5, padx=5)
        ttk.Label(pop_up, text = "Urlop 2 lata wstecz: " + str(data[str("holiday_left_") + str(date[1] - 2)])).grid(row = 3, column = 0, pady=5, padx=5)

        e1 = ttk.Entry(pop_up, justify = "center", width = 8)
        e2 = ttk.Entry(pop_up, justify = "center", width = 8)
        e3 = ttk.Entry(pop_up, justify = "center", width = 8)

        ok = ttk.Button(pop_up, text = "Zapisz", command = lambda: save())
        e1.grid(row = 1, column = 2, pady=5, padx=5)
        e2.grid(row = 2, column = 2, pady=5, padx=5)
        e3.grid(row = 3, column = 2, pady=5, padx=5)
        ok.grid(row = 5, column = 0, sticky = NSEW, columnspan = 3)

        pop_up.focus_force()
        e1.focus_set()
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        pop_up.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - pop_up.winfo_width()/2, y + 200))

        def save():
            if e1.get() != "":
                data["yearly_holiday"] = e1.get()
            if e2.get() != "":
                data[str("holiday_left_") + str(date[1] - 1)] = e2.get()
            if e3.get() != "":
                data[str("holiday_left_") + str(date[1] - 2)] = e3.get()

            with open("./Pracownicy/"+ page.employee.name.get() + "/" + str(date[1]) + ".json", "w") as f:
                json.dump(data, f, indent=4)

            pop_up.destroy()    
            self.controller.focus_set()
            page.employee.save_data()
            page.employee.read_data()
            self.controller.set_status(f"Zmieniono wymiar urlopu pracwonika {page.employee.name.get()}")
    
    # edit employee's name
    def edit_employee(self):
        page = self.controller.get_page("Em_App")
        name = page.employee.name.get()
        curr_year = page.month.selected_year.get()

        with open("./Roczne podsumowanie/"+ str(curr_year) + ".json", "r") as f:
            data = json.load(f)
  
        pop_up = Toplevel(background = self.controller.bg)
        pop_up.iconbitmap(r"./data/ecp.ico")
        pop_up.title("Edytowanie pracownika")
        pop_up.focus_set()

        pop_up.grid_columnconfigure(0, weight=1)
        pop_up.grid_columnconfigure(3, weight=1)
        pop_up.grid_rowconfigure(0, weight=1)

        ttk.Label(pop_up, text = "Aktualne imię i nazwisko: ").grid(row=1, column=1, pady=5, padx=5)
        ttk.Label(pop_up, text = name, font = "Arial 8 italic").grid(row = 1, column = 2, pady=5, padx=5)
        ttk.Label(pop_up, text = "Nowe imię i nazwisko: ").grid(row = 2, column = 1, pady=5, padx=5)
        ok = ttk.Button(pop_up, text = "Zapisz", command = lambda: save())

        var = StringVar()
        entry = ttk.Entry(pop_up, text = var)
        entry.grid(row=2, column=2, pady=5, padx=5)
        ok.grid(row=3, column=0, columnspan= 3, sticky=NSEW)

        pop_up.focus_force()
        entry.focus_set()
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        pop_up.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - pop_up.winfo_width()/2, y + 200))

        def autocapitalize(*arg):
            var.set(var.get().title())

        var.trace("w", autocapitalize)

        def save():
            try:
                if entry.get() != "":
                    os.rename("./Pracownicy/" + name, "./Pracownicy/" + entry.get())

                data["employees"][entry.get()] = data["employees"].pop(name)

                for file in os.listdir("./Roczne podsumowanie/"):
                    if str(file).endswith('.json'):
                        with open("./Roczne podsumowanie/"+ str(file), "r") as f:
                            x = json.load(f)
                        with open("./Roczne podsumowanie/"+ str(file), "w") as f:
                            x["employees"][entry.get()] = x["employees"].pop(name)
                            json.dump(x, f, indent=4, ensure_ascii=False)

                page.employee.reload_list()
                page.employee.change_combo()
                page.employee.read_data()
            except Exception as e:
                messagebox.showerror("Ups", e)
            pop_up.destroy()
            self.controller.focus_set()
            self.controller.set_status(f"Zmieniono nazwe pracownika z {name} na {entry.get()}")

    # adds holiday for rota's
    def add_holiday(self):

        page = self.controller.get_page("Em_App")
        name = page.employee.name.get()

        top = Toplevel(background = self.controller.bg)
        top.title("Dodawanie świąt")
        top.focus_set()

        # check if file exists
        if not os.path.isfile('./Harmonogramy/' + 'swieta.json'):
            with open('./Harmonogramy/' + 'swieta.json', 'w') as f:
                to_save = {
                     "2019" : {},
                     "2020" : {}
                }
                json.dump(to_save, f, indent=4)

        # load the existing holiday
        with open('./Harmonogramy/' + 'swieta.json', 'r') as f:
            data = json.load(f)

        # list of added and deleted holidays
        add_holiday = []
        remove_holiday = []

        # color a day, if colored then decolor
        def color_day(e):          
            date_patterns = ['%m/%d/%y', "%d.%m.%Y"]
            for pattern in date_patterns:
                try:
                    x_date = datetime.datetime.strptime(cal.get_date(), pattern).date()
                except:
                    pass
            if cal.get_calevents(x_date):
                remove_holiday.append(x_date)
                cal.calevent_remove(date=x_date)
            else:
                add_holiday.append(x_date)
                cal.calevent_create(x_date, 'X', 'swieto')

        def save():
            # create lists without duplicats
            add = list(set(add_holiday) - set(remove_holiday))
            rmv = list(set(remove_holiday) - set(add_holiday))
            for holiday in add:
                if not str(holiday.year) in data:
                    data[str(holiday.year)] = {}
                if not str(holiday.month) in data[str(holiday.year)]:
                    data[str(holiday.year)][str(holiday.month)] = []
                data[str(holiday.year)][str(holiday.month)].append(holiday.day)
            for not_holiday in rmv:
                if not str(not_holiday.year) in data:
                    data[str(not_holiday.year)] = {}
                if not str(not_holiday.month) in data[str(not_holiday.year)]:
                    data[str(not_holiday.year)][str(not_holiday.month)] = []
                data[str(not_holiday.year)][str(not_holiday.month)].remove(not_holiday.day)

            with open('./Harmonogramy/' + 'swieta.json', 'w') as f:
                json.dump(data, f, indent=4)

            top.destroy()
            self.controller.focus_set()
            self.controller.set_status("Zapisano świętą")

        cal = tkcalendar.Calendar(top, selectmode='day')
        cal.tag_config('swieto', background='blue')
        cal.bind('<<CalendarSelected>>', color_day)
        cal.pack(fill="both", expand=True)
        ttk.Button(top, text="Zapisz", command = save).pack(expand=True)
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        top.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - top.winfo_width()/2, y + 200))

        # add exisiting holiday
        for year in data:
            for month in data[year]:
                for day in data[year][month]:
                    date = datetime.date(year=int(year), month=int(month), day=int(day))
                    cal.calevent_create(date, 'X', 'swieto')

    # edit schedules fore selected employees
    def edit_schedule(self):
        page = self.controller.get_page("Em_App")
        pop_up = Toplevel(background = self.controller.bg)
        pop_up.focus_set()

        index_ = 0
        edit_default = False

        labels = {}
        edited = {}

        def dbclick(e):
            item = listbox.get('active')  #get clicked item
            listbox.delete(0, END)
            with open('./Harmonogramy/' + item.split('/')[1] + '/' + item.split('/')[0] + '.json', 'r') as f:
                curr_schedule = json.load(f)
            for s_id, schedule in enumerate(curr_schedule["harmonograms"]):
                if schedule["employees"]:
                    s = ''
                    for empl in schedule["employees"]:
                        s += empl + ', '
                    listbox.insert(END, s)
                else:
                    listbox.insert(END, 'DOMYŚLNY')
            listbox.unbind('<Double-1>')
            listbox.bind('<Double-1>', dbclick2)
            label_text.set("Obecny plik: " + './Harmonogramy/' + item.split('/')[1] + '/' + item.split('/')[0] + '.json')
                    

        def dbclick2(e):
            global index_
            global edit_default
            item = listbox.get('active')
            if item == "DOMYŚLNY":
                edit_default = True
            else:
                edit_default = False
            to_open = (label_text.get().strip(' ').split(":")[1])
            with open(to_open[1:], 'r') as f:
                curr_schedule = json.load(f)
            for s_id, schedule in enumerate(curr_schedule["harmonograms"]):
                if edit_default:
                    if schedule["default"]:
                        edited_ = schedule
                        index_ = s_id
                        break
                else:
                    if item.split(",")[0] in schedule["employees"]:
                        edited_ = schedule
                        index_ = s_id
                        break
            
            listbox.grid_remove()

            for day, hours in curr_schedule["harmonograms"][index_]["days"].items():
                def make_lambda(x):
                    return lambda ev: colorize(x)
                entries_[int(day)] = ttk.Entry(pop_up, width=12)
                entries_[int(day)].insert(0, hours)
                entries_[int(day)].grid(row= int(day), column = 1)
                

                labels[int(day)] = ttk.Label(pop_up, text = day)
                labels[int(day)].grid(row = int(day), column = 0)
                labels[int(day)].bind("<Button-1>", make_lambda(day))
                # then load the days off
            for day in curr_schedule["harmonograms"][index_]["days_off"]:
                labels[int(day)].config(background="red")
            
            save_button.grid(row=24, rowspan=2, column=5, sticky=NSEW)
            if not edit_default:
                del_button.grid(row=27, rowspan=2, column=5, sticky=NSEW)
                listbox2.grid(row=3, rowspan=20, column=5, sticky=NSEW)

        def del_schedule():
            global index_
            empl_list = [listbox2.get(i) for i in listbox2.curselection()]
            to_open = (label_text.get().strip(' ').split(":")[1])
            with open(to_open[1:], 'r') as f:
                data = json.load(f)
            for em in data["harmonograms"][index_]["employees"]:
                try:
                    data["custom_rota"].remove(em)
                except ValueError:
                    pass

            data["harmonograms"].pop(index_)
            with open(to_open[1:], 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            page.employee.reload_list()
            page.employee.change_combo()
            page.employee.read_data()
            pop_up.destroy()    
            self.controller.focus_set()

            self.controller.set_status("Usunięto harmonogram")

        def save():
            global index_
            global edit_default
            empl_list = [listbox2.get(i) for i in listbox2.curselection()]
            to_open = (label_text.get().strip(' ').split(":")[1])
            with open(to_open[1:], 'r') as f:
                data = json.load(f)
            for schedule in data["harmonograms"]:
                for empl in empl_list:
                    try:
                        schedule["employees"].remove(empl)
                    except ValueError:
                        pass
                    if not schedule["employees"] and not schedule["default"]:
                        try:
                            data["harmonograms"].remove(schedule)
                        except ValueError:
                            pass

            # json dict for rota
            to_save = {
            "default":edit_default,
            "employees":[],
            "days":{},
            "days_off":[],     
            }

            for day in range(1, len(labels) + 1):
                to_save["days"][day] = entries_[day].get()
                if labels[day].cget("background") == "red":
                    to_save["days_off"].append(day)
            
            # add current employee to employees
            for empl in empl_list:
                to_save["employees"].append(empl)

            with open(to_open[1:], 'w') as f:
                if edit_default:
                    data["harmonograms"][index_] = to_save
                else:
                    data["harmonograms"].append(to_save)
                json.dump(data, f, indent=4, ensure_ascii=False)

            page.employee.reload_list()
            page.employee.change_combo()
            page.employee.read_data()
            pop_up.destroy()
            self.controller.focus_set()

            self.controller.set_status("Zapisano harmonogram")
            

        # list of schedule files
        files = ["Kliknij podwójnie aby zedytować harmonogram"]

        for file in os.listdir('./Harmonogramy/'):
            if not str(file).endswith('.json'):
                for subfile in os.listdir('./Harmonogramy/' + file + '/'):
                    if str(subfile).endswith('.json'):
                        files.append(str(subfile.strip('.json') + "/" + file))

        # colorize the tile when clicked on
        def colorize(row):
            if labels[int(row)].cget("background") == "red":
                labels[int(row)].configure(background = "SystemButtonFace")
                entries_[int(row)].delete(0, END)
            else:
                labels[int(row)].configure(background = "red")
                entries_[int(row)].delete(0, END)


        # make a listbox of files
        listbox = Listbox(pop_up, selectmode=SINGLE, height=len(files), width=40)
        for f in files:
            listbox.insert(END, f)
        label_text = StringVar()
        label_text.set("Obecny plik: ")
        label = ttk.Label(pop_up, textvariable=label_text)

        listbox2 = Listbox(pop_up, selectmode=MULTIPLE, height=len(page.employee.names))
        for name in page.employee.names:
            listbox2.insert(END, name)

        listbox.bind('<Double-1>', dbclick)

        listbox.grid(row=0)
        label.grid(row=40, columnspan = 6, sticky=NSEW)

        del_button = ttk.Button(pop_up, text="Usuń harmonogram", command=del_schedule)
        save_button = ttk.Button(pop_up, text="Zapisz harmonogram", command=save)
        entries_ = {}
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        pop_up.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - pop_up.winfo_width()/2, y + 200))
              
    # hire an employee once again
    def unfire_employee(self):
        page = self.controller.get_page("Em_App")
        pop_up = Toplevel(background = self.controller.bg)
        pop_up.focus_set()

        names = []
        # list of fired employees
        for file in sorted(os.listdir("./Pracownicy")):
            if str(file).startswith("_"):
                names.append(str(file).strip("_"))

        def save():
            empl_list = [listbox.get(i) for i in listbox.curselection()]
            for curr_empl in empl_list:
                os.rename("./Pracownicy/_" + curr_empl, "./Pracownicy/" + curr_empl)

                for file in os.listdir("./Roczne podsumowanie/"):
                        if str(file).endswith('.json'):
                            with open("./Roczne podsumowanie/"+ str(file), "r") as f:
                                x = json.load(f)
                            with open("./Roczne podsumowanie/"+ str(file), "w") as f:
                                try:
                                    x["employees"][curr_empl] = x["employees"].pop(str("_" + curr_empl))
                                # if employee doesnt exist in summary
                                except KeyError:
                                    pass
                                json.dump(x, f, indent=4, ensure_ascii=False)

            try:
                with open('./Pracownicy/' + curr_empl + "/settings.json", "r") as f:
                    settings = json.load(f)
                settings["fire_date"] = ""
                
            except FileNotFoundError:
                settings= {
                    "hire_date" : "01/01/2000",
                    "fire_date" : ""
                }

            with open('./Pracownicy/' + curr_empl + "/settings.json", "w") as f:
                    json.dump(settings, f, indent=4, ensure_ascii=False)
        
            page.employee.reload_list()
            page.employee.change_combo()
            page.employee.read_data()
            pop_up.destroy()
            self.controller.focus_set()

            self.controller.set_status("Zatrudniono ponownie: " + "".join([a for a in empl_list]))

        listbox = Listbox(pop_up, selectmode=MULTIPLE, height= len(names))
        for name in names:
            listbox.insert(END, name)
        save_button = ttk.Button(pop_up, text="Odzwolnij", command=save)

        listbox.grid(row=0, sticky=NSEW)
        save_button.grid(row=999, sticky=NSEW)
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        pop_up.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - pop_up.winfo_width()/2, y + 200))

    # ask to exit    
    def on_exit(self):
        self.controller.on_exit()

    def change_show(self):
        page = self.controller.get_page("Em_App")

        page.employee.reload_list()
        page.employee.read_data()

        if self.show_all.get():
            self.controller.set_status("Włączono wyświetlanie zwolnionych pracowników")
        else:
            self.controller.set_status("Wyłączono wyświetlanie zwolnionych pracowników")

    def verify_holiday(self):

        # year is selected and next button is pressed
        def next():
            sel_year = listbox.get(listbox.curselection())
            all_em = str(len(empl_dic))
            work_dic = empl_dic.copy()
            for em in empl_dic:
                if not str(sel_year) in empl_dic[em] or not str(sel_year + 1) in empl_dic[em]:
                    work_dic.pop(em)

            q = messagebox.askyesno("Informacja", "Zmiany wpłyną na " + str(len(work_dic)) + " z " + all_em + " pracowników. Kontynuować?")
            if q:
                num = IntVar()
                num.set(0)

                # indexing a dictionary
                def get_nth_key(dictionary, n=0):
                    if n < 0:
                        n += len(dictionary)
                    for i, key in enumerate(dictionary.keys()):
                        if i == n:
                            return key
                    raise IndexError("dictionary index out of range") 

                # calls itself
                def next():
                    n = num.get()
                    calculate_holiday(n)
                    n += 1
                    num.set(n)
                    if n < progress["maximum"]:
                        self.after(500, next)
                    else:
                        close()

                # calculate holiday for employee
                def calculate_holiday(emp_num):
                    emp = get_nth_key(work_dic, emp_num)
                    y = work_dic[emp][0]
                    with open("./Pracownicy/" + emp + "/" + str(y) + ".json", "r") as f:
                        data = json.load(f)

                    # load the holiday
                    used = sum(data["holiday"])
                    yearly = int(data["yearly_holiday"])
                    back_1 = int(data["holiday_left_" + str((int(y) - 1))])
                    back_2 = int(data["holiday_left_" + str((int(y) - 2))])

                    # calculate new values: back_1 and back_2
                    if used > back_2:
                        if used > back_2 + back_1:
                            n_back_2 = 0
                            n_back_1 = yearly + back_1 + back_2 - used
                        else:
                            n_back_2 = back_1 + back_2 - used
                            n_back_1 = yearly
                    else:
                        n_back_2 = back_1
                        n_back_1 = yearly

                    # laod the next year file
                    with open("./Pracownicy/" + emp + "/" + str(int(y) + 1) + ".json", "r") as f:
                        data_1 = json.load(f)

                    data_1["holiday_left_" + str((int(y)))] = n_back_1
                    data_1["holiday_left_" + str((int(y) - 1))] = n_back_2

                    # overwrite the next year file
                    with open("./Pracownicy/" + emp + "/" + str(int(y) + 1) + ".json", "w") as f:
                        json.dump(data_1, f, indent=4, ensure_ascii=False)

                # close window
                def close(event=None):
                    if progress['value'] == progress["maximum"]:
                        messagebox.showinfo("Informacja", "Poprawnie obliczono wszystkie urlopy")
                    else:
                        messagebox.showinfo("Informacja", "Anulowano obliczanie urlopów")
                    self.controller.focus_set()  # put focus back to the parent window
                    pop_up.destroy()    # destroy first pop up
                    new_pop.destroy()   # destroy progress window  
                    self.master.employee.read_data()                  
                    

                new_pop = Toplevel(background=self.controller.bg)
                new_pop.focus_set()

                progress = ttk.Progressbar(new_pop, orient="horizontal", length=100, mode="determinate", variable=num)
                progress["maximum"] = len(work_dic)
                ttk.Label(new_pop, text="Obliczam wszystkie urlopy, może to zająć chwilkę.").grid(row=0, sticky=NSEW)
                progress.grid(row=1, sticky=NSEW)
                x = self.controller.winfo_x()
                y = self.controller.winfo_y()
                new_pop.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - 200, y + 200))

                next()
                    

        pop_up = Toplevel(background = self.controller.bg)
        pop_up.title("Ponowne przeliczanie urlopów")
        pop_up.focus_set()
        min_year = datetime.datetime.now().year
        max_year = datetime.datetime.now().year
        empl_dic = {}

        # find min and max year in the app
        for directory in os.listdir("./Pracownicy/"):
            empl_dic[directory] = []
            for file in os.listdir("./Pracownicy/" + directory):
                if file.endswith(".json") and not file.startswith("settings"):
                    empl_dic[directory].append(file.split(".")[0])
                    if int(file.split(".")[0]) < min_year:
                        min_year = int(file.split(".")[0])
                    if int(file.split(".")[0]) > max_year:
                        max_year = int(file.split(".")[0])


        # create a list of possible years
        if min_year == max_year:
            messagebox.showinfo("Błąd", "Nie można przeliczyć urlopów dla żadnego roku. Przy przejściu na następny rok zostaną one policzone same. Dopiero wtedy można spróbować przeliczyć je jeszcze raz")
            pop_up.destroy()
            self.controller.focus_set()

        possible_years = []
        for i in range(0, max_year-min_year):
            possible_years.append(min_year+i)

        ttk.Label(pop_up, text="Wybierz z którego roku chcesz przeliczyć urlopy. Wpłynie to na urlopy w roku następnym").grid(row=0, pady = 6)
        listbox = Listbox(pop_up, selectmode=SINGLE, height= len(possible_years), justify=CENTER)
        # fill the listbox with years
        for year in possible_years:
            listbox.insert(END, year)
        listbox.grid(row=1)
        ttk.Button(pop_up, text="Dalej", command=next).grid(row=3, sticky=NSEW)
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        pop_up.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - 200, y + 200))


    def edit_dates(self):
        pop_up = Toplevel(background = self.controller.bg)
        page = self.controller.get_page("Em_App")
        settings = page.employee.employee_sett.copy()

        ttk.Label(pop_up, text="Aktualnie").grid(row=0, column=1, pady=5)
        ttk.Label(pop_up, text="Nowe wartości").grid(row=0, column=2, pady=5)
        ttk.Label(pop_up, text="Data zatrudnienia").grid(row=1, column=0, pady=5)
        ttk.Label(pop_up, text=settings["hire_date"]).grid(row=1, column=1, pady=5)
        if settings["fire_date"] != "":
            ttk.Label(pop_up, text="Data zwolnienia").grid(row=2, column=0, pady=5)
            ttk.Label(pop_up, text=settings["fire_date"]).grid(row=2, column=1, pady=5)
            fire_cal = tkcalendar.DateEntry(pop_up, borderwidth=2, year=datetime.datetime.now().year)
            fire_date = datetime.datetime.strptime(settings["fire_date"], "%d/%m/%Y")
            fire_cal.set_date(fire_date)
            fire_cal.grid(row = 2, column=2, pady=5)


        hire_date = datetime.datetime.strptime(settings["hire_date"], "%d/%m/%Y")
        hire_cal = tkcalendar.DateEntry(pop_up, borderwidth=2, year=datetime.datetime.now().year)
        hire_cal.set_date(hire_date)
        hire_cal.grid(row = 1, column=2, pady=5)

        def save():
            name = page.employee.name.get()
            if "[Z]" in name:
                name = name.replace("[Z]", "_")
            with open("./Pracownicy/" + name + "/" + "settings.json", "r") as f:
                data = json.load(f)
            data["hire_date"] = hire_cal.get_date().strftime("%d/%m/%Y")
            if settings["fire_date"] != "":
                data["fire_date"] = fire_cal.get_date().strftime("%d/%m/%Y")

            with open("./Pracownicy/" + name + "/" + "settings.json", "w") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            page.employee.read_data()
            page.controller.set_status("Zmieniono daty pracownika: " + name)
            pop_up.destroy()
            

        save = ttk.Button(pop_up, text="Zapisz", command=save)
        save.grid(row=3, column=0, columnspan = 3, sticky=NSEW)
        
        x = self.controller.winfo_x()
        y = self.controller.winfo_y()
        pop_up.geometry("+%d+%d" % (x + self.controller.winfo_reqwidth()/2 - pop_up.winfo_width()/2, y + 200))






