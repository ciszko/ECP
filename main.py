from tkinter import *
import tkinter.messagebox
from tkinter import simpledialog
from tkinter import ttk
import calendar
import datetime
import re
import os.path
import io
from fpdf import FPDF
from worktime       import *
from inputtable     import *
from summary        import *
from monthdisplay   import *
from employee       import *
from menu           import *
from data_convert   import *

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
                
        pdf_name = (self.title_str.get() + ' raport.pdf')
        pdf.output(os.path.join(os.getcwd(), "Raporty", pdf_name))

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
        pdf.set_font("DejaVuSans", size=10)
        pdf.set_left_margin(16)

        pdf.add_page()

        spacing = 1.2
        
        data = [["", "Godz. pracy", "Czas przepr.", "50%", "100%", "Noc", "Szko", "Inne", "Urlop", "Chor", "Uwagi"]]
        
        for row in range(1, calendar.monthrange(int(c_year), int(c_month))[1] + 1):
            del(x)
            x= []
            for col in range(0, 11):
                if col == 0:
                    x.append(str(row))
                else:
                    x.append(self.master.work_time.entries[row, col].get())
            data.append(x)

        col0_width = 8
        col1_width = pdf.w / 9
        col2_width = 23
        col10_width = 36
        col_width = 12

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
                    pdf.cell(col1_width, row_height*spacing, txt=item, border=1, align = 'C')
                elif ir == 2:
                    pdf.cell(col2_width, row_height*spacing, txt=item, border=1, align = 'C')
                elif ir == 10:
                    pdf.cell(col10_width, row_height*spacing, txt=item, border=1, align = 'C')
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
    data_convert()
    app = App()
    app.mainloop()

