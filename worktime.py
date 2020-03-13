from tkinter import *
import calendar
import datetime
from tkinter import simpledialog
from tkinter import ttk
import os

# Calculation table
class Work_Time(ttk.LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        ttk.LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        self.night_start_value = "22:00"
        self.night_stop_value = "6:00"

        self.night_start = datetime.datetime.strptime(self.night_start_value, "%H:%M")
        self.night_stop = datetime.datetime.strptime(self.night_stop_value, "%H:%M")

        self.t_height = 32
        self.t_width = 10+1
        self.entries ={}
        self.title_labels_text = ("Godziny pracy","Czas", "50%", "100%", "Noc", "Szko", "Inne", "Urlop", "Chor", "Opis")
        self.title_labels = []
        self.labels = {}
        counter = 0

        for i in range(1,32):
            self.grid_rowconfigure(i, weight = 1)

        for i in range(1,10):
            self.grid_columnconfigure(i, weight = 1)

        
        # Headers for a table
        for title in range(len(self.title_labels_text)):
            self.title_labels.append(self.title_labels_text[title])
            self.title_labels[title] = ttk.Label(self, text=self.title_labels_text[title])
            self.title_labels[title].grid(row=0, column = counter+1)
            counter += 1

        # Table itself
        for column in range(1, self.t_width):
        
            for row in range(1, self.t_height):
                def make_lambda(x):
                    return lambda ev: self.calculate(x)
                def focus_next_widget(event):
                    event.widget.event_generate("<<NextWindow>>")
                    return("break")
                def make_save():
                    return lambda ev: self.master.employee.save_data()
                def combine_funcs(*funcs):
                    def combined_func(*args, **kwargs):
                        for f in funcs:
                            f(*args, **kwargs)
                    return combined_func
                if column == 1:
                    self.entries[row, column] = ttk.Entry(self, width = 12)
                    self.entries[row, column].bind("<Return>", combine_funcs(make_lambda(row), make_save(), focus_next_widget))
                    self.entries[row, column].grid(row=row, column=column,)
                elif column <= 4:
                    self.entries[row, column] = ttk.Entry(self, width = 5, justify = "center")
                    self.entries[row, column].bind("<Return>", combine_funcs(make_lambda(row), make_save(), focus_next_widget))
                    self.entries[row, column].grid(row=row, column=column)         
                elif column == 10:
                    self.entries[row, column] = ttk.Entry(self, width = 10, justify = "center")
                    self.entries[row, column].bind("<Return>", combine_funcs(make_save(), focus_next_widget))
                    self.entries[row, column].grid(row=row, column=column)                                             
                else:
                    self.entries[row, column] = ttk.Entry(self, width = 5, justify = "center")
                    self.entries[row, column].grid(row=row, column=column)


    def after_init(self):
        d_day = datetime.datetime(year = datetime.datetime.now().year, month = datetime.datetime.now().month, day = 1)
        self.make_month(d_day)

        the_date = self.master.month.get_date()


    # Insert values in correct frames
    def calculate(self, row):

        # Entry text
        text = str(self.entries[row, 1].get())

        # midnight
        midnight = datetime.datetime.strptime("00:00", "%H:%M")

        zero_p = re.compile("0")                        # 0 input
        h_p = re.compile("\d+-\d(\d)?")                 # 7-15 hours pattern
        h2_p = re.compile("\d+:\d+-\d+:\d+")            # 7:30-15:15 hours pattern
        h3_p = re.compile("\d+:\d+-\d+")                # 7:30-15 hours pattern
        h4_p = re.compile("\d+-\d+:\d+")                # 7-15:15 hours pattern
        s_p = re.compile("(?i)S")                       # training pattern
        i_p = re.compile("(?i)I")                       # other pattern
        u_p = re.compile("(?i)U")                       # vacation pattern
        c_p = re.compile("(?i)C")                       # sick pattern
        e_p = re.compile("")                            # empty pattern

        # "0" input
        def f0():
            var = text
            for col in range(2,10):
                self.entries[row, col].delete(0, 10)
            self.entries[row, 2].insert(0, int(var))

        # \d - \d insert
        def f1():
            var = text.split("-")
            FRT = "%H"
            # delete unneccessary columns
            for col in range (5,10):
                self.entries[row, col].delete(0, 10)
            self.entries[row, 2].delete(0, 10)
            
            end = datetime.datetime.strptime(var[1],FRT)
            start = datetime.datetime.strptime(var[0], FRT)
            tdelta = end - start
            
            if tdelta.days < 0:              
                tdelta = (datetime.timedelta(days=0, seconds=tdelta.seconds))
                max_n = midnight - max([self.night_start, start])

                if max_n.days < 0:
                    var1 = (datetime.timedelta(days=0, seconds=max_n.seconds))
                    night_delta = (var1 + (min([self.night_stop, end]) - midnight))

                night_delta = str(night_delta).split(":")             
                self.entries[row, 5].insert(0, night_delta[0] + ":" + night_delta[1])
            
            tdelta = str(tdelta).split(":")        
            self.entries[row, 2].insert(0, tdelta[0] + ":" + tdelta[1])
            

        def f12():            
            var = text.split("-")
            FRT = "%H:%M"
            for col in range (5,10):
                self.entries[row, col].delete(0, 10)
            self.entries[row, 2].delete(0,10)

            end = datetime.datetime.strptime(var[1],FRT)
            start = datetime.datetime.strptime(var[0], FRT)
            tdelta = end - start
            
            if tdelta.days < 0:              
                tdelta = (datetime.timedelta(days=0, seconds=tdelta.seconds))
                max_n = midnight - max([self.night_start, start])

                if max_n.days < 0:
                    var1 = (datetime.timedelta(days=0, seconds=max_n.seconds))
                    night_delta = (var1 + (min([self.night_stop, end]) - midnight))

                night_delta = str(night_delta).split(":")             
                self.entries[row, 5].insert(0, night_delta[0] + ":" + night_delta[1])

            tdelta = str(tdelta).split(":")
            self.entries[row, 2].insert(0, tdelta[0] + ":" + tdelta[1])

        def f13():           
            var = text.split("-")
            F1 = "%H:%M"
            F2 = "%H"
            for col in range (5,10):
                self.entries[row, col].delete(0, 10)
            self.entries[row, 2].delete(0,10)

            end = datetime.datetime.strptime(var[1],F2)
            start = datetime.datetime.strptime(var[0], F1)
            tdelta = end - start
            
            if tdelta.days < 0:              
                tdelta = (datetime.timedelta(days=0, seconds=tdelta.seconds))
                max_n = midnight - max([self.night_start, start])

                if max_n.days < 0:
                    var1 = (datetime.timedelta(days=0, seconds=max_n.seconds))
                    night_delta = (var1 + (min([self.night_stop, end]) - midnight))

                night_delta = str(night_delta).split(":")             
                self.entries[row, 5].insert(0, night_delta[0] + ":" + night_delta[1])

            tdelta = str(tdelta).split(":")
            self.entries[row, 2].insert(0, tdelta[0] + ":" + tdelta[1])

        def f14():           
            var = text.split("-")
            F1 = "%H:%M"
            F2 = "%H"
            for col in range (5,10):
                self.entries[row, col].delete(0, 10)
            self.entries[row, 2].delete(0,10)

            end = datetime.datetime.strptime(var[1],F1)
            start = datetime.datetime.strptime(var[0], F2)
            tdelta = end - start
            
            if tdelta.days < 0:              
                tdelta = (datetime.timedelta(days=0, seconds=tdelta.seconds))
                max_n = midnight - max([self.night_start, start])

                if max_n.days < 0:
                    var1 = (datetime.timedelta(days=0, seconds=max_n.seconds))
                    night_delta = (var1 + (min([self.night_stop, end]) - midnight))

                night_delta = str(night_delta).split(":")             
                self.entries[row, 5].insert(0, night_delta[0] + ":" + night_delta[1])
                
            tdelta = str(tdelta).split(":")
            self.entries[row, 2].insert(0, tdelta[0] + ":" + tdelta[1])

        # "Szkolenie" insert
        def f3():
            for col in range (3,10):
                self.entries[row, col].delete(0, 10)   
            if self.entries[row, 2].get() == "":
                self.entries[row, 6].insert(0, 8)
            else:
                self.entries[row, 6].insert(0, 8)

        # "Inne" insert
        def f4():
            for col in range (3,10):
                self.entries[row, col].delete(0, 10)   
            if self.entries[row, 2].get() == "":
                self.entries[row, 7].insert(0, 8)
            else:
                self.entries[row, 7].insert(0, 8)

        # "Urlop insert"
        def f5():
            for col in range (3,10):
                self.entries[row, col].delete(0, 10)   
            if self.entries[row, 2].get() == "":
                self.entries[row, 8].insert(0, 8)
                self.entries[row, 2].insert(0, 0)
            else:
                self.entries[row, 2].delete(0, 10)
                self.entries[row, 8].insert(0, 8)
                self.entries[row, 2].insert(0, 0)

        # "Chorobowe" insert
        def f6():
            for col in range (3,10):
                self.entries[row, col].delete(0, 10)   
            if self.labels[row].cget("background") == "red":
                self.entries[row, 9].insert(0, 8)        
            elif self.entries[row, 2].get() == "":
                self.entries[row, 9].insert(0, 8)
                self.entries[row, 2].insert(0, 0)
            else:
                self.entries[row, 9].insert(0, 8)
                self.entries[row, 2].delete(0, 10)
                self.entries[row, 2].insert(0, 0)

        def f7():
            for col in range (2,10):
                self.entries[row, col].delete(0, 10)   

        regex_handlers= [
            (zero_p, f0),
            (h4_p, f14),
            (h2_p, f12),
            (h3_p, f13),
            (h_p, f1),
            (s_p, f3),
            (i_p, f4),
            (u_p, f5),
            (c_p, f6),
            (e_p, f7)
        ]

        def do_it(string):
            for regex, f in regex_handlers:
                if re.match(regex, string):
                    f()
                    break
            self.master.summary.sum_hours()
        do_it(text)

        if self.master.loaded is True:
            self.master.summary.sum_holiday()
        
    def calculate_all(self):
        for i in range(1, self.master.month.get_month_len()):
            self.calculate(i)


    def make_month(self, date):
        for l in self.labels:
            self.labels[l].destroy()
        del(self.labels)
        self.labels = {} 

        for en in self.entries:
            self.entries[en].delete(0, 10)

        # Copy the values from input_table
        for row in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
            self.labels[row] = ttk.Label(self, text=self.master.input_table.labels[row]["text"])
            self.labels[row].config(background=self.master.input_table.labels[row].cget("background"))
            
            self.labels[row].grid(row = row, column = 0)

        # if os.path.isfile("./Harmonogramy/" + str(date.year) + "/" + str(date.month) + ".txt"):
        #     with open("./Harmonogramy/" + str(date.year) + "/" + str(date.month) + ".txt", "r") as f:
        #         for day,line in enumerate(f, 1):
        #             line.strip()
        #             x = line.split(",") 
        #             if x[0] == "":
        #                 self.labels[day] = Label(self, text = day)            
        #             else:
        #                 self.labels[day] = Label(self, text = day, bg="red")
        #             self.labels[day].grid(row = day, column = 0)

        # # If schedule not found make a normal month
        # else:
        #     for day in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
        #         if (the_day) == 5 or (the_day) == 6:
        #             self.labels[day] = Label(self, text=day, bg="red")
        #         else:
        #             self.labels[day] = Label(self, text=day)               
        #         self.labels[day].grid(row=day, column=0)
        #         date += datetime.timedelta(days = 1)
        #         the_day = datetime.datetime.weekday(date)

    def color_labels(self):
        for l in self.labels:
            self.labels[l].destroy()
        del(self.labels)
        self.labels = {} 

        for en in self.entries:
            self.entries[en].delete(0, 10)

        # Copy the values from input_table
        for row in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
            self.labels[row] = ttk.Label(self, text=self.master.input_table.labels[row]["text"])
            self.labels[row].config(background=self.master.input_table.labels[row].cget("background"))         
            self.labels[row].grid(row = row, column = 0)        
