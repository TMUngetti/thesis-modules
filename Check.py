from SimulationLauncher import *
from ImportDatas import *
from CumulativeIntegral import *
from MovingSpansAverage import *



class Check:

    def __init__(self,dt,initial_Nrep,N,perc_incr,set_err_ass_visc):
        self.dt = dt
        self.in_Nrep = initial_Nrep
        self.N = N
        self.incr = perc_incr
        self.set_err_ass_visc = set_err_ass_visc

    def startAnalysis(self):

        list_viscosities = []

        while True:

            # Convert to int values
            self.in_Nrep = int(self.in_Nrep)
            new_file = Launcher_dt(self.dt,self.in_Nrep,self.N)
            new_file.generateTxt()

            # Launch the simulation
            new_file.launchSims(6)
            print("\nSimulation Ended - Extracting Datas from Output File\n")

            # Get datas
            dataframe = importdatas(f"time_cor.txt_1_{self.in_Nrep}",self.in_Nrep)

            # Check Viscosity Plateau
            window = 8
            err_rel = 1.0e-4
            print(f"\nEvaluating the Viscosity Value by MOVING SPANS - .runIntAve module\n\n Choosen Window = {window}, Err_Rel = {err_rel}\n")
            K_value = K(new_file.kb,new_file.Nev,new_file.xsize*new_file.ysize*new_file.zsize,self.dt,return_value="n")
            cum_int = cum_integral(dataframe[0],dataframe[1],dataframe[2],dataframe[3],K_value)
            input_val = MovingSpans(cum_int)
            viscosity = input_val.runAve(window,err_rel,1,printNrep="n")
            list_viscosities.append(viscosity)
            print(list_viscosities)

            # Check the error between two consecutive viscosity values
            if len(list_viscosities) > 1:
                err_ass_visc = abs(list_viscosities[-1]-list_viscosities[-2])

                if err_ass_visc < self.set_err_ass_visc:
                    print(f"\n\nSolution Found!\n\nViscosity Value: {list_viscosities[-1]}")
                    break
                else:
                    print("\n\nSolution Not Found! New Iteration\n\n")


            # Incremento
            self.in_Nrep = self.in_Nrep + 200     # self.in_Nrep*self.incr
