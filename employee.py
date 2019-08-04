from tkinter import *
import os
import calendar
import io


# Employee at the top 
class Employee(LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller
        self.names = []
        self.hol_days = 0
        
        for file in sorted(os.listdir("./Pracownicy")):
            if not str(file).startswith("X"):
                self.names.append(str(file).split(".")[0])

        self.index = 0              # index of names list
        self.name = StringVar()

        # Combobox with employee names
        self.name_box = ttk.Combobox(self, justify = "center", textvariable = self.name, height = 30)
        self.name_box['values'] = self.names
        self.name_box.bind("<<ComboboxSelected>>", lambda _ : self.change_combo())

        self.name.set(self.names[self.index])
        self.name_box.grid(row=0, column=1)

        # buttons to navigate through employees 
        self.button_left = Button(self, text="<<", command=lambda : self.change_employee(-1), cursor = "sb_left_arrow")
        self.button_left.grid(row=0, column = 0)

        self.button_right = Button(self, text=">>", command=lambda: self.change_employee(1), cursor = "sb_right_arrow")
        self.button_right.grid(row=0, column = 2)

    # changing the employee
    def change_employee(self, offstet):
        self.index += offstet
        if self.index >= len(self.names):
            self.index = 0
        elif self.index < 0:
            self.index = len(self.names) -1
        self.name.set(self.names[self.index])
        self.read_data()
        self.read_data()
        self.master.work_time.calculate_all()

    def change_combo(self):
        self.name.set(self.name.get())
        self.index = self.name_box.current()
        self.read_data()
        self.read_data()
        self.master.work_time.calculate_all()
        self.master.summary.sum_holiday()

    def reload_list(self):
        del self.names[:]
        for file in sorted(os.listdir("./Pracownicy")):
            if not str(file).startswith("X"):
                self.names.append(str(file).split(".")[0])
                self.name_box['values'] = self.names
                self.index = 0
                self.name.set(self.names[self.index])


    def read_data(self):
        date = self.master.month.get_date()
        lenght = (calendar.monthrange(date[1], date[0])[1])
        with open("./Pracownicy/" +self.name.get() + ".txt", "r+") as f:
            num = str(self.master.month.selected_month.get()) + "/" +str(self.master.month.selected_year.get())
            offset = 0
            lock = True
            h = []
            for i, line in enumerate(f):
                line = line.strip()
                # TODO: change it to year format eg. 2019 holiday, 2018 holiday
                # holiday days
                if i == 0:
                    self.hol_days = line.split(":")[1]
                # holiday -1 year
                elif i == 1:
                    self.master.summary.back_1.delete(0, 10)
                    self.master.summary.back_1.insert(0, line.split(":")[1])
                # holiday -2 years
                elif i == 2:
                    self.master.summary.back_2.delete(0, 10)
                    self.master.summary.back_2.insert(0, line.split(":")[1])    
                if line.startswith(num):
                    lock = False
                elif lock is False:
                    h.append(line)
                    offset += 1
                    if offset == lenght:
                        lock = True
                    
            if h:
                for i in range(lenght):
                    g = str(h[i]).split(",")
                    for j in range(1,5):                  
                        self.master.work_time.entries[i+1, j].delete(0, 10)
                        self.master.work_time.entries[i+1, j].insert(0, g[j-1])
                    self.master.work_time.entries[i+1, 10].delete(0, 'end')
                    self.master.work_time.entries[i+1, 10].insert(0, g[4])

            else:
                f.seek(0, 2)
                f.write(num + "\n")
                for i in range(1, lenght + 1):
                    x = self.master.input_table.entries[i, 1].get().strip() + "," + self.master.input_table.entries[i, 2].get().strip() + ",,,"
                    f.write(x + "\n")
            
        with io.open("./Roczne podsumowanie/" + str(self.master.month.selected_year.get()) + ".txt", "r", encoding ="utf-8-sig") as f:
            year_hol = 0
            for line in f:
                if line.startswith(str(self.name.get())):
                    line.strip()
                    x = line.split(",")
                    for el in x:
                        if ":" in el:
                            y = el.split(".")
                            year_hol += int(y[1])

        self.master.summary.used_leave_y.delete(0, 10)
        self.master.summary.used_leave_y.insert(0, year_hol)
        self.master.work_time.calculate_all()

    def save_data(self):
        self.master.summary.sum_holiday()

        date = self.master.month.get_date()
        lenght = calendar.monthrange(date[1], date[0])[1]
        with open("./Pracownicy/" +self.name.get() + ".txt", "r") as f:
            number = 0
            data = f.readlines()
            num = str(self.master.month.selected_month.get()) + "/" +str(self.master.month.selected_year.get())
            offset = 1
            lock = True
            for line in data:
                line.strip()
                if line.startswith(num):
                    lock = False
                elif lock is False:                      
                    data[number] = self.master.work_time.entries[offset, 1].get() + "," + self.master.work_time.entries[offset, 2].get() + "," + self.master.work_time.entries[offset, 3].get() + "," + self.master.work_time.entries[offset, 4].get() + "," + self.master.work_time.entries[offset, 10].get() + "\n"
                    offset += 1
                if offset-1 == lenght:
                    lock = True
                number += 1

        with open("./Pracownicy/" +self.name.get() + ".txt", "w") as f:
            f.writelines(data)

        with io.open("./Roczne podsumowanie/" + str(self.master.month.selected_year.get()) + ".txt", "r", encoding = "utf-8-sig") as f:
            data = f.readlines()
        number = 0
        for line in data:
            line.strip()
            if line.startswith(self.name.get()):
                x = line.split(",")
                x[int(self.master.month.selected_month.get())] = str(self.master.summary.sum_entries[1,1].get()) + "." + str(self.master.summary.used_leave_m.get())
                x[13] = self.master.summary.total.get() + "\n"
                data[number] = ",".join(x)

            number += 1

        with io.open("./Roczne podsumowanie/" + str(self.master.month.selected_year.get()) + ".txt", "w", encoding = "utf-8-sig") as f:
            f.writelines(data)

        self.read_data()
        self.master.summary.sum_holiday()
