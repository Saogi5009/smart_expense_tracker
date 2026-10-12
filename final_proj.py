import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import datetime
import easyocr
import pickle
from abc import ABC, abstractmethod

class Record(ABC):
    def __init__(self, amount):
        self.amount = amount
        self.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @abstractmethod
    def add_log(self):
        pass

    def get_type(self):
        pass

    def get_amount(self):
        return self.amount

    def get_time(self):
        return self.time

class Income(Record):
    def __init__(self, amount):
        super().__init__(amount)
        self.type = "Income"
    
    def get_type(self):
        return self.type

    def add_log(self):
        return f"{self.time}: Earned {self.amount} Baht"
    
class Expense(Record):
    def __init__(self, amount, category):
        super().__init__(amount)
        self.type = "Expense"
        self.cat = category
    
    def get_type(self):
        return self.type

    def add_log(self):
        return f"{self.time}: Spent {self.amount} Baht"
    
    def get_category(self):
        return self.cat

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rec = []
        self.categories = ["Income", "Food", "Transportation", "Personal", "Cloth", "Utility", "Etc."]

        self.sum = [0, 0, 0, 0, 0, 0, 0]
        self.calculate_sum(self.rec)

        container = tk.Frame(self)
        container.pack()

        self.frames = {}
        for F in (StartPage, Update, History, Graph):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def calculate_sum(self, d):
        self.sum = [0, 0, 0, 0, 0, 0, 0]
        for i in d:
            try:
                if i.get_type() == "Income":
                    self.sum[0] += i.get_amount()
                elif i.get_category() == "Food":
                    self.sum[1] += i.get_amount()
                elif i.get_category() == "Transportation":
                    self.sum[2] += i.get_amount()
                elif i.get_category() == "Personal":
                    self.sum[3] += i.get_amount()
                elif i.get_category() == "Cloth":
                    self.sum[4] += i.get_amount()
                elif i.get_category() == "Utility":
                    self.sum[5] += i.get_amount()
                elif i.get_category() == "Etc.":
                    self.sum[6] += i.get_amount()
            except:
                messagebox.showerror("Error", "Error calculating summation for each categories.")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def get_data(self, month):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if len(month) == 1:
            month = "0" + str(month)
        ret = []
        for i in self.rec:
            if i.get_time()[5:7] == str(month) and i.get_time()[0:5] == now[0:5]:
                ret.append(i)

        return ret

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Home", font=("Arial", 20))
        label.pack(pady=10, padx=10)

        tk.Button(self, text= "Update", command=lambda: controller.show_frame(Update), width=15, height=2).pack(pady= 10)
        tk.Button(self, text= "Show record", command=lambda: controller.show_frame(History), width=15, height=2).pack(pady= 10)
        tk.Button(self, text= "Show Graph", command=lambda: controller.show_frame(Graph), width=15, height=2).pack(pady= 10)
        tk.Button(self, text= "Calculate", command=lambda: self.calc(controller), width=15, height=2).pack(pady= 10)
        tk.Button(self, text= "Save Changes", command=lambda: self.save(controller), width=15, height=2).pack(pady= 10)
        tk.Button(self, text= "Load Data", command=lambda: self.load(controller), width=15, height=2).pack(pady= 10)
    
    def calc(self, controller):
        sum = 0
        try:
            for i in controller.rec:
                if i.get_type() == "Income":
                    sum += i.get_amount()
                elif i.get_type() == "Expense":
                    sum -= i.get_amount()
            if sum >= 0:
                messagebox.showinfo("Information", f"You now have {sum} Baht.")
            else:
                messagebox.showwarning("Warning", f"You now have {sum} Baht.")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {e}")

    def save(self, controller):
        f = filedialog.asksaveasfile(mode='wb', defaultextension=".pkl")
        try:
            pickle.dump(controller.rec, f)
            f.close()
            messagebox.showinfo("Information", "Saved record")
        except: 
            messagebox.showerror("Error", "You haven't selected the file.")
    
    def load(self, controller):
        f = filedialog.askopenfilename(
            title="Select a Pickle File",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
        )
        try:
            with open(f, 'rb') as f:
                data = pickle.load(f)

            if not isinstance(data, list):
                raise TypeError
            
            for item in data:
                if not isinstance(item, Record):
                    raise TypeError
                
            controller.rec = data
            messagebox.showinfo("Information", "Loaded record")
        except (TypeError, AttributeError):
            messagebox.showerror("Error", "Invalid file data structure")
        except:
            messagebox.showerror("Error", "Failed to load file")

