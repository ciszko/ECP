import calendar
import datetime
import json
import os
from tkinter import END, StringVar, ttk

from common import EMPLOYEES_DIR, YEARLY_SUMMARY_DIR


# Employee at the top
class Employee(ttk.LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        ttk.LabelFrame.__init__(self, parent, *args, **kwargs)

        # styles
        style = ttk.Style()
        style.configure("Next.TButton", width=3, height=3)

        self.controller = controller
        self.names = []
        self.hol_days = 0

        # initialize employee list
        for file in sorted(os.listdir(EMPLOYEES_DIR)):
            if not str(file).startswith("_"):
                self.names.append(str(file))

        self.index = 0  # index of names list
        self.name = StringVar()
        self.employee_data = 0
        self.employee_sett = {}

        # Combobox with employee names
        self.name_box = ttk.Combobox(
            self,
            justify="center",
            textvariable=self.name,
            height=30,
            width=25,
            font=("Arial", 10),
        )
        self.name_box["values"] = self.names
        self.name_box.bind("<<ComboboxSelected>>", lambda _: self.change_combo())

        self.name.set(self.names[self.index])
        self.name_box.grid(row=0, column=1)

        # buttons to navigate through employees
        self.button_left = ttk.Button(
            self,
            text="<<",
            command=lambda: self.change_employee(-1),
            cursor="sb_left_arrow",
            style="Next.TButton",
        )
        self.button_right = ttk.Button(
            self,
            text=">>",
            command=lambda: self.change_employee(1),
            cursor="sb_right_arrow",
            style="Next.TButton",
        )
        self.button_left.grid(row=0, column=0)
        self.button_right.grid(row=0, column=2)

        # hire/fire date
        self.hire_s = StringVar()
        self.fire_s = StringVar()
        self.hire = ttk.Label(self, textvariable=self.hire_s)
        self.fire = ttk.Label(self, textvariable=self.fire_s)
        self.hire_s.set("Zatrudniony od: ")
        self.fire_s.set("Zatrudniony do: ")

        self.hire.grid(row=1, column=0, columnspan=3)
        self.fire.grid(row=2, column=0, columnspan=3)

    # changing the employee
    def change_employee(self, offstet):
        self.save_data()
        self.index += offstet
        if self.index >= len(self.names):
            self.index = 0
        elif self.index < 0:
            self.index = len(self.names) - 1
        self.name.set(self.names[self.index])
        x = self.master.month.get_date()
        date = datetime.datetime(year=x[1], month=x[0], day=1)
        self.master.input_table.make_month(date)
        self.master.work_time.make_month(date)
        self.read_data()

    def change_combo(self):
        self.name.set(self.name.get())
        self.index = self.name_box.current()
        x = self.master.month.get_date()
        date = datetime.datetime(year=x[1], month=x[0], day=1)
        self.master.input_table.make_month(date)
        self.master.work_time.make_month(date)
        self.read_data()

    def reload_list(self):
        del self.names[:]

        for file in sorted(os.listdir(EMPLOYEES_DIR)):
            if self.controller.menu.show_all.get():
                if "." not in str(file):
                    if str(file).startswith("_"):
                        file = "[Z]" + str(file)[1:]
                    self.names.append(str(file))
                    self.name_box["values"] = self.names
                    self.index = 0
                    self.name.set(self.names[self.index])
            else:
                if not str(file).startswith("_"):
                    if "." not in str(file):
                        self.names.append(str(file))
                        self.name_box["values"] = self.names
                        self.index = 0
                        self.name.set(self.names[self.index])

    def read_data(self):
        date = self.master.month.get_date()  # selected date
        curr_empl = self.name.get()  # selected employee
        month_len = calendar.monthrange(date[1], date[0])[1]

        if curr_empl.startswith("[Z]"):
            curr_empl = "_" + curr_empl[3:]

        # if file doesnt exist -> jump to next year
        employee_file = EMPLOYEES_DIR / curr_empl / (str(date[1]) + ".json")
        settings_file = EMPLOYEES_DIR / curr_empl / "settings.json"
        if not employee_file.exists():
            self.make_new_year(date, curr_empl)

        # load the self.employee_sett
        try:
            with settings_file.open() as f:
                self.employee_sett = json.load(f)
        except FileNotFoundError:
            self.employee_sett = {"hire_date": "01/01/2000", "fire_date": ""}
            with settings_file.open("w") as f:
                json.dump(self.employee_sett, f, indent=4, ensure_ascii=False)

        self.hire_s.set("Zatrudniony od: " + str(self.employee_sett["hire_date"]))
        self.fire_s.set("Zatrudniony do: " + str(self.employee_sett["fire_date"]))
        self.fire.grid()

        # check the hire/fire dates
        if self.employee_sett["fire_date"] == "":
            self.fire.grid_remove()
        if datetime.datetime.strptime(
            self.employee_sett["hire_date"], "%d/%m/%Y"
        ) > datetime.datetime(date[1], date[0], month_len):
            self.controller.set_status("Pracownik nie był zatrudniony w tym miesiącu")
            return
        if self.employee_sett["fire_date"] != "":
            if datetime.datetime.strptime(
                self.employee_sett["fire_date"], "%d/%m/%Y"
            ) < datetime.datetime(date[1], date[0], 1):
                self.controller.set_status(
                    "Pracownik nie był zatrudniony w tym miesiącu"
                )
                return

        with employee_file.open() as f1:
            data = json.load(f1)

            # check if all empty
            def is_empty():
                if not data["worked"][str(date[0])]:
                    return True
                for day in data["worked"][str(date[0])]:
                    for val in data["worked"][str(date[0])][day]:
                        if val != "":
                            return False
                return True

            if is_empty():
                for row in range(1, month_len + 1):
                    data["worked"][str(date[0])][str(row)] = []
                    # iterate over columns
                    for col in range(1, 5):
                        if col < 3:
                            self.master.work_time.entries[row, col].delete(0, END)
                            self.master.work_time.entries[row, col].insert(
                                0, self.master.input_table.entries[row, col].get()
                            )
                        data["worked"][str(date[0])][str(row)].append(
                            self.master.work_time.entries[row, col].get()
                        )
                data["worked"][str(date[0])][str(row)].append(
                    self.master.work_time.entries[row, 10].get()
                )
                self.master.summary.sum_hours()
                self.save_data()

            # deal with holidays
            self.hol_days = data["yearly_holiday"]
            self.master.summary.back_1.delete(0, END)
            self.master.summary.back_1.insert(
                0, data[str("holiday_left_" + str(date[1] - 1))]
            )
            self.master.summary.back_2.delete(0, END)
            self.master.summary.back_2.insert(
                0, data[str("holiday_left_" + str(date[1] - 2))]
            )
            # iterate over days in current month
            for row, day in enumerate(data["worked"][str(date[0])], 1):
                # iterate over hours in current day
                for col, hour in enumerate(data["worked"][str(date[0])][day], 1):
                    # 5th item in array is a description
                    if col == 5:
                        self.master.work_time.entries[row, 10].delete(0, END)
                        self.master.work_time.entries[row, 10].insert(0, hour)
                    else:
                        self.master.work_time.entries[row, col].delete(0, END)
                        self.master.work_time.entries[row, col].insert(0, hour)

            # sum used holiday
            self.master.summary.used_leave_y.delete(0, 10)
            self.master.summary.used_leave_y.insert(0, sum(data["holiday"]))
            self.master.work_time.calculate_all()
            self.master.summary.sum_holiday()

        self.controller.set_status("Wczytano dane pracownika " + self.name.get())

    def save_data(self, y=0, b_1=0, b_2=0):
        self.master.summary.sum_holiday()
        date = self.master.month.get_date()  # selected date
        curr_empl = self.name.get()  # selected employee

        if curr_empl.startswith("[Z]"):
            curr_empl = "_" + curr_empl[3:]

        # if employee file doesnt exist, create a new one
        employee_file = EMPLOYEES_DIR / curr_empl / (str(date[1]) + ".json")
        if not employee_file.exists():
            with employee_file.open("w") as f1:
                to_save = {
                    "yearly_holiday": y,
                    str("holiday_left_" + str(date[1] - 1)): b_1,
                    str("holiday_left_" + str(date[1] - 2)): b_2,
                    "holiday": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "worked": {
                        "1": {},
                        "2": {},
                        "3": {},
                        "4": {},
                        "5": {},
                        "6": {},
                        "7": {},
                        "8": {},
                        "9": {},
                        "10": {},
                        "11": {},
                        "12": {},
                    },
                }
                json.dump(to_save, f1, indent=4)

        # change to save
        with employee_file.open() as f1:
            x = json.load(f1)

        lenght = calendar.monthrange(date[1], date[0])[1]
        to_save = {}  # dictionary to change
        # iterate over rows
        for row in range(1, lenght + 1):
            x["worked"][str(date[0])][str(row)] = []
            # iterate over columns
            for col in range(1, 5):
                x["worked"][str(date[0])][str(row)].append(
                    self.master.work_time.entries[row, col].get()
                )
            x["worked"][str(date[0])][str(row)].append(
                self.master.work_time.entries[row, 10].get()
            )
        # add holiday
        x["holiday"][date[0] - 1] = int(self.master.summary.used_leave_m.get())

        # save to employee file
        with employee_file.open("w") as f1:
            json.dump(x, f1, indent=4, ensure_ascii=False)

        # save to yearly summary

        # if yearly summary doesnt exist
        yearly_summary_file = YEARLY_SUMMARY_DIR / (str(date[1]) + ".json")
        if not yearly_summary_file.exists():
            self.make_summary(date)

        with yearly_summary_file.open() as f:
            summ = json.load(f)

        # check if employee is in summary
        if self.name.get() in summ["employees"]:
            summ["employees"][self.name.get()]["holiday"][date[0] - 1] = int(
                self.master.summary.used_leave_m.get()
            )
            summ["employees"][self.name.get()]["work"][
                date[0] - 1
            ] = self.master.summary.sum_entries[1, 1].get()
            summ["employees"][self.name.get()]["yearly_holiday"] = x["yearly_holiday"]
            summ["employees"][self.name.get()][
                str("holiday_left_" + str(date[1] - 1))
            ] = x[str("holiday_left_" + str(date[1] - 1))]
            summ["employees"][self.name.get()][
                str("holiday_left_" + str(date[1] - 2))
            ] = x[str("holiday_left_" + str(date[1] - 2))]
        else:
            summ["employees"][self.name.get()] = {
                "work": 12 * [0],
                "holiday": 12 * [0],
                "yearly_holiday": x["yearly_holiday"],
                str("holiday_left_" + str(date[1] - 1)): 0,
                str("holiday_left_" + str(date[1] - 2)): 0,
            }

        with yearly_summary_file.open("w") as f:
            json.dump(summ, f, indent=4)

        # self.read_data()
        self.master.work_time.calculate_all()
        self.master.summary.sum_holiday()

        self.controller.set_status(
            "Ostatni zapis: " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        )

    def make_new_year(self, date, curr_empl):
        # copy the values to summary from previous year file
        try:
            with open(
                EMPLOYEES_DIR / curr_empl / (str(date[1] - 1) + ".json"), "r"
            ) as f1:
                year_1 = json.load(f1)
                # if employee didnt use everything from back_2
                b2 = int(year_1[str("holiday_left_" + str(date[1] - 2))])
                b1 = int(year_1[str("holiday_left_" + str(date[1] - 3))])
                u_y = sum(year_1["holiday"])
                t = int(year_1["yearly_holiday"]) - u_y + b2 + b1

        except FileNotFoundError:
            b2 = 0
            b1 = 0
            u_y = 0
            t = 26

        if b2 >= u_y:
            back_2 = b1
            yearly_hol = t - b1 - b2 + u_y
            back_1 = yearly_hol
        # if employee used everything from back_2 but not from back_1
        else:
            if b2 + b1 >= u_y:
                back_2 = 0
                yearly_hol = t - b1 - b2 + u_y
                back_1 = yearly_hol
            # if employee used part of holiday from last year
            else:
                back_2 = 0
                yearly_hol = t - b1 - b2 + u_y
                back_1 = t
        self.master.summary.used_leave_m.delete(0, END)
        self.master.summary.used_leave_m.insert(0, "0")

        self.save_data(y=yearly_hol, b_1=back_1, b_2=back_2)

    def make_summary(self, date):
        # create a new dict
        summary = {"employees": {}}
        names = []
        # iterate over employees
        for file in sorted(os.listdir(EMPLOYEES_DIR)):
            names.append(str(file))

        for name in names:
            summary["employees"][name] = {
                "work": 12 * [0],
                "holiday": 12 * [0],
                "yearly_holiday": 0,
                str("holiday_left_" + str(date[1] - 1)): 0,
                str("holiday_left_" + str(date[1] - 2)): 0,
            }
        with open(YEARLY_SUMMARY_DIR / (str(date[1]) + ".json"), "w") as to_save:
            json.dump(summary, to_save, indent=4, ensure_ascii=False)
