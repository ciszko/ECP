from tkinter import *
import datetime
import os
import calendar

# Schedule table
class Input_Table(LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        self.entries = {}               # Entries with hours and time
        self.labels = {}                # Day labels
        self.title_labels = []          # titles
        self.t_height = 32
        self.t_width = 2
        
        counter = 0
        self.title_labels_text = ("Godziny pracy", "Czas")

        for i in range(1,32):
            self.grid_rowconfigure(i, weight = 1)

        for i in range(1,3):
            self.grid_columnconfigure(i, weight = 1)

    
        # Headers for a table
        for title in range(len(self.title_labels_text)):
            self.title_labels.append(self.title_labels_text[title])
            self.title_labels[title] = Label(self, text=self.title_labels_text[title])
            self.title_labels[title].grid(row=0, column = counter+1)
            counter += 1

        # Table itself
        for row in range(1, self.t_height):
            for column in range(1, self.t_width+1):
                def make_lambda(x):
                    return lambda ev: self.calculate(x)
                if column == 1:
                    self.entries[row, column] = Entry(self, width = 12)
                    self.entries[row, column].bind("<Return>", make_lambda(row))
                    self.entries[row, column].grid(row=row, column=column, pady = 1)
                else:
                    self.entries[row, column] = Entry(self, width = 5, justify = "center")
                    self.entries[row, column].grid(row=row, column=column, pady = 1)

        d_day = datetime.datetime(year = datetime.datetime.now().year, month = datetime.datetime.now().month, day = 1)
        self.make_month(d_day)


    def calculate(self, row):

        text = str(self.entries[row, 1].get())
        var = text.split("-")

        self.entries[row, 2].delete(0, 100)
        self.entries[row, 2].insert(0,int(int(var[1])- int(var[0])))

        self.master.work_time.entries[row, 1].delete(0,100)
        self.master.work_time.entries[row, 1].insert(0, text)
        self.master.work_time.calculate(row)


    def make_month(self, date):
        for l in self.labels:
            self.labels[l].destroy()
        for en in self.entries:
            self.entries[en].delete(0, 10)
        the_day = datetime.datetime.weekday(date)

        # Look for a schedule file
        if os.path.isfile("./Harmonogramy/" + str(date.year) + "/" + str(date.month) + ".txt"):
            with open("./Harmonogramy/" + str(date.year) + "/" + str(date.month) + ".txt", "r") as f:
                for day,line in enumerate(f, 1):
                    line.strip()
                    x = line.split(",") 
                    if x[0] == "":
                        self.labels[day] = Label(self, text = day)
                        self.entries[day, 1].insert(0, x[1])
                        self.entries[day, 2].insert(0, "8")                       
                    else:
                        self.labels[day] = Label(self, text = day, bg="red")
                        self.entries[day, 1].insert(0, x[1])
                    self.labels[day].grid(row = day, column = 0)

        # If schedule not found make a normal month
        else:
            for day in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
                if (the_day) == 5 or (the_day) == 6:
                    self.labels[day] = Label(self, text=day, bg="red")
                else:
                    self.labels[day] = Label(self, text=day)
                    self.entries[day, 1].insert(0, "7-15")
                    self.entries[day, 2].insert(0, "8")
                
                self.labels[day].grid(row=day, column=0)
                date += datetime.timedelta(days = 1)
                the_day = datetime.datetime.weekday(date)

