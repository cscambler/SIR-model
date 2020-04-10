#I wrote this little GUI to let us see how changing the parameters in the SIR model affects things.
#One upshot seems to be that setting N = 1 makes the infection rate redundant. Makes sense I guess; only one person means noone gets infected!
#One other thing: I think it's best to keep the numbers low, below 1000 at the most. 
#Would appreciate mathematical insight on why. Is something deeper wrong?

import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

#model class        
class SIR_model():
    #initializing the model class basically just creates the vectors for plotting.
    #the method is a straight copy of the MATLAB thing.
    def __init__(self, controller):
        self.get_parameters(controller)
        self.T = np.arange(1, self.total_days, self.dt)
        
        self.S = np.zeros(self.T.shape)
        self.S[0] = self.population - self.initial_infects - self.immune_at_outset
        
        self.I = np.zeros(self.T.shape)
        self.I[0] = self.initial_infects
        
        self.R = np.zeros(self.T.shape)
        self.R[0] = self.immune_at_outset

        self.D = np.zeros(self.T.shape)
        
        self.N = self.population
        
        for i in range(0, len(self.T)-1):
            self.dS = -self.beta*self.I[i]*self.S[i]/self.N
            self.dI =  self.beta*self.I[i]*self.S[i]/self.N - self.gamma*self.I[i]
            self.dR =  self.gamma*self.I[i]

            self.S[i+1] = self.S[i]+self.dS*self.dt
            self.I[i+1] = self.I[i]+self.dI*self.dt
            self.R[i+1] = self.R[i]+self.dR*self.dt
            self.D[i+1] = self.R[i+1]*self.delta
            
    def get_parameters(self, controller):
        controls = controller.controls
        self.total_days = int(controls.total_time.get())
        self.dt = .1
        self.population = int(controls.total_pop.get())
        self.initial_infects = int(controls.initial_infects.get())
        self.immune_at_outset = int(controls.immune.get())
        self.beta = float(controls.beta_scale.get())
        self.gamma = float(controls.gamma_scale.get())
        self.delta = float(controls.delta_scale.get())

#main application window
class main_window(Tk):
    def __init__(self, parent = None):
        Tk.__init__(self, parent)
        self.initialize()
        self.title('SIR Model App')
    def initialize(self):
        #add menu to control parameters
        self.controls = parameter_menu(self)
        self.controls.grid(row = 1, column = 0)
        #add frame for displaying plots
        self.display_frame = display_frame(self)
        self.display_frame.grid(row = 0, column = 0, columnspan = 3)
        self.bind("<ButtonRelease-1>", callback)
 
#controls menu
class parameter_menu(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()
    def initialize(self):
        #sliding scales to control gamma and beta and delta (but where is alpha in all this?)
        self.infection_frame = Frame(self.parent)
        gamma_scale_box = LabelFrame(self.infection_frame, text="Gamma = recovery rate", padx=5, pady=5)
        self.gamma_scale = Scale(gamma_scale_box, from_=0, to=1, resolution = .01)
        self.gamma_scale.grid()
        gamma_scale_box.grid(row = 0, column = 0)
        
        beta_scale_box = LabelFrame(self.infection_frame, text="Beta = infection rate", padx=5, pady=5)
        self.beta_scale = Scale(beta_scale_box, from_=0, to=1, resolution = .01)
        self.beta_scale.grid()
        beta_scale_box.grid(row = 0, column = 1)

        delta_scale_box = LabelFrame(self.infection_frame, text="Delta = deaths/recoveries", padx=5, pady=5)
        self.delta_scale = Scale(delta_scale_box, from_=0, to=1, resolution = .01)
        self.delta_scale.grid()
        delta_scale_box.grid(row = 0, column = 2)
        self.infection_frame.grid(row = 1, column = 0)

        self.pop_and_days = Frame(self.parent)
        #spinbox for population (can also manually enter)
        population_box = LabelFrame(self.pop_and_days, text="Total Population = N", padx=5, pady=5)
        self.total_pop = Spinbox(population_box, from_= 1, to = 1000)
        self.total_pop.grid()
        population_box.grid()

        #spinbox for number of days
        time_box = LabelFrame(self.pop_and_days, text="Number of Days = T", padx=5, pady=5)
        self.total_time = Spinbox(time_box, from_= 10, to = 1000)
        self.total_time.grid()
        time_box.grid()
        self.pop_and_days.grid(row = 1, column = 1)
        
        self.immune_and_infected = Frame(self.parent)
        #spinbox for immune at outset
        immune_box = LabelFrame(self.immune_and_infected, text="Immune at Outset = R(0)", padx=5, pady=5)
        self.immune = Spinbox(immune_box, from_= 0, to = 1000)
        self.immune.grid()
        immune_box.grid()

        #spinbox for initial infects
        initial_box = LabelFrame(self.immune_and_infected, text="Initial Infections = I(0)", padx=5, pady=5)
        self.initial_infects = Spinbox(initial_box, from_= 0, to = 1000)
        self.initial_infects.grid()
        initial_box.grid()
        self.immune_and_infected.grid(row = 1, column = 2)

class display_frame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()
    def initialize(self):
        #plot the figure
        self.figure = plt.Figure(figsize=(8,5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid()
        update(self)

def update(display_frame):
    controls = display_frame.parent.controls
    #make sure parameters make sense
    if int(controls.initial_infects.get()) + int(controls.immune.get()) > int(controls.total_pop.get()):
        messagebox.showerror("Are you crazy?", "Illegitimate values.")
    #update axis with new model
    else:
        display_frame.ax.clear()
        model = SIR_model(display_frame.parent)
        display_frame.ax.plot(model.T, model.S)
        display_frame.ax.plot(model.T, model.I)
        display_frame.ax.plot(model.T, model.R)
        display_frame.ax.plot(model.T, model.D)
        display_frame.ax.legend(['Susceptible','Infected', 'Removed', 'Dead'])
        display_frame.canvas.draw()
        
#event handler
def callback(event):
    update(app.display_frame)

app = main_window()
app.mainloop()


        
        
