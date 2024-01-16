import calendar
import datetime
from tkinter import IntVar, ttk


# Date manipulation
class Month_Display(ttk.LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        ttk.LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        # style
        style = ttk.Style()
        style.configure("Month.TButton", width=3, height=3)

        self.selected_month = IntVar()
        self.selected_month.set(datetime.datetime.now().month)
        self.selected_year = IntVar()
        self.selected_year.set(datetime.datetime.now().year)
        # Widgets

        self.button_left = ttk.Button(
            self,
            text="<<",
            command=lambda: self.update_month(-1),
            cursor="sb_left_arrow",
            style="Month.TButton",
        )
        self.button_left.grid(row=1, column=0)

        self.button_right = ttk.Button(
            self,
            text=">>",
            command=lambda: self.update_month(1),
            cursor="sb_right_arrow",
            style="Month.TButton",
        )
        self.button_right.grid(row=1, column=4)

        self.month_label = ttk.Entry(
            self,
            textvariable=self.selected_month,
            width=3,
            justify="center",
            style="my.TEntry",
            font=("Arial", 10),
        )
        self.month_label.grid(row=1, column=1)

        self.slash = ttk.Label(self, text="/", font=("Arial", 13, "bold"))
        self.slash.grid(row=1, column=2)

        self.year_label = ttk.Entry(
            self,
            textvariable=self.selected_year,
            width=5,
            justify="center",
            style="my.TEntry",
            font=("Arial", 10),
        )
        self.year_label.grid(row=1, column=3)

    # Updating month and year
    def update_month(self, offstet):
        self.selected_month.set(self.selected_month.get() + offstet)
        if self.selected_month.get() > 12:
            self.selected_year.set(self.selected_year.get() + offstet)
            self.selected_month.set(1)
            self.master.summary.back_0_s.set(self.selected_year.get())
            self.master.summary.back_1_s.set(self.selected_year.get() - 1)
            self.master.summary.back_2_s.set(self.selected_year.get() - 2)
        elif self.selected_month.get() < 1:
            self.selected_year.set(self.selected_year.get() + offstet)
            self.selected_month.set(12)
            self.master.summary.back_0_s.set(self.selected_year.get())
            self.master.summary.back_1_s.set(self.selected_year.get() - 1)
            self.master.summary.back_2_s.set(self.selected_year.get() - 2)
        self.master.input_table.make_month(
            datetime.datetime(
                year=self.selected_year.get(), month=self.selected_month.get(), day=1
            )
        )
        self.master.work_time.make_month(
            datetime.datetime(
                year=self.selected_year.get(), month=self.selected_month.get(), day=1
            )
        )
        self.master.employee.read_data()

        self.master.summary.sum_hours()

    def get_date(self):
        month = self.selected_month.get()
        year = self.selected_year.get()
        return (month, year)

    def get_month_len(self):
        return (
            calendar.monthrange(
                year=self.selected_year.get(), month=self.selected_month.get()
            )[1]
            + 1
        )
