from tkinter import *
import datetime
import calendar


# Date manipulation
class Month_Display(LabelFrame):

    def __init__(self, parent, controller, *args, **kwargs):
        LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        self.selected_month = IntVar()
        self.selected_month.set(datetime.datetime.now().month)
        self.selected_year = IntVar()
        self.selected_year.set(datetime.datetime.now().year)
        # Widgets

        self.button_left = Button(self, text="<<", command=lambda: self.update_month(-1), cursor = "sb_left_arrow")
        self.button_left.grid(row=1, column = 0)


        self.button_right = Button(self, text=">>", command=lambda: self.update_month(1), cursor = "sb_right_arrow")
        self.button_right.grid(row=1, column = 4)

        
        self.month_label = Entry(self, textvariable=self.selected_month, width=3, justify = "center")
        self.month_label.grid(row=1, column = 1)

        self.slash = Label(self, text="/")
        self.slash.grid(row=1, column = 2)

        
        self.year_label = Entry(self, textvariable=self.selected_year, width=5, justify = "center")
        self.year_label.grid(row=1, column = 3)


    # Updating month and year
    def update_month(self, offstet):
        self.selected_month.set(self.selected_month.get() + offstet)
        if self.selected_month.get() > 12:
            self.selected_year.set(self.selected_year.get() + offstet)
            self.selected_month.set(1)
        elif self.selected_month.get() < 1:
            self.selected_year.set(self.selected_year.get() + offstet)
            self.selected_month.set(12)
        self.master.input_table.make_month(datetime.datetime(year=self.selected_year.get(), month=self.selected_month.get(), day=1))
        self.master.work_time.make_month(datetime.datetime(year=self.selected_year.get(), month=self.selected_month.get(), day=1))
        self.master.employee.read_data()
        self.master.employee.read_data()
        self.master.work_time.calculate_all()
        self.master.summary.sum_hours()
        self.master.summary.sum_holiday()

    def get_date(self):
        month = self.selected_month.get()
        year = self.selected_year.get()
        return (month, year)

