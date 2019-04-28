from tkinter import *
import tkinter.messagebox
from tkinter import simpledialog
from tkinter import ttk
import calendar
import datetime
import os
import re
import os.path
import io
from fpdf import FPDF


class App(Tk):
    def __init__(self, *kwargs, **args):
        Tk.__init__(self)

        self.option_add("*Font", "Arial 8")                     # default font 
        self.iconbitmap(r"./data/ecp.ico")                      # window icon
        self.menu = My_Menu(self, self)
        self.config(menu = self.menu)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.grid_propagate(False)
        self.title("Ewidencja czasu pracy")

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}

        for F in (Em_App, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller = self)
            self.frames[page_name] = frame 
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Em_App")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def on_exit(self):
        if tkinter.messagebox.askyesno("Zakończ pracę", "Czy na pewno chcesz wyjść? \n \t   :("):
            self.destroy()

    def get_page(self, page_class):
        return self.frames[page_class]

class DoubleSlider(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.job = None

        self.top_slider = Scale(self, from_= 1, to = 12, orient=HORIZONTAL, length = 200, tickinterval = 1)
        self.top_slider.grid(row = 0, column = 0)
        self.top_slider.set(12)
        self.top_slider.bind("<ButtonRelease-1>", self.update_value)

        self.bot_slider = Scale(self, from_= 1, to = 12, orient=HORIZONTAL, length = 200)
        self.bot_slider.grid(row = 1, column = 0)
        self.bot_slider.bind("<ButtonRelease-1>", self.update_value)


    def reset(self):
        self.top_slider.set(12)
        self.bot_slider.set(1)
        self.update_value(None)

    def update_value(self, event):

        entries_len = len(self.master.entries)//14
        total = [0] * (entries_len + 1)

        if self.top_slider.get() <= self.bot_slider.get():
            smaller_slider = self.top_slider.get()
            bigger_slider = self.bot_slider.get()
        else:
            smaller_slider = self.bot_slider.get()
            bigger_slider = self.top_slider.get()

        for i in range(1,13):
            self.master.labels[i].configure(fg = "black")

        
        
        for i in range(smaller_slider, bigger_slider + 2):
            
            if i < bigger_slider + 1 and i >= smaller_slider:
                self.master.labels[i].configure(fg = "#0099ff")

            if i > smaller_slider:
                for j in range(1, entries_len+1):
                    entry = self.master.entries[i, j].get()
                    if ":" in entry:
                        delta = int(entry.split(":")[0]) * 3600 + int(entry.split(":")[1]) * 60
                        total[j] += delta
            

        for i in range(1, entries_len+1):
            self.master.entries[14, i].delete(0, 10)
            self.master.entries[14, i].insert(0, str(int((total[i] // 3600))) + ":" + str(int(total[i]%3600)// 60).zfill(2))

class PageTwo(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.entries = {}
        self.labels = {}
        self.total = {}
        self.offset = 0
        self.onset = 1

        self.headers_s = ("Pracownik", "STY", "LUT", "MAR", "KWI", "MAJ", "CZE", "LIP", "SIE", "WRZ", "PAŹ", "LIS", "GRU", "Razem", "Pozostało")
        self.change_str = StringVar()
        self.change_str.set("Godz. pracy")
        self.title_str = StringVar()
        self.title_str.set("URLOP")

        self.title = Label(self, textvariable = self.title_str, width = 20, font = "Arial 8 bold")
        self.title.grid(row = 0, column = 3)

        self.table_frame = Frame(self, borderwidth = 3, relief = RIDGE)
        self.table_frame.grid(row = 1, column=1, columnspan = 6)

        for i in range(7):
            self.grid_columnconfigure(i, weight = 1)

        def go_back():
            self.controller.show_frame("Em_App")
            

        self.back = Button(self, text="Powrót", width=15, cursor = "sb_left_arrow", command= go_back)
        self.back.grid(row = 4, column = 1)

        self.change = Button(self, textvariable = self.change_str, command = self.change, width = 15, cursor = "exchange")
        self.change.grid(row = 4 , column = 3)

        self.print_butt = Button(self, text = "Drukuj", command = self.to_print, width = 15)
        self.print_butt.grid(row = 4, column = 5)

        for m in range(14 + self.offset):
            Label(self.table_frame, text = self.headers_s[m], justify = "center", anchor = "c").grid(row = 0, column = m+1)

        self.slider = DoubleSlider(self, controller)
        self.slider.grid(row = 30, column = 3)

        self.on_init()     

        

    def change(self):
        if self.change_str.get() == "Godz. pracy":
            self.change_str.set("Urlop")
            self.on_init("holiday")
            self.title_str.set("GODZINY PRACY")
        elif self.change_str.get() == "Urlop":
            self.change_str.set("Godz. pracy")
            self.on_init("work")
            self.title_str.set("URLOP")

    def to_print(self):

        x = []
        pdf = FPDF('L', 'mm', 'A4')

        pdf.add_font("DejaVuSans", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVuSans", size=11)
        
        pdf.add_page()

        spacing = 1.2

        if self.offset == 1:

            data = [["Imię i nazwisko", "STY", "LUT", "MAR", "KWI", "MAJ", "CZE", "LIP", "SIE", "WRZ", "PAŹ", "LIS", "GRU", "Razem", "Pozostało"]]
            
            for row in range(1, int(len(self.entries)/15 + 1)):
                del(x)
                x= []
                for col in range(1, 16):
                    x.append(self.entries[col, row].get())
                data.append(x)

            col1_width = pdf.w / 6
            col2_width = pdf.w / 15
            col_width = pdf.w / 19
            row_height = pdf.font_size + 1
            pdf.cell(0, 10, 'Wykorzystany urlop', 0, 1, 'C')

            rn = 0
            ir = 0
            for row in data:
                for item in row:
                    if rn == 0:
                        if ir == 14:
                            pdf.cell(col2_width, row_height*spacing, txt=item, border=1, align = 'C')
                        elif ir == 0:
                            pdf.cell(col1_width, row_height*spacing, txt=item, border=1)
                        else:
                            pdf.cell(col_width, row_height*spacing, txt=item, border=1, align = 'C')
                    else:
                        if ir == 14:
                            pdf.cell(col2_width, row_height*spacing, txt=item, border=1, align = 'C')
                        elif ir == 0:
                            pdf.cell(col1_width, row_height*spacing, txt=item, border=1)
                        else:
                            pdf.cell(col_width, row_height*spacing, txt=item, border=1, align = 'C')
                    ir += 1
                pdf.ln(row_height*spacing) 
                    
                rn += 1 
                ir = 0     
                  
        elif self.offset == 0:

            data = [["Imię i nazwisko", "STY", "LUT", "MAR", "KWI", "MAJ", "CZE", "LIP", "SIE", "WRZ", "PAŹ", "LIS", "GRU", "Razem"]]

            for row in range(1, int(len(self.entries)/14 + 1)):
                del(x)
                x= []
                for col in range(1, 15):
                    x.append(self.entries[col, row].get())
                data.append(x)

            col1_width = pdf.w / 6
            col2_width = pdf.w / 13
            col_width = pdf.w / 19
            row_height = pdf.font_size + 1
            pdf.cell(0, 10, 'Godziny pracy  (GG:MM)', 0, 1, 'C')

            i = 1

            for row in data:
                for item in row:
                    if row.index(item) == 0:
                        pdf.cell(col1_width, row_height*spacing, txt=item, border=1)
                    elif i == 14:
                        pdf.cell(col2_width, row_height*spacing, txt=item, border=1, align = 'C')
                    else:
                        pdf.cell(col_width, row_height*spacing, txt=item, border=1, align = 'C')
                    i += 1
                i = 1
                pdf.ln(row_height*spacing)
                
        pdf.output(self.title_str.get() + ' raport.pdf')

        os.startfile(os.path.join(os.getcwd(), str(self.title_str.get() + " raport")) +  ".pdf")


    def on_init(self, type = "work"):

        if type == "work":
            self.offset = 1
        if type == "holiday":
            self.offset = 0
        
        for l in self.labels:
            self.labels[l].destroy()

        for m in range(14 + self.offset):
            self.labels[m] = Label(self.table_frame, text = self.headers_s[m], justify = "center", anchor = "c")
            self.labels[m].grid(row = 0, column = m+1)

        for en in self.entries:
            self.entries[en].destroy()

        self.entries = {}

        page = self.controller.get_page("Em_App")

        # make a table
        with io.open("./Roczne podsumowanie/" + str(page.month.selected_year.get()) + ".txt", "r", encoding='utf-8-sig') as f:
            data = sorted(f.readlines())
            
        i = 1

        for line in data:
            sum1 = 0
            x = line.strip().split(",")

            if x != "" or x != "\n":
                for col in range(1,15 + self.offset):
                    if col == 1:
                        self.entries[col, i] = Entry(self.table_frame, width = 16)
                        self.entries[col, i].grid(row = i, column = col, padx = 4, pady = 1)
                        self.entries[col, i].insert(0, x[0])
                    elif col < 14:
                        y = x[col-1].split(".")[self.offset]
                        if y != "0" and self.offset == 1:
                            self.entries[col, i] = Entry(self.table_frame, width = 6, justify = "center", fg = "red")
                        else:
                            self.entries[col, i] = Entry(self.table_frame, width = 6, justify = "center")
                        self.entries[col, i].grid(row = i, column = col, padx = 2, pady = 1)
                        self.entries[col, i].insert(0, y)
                        
                        if self.offset == 1:
                            sum1 += int(y)
                        else:
                            if ":" in str(y):
                                delta = int(y.split(":")[0]) * 3600 + int(y.split(":")[1]) * 60
                                sum1 += delta
                    elif col == 14:
                        self.entries[col, i] = Entry(self.table_frame, width = 7, justify = "center")
                        self.entries[col, i].grid(row = i, column = col, padx = 1, pady = 1)
                        if self.offset == 1:
                            self.entries[col, i].insert(0, sum1)
                        else:
                            m = int((sum1%3600) // 60)
                            h = int(sum1 // 3600) 
                            self.entries[col, i].insert(0, str(str(h) + ":" + str(m).zfill(2)))   
                    elif self.offset == 1:
                        self.entries[col, i] = Entry(self.table_frame, width = 7, justify = "center")
                        self.entries[col, i].grid(row = i, column = col, padx = 1, pady = 1)
                        self.entries[col, i].insert(0, x[13])
            i += 1

        if type == "holiday":
            self.slider.grid(row = 30, column = 3)
            self.slider.reset()
        if type == "work":
            self.slider.grid_remove()


class Em_App(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.grid()
        
        self.loaded = False
        # Widgets
        
        self.controller = controller

        self.input_table = Input_Table(self, controller, borderwidth = 3, relief = RIDGE, text = "HARMONOGRAM", labelanchor = 'n', font = "Arial 8 bold")       
        self.month = Month_Display(self, controller, borderwidth = 3, relief = RIDGE, text = "Data", labelanchor = 'n', font = "Arial 8 bold")
        self.employee = Employee(self, controller, borderwidth = 3, relief = RIDGE, text = "Pracownik", labelanchor = 'n', font = "Arial 8 bold")
        self.work_time = Work_Time(self, controller, borderwidth = 3, relief = RIDGE, text = " WYKONANIE", labelanchor = 'n', font = "Arial 8 bold")
        self.summary = Summary(self, controller, borderwidth = 3, relief = RIDGE, text = "PODSUMOWANIE", labelanchor = 'n', font = "Arial 8 bold")
        self.action_buttons = Action_Buttons(self, controller, borderwidth = 3, relief = RIDGE, text = "OPCJE", labelanchor = 'n', font = "Arial 8 bold")
        

        # Frame positioning 
        self.employee.grid(row=0, column=2, sticky = N)       
        self.input_table.grid(row=0, column=0, rowspan = 4, sticky = NSEW)
        self.work_time.grid(row=0, column = 1, rowspan = 4, sticky = NSEW)
        self.month.grid(row=1, column=2, sticky = N)      
        self.summary.grid(row = 2, column = 2, sticky = NSEW)
        self.action_buttons.grid(row = 3 , column = 2, sticky = NSEW)

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        self.grid_rowconfigure(3,weight=1)
                
        
        self.employee.read_data()
        self.work_time.calculate_all()
        self.summary.sum_hours()
        self.summary.sum_holiday()

        self.loaded = True


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
                if i == 0:
                    self.hol_days = line.split(":")[1]
                elif i == 1:
                    self.master.summary.back_1.delete(0, 10)
                    self.master.summary.back_1.insert(0, line.split(":")[1])
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
            else:
                f.seek(0, 2)
                f.write(num + "\n")
                for i in range(1, lenght + 1):
                    x = self.master.input_table.entries[i, 1].get().strip() + "," + self.master.input_table.entries[i, 2].get().strip() + ",,"
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
                    data[number] = self.master.work_time.entries[offset, 1].get() + "," + self.master.work_time.entries[offset, 2].get() + "," + self.master.work_time.entries[offset, 3].get() + "," + self.master.work_time.entries[offset, 4].get() + "\n"
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


# Calculation table
class Work_Time(LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        self.night_start_value = "22:00"
        self.night_stop_value = "6:00"

        self.night_start = datetime.datetime.strptime(self.night_start_value, "%H:%M")
        self.night_stop = datetime.datetime.strptime(self.night_stop_value, "%H:%M")

        self.t_height = 32
        self.t_width = 10
        self.entries ={}
        self.title_labels_text = ("Godziny pracy","Czas", "50%", "100%", "Noc", "Szko", "Inne", "Urlop", "Chor")
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
            self.title_labels[title] = Label(self, text=self.title_labels_text[title])
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
                    self.entries[row, column] = Entry(self, width = 12)
                    self.entries[row, column].bind("<Return>", combine_funcs(make_lambda(row), make_save(), focus_next_widget))
                    self.entries[row, column].grid(row=row, column=column, pady = 1)
                elif column <= 4:
                    self.entries[row, column] = Entry(self, width = 5, justify = "center")
                    self.entries[row, column].bind("<Return>", combine_funcs(make_lambda(row), make_save(), focus_next_widget))
                    self.entries[row, column].grid(row=row, column=column, pady = 1)                             
                else:
                    self.entries[row, column] = Entry(self, width = 5, justify = "center")
                    self.entries[row, column].grid(row=row, column=column, pady = 1)

        d_day = datetime.datetime(year = datetime.datetime.now().year, month = datetime.datetime.now().month, day = 1)
        self.make_month(d_day)

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

        #TODO: Ogarnac czy musi byc po 8h
        # "Szkolenie" insert
        def f3():
            for col in range (3,10):
                self.entries[row, col].delete(0, 10)   
            if self.entries[row, 2].get() == "":
                self.entries[row, 6].insert(0, 8)
            else:
                self.entries[row, 6].insert(0, int(self.entries[row, 2].get()))

        # "Inne" insert
        def f4():
            for col in range (3,10):
                self.entries[row, col].delete(0, 10)   
            if self.entries[row, 2].get() == "":
                self.entries[row, 7].insert(0, 8)
            else:
                self.entries[row, 7].insert(0, int(self.entries[row, 2].get()))

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
        for i in range(1, 31):
            self.calculate(i)


    def make_month(self, date):
        for l in self.labels:
            self.labels[l].destroy()
        del(self.labels)
        self.labels = {} 

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
                    else:
                        self.labels[day] = Label(self, text = day, bg="red")
                    self.labels[day].grid(row = day, column = 0)

        # If schedule not found make a normal month
        else:
            for day in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
                if (the_day) == 5 or (the_day) == 6:
                    self.labels[day] = Label(self, text=day, bg="red")
                else:
                    self.labels[day] = Label(self, text=day)               
                self.labels[day].grid(row=day, column=0)
                date += datetime.timedelta(days = 1)
                the_day = datetime.datetime.weekday(date)


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


# Summary of hours
class Summary(LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        for i in range(3):
            self.grid_rowconfigure(i, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Top frame
        self.top_frame = LabelFrame(self, bd=2, relief = RIDGE, text="Harmonogram a wykonanie", fg = "blue")

        for i in range(3):
            self.top_frame.grid_rowconfigure(i, weight = 1)
        for i in range(3):
            self.top_frame.grid_columnconfigure(i, weight = 1)

        self.s_hours_s = StringVar()
        self.s_days_s = StringVar()
        self.w_hours_s = StringVar()
        self.w_days_s = StringVar()

        self.s_hours = Entry(self.top_frame, textvariable = self.s_hours_s, justify = "center", width = 10)
        self.s_days = Entry(self.top_frame, textvariable = self.s_days_s, justify = "center", width = 10)
        self.w_hours = Entry(self.top_frame, textvariable = self.w_hours_s, justify = "center", width = 10)
        self.w_days = Entry(self.top_frame, textvariable = self.w_days_s, justify = "center", width = 10)

        self.days_label = Label(self.top_frame, text="Dni")
        self.hours_label = Label(self.top_frame, text="Godz")
        self.s_label = Label(self.top_frame, text="Harmonogram")
        self.w_label = Label(self.top_frame, text="Wykonanie")
        
        self.days_label.grid(row = 1, column = 0)
        self.hours_label.grid(row = 2, column = 0)
        self.s_label.grid(row = 0, column = 1)
        self.w_label.grid(row = 0, column = 2)

        self.s_days.grid(row = 1, column = 1, padx = 10)
        self.s_hours.grid(row = 2, column = 1, padx = 10)
        self.w_hours.grid(row = 2, column = 2, padx = 10)
        self.w_days.grid(row = 1, column = 2, padx = 10)

        self.top_frame.grid(row=0, sticky = NSEW)

        # Middle Frame
        self.mid_frame = LabelFrame(self, bd = 2, relief = RIDGE, text = "Podsumowanie", fg = "blue")

        for i in range(9):
            self.mid_frame.grid_rowconfigure(i, weight = 1)
        for i in range(3):
            self.mid_frame.grid_columnconfigure(i, weight = 1)

        self.sum_entries = {}
        self.m_labels_s = ("Godz : Min", "Dni", "Czas pracy", "50%", "100%", "Noc", "Szkolenie", "Inne", "Urlop", "Zwolnienie")
        self.m_labels = {}

        # summary table
        for col in range(3):
            for row in range(9):
                if col == 0 and row > 0:
                    self.m_labels[row, col] = Label(self.mid_frame, text = self.m_labels_s[row+1])
                    self.m_labels[row, col].grid(row = row, column = col)

                if col == 1:
                    if row == 0:
                        self.m_labels[row, col] = Label(self.mid_frame, text = self.m_labels_s[0])
                        self.m_labels[row, col].grid(row = row, column = col)
                    else:
                        self.sum_entries[row, col] = Entry(self.mid_frame, width = 10, justify = "center")
                        self.sum_entries[row, col].grid(row = row, column = col, padx = 10)
                if col == 2:
                    if row == 0:
                        self.m_labels[row, col] = Label(self.mid_frame, text = self.m_labels_s[1])
                        self.m_labels[row, col].grid(row = row, column = col)
                    elif row == 1 or row == 7 or row == 8:
                        self.sum_entries[row, col] = Entry(self.mid_frame, width = 10, justify = "center")
                        self.sum_entries[row, col].grid(row = row, column = col, padx = 10)



        self.mid_frame.grid(row = 1, sticky = NSEW)
        
        #bottom frame

        self.bot_frame = LabelFrame(self, text = "Urlop", bd = 2, relief = RIDGE, fg = "blue")

        for i in range(5):
            self.bot_frame.grid_rowconfigure(i, weight = 1)
        for i in range(3):
            self.bot_frame.grid_columnconfigure(i, weight = 1)

        self.in_month = Label(self.bot_frame, text = "W miesiącu")   
        self.in_year = Label(self.bot_frame, text = "W roku")      
        self.back_l = Label(self.bot_frame, text = "Zaległy:")      
        self.back_1_l = Label(self.bot_frame, text = datetime.datetime.now().year - 1)     
        self.back_2_l = Label(self.bot_frame, text =datetime.datetime.now().year - 2)       
        self.used_leave_l = Label(self.bot_frame, text = "Wykorzystany:")   
        self.used_leave_m = Entry(self.bot_frame, width = 7, justify = "center")      
        self.used_leave_y = Entry(self.bot_frame, width = 7, justify = "center")        
        self.back_1 = Entry(self.bot_frame, width = 7, justify = "center")       
        self.back_2 = Entry(self.bot_frame, width = 7, justify = "center")
        self.total_l = Label(self.bot_frame, text = "Pozostały:")
        self.total = Entry(self.bot_frame, width = 7, justify = "center")

        self.in_month.grid(row = 0, column = 1)
        self.in_year.grid(row = 0, column = 2)
        self.back_l.grid(row = 3, column = 0, sticky = E)
        self.back_1_l.grid(row = 2, column = 1, sticky = S)
        self.back_2_l.grid(row = 2, column = 2, sticky = S)
        self.used_leave_l.grid(row = 1, column = 0, sticky = E)
        self.used_leave_l.grid(row = 1, column = 0)
        self.used_leave_m.grid(row = 1, column = 1, padx = 10)
        self.used_leave_y.grid(row = 1, column = 2, padx =10)
        self.back_1.grid(row = 3, column = 1, padx =10)
        self.back_2.grid(row = 3, column = 2, padx =10)
        self.total_l.grid(row = 4, column = 0, sticky = E)
        self.total.grid(row = 4, column = 1, columnspan = 3, pady = 10)


        self.bot_frame.grid(row = 2, sticky = NSEW)

        self.sum_hours()

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

        values = [0, 0, 0, 0, 0, 0, 0]

        the_date = self.master.month.get_date()

        for col in range(2,10):      
            for row in range(1, calendar.monthrange(year = the_date[1], month = the_date[0])[1]):
                if col == 2:

                    s = self.master.input_table.entries[row, col].get()
                    w = self.master.work_time.entries[row, col].get()
              
                    if w != "":
                        if ":" in str(w):
                            delta = datetime.datetime.strptime(str(w), F2)
                            sum1 += datetime.timedelta(hours = delta.hour, minutes = delta.minute)
                        else:
                            delta = datetime.datetime.strptime(str(w), F1)
                            sum1 += datetime.timedelta(hours = delta.hour, minutes = delta.minute)
                        w_d += 1                  
                    if s != "":
                        s_h += int(self.master.input_table.entries[row, col].get())
                        s_d += 1

                elif col == 3:

                    w = self.master.work_time.entries[row, col].get()

                    if w != "":
                        if ":" in str(w):
                            delta = datetime.datetime.strptime(str(w), F2)
                            sum2 += datetime.timedelta(hours = delta.hour, minutes = delta.minute)
                        else:
                            delta = datetime.datetime.strptime(str(w), F1)
                            sum2 += datetime.timedelta(hours = delta.hour, minutes = delta.minute)

                elif col == 4:

                    w = self.master.work_time.entries[row, col].get()

                    if w != "":
                        if ":" in str(w):
                            delta = datetime.datetime.strptime(str(w), F2)
                            sum3 += datetime.timedelta(hours = delta.hour, minutes = delta.minute)
                        else:
                            delta = datetime.datetime.strptime(str(w), F1)
                            sum3 += datetime.timedelta(hours = delta.hour, minutes = delta.minute)

                elif col == 5:

                    w = self.master.work_time.entries[row, col].get()

                    if w != "":
                        if ":" in str(w):
                            delta = datetime.datetime.strptime(str(w), F2)
                            sum4 += datetime.timedelta(hours = delta.hour, minutes = delta.minute)
                        else:
                            delta = datetime.datetime.strptime(str(w), F1)
                            sum4 += datetime.timedelta(hours = delta.hour, minutes = delta.minute)

                elif col == 9:
                    if self.master.work_time.labels[row].cget("background") != "red":
                        s = self.master.work_time.entries[row, col].get()
                        if s != "":
                            values[col-3] += int(self.master.work_time.entries[row, col].get())

                else:
                    s = self.master.work_time.entries[row, col].get()
                    if s != "":
                        values[col-3] += int(self.master.work_time.entries[row, col].get())

        sec = sum1.total_seconds()
        m = int((sec%3600) // 60)
        h = int(sec // 3600)

        sec2 = sum2.total_seconds()
        m2 = int((sec2%3600) // 60)
        h2 = int(sec2 // 3600)

        sec3 = sum3.total_seconds()
        m3 = int((sec3%3600) // 60)
        h3 = int(sec3 // 3600)

        sec4 = sum4.total_seconds()
        m4 = int((sec4%3600) // 60)
        h4 = int(sec4 // 3600)

        x = str(str(h) + ":" + str(m).zfill(2))
        x2 = str(str(h2) + ":" + str(m2).zfill(2))
        x3 = str(str(h3) + ":" + str(m3).zfill(2))
        x4 = str(str(h4) + ":" + str(m4).zfill(2))       

        self.w_hours_s.set((x))
        self.w_days_s.set((w_d))
        self.s_hours_s.set(int(s_h))
        self.s_days_s.set(int(s_d))

        self.sum_entries[2,1].delete(0, 10)
        self.sum_entries[2,1].insert(0, x2)

        self.sum_entries[3,1].delete(0, 10)
        self.sum_entries[3,1].insert(0, x3)

        self.sum_entries[4,1].delete(0, 10)
        self.sum_entries[4,1].insert(0, x4)       

        # Summaries
        self.sum_entries[1,1].delete(0, 10)
        self.sum_entries[1,1].insert(0, x)

        self.sum_entries[1,2].delete(0, 10)
        self.sum_entries[1,2].insert(0, int(w_d))

        for v in range(3,7):
            self.sum_entries[v+2, 1].delete(0, 10)
            self.sum_entries[v+2, 1].insert(0, values[v])

        self.sum_entries[7, 2].delete(0,10)
        self.sum_entries[7, 2].insert(0, int(values[5]/8))

        self.used_leave_m.delete(0,10)
        self.used_leave_m.insert(0, int(values[5]/8))
        
        self.sum_entries[8, 2].delete(0,10)
        self.sum_entries[8, 2].insert(0, int(values[6]/8))

        # Holiday

        self.total.delete(0, 10)

    def sum_holiday(self):
        
        total = 0
        total = int(self.master.employee.hol_days) + int(self.back_1.get()) + int(self.back_2.get()) - int(self.used_leave_y.get())
        self.total.delete(0, 10)
        self.total.insert(0, total)

#Save and next frame buttons
class Action_Buttons(LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        self.save_but = Button(self, text = "Zapisz", command = self.save)
        self.next_frame_but = Button(self, text = "Roczne podsumowanie", cursor = "sb_right_arrow", command = self.change)
        self.print_but = Button(self, text = "Drukuj", command = self.to_pdf)
        
        self.print_but.grid(row = 0, column = 1)
        self.save_but.grid(row = 0, column = 0)
        self.next_frame_but.grid(row = 0, column = 2)

    def change(self):
        self.master.employee.save_data()
        page = self.controller.get_page("PageTwo")
        page.on_init()
        self.controller.show_frame("PageTwo")
    
    def save(self):
        self.master.employee.save_data()


    def to_pdf(self):

        c_name = str(self.master.employee.name.get())
        c_month = self.master.month.selected_month.get()
        c_year = self.master.month.selected_year.get()
        f_name = str(c_name + "_" + str(c_month) + "_" + str(c_year) + ".pdf")

        x = []
        pdf = FPDF('P', 'mm', 'A4')

        pdf.add_font("DejaVuSans", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVuSans", size=11)
        pdf.set_left_margin(18)

        pdf.add_page()

        spacing = 1.2
        
        data = [["", "Godz. pracy", "Przepracowan czas", "50%", "100%", "Noc", "Szko", "Inne", "Urlop", "Chor"]]
        
        for row in range(1, calendar.monthrange(int(c_year), int(c_month))[1] + 1):
            del(x)
            x= []
            for col in range(0, 10):
                if col == 0:
                    x.append(str(row))
                else:
                    x.append(self.master.work_time.entries[row, col].get())
            data.append(x)

        col0_width = 8
        col1_width = pdf.w / 8
        col2_width = 40
        col_width = 14

        row_height = pdf.font_size + 1
        pdf.cell(0, 10, c_name, 0, 1, 'C')     
        pdf.ln(row_height * spacing)   
        pdf.cell(0, 10, str(str(c_month) + "/" + str(c_year)), 0, 1, 'C')

        rn = 0
        ir = 0
        for row in data:
            for item in row:
                if ir == 0:
                    pdf.cell(col0_width, row_height*spacing, txt=item, border=1, align = 'C')
                elif ir == 1:
                    pdf.cell(col1_width, row_height*spacing, txt=item, border=1)
                elif ir == 2:
                    pdf.cell(col2_width, row_height*spacing, txt=item, border=1, align = 'C')
                else:
                    pdf.cell(col_width, row_height*spacing, txt=item, border=1, align = 'C')
                ir += 1
            pdf.ln(row_height*spacing) 
                
            rn += 1 
            ir = 0 

        pdf.ln(row_height*spacing) 

        pdf.cell(35, row_height*spacing, str("Harmonogram:"), 1)
        pdf.cell(17, row_height*spacing, str(self.master.summary.s_hours_s.get()), 1)
        pdf.ln(row_height*spacing) 
        pdf.cell(35, row_height*spacing, str("Wykonanie:"), 1)
        pdf.cell(17, row_height*spacing, str(self.master.summary.w_hours_s.get()), 1)
        

        pdf.output(os.path.join(os.getcwd(), "Raporty", f_name))
        os.startfile(os.path.join(os.getcwd(), "Raporty", f_name))


if __name__ == "__main__":
    app = App()
    app.mainloop()

