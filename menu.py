from tkinter import *
import io
import os
import datetime
import calendar


# Simple menu
class My_Menu(Menu):
    def __init__(self, parent, controller, *args, **kwargs):
        Menu.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        self.employee = Menu(self, tearoff=0)
        self.file = Menu(self, tearoff=0)
        self.exit = Menu(self, tearoff=0)

        self.add_cascade(label="Harmonogram", menu=self.file)
        self.add_cascade(label="Opcje pracownika", menu=self.employee)
        self.add_command(label="Wyjście", command = lambda: self.on_exit())
        
        # Employee menu
        self.employee.add_command(label="Dodaj pracownika", command = self.add_employee)
        self.employee.add_command(label="Usuń pracownika",underline = 1, command =  self.del_employee)
        self.employee.add_command(label="Zwolnij pracownika", command = self.fire_employee)
        self.employee.add_command(label="Edytuj wymiar urlopu", command = self.edit_holiday)
        self.employee.add_command(label="Edytuj imię i nazwisko", command = self.edit_employee)
        
        #File menu
        self.file.add_command(label="Dodaj nowy harmonogram", command = self.add_schedule)

    # add an employee and set it to the current employee
    def add_employee(self):

        page = self.controller.get_page("Em_App")

        curr_year = page.month.selected_year.get()

        pop_up = Toplevel()
        pop_up.iconbitmap(r"./data/ecp.ico")
        pop_up.title("Dodawanie pracownika")
        pop_up.wm_geometry("300x120")
        var = StringVar()

        for i in range(5):
            pop_up.grid_rowconfigure(i, weight = 1)
        for i in range(5):
            pop_up.grid_columnconfigure(i, weight = 1)

        Label(pop_up, text = "Imię i nazwisko").grid(row = 0, column = 1)
        Label(pop_up, text = "Roczny wymiar urlopu: ").grid(row = 1, column = 1)
        Label(pop_up, text = "Pozostały urlop z " + str(int(curr_year - 1)) + ":").grid(row = 2, column = 1)
        Label(pop_up, text = "Pozostały urlop z " + str(int(curr_year - 2)) + ":").grid(row = 3, column = 1)

        e1 = Entry(pop_up, justify = "center", width = 15, textvariable = var)
        e2 = Entry(pop_up, justify = "center", width = 15)
        e3 = Entry(pop_up, justify = "center", width = 15)
        e4 = Entry(pop_up, justify = "center", width = 15)

        ok = Button(pop_up, text = "Zapisz", command = lambda: save())

        e1.grid(row = 0, column = 3)
        e2.grid(row = 1, column = 3)
        e3.grid(row = 2, column = 3)
        e4.grid(row = 3, column = 3)
        ok.grid(row = 4, column = 1 ,columnspan = 3, sticky = S)

        def autocapitalize(*arg):
            var.set(var.get().title())

        var.trace("w", autocapitalize)

        pop_up.focus_force()
        e1.focus_set()

        def save():
            answer = e1.get()
            if answer != "":
                f = open(os.path.join(os.getcwd(), "Pracownicy" ,answer) + ".txt", "w")
                f.write("Roczny wymiar urlopu:" + str(e2.get()) + "\n")
                f.write("Urlop 1 rok wstecz:" + str(e3.get()) + "\n")
                f.write("Urlop 2 lata wstecz:" + str(e4.get()) + "\n")
                f.close()

                f = io.open("./Roczne podsumowanie/" + str(curr_year) + ".txt", "a+", encoding = "utf-8-sig")
                f.write(answer + ",0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0\n")
                f.close()
            page.employee.reload_list()
            page.employee.change_combo()
            page.employee.read_data()
            pop_up.destroy()

    # deletes a file of the employee
    def del_employee(self):
        page = self.controller.get_page("Em_App")
        
        if len(page.employee.names) == 1:
            tkinter.messagebox.showerror("Ostrzeżenie", "Nie można usunąć jedynego pracownika. \nAby usunąć obecnego pracownika musisz dodać nowego.")
        else:

            answer = tkinter.messagebox.askyesno("Usun pracownika", str("Usunąć pracownika: \n" + page.employee.name_box.get()) )
            if answer:
                with io.open("./Roczne podsumowanie/" + str(page.month.selected_year.get()) + ".txt", "r", encoding = "utf-8-sig") as f:
                    data = f.readlines()
                    number = 0
                for line in data:
                    line.strip()
                    if line.startswith(page.employee.name.get()):
                        data[number] = ""

                    number += 1
                with io.open("./Roczne podsumowanie/" + str(page.month.selected_year.get()) + ".txt", "w", encoding = "utf-8-sig") as f:
                    f.writelines(data)
                
                os.remove(os.path.join(os.getcwd(), "Pracownicy", page.employee.name_box.get()) + ".txt")

                page = self.controller.get_page("Em_App")
                page.employee.reload_list()
                page.employee.change_combo()
                page.employee.read_data()
 

    # add an X on the begining of the file
    def fire_employee(self):
        page = self.controller.get_page("Em_App")

        answer = tkinter.messagebox.askyesno("Zwolnij pracownika", str("Zwolnić pracownika: \n" + page.employee.name_box.get()))
        if answer:
            os.rename("./Pracownicy/" + str(page.employee.name_box.get()) + ".txt", "./Pracownicy/X" + str(page.employee.name_box.get() + ".txt"))
            page.employee.reload_list()
            page.employee.name_box.current(0)
            page.employee.change_combo()
            page.employee.read_data()

    # add a working schedule for current month
    def add_schedule(self):

        def save():
            d = page.month.get_date()
            date = datetime.datetime(day = 1, month = d[0], year = d[1]) 
            lenght = calendar.monthrange(date.year, date.month)[1] + 1        
            with open("./Harmonogramy/" + str(page.month.get_date()[1]) + "/" + str(page.month.get_date()[0]) + ".txt", "w") as f:
                 for row in range(1, lenght):
                    if row == lenght:
                        if labels[row].cget("background") == "red":
                            f.write("R,")
                        else:
                            f.write(",7-15")
                    else:
                        if labels[row].cget("background") == "red":
                            f.write("R,\n")
                        else:
                            f.write(",7-15\n")
            pop_up.destroy()


        def color(row):
            if labels[row].cget("background") == "red":
                labels[row].configure(background = "SystemButtonFace")
                entries[row].delete(0, 10)
                entries[row].insert(0, "7-15")
            else:
                labels[row].configure(background = "red")
                entries[row].delete(0, 10)

        page = self.controller.get_page("Em_App")

        pop_up = Toplevel()
        pop_up.iconbitmap(r"./data/ecp.ico")
        pop_up.title("Dodawanie harmonogramu")

        pop_up.grid_columnconfigure(0, weight = 1)
        pop_up.grid_columnconfigure(3, weight = 1)

        date = datetime.datetime(day = 1, month = page.month.get_date()[0], year = page.month.get_date()[1])

        Label(pop_up, text = str(page.month.selected_month.get()) + "/" + str(page.month.selected_year.get()), font = "Arial 8 bold").grid(row = 0, column = 1, sticky = N, columnspan = 2)

        Button(pop_up, text = "Zapisz", command = save).grid(row = 40, column = 1, columnspan = 2, sticky = N)
        labels = {}
        entries = {}

        # generate table

        for row in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
            entries[row] = Entry(pop_up, width = 12)
            entries[row].grid(row=row, column = 2)
        
        the_day = datetime.datetime.weekday(date)
        for day in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
            def make_lambda(x):
                    return lambda ev: color(x)
            if (the_day) == 5 or (the_day) == 6:
                labels[day] = Label(pop_up, text=day, bg="red")
            else:
               labels[day] = Label(pop_up, text=day)
               entries[day].insert(0, "7-15")
            
            labels[day].grid(row=day, column=1)
            labels[day].bind("<Button-1>", make_lambda(day))
            date += datetime.timedelta(days = 1)
            the_day = datetime.datetime.weekday(date)

        pop_up.focus_force()
        entries[1].focus_set()

    # edit employee's holiday
    def edit_holiday(self):

        page = self.controller.get_page("Em_App")

        with io.open("./Pracownicy/"+ page.employee.name.get() + ".txt", "r", encoding = "utf-8-sig") as f:
            data = f.readlines()

        
        pop_up = Toplevel()
        pop_up.iconbitmap(r"./data/ecp.ico")
        pop_up.title("Edytowanie pracownika")

        for i in range(6):
            pop_up.grid_rowconfigure(i, weight = 1)
        for i in range(3):
            pop_up.grid_columnconfigure(i, weight = 1)

        Label(pop_up, text = "Aktualne wartości", font = "Arial 8 bold").grid(row = 0, column = 0, padx = 10)
        Label(pop_up, text = "Nowe wartości", font = "Arial 8 bold").grid(row = 0, column = 2, padx = 10)
        Label(pop_up, text = "Roczny wymiar urlopu: " + data[0].strip().split(":")[1]).grid(row = 1, column = 0, padx = 10)
        Label(pop_up, text = "Urlop 1 rok wstecz: " + data[1].strip().split(":")[1]).grid(row = 2, column = 0, padx = 10)
        Label(pop_up, text = "Urlop 2 lata wstecz: " + data[2].strip().split(":")[1]).grid(row = 3, column = 0, padx = 10)

        e1 = Entry(pop_up, justify = "center", width = 8)
        e2 = Entry(pop_up, justify = "center", width = 8)
        e3 = Entry(pop_up, justify = "center", width = 8)

        ok = Button(pop_up, text = "Zapisz", command = lambda: save())
        e1.grid(row = 1, column = 2)
        e2.grid(row = 2, column = 2)
        e3.grid(row = 3, column = 2)
        ok.grid(row = 5, column = 0, sticky = S, columnspan = 3)

        pop_up.focus_force()
        e1.focus_set()

        def save():
            if e1.get() != "":
                data[0] = "Roczny wymiar urlopu:" + e1.get() + "\n"
            if e2.get() != "":
                data[1] = "Urlop 1 rok wstecz:" + e2.get() + "\n"
            if e3.get() != "":
                data[2] = "Urlop 2 lata wstecz:" + e3.get() + "\n"
            with open("./Pracownicy/"+ page.employee.name.get() + ".txt", "w") as f:
                f.writelines(data)
                pop_up.destroy()    
            page.employee.save_data()
            page.employee.read_data()
    
    # edit employee's name
    def edit_employee(self):
        page = self.controller.get_page("Em_App")
        name = page.employee.name.get()
        curr_year = page.month.selected_year.get()

        with io.open("./Roczne podsumowanie/"+ str(curr_year) + ".txt", "r", encoding = "utf-8-sig") as f:
            data = f.readlines()
  
        pop_up = Toplevel()
        pop_up.iconbitmap(r"./data/ecp.ico")
        pop_up.title("Edytowanie pracownika")

        pop_up.grid_columnconfigure(0, weight=1)
        pop_up.grid_columnconfigure(3, weight=1)
        pop_up.grid_rowconfigure(0, weight=1)

        Label(pop_up, text = "Aktualne imię i nazwisko: ").grid(row=1, column=1)
        Label(pop_up, text = name, font = "Arial 8 italic").grid(row = 1, column = 2)
        Label(pop_up, text = "Nowe imię i nazwisko: ").grid(row = 2, column = 1)
        ok = Button(pop_up, text = "Zapisz", command = lambda: save())

        var = StringVar()
        entry = Entry(pop_up, text = var)
        entry.grid(row=2, column=2)
        ok.grid(row=3, column=0, columnspan= 3)

        pop_up.focus_force()
        entry.focus_set()

        def autocapitalize(*arg):
            var.set(var.get().title())

        var.trace("w", autocapitalize)

        def save():
            if entry.get() != "":
                os.rename("./Pracownicy/" + name + ".txt", "./Pracownicy/" + entry.get() + ".txt")

            number = 0
            for i in data:
                if i.startswith(name):
                    x = i.split(",")
                    x[0] = entry.get()
                    data[number] = ",".join(x)
                number += 1
            with io.open("./Roczne podsumowanie/" + str(page.month.selected_year.get()) + ".txt", "w", encoding = "utf-8-sig") as f:
                f.writelines(data)

            page.employee.reload_list()
            page.employee.change_combo()
            page.employee.read_data()
            pop_up.destroy()

    # ask to exit    
    def on_exit(self):
        self.controller.on_exit()
