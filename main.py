from tkinter import *
import tkinter.messagebox
from tkinter import simpledialog
from tkinter import ttk
from ttkwidgets import TickScale
import calendar
import datetime
import re
import os.path
from fpdf import FPDF
from worktime       import *
from inputtable     import *
from summary        import *
from monthdisplay   import *
from employee       import *
from menu           import *

class App(Tk):
    def __init__(self, *kwargs, **args):
        Tk.__init__(self)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelframe', labelanchor='n')
        self.bg = style.lookup('TFrame', 'background')
        kasia = 'fajna'

        self.option_add("*Font", "Arial 8")                     # default font 
        self.iconbitmap(r"./data/ikonka.ico")                      # window icon
        self.menu = My_Menu(self, controller=self, background = self.bg)
        self.config(background = self.bg, menu = self.menu)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.grid_propagate(True)
        self.title("Ewidencja czasu pracy")



        container = ttk.Frame(self)
        container.grid(row=0, column = 0, sticky=NSEW)
        #container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}

        # initiate status bar
        self.status_text = StringVar()
        self.status_text.set("Działam :)")
        self.status = ttk.Label(self, textvariable=self.status_text, anchor=W, relief=SUNKEN)
        self.status.grid(row=1, column=0, sticky=EW)
        #self.status.pack(fill=X, side="bottom")

        for F in (Em_App, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller = self)
            self.frames[page_name] = frame 
            frame.grid(row=0, column=0, sticky=NSEW)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

        self.show_frame("Em_App")
        # Gets the requested values of the height and widht.
        windowWidth = self.winfo_reqwidth()
        windowHeight = self.winfo_reqheight()
        
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.winfo_screenheight()/2 - windowHeight/2)
        
        # Positions the window in the center of the page.
        self.geometry("+{}+{}".format(positionRight, positionDown))

        self.set_status("Wszystko wczytane poprawnie")

    # Show a frame for the given page name
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    # when exiting an app
    def on_exit(self):
        if tkinter.messagebox.askyesno("Zakończ pracę", "Czy na pewno chcesz wyjść? \n \t   :("):
            self.destroy()

    # get page for a reference
    def get_page(self, page_class):
        return self.frames[page_class]

    # set text on status bar
    def set_status(self, message):
        self.status_text.set(message)


class Limiter(ttk.Scale):
    """ ttk.Scale sublass that limits the precision of values. """

    def __init__(self, *args, **kwargs):
        self.precision = kwargs.pop('precision')  # Remove non-std kwarg.
        self.chain = kwargs.pop('command', lambda *a: None)  # Save if present.
        super(Limiter, self).__init__(*args, command=self._value_changed, **kwargs)

    def _value_changed(self, newvalue):
        newvalue = round(float(newvalue), self.precision)
        self.winfo_toplevel().globalsetvar(self.cget('variable'), (newvalue))
        self.chain(newvalue)  # Call user specified function.