class Update(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Update page", font=("Arial", 20)).pack(pady=10, padx=10)

        self.img = None
        self.val = tk.DoubleVar()
        self.tk_img = None

        m_frame = tk.Frame(self)
        m_frame.pack(pady=10, padx=20)

        l_frame = tk.Frame(m_frame)
        l_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        self.image_label = tk.Label(l_frame)
        self.image_label.pack()

        tk.Button(l_frame, text="Select Image", command=lambda: self.select_image(), width=15, height=2).pack()
        
        r_frame = tk.Frame(m_frame)
        r_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        ent_frame = tk.Frame(r_frame)
        ent_frame.pack(pady=10)
        tk.Label(ent_frame, text="Amount: ").grid(row=0, column=0)
        tk.Entry(ent_frame, textvariable= self.val).grid(row= 0, column= 1)

        self.choice = tk.StringVar()
        self.choice.set("Income")
        self.category = tk.StringVar()
        self.category.set(None)

        t_frame = tk.Frame(r_frame)
        t_frame.pack(pady=10)

        tk.Radiobutton(t_frame, text="Income", variable=self.choice, value="Income").grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        tk.Radiobutton(t_frame, text="Expense", variable=self.choice, value="Expense").grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.category_frame = tk.Frame(r_frame)
        
        self.c_label = tk.Label(self.category_frame, text="Select category: ").grid(row= 0, column= 0, padx= 10, pady= 10)
        self.food_radio = tk.Radiobutton(self.category_frame, text="Food", variable=self.category, value="Food").grid(row= 1, column= 0, padx= 10, pady= 10)
        self.transport_radio = tk.Radiobutton(self.category_frame, text="Transportation", variable=self.category, value="Transportation").grid(row= 1, column= 1, padx= 10, pady= 10)
        self.personal_radio = tk.Radiobutton(self.category_frame, text="Personal", variable=self.category, value="Personal").grid(row= 2, column= 0, padx= 10, pady= 10)
        self.cloth_radio = tk.Radiobutton(self.category_frame, text="Cloth", variable=self.category, value="Cloth").grid(row= 2, column= 1, padx= 10, pady= 10)
        self.utility_radio = tk.Radiobutton(self.category_frame, text="Utility", variable=self.category, value="Utility").grid(row= 3, column= 0, padx= 10, pady= 10)
        self.etc_radio = tk.Radiobutton(self.category_frame, text="Etc.", variable=self.category, value="Etc.").grid(row= 3, column= 1, padx= 10, pady= 10)

        self.choice.trace("w", self.show_categories)

        self.b_frame = tk.Frame(r_frame)
        self.b_frame.pack()

        tk.Button(self.b_frame, text="Home", command=lambda: controller.show_frame(StartPage), width=15, height=2).grid(row= 0, column= 0, padx= 10, pady= 10)
        tk.Button(self.b_frame, text="Submit", command=lambda: self.add_history(controller), width=15, height=2).grid(row= 0, column= 1, padx= 10, pady= 10)

    def show_categories(self, *args):
        if self.choice.get() == "Expense":
            self.b_frame.pack_forget()
            self.category_frame.pack()
            self.b_frame.pack()
            self.category.set("Etc.")
        else:
            self.category_frame.pack_forget()
            self.category.set(None)


    def select_image(self):
        f = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )

        try:
            pil_image = Image.open(f)
            
            max_size = (450, 450)
            pil_image.thumbnail(max_size)

            self.tk_img = ImageTk.PhotoImage(pil_image)

            self.image_label.config(image=self.tk_img)
            self.image_label.image = self.tk_img
                
            self.img = cv2.imread(f)

        except:
            messagebox.showerror("Error", "Failed to load image.")

        self.fill_data()
        

    def add_history(self, controller):
        try:
            if self.val.get() <= 0:
                messagebox.showwarning("Warning", "Amount cannot be less than 0")
                self.reset_page()
                return
            
            if self.choice.get() == "Income":
                controller.rec.append(Income(self.val.get()))
            else:
                controller.rec.append(Expense(self.val.get(), self.category.get()))

            messagebox.showinfo("Information", "Record updated")
            self.reset_page()
        except tk.TclError:
            messagebox.showerror("Error", "Invalid amount data")
        except:
            messagebox.showerror("Error", "Unexpected error occur")
        
    def reset_page(self):
        self.val.set(0.0)
        self.image_label.config(image='', text='')
        self.tk_img = None
        self.img = None
        self.choice.set("Income")
        self.category.set(None)

    def fill_data(self):
        try:
            reader = easyocr.Reader(['th', 'en'])
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            result = reader.readtext(blurred)
        except:
            messagebox.showerror("Error", "Reading image failed")
            return
        ret = ""
        val = 0
        case_handle = [",", "บาท", "THB"]

        for i, detection in enumerate(result):
            _, text, _ = detection
            ret += text + "\n"
            if "จำนวน" in text or "จานวน" in text or "amount" in text.lower():
                try:
                    replaced = result[i+1][1]
                    for j in case_handle:
                        replaced = replaced.replace(j, "")
                    replaced = replaced.strip()
                    val += float(replaced)
                except:
                    messagebox.showerror("Error", "slip format does not match")
                    self.reset_page()
        if val == 0:
            messagebox.showerror("Error", "cannot detect amount")
            self.reset_page()

        self.val.set(val)

