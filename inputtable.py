from tkinter import *
import datetime
import os
import calendar
import json

# Schedule table
class Input_Table(ttk.LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        ttk.LabelFrame.__init__(self, parent, *args, **kwargs)

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
            self.title_labels[title] = ttk.Label(self, text=self.title_labels_text[title])
            self.title_labels[title].grid(row=0, column = counter+1, sticky=NSEW)
            counter += 1

        # Table itself
        for row in range(1, self.t_height):
            for column in range(1, self.t_width+1):
                def make_lambda(x):
                    return lambda ev: self.calculate(x)
                if column == 1:
                    self.entries[row, column] = ttk.Entry(self, width = 12)
                    self.entries[row, column].bind("<Return>", make_lambda(row))
                    self.entries[row, column].grid(row=row, column=column)
                else:
                    self.entries[row, column] = ttk.Entry(self, width = 5, justify = "center")
                    self.entries[row, column].grid(row=row, column=column)


    def after_init(self):
        d_day = datetime.datetime(year = datetime.datetime.now().year, month = datetime.datetime.now().month, day = 1)
        # load holiday
        try:
            with open("./Harmonogramy/" + "swieta.json", "r") as f:
                self.holiday = json.load(f)
        except Exception as e:
            self.controller.set_status(e)
        self.make_month(d_day)


    def calculate(self, row):

        text = str(self.entries[row, 1].get())
        var = text.split("-")

        self.entries[row, 2].delete(0, END)
        self.entries[row, 2].insert(0,int(int(var[1])- int(var[0])))

        self.master.work_time.entries[row, 1].delete(0, END)
        self.master.work_time.entries[row, 1].insert(0, text)
        self.master.work_time.calculate(row)


    #TODO: gdy tworzy sie nowy harmonogram przeladuj pracownika
    def make_month(self, date):
        for l in self.labels:
            self.labels[l].destroy()
        for en in self.entries:
            self.entries[en].delete(0, END)
        the_day = datetime.datetime.weekday(date)

        # Look for a schedule file
        if os.path.isfile("./Harmonogramy/" + str(date.year) + "/" + str(date.month) + ".json"):
            with open("./Harmonogramy/" + str(date.year) + "/" + str(date.month) + ".json", "r") as f:
                data = json.load(f)

            # if current employee has a custom rota
            curr_employee = self.master.employee.name.get()
            if curr_employee in data["custom_rota"]:
                for rota in data["harmonograms"]:
                    if curr_employee in rota["employees"]:
                        index = data["harmonograms"].index(rota)
            # if not -> load the default one
            else:
                for rota in data["harmonograms"]:
                    if rota["default"]:
                        index = data["harmonograms"].index(rota)

            # load the hours first
            for day, hours in data["harmonograms"][index]["days"].items():
                if hours != "":
                    duration = hours.split("-")                     # calculate hours 7-16 
                    duration = [ int(x) for x in duration ]  
                    if duration[0] > duration[1]:
                        total = (24 - duration[0]) + duration[1]
                    else:
                        total = duration[1] - duration[0]
                else:
                    total = ""
                self.entries[int(day), 1].insert(0, hours)
                self.entries[int(day), 2].insert(0, total)

                self.labels[int(day)] = ttk.Label(self, text = day)
                self.labels[int(day)].grid(row = int(day), column = 0)
            # then load the days off
            for day in data["harmonograms"][index]["days_off"]:
                self.labels[int(day)].config(background="red")

        # If schedule not found make a new file and then load it
        else:
            to_save = {}
            to_save["harmonograms"] = []
            to_save["custom_rota"] = []
            to_save["harmonograms"].append({
                "default":True,
                "employees":[],
                "days":{},
                "days_off":[],     
                })

            # if there is no directory with the year make a new one
            if not os.path.isdir(str('./Harmonogramy/' + str(date.year))):
                os.mkdir(str('./Harmonogramy/' + str(date.year))) 
            
            with open("./Harmonogramy/" + str(date.year) + "/" + str(date.month) + ".json", "w") as f:
                for day in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
                    put_hours = True
                    to_save["harmonograms"][0]["days"][int(day)] = ""

                    if (the_day) == 5 or (the_day) == 6:
                        to_save["harmonograms"][0]["days_off"].append(day)
                        put_hours = False
                    elif str(date.year) in self.holiday:
                        if str(date.month) in self.holiday[str(date.year)]:
                            if day in self.holiday[str(date.year)][str(date.month)]:
                                to_save["harmonograms"][0]["days_off"].append(day)
                                put_hours = False
                    if put_hours:
                        to_save["harmonograms"][0]["days"][int(day)] = "7-15"
                    date += datetime.timedelta(days = 1)
                    the_day = datetime.datetime.weekday(date)        
                       
                json.dump(to_save, f, indent=4)

            # load the hours first
            for day, hours in to_save["harmonograms"][0]["days"].items():
                if hours != "":
                    duration = hours.split("-")    
                    duration = [ int(x) for x in duration ]                 # calculate hours 7-16 
                    if duration[0] > duration[1]:
                        total = (24 - duration[0]) + duration[1]
                    else:
                        total = duration[1] - duration[0]
                else:
                    total = ""
                self.entries[int(day), 1].insert(0, hours)
                self.entries[int(day), 2].insert(0, total)
                self.labels[int(day)] = ttk.Label(self, text = day)
                self.labels[int(day)].grid(row = int(day), column = 0)
            # then load the days off
            for day in to_save["harmonograms"][0]["days_off"]:
                self.labels[int(day)].config(background="red")

        try:
            if self.holiday[str(date.year)][str(date.month)]:
                for day in self.holiday[str(date.year)][str(date.month)]:
                    self.labels[int(day)].config(background="red")
        except KeyError:
            pass
            
                    