class DoubleSlider(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        #style
        style = ttk.Style()
        style.configure('Double.Horizontal.TScale', sliderlenght=30)

        self.top_slider = TickScale(self, style='Double.Horizontal.TScale', tickinterval=1, resolution=1, from_=1, to=12, length=400, labelpos='s', command=self.update_value)
        self.top_slider.grid(row = 0, column = 0, sticky=S)
        self.top_slider.set(12)
        self.top_slider.bind("<ButtonRelease-1>", self.update_value)

        self.bot_slider = TickScale(self, style='Double.Horizontal.TScale', tickinterval=1, resolution=1, from_=1, to=12, length=400, labelpos='n', command=self.update_value)
        self.bot_slider.grid(row = 1, column = 0, sticky=N)


    def reset(self):
        self.top_slider.set(12)
        self.bot_slider.set(1)
        #self.update_value(None)

    def update_value(self, event):
        try:
            entries_len = len(self.master.entries)//14
            total = [0] * (entries_len)

            if self.top_slider.get() <= self.bot_slider.get():
                smaller_slider = int(self.top_slider.get())
                bigger_slider = int(self.bot_slider.get())
            else:
                smaller_slider = int(self.bot_slider.get())
                bigger_slider = int(self.top_slider.get())

            for i in range(1,13):
                self.master.labels[i].configure(foreground = "black")
    
            for i in range(smaller_slider, bigger_slider + 2):
                
                if i < bigger_slider + 1 and i >= smaller_slider:
                    self.master.labels[i].configure(foreground = "#0099ff")

                if i > smaller_slider:
                    for j in range(1, entries_len+1):
                        entry = self.master.entries[i, j].get()
                        if ":" in entry:
                            delta = int(entry.split(":")[0]) * 3600 + int(entry.split(":")[1]) * 60
                            total[j-1] += delta
                        else:
                            total[j-1] += int(entry) * 3600
                

            for i in range(1, entries_len+1):
                self.master.entries[14, i].delete(0, 10)
                self.master.entries[14, i].insert(0, str(int((total[i-1] // 3600))) + ":" + str(int(total[i-1]%3600)// 60).zfill(2))
        except AttributeError:
            pass

    # returns the range of sliders e.g (2,7)
    def get_range(self):
        less = min(int(self.top_slider.get()), int(self.bot_slider.get()))
        more = max(int(self.top_slider.get()), int(self.bot_slider.get()))
        return((less, more))

class PageTwo(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.entries = {}
        self.labels = {}
        self.total = {}
        self.offset = 0
        self.onset = 1

        self.headers_s = ("Pracownik", "STY", "LUT", "MAR", "KWI", "MAJ", "CZE", "LIP", "SIE", "WRZ", "PAŹ", "LIS", "GRU", "Razem", "Pozostało")
        self.change_str = StringVar()
        self.change_str.set("Urlop")
        self.title_str = StringVar()
        self.title_str.set("Godz. pracy")

        self.title = ttk.Label(self, textvariable = self.title_str, width = 20, font = "Arial 8 bold", justify="center")
        self.title.grid(row = 0, column = 0, sticky=NS, columnspan=6)

        self.table_frame = ttk.Frame(self, borderwidth = 3, relief = RIDGE)
        self.table_frame.grid(row = 1, column=0, columnspan =6 , sticky=N)

        for i in range(7):
            self.grid_columnconfigure(i, weight = 1)
            self.grid_rowconfigure(i, weight=1)

        def go_back():
            self.controller.show_frame("Em_App")
            

        self.back = ttk.Button(self, text="Powrót", width=15, cursor = "sb_left_arrow", command= go_back)
        self.back.grid(row = 2, column = 1, sticky=N)

        self.change = ttk.Button(self, textvariable = self.change_str, command = self.change, width = 15, cursor = "exchange")
        self.change.grid(row = 2 , column = 3, sticky=N)

        self.print_butt = ttk.Button(self, text = "Drukuj", command = self.to_print, width = 15)
        self.print_butt.grid(row = 2, column = 5, sticky=N)

        for m in range(14 + self.offset):
            self.labels[m] = ttk.Label(self.table_frame, text = self.headers_s[m], justify = "center", anchor = "c")
            self.labels[m].grid(row = 0, column = m+1)  

        self.slider = DoubleSlider(self, controller)
        self.slider.grid(row = 3, column=3, sticky=W)

        self.on_init()     

        
    # buttons to change working_hours/holiday
    def change(self):
        if self.change_str.get() == "Godz. pracy":
            self.change_str.set("Urlop")
            self.on_init("work")
            self.title_str.set("GODZINY PRACY")
        elif self.change_str.get() == "Urlop":
            self.change_str.set("Godz. pracy")
            self.on_init("holiday")
            self.title_str.set("URLOP")

    # make a pdf file
    def to_print(self):

        x = []
        pdf = FPDF('L', 'mm', 'A4')

        try:
            pdf.add_font("./data/DejaVuSans", "", "DejaVuSans.ttf", uni=True)
        except Exception as e:
            messagebox.showerror("Błąd", e)
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

            rn = 0  # row number
            ir = 0  # item in row

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

            # make a range of numbers between sliders + 0,13 
            slider_range = self.slider.get_range()
            applicable_range = [0]
            applicable_range.extend(list(range(slider_range[0], slider_range[1] + 1)))
            applicable_range.append(13)
            
            # column headers
            data = [["Imię i nazwisko", "STY", "LUT", "MAR", "KWI", "MAJ", "CZE", "LIP", "SIE", "WRZ", "PAŹ", "LIS", "GRU", "Razem"]]

            for row in range(1, int(len(self.entries)/14 + 1)):
                del(x)
                x= []
                for col in range(1, 15):
                    if col-1 not in applicable_range:
                        x.append('X')
                    else:
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
        
        os.startfile(os.path.join(os.getcwd(), "Raporty", str(self.title_str.get() + " raport")) +  ".pdf")


    def on_init(self, type = "work"):

        if type == "work":
            self.offset = 0
            self.change_str.set("Urlop")
            self.title_str.set("Godz. pracy")
        if type == "holiday":
            self.offset = 1
            self.change_str.set("Godz. pracy")
            self.title_str.set("Urlop")

        
        
        for l in self.labels:
            self.labels[l].destroy()

        for m in range(14 + self.offset):
            self.labels[m] = ttk.Label(self.table_frame, text = self.headers_s[m], justify = "center", anchor = "c")
            self.labels[m].grid(row = 0, column = m+1)

        for en in self.entries:
            self.entries[en].destroy()

        self.entries = {}

        page = self.controller.get_page("Em_App")

        # check if the file exists, if not then make one
        current_year = page.month.selected_year.get()
        if not os.path.isfile('./Roczne podsumowanie/' + str(current_year) + ".json"):
            # create a new dict 
            summary = {
                "employees" : {}
            }
            names = []
            # iterate over employees
            for file in sorted(os.listdir("./Pracownicy")):
                names.append(str(file))

            for name in names:
                    summary["employees"][name] = {
                        "work" : 12 * [0],
                        "holiday" : 12 * [0],
                        "yearly_holiday" : 0,
                        str("holiday_left_" + str(current_year - 1)) : 0,
                        str("holiday_left_" + str(current_year - 2)) : 0,
                    }
            with open('./Roczne Podsumowanie/' + str(current_year) + ".json", 'w') as to_save:
                json.dump(summary, to_save, indent=4, ensure_ascii=False)


        with open('./Roczne podsumowanie/' + str(current_year) + ".json", "r") as f1:
            x = json.load(f1)

        row = 1
        # iterate over employees
        for empl in sorted(x["employees"]) :
            if self.controller.menu.show_all.get() is True:
                pass
            else:
                if str(empl).startswith("_"):
                    continue
            # employees names
            sum1 = 0
            self.entries[1, row] = Entry(self.table_frame, width = 16)
            self.entries[1, row].grid(row = row, column = 1, padx = 4, pady = 1)
            if str(empl).startswith("_"):
                self.entries[1, row].insert(0, str(empl).replace("_", "[Z]"))
            else:
                 self.entries[1, row].insert(0, str(empl))
            #iterate over records
            for col, month in enumerate(x["employees"][empl][type], 2):
                self.entries[col, row] = Entry(self.table_frame, width = 6, justify = "center")
                self.entries[col, row].insert(0, month)
                self.entries[col, row].grid(row = row, column = col, padx = 2, pady = 1)
                # if type is work calculate sum of hours
                if type == "work":
                    if isinstance(month, str):
                        delta = int(month.split(":")[0]) * 3600 + int(month.split(":")[1]) * 60
                        sum1 += delta
                elif type == "holiday":                       
                    sum1 += int(month)
            # add sum entries
            self.entries[14, row] = Entry(self.table_frame, width = 7, justify = "center")
            self.entries[14, row].grid(row = row, column =14, padx = 1, pady = 1)
            # when calculating holiday, add additional column with summary
            # calculated based on employees holidays from current and -2 previous years
            if type == "holiday":
                self.entries[14, row].insert(0, sum1)
                self.entries[15, row] = Entry(self.table_frame, width = 7, justify = "center")
                self.entries[15, row].grid(row = row, column = 15, padx = 1, pady = 1)
                left = int(x["employees"][empl]["yearly_holiday"]) - sum1 + int(x["employees"][empl][str("holiday_left_" + str(current_year-1))]) + int(x["employees"][empl][str("holiday_left_" + str(current_year-2))])
                self.entries[15, row].insert(0, left)
            elif type == "work":
                m = int((sum1%3600) // 60)
                h = int(sum1 // 3600) 
                self.entries[14, row].insert(0, str(str(h) + ":" + str(m).zfill(2)))  
            row += 1

        self.controller.set_status("Wczytano Roczne podsumowanie")

        # add a sdouble slider when neccessary
        if type == "work":
            self.slider.grid(row = 30, column = 3)
            self.slider.reset()
        if type == "holiday":
            self.slider.grid_remove()
   

class Em_App(ttk.Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid()
        
        self.loaded = False

        # Widgets
        
        self.controller = controller

        self.input_table = Input_Table(self, controller, borderwidth = 3, relief = RIDGE, text = "HARMONOGRAM", labelanchor=N)       
        self.month = Month_Display(self, controller, borderwidth = 3, relief = RIDGE, text = "Data", labelanchor='n', style='my.TLabelframe')
        self.employee = Employee(self, controller, borderwidth = 3, relief = RIDGE, text = "Pracownik",labelanchor='n', style='my.TLabelframe')
        self.work_time = Work_Time(self, controller, borderwidth = 3, relief = RIDGE, text = " WYKONANIE", labelanchor='n',style='my.TLabelframe')
        self.summary = Summary(self, controller, borderwidth = 3, relief = RIDGE, text = "PODSUMOWANIE", labelanchor='n', style='my.TLabelframe')
        self.action_buttons = Action_Buttons(self, controller, borderwidth = 3, relief = RIDGE, text = "OPCJE", labelanchor='n', style='my.TLabelframe')
        

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
                
        # functions to call after the init
        self.input_table.after_init()
        self.work_time.after_init()
        self.summary.after_init()        
        
        self.employee.read_data()
        # self.work_time.calculate_all()
        self.summary.sum_hours()
        # self.summary.sum_holiday()


#Save and next frame buttons
class Action_Buttons(ttk.LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        ttk.LabelFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        self.reload_but = ttk.Button(self, text = "Odśwież", command = self.reload, width=8)
        self.next_frame_but = ttk.Button(self, text = "Roczne podsumowanie", cursor = "sb_right_arrow", command = self.change)
        self.print_but = ttk.Button(self, text = "Drukuj", command = self.to_pdf, width=6)
        
        self.print_but.grid(row = 0, column = 1)
        self.reload_but.grid(row = 0, column = 0)
        self.next_frame_but.grid(row = 0, column = 2)


    def change(self):
        if not self.master.employee.name.get().startswith("[Z]"):
            self.master.employee.save_data()
        page = self.controller.get_page("PageTwo")
        page.on_init("work")
        self.controller.show_frame("PageTwo")
        
    
    def reload(self):
        self.master.employee.read_data()


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

    app = App()

    app.mainloop()