class History(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="History page", font=("Arial", 20)).pack()
        tk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage), width=15, height=2).pack(pady=10)

        container = tk.Frame(self)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(container, bg='white', highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(container, orient='vertical', command=self.canvas.yview)
        scrollbar.pack(side='right', fill='y')
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.history_frame = tk.Frame(self.canvas, bg='white')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.history_frame, anchor='nw')
        
        self.history_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)
        
    def tkraise(self):
        self.refresh_history()
        super().tkraise()

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def refresh_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        if not self.controller.rec:
            tk.Label(self.history_frame, text="No history yet.").pack()
            return
        
        for val in self.controller.rec[::-1]:
            tk.Label(self.history_frame, text=val.add_log()).pack(anchor='w', padx=20, pady=2)

class Graph(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Graph page", font=("Arial", 20)).pack()
        self.month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.controller = controller
        tk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage), width=15, height=2).pack(pady= 10)
        
        m_frame = tk.Frame(self)
        m_frame.pack()

        month_frame = tk.Frame(m_frame)
        month_frame.grid(row= 0, column= 0)

        self.month_buttons = []

        self.all_btn = tk.Button(month_frame, text="All", width=10, command=self.show_all_data)
        self.all_btn.grid(row=0, column=0, columnspan=2, pady=5)
        self.month_buttons.append(self.all_btn)

        for i in range(12):
            btn = tk.Button(month_frame, text=self.month[i], width=10, command=lambda m=i+1: self.show_month_data(m))
            btn.grid(row=i+1, column=0, padx=2, pady= 5)
            self.month_buttons.append(btn)

        c_frame = tk.Frame(m_frame)
        c_frame.grid(row=0, column=1)
        self.canvas = tk.Canvas(c_frame, width= 1100, height= 600, bg= "white")
        self.canvas.pack()
    
    def tkraise(self):
        self.show_all_data()
        super().tkraise()
    
    def show_month_data(self, month):
        self.refresh_graph(self.controller.get_data(str(month)))
        self.select_button(month)
    
    def show_all_data(self):
        self.refresh_graph(self.controller.rec)
        self.select_button(0)
    
    def select_button(self, ind):
        default = "SystemButtonFace"
        selected_color = "#6475d1"
        selected_text_color = "white"
        default_text_color = "black"

        for i, button in enumerate(self.month_buttons):
            if i == ind:
                button.config(bg=selected_color, fg=selected_text_color)
            else:
                button.config(bg=default, fg=default_text_color)

    def refresh_graph(self, d):
        self.canvas.delete("all")
        self.controller.calculate_sum(d)

        self.x_init = 260
        self.max = max(self.controller.sum)
        if self.max == 0:
            messagebox.showinfo("Information", "No graph info")
            return
        
        try:
            self.canvas.create_line(200, 400, 800, 400)
            self.canvas.create_line(200, 400, 200, 100)

            for i, j in enumerate(self.controller.categories):
                color = "white"
                if i == 0:
                    color = "#aeeda8"
                else:
                    color = "#ed7979"
                self.canvas.create_text(self.x_init, 420, text=j)
                self.canvas.create_rectangle(self.x_init, 400-((self.controller.sum[i]/self.max)*260), self.x_init + 30, 400, fill=color)
                self.x_init += 80

            for i in range(7):
                val = i * self.max / 6
                self.canvas.create_text(175, 400 - ((i/6)*260), text=f'{val:.2f}')
        except ZeroDivisionError:
            messagebox.showerror("Error", "Graph calculating error")
        except:
            messagebox.showerror("Error", "Failed to load graph")

app = App()
try:
    app.mainloop()
except:
    messagebox.showerror("Error", "Some app error occur")