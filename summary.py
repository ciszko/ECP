import datetime
from tkinter import END, NSEW, RIDGE, E, S, StringVar, messagebox, ttk


# Summary of hours
class Summary(ttk.LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        ttk.LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top frame
        self.top_frame = ttk.LabelFrame(
            self,
            borderwidth=2,
            relief=RIDGE,
            text="Harmonogram a wykonanie",
            labelanchor="nw",
        )

        for i in range(3):
            self.top_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.top_frame.grid_columnconfigure(i, weight=1)

        self.s_hours_s = StringVar()
        self.s_days_s = StringVar()
        self.w_hours_s = StringVar()
        self.w_days_s = StringVar()

        self.s_hours = ttk.Entry(
            self.top_frame, textvariable=self.s_hours_s, justify="center", width=10
        )
        self.s_days = ttk.Entry(
            self.top_frame, textvariable=self.s_days_s, justify="center", width=10
        )
        self.w_hours = ttk.Entry(
            self.top_frame, textvariable=self.w_hours_s, justify="center", width=10
        )
        self.w_days = ttk.Entry(
            self.top_frame, textvariable=self.w_days_s, justify="center", width=10
        )

        self.days_label = ttk.Label(self.top_frame, text="Dni")
        self.hours_label = ttk.Label(self.top_frame, text="Godz")
        self.s_label = ttk.Label(self.top_frame, text="Harmonogram")
        self.w_label = ttk.Label(self.top_frame, text="Wykonanie")

        self.days_label.grid(row=1, column=0)
        self.hours_label.grid(row=2, column=0)
        self.s_label.grid(row=0, column=1)
        self.w_label.grid(row=0, column=2)

        self.s_days.grid(row=1, column=1, padx=10)
        self.s_hours.grid(row=2, column=1, padx=10)
        self.w_hours.grid(row=2, column=2, padx=10)
        self.w_days.grid(row=1, column=2, padx=10)

        self.top_frame.grid(row=0, sticky=NSEW)

        # Middle Frame
        self.mid_frame = ttk.LabelFrame(
            self, borderwidth=2, relief=RIDGE, text="Podsumowanie"
        )

        for i in range(9):
            self.mid_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.mid_frame.grid_columnconfigure(i, weight=1)

        self.sum_entries = {}
        self.m_labels_s = (
            "Godz : Min",
            "Dni",
            "Czas pracy",
            "50%",
            "100%",
            "Noc",
            "Szkolenie",
            "Inne",
            "Urlop",
            "Zwolnienie",
        )
        self.m_labels = {}

        # summary table
        for col in range(3):
            for row in range(9):
                if col == 0 and row > 0:
                    self.m_labels[row, col] = ttk.Label(
                        self.mid_frame, text=self.m_labels_s[row + 1]
                    )
                    self.m_labels[row, col].grid(row=row, column=col)

                if col == 1:
                    if row == 0:
                        self.m_labels[row, col] = ttk.Label(
                            self.mid_frame, text=self.m_labels_s[0]
                        )
                        self.m_labels[row, col].grid(row=row, column=col)
                    else:
                        self.sum_entries[row, col] = ttk.Entry(
                            self.mid_frame, width=10, justify="center"
                        )
                        self.sum_entries[row, col].grid(row=row, column=col, padx=10)
                if col == 2:
                    if row == 0:
                        self.m_labels[row, col] = ttk.Label(
                            self.mid_frame, text=self.m_labels_s[1]
                        )
                        self.m_labels[row, col].grid(row=row, column=col)
                    elif row == 1 or row == 7 or row == 8:
                        self.sum_entries[row, col] = ttk.Entry(
                            self.mid_frame, width=10, justify="center"
                        )
                        self.sum_entries[row, col].grid(row=row, column=col, padx=10)

        self.mid_frame.grid(row=1, sticky=NSEW)

        # bottom frame

        self.bot_frame = ttk.LabelFrame(self, text="Urlop", borderwidth=2, relief=RIDGE)

        for i in range(5):
            self.bot_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.bot_frame.grid_columnconfigure(i, weight=1)

        self.in_month = ttk.Label(self.bot_frame, text="W miesiącu")
        self.in_year = ttk.Label(self.bot_frame, text="W roku")
        self.back_0_s = StringVar()
        self.back_1_s = StringVar()
        self.back_2_s = StringVar()
        self.back_0_s.set(str(datetime.datetime.now().year - 0))
        self.back_1_s.set(str(datetime.datetime.now().year - 1))
        self.back_2_s.set(str(datetime.datetime.now().year - 2))
        self.back_0_l = ttk.Label(self.bot_frame, textvariable=self.back_0_s)
        self.back_1_l = ttk.Label(self.bot_frame, textvariable=self.back_1_s)
        self.back_2_l = ttk.Label(self.bot_frame, textvariable=self.back_2_s)
        self.used_leave_l = ttk.Label(self.bot_frame, text="Wykorzystany:")
        self.used_leave_m = ttk.Entry(self.bot_frame, width=7, justify="center")
        self.used_leave_y = ttk.Entry(self.bot_frame, width=7, justify="center")
        self.back_0 = ttk.Entry(self.bot_frame, width=7, justify="center")
        self.back_1 = ttk.Entry(self.bot_frame, width=7, justify="center")
        self.back_2 = ttk.Entry(self.bot_frame, width=7, justify="center")
        self.total_l = ttk.Label(self.bot_frame, text="Pozostały:")
        self.total = ttk.Entry(self.bot_frame, width=7, justify="center")

        self.in_month.grid(row=0, column=1)
        self.in_year.grid(row=0, column=2)
        self.back_0_l.grid(row=2, column=0, sticky=S)
        self.back_1_l.grid(row=2, column=1, sticky=S)
        self.back_2_l.grid(row=2, column=2, sticky=S)
        self.used_leave_l.grid(row=1, column=0, sticky=E)
        self.used_leave_l.grid(row=1, column=0)
        self.used_leave_m.grid(row=1, column=1, padx=10)
        self.used_leave_y.grid(row=1, column=2, padx=10)
        self.back_0.grid(row=3, column=0, padx=10)
        self.back_1.grid(row=3, column=1, padx=10)
        self.back_2.grid(row=3, column=2, padx=10)
        self.total_l.grid(row=4, column=0, sticky=E)
        self.total.grid(row=4, column=1, pady=10)

        self.bot_frame.grid(row=2, sticky=NSEW)

    def after_init(self):
        self.sum_hours()

    # summing hours for every employee
    def sum_hours(self):
        w_d = 0

        s_h = 0
        s_d = 0

        F1 = "%H"
        F2 = "%H:%M"
        sum1 = datetime.timedelta()
        sum2 = datetime.timedelta()
        sum3 = datetime.timedelta()
        sum4 = datetime.timedelta()

        # values for worked time, holiday...
        values = [0, 0, 0, 0, 0, 0, 0]

        month_len = self.master.month.get_month_len()

        for col in range(2, 10):
            for row in range(1, month_len):
                if col == 2:
                    s = self.master.input_table.entries[row, col].get()
                    w = self.master.work_time.entries[row, col].get()

                    if w != "":
                        if ":" in str(w):
                            delta = datetime.datetime.strptime(str(w), F2)
                            sum1 += datetime.timedelta(
                                hours=delta.hour, minutes=delta.minute
                            )
                        else:
                            delta = datetime.datetime.strptime(str(w), F1)
                            sum1 += datetime.timedelta(
                                hours=delta.hour, minutes=delta.minute
                            )
                        w_d += 1
                    if s != "":
                        s_h += int(self.master.input_table.entries[row, col].get())
                        s_d += 1

                elif col == 3:
                    w = self.master.work_time.entries[row, col].get()

                    if w != "":
                        if ":" in str(w):
                            delta = datetime.datetime.strptime(str(w), F2)
                            sum2 += datetime.timedelta(
                                hours=delta.hour, minutes=delta.minute
                            )
                        else:
                            delta = datetime.datetime.strptime(str(w), F1)
                            sum2 += datetime.timedelta(
                                hours=delta.hour, minutes=delta.minute
                            )

                elif col == 4:
                    w = self.master.work_time.entries[row, col].get()

                    if w != "":
                        if ":" in str(w):
                            delta = datetime.datetime.strptime(str(w), F2)
                            sum3 += datetime.timedelta(
                                hours=delta.hour, minutes=delta.minute
                            )
                        else:
                            delta = datetime.datetime.strptime(str(w), F1)
                            sum3 += datetime.timedelta(
                                hours=delta.hour, minutes=delta.minute
                            )

                elif col == 5:
                    w = self.master.work_time.entries[row, col].get()

                    if w != "":
                        if ":" in str(w):
                            delta = datetime.datetime.strptime(str(w), F2)
                            sum4 += datetime.timedelta(
                                hours=delta.hour, minutes=delta.minute
                            )
                        else:
                            delta = datetime.datetime.strptime(str(w), F1)
                            sum4 += datetime.timedelta(
                                hours=delta.hour, minutes=delta.minute
                            )

                elif col == 9:
                    if self.master.work_time.labels[row].cget("background") != "red":
                        s = self.master.work_time.entries[row, col].get()
                        if s != "":
                            values[col - 3] += int(
                                self.master.work_time.entries[row, col].get()
                            )

                else:
                    s = self.master.work_time.entries[row, col].get()
                    if s != "":
                        values[col - 3] += int(
                            self.master.work_time.entries[row, col].get()
                        )

        sec = sum1.total_seconds()
        m = int((sec % 3600) // 60)
        h = int(sec // 3600)

        sec2 = sum2.total_seconds()
        m2 = int((sec2 % 3600) // 60)
        h2 = int(sec2 // 3600)

        sec3 = sum3.total_seconds()
        m3 = int((sec3 % 3600) // 60)
        h3 = int(sec3 // 3600)

        sec4 = sum4.total_seconds()
        m4 = int((sec4 % 3600) // 60)
        h4 = int(sec4 // 3600)

        x = str(str(h) + ":" + str(m).zfill(2))
        x2 = str(str(h2) + ":" + str(m2).zfill(2))
        x3 = str(str(h3) + ":" + str(m3).zfill(2))
        x4 = str(str(h4) + ":" + str(m4).zfill(2))

        self.w_hours_s.set((x))
        self.w_days_s.set((w_d))
        self.s_hours_s.set(int(s_h))
        self.s_days_s.set(int(s_d))

        self.sum_entries[2, 1].delete(0, 10)
        self.sum_entries[2, 1].insert(0, x2)

        self.sum_entries[3, 1].delete(0, 10)
        self.sum_entries[3, 1].insert(0, x3)

        self.sum_entries[4, 1].delete(0, 10)
        self.sum_entries[4, 1].insert(0, x4)

        # Summaries
        self.sum_entries[1, 1].delete(0, 10)
        self.sum_entries[1, 1].insert(0, x)

        self.sum_entries[1, 2].delete(0, 10)
        self.sum_entries[1, 2].insert(0, int(w_d))

        for v in range(3, 7):
            self.sum_entries[v + 2, 1].delete(0, 10)
            self.sum_entries[v + 2, 1].insert(0, values[v])

        self.sum_entries[7, 2].delete(0, 10)
        self.sum_entries[7, 2].insert(0, int(values[5] / 8))

        self.used_leave_m.delete(0, 10)
        self.used_leave_m.insert(0, int(values[5] / 8))

        self.sum_entries[8, 2].delete(0, 10)
        self.sum_entries[8, 2].insert(0, int(values[6] / 8))

    def sum_holiday(self):
        try:
            total = (
                int(self.master.employee.hol_days)
                + int(self.back_1.get())
                + int(self.back_2.get())
                - int(self.used_leave_y.get())
            )

            self.total.delete(0, END)
            self.total.insert(0, total)
            self.back_0.delete(0, END)
            self.back_0.insert(0, self.master.employee.hol_days)
        except Exception as e:
            self.controller.set_status(
                "Coś poszło nie tak, spróbuj cofnąć miesiąc i ponownie wczytaj ten miesiąc"
            )
            messagebox.showerror("Błąd", e)
