
class MovingSpans:

    # Simple Moving Average

    def __init__(self, cum_int_data):

        self.cum_int_data = cum_int_data
        self.count = 1
    
    def runAve(self,window,err_rel,jump_index,printNrep="y",err_rel_nest=1.0e-2):

        # Moving Spans Averages

        moving_averages, val_temp,nested_error_list = [], [], []
        Nrep, val_media = 1, 0

        for i in range(0,len(self.cum_int_data),1):     # (.1)

            val_temp.append(self.cum_int_data[i])

            if len(val_temp) == window:                 # Riempimento della lista con all'interno i valori dell'integrale cumulativo
                val_media = sum(val_temp)/window        # e calcolo della media dell'intervallo
                moving_averages.append(val_media)

                if len(moving_averages)>1+jump_index:   # (.2)

                    # Ciclo di controllo definito dal jump index (numero di "spazi" da saltare nella lista delle medie) e calcolo
                    # dell'errore relativo tra i due valori di media degli intervalli definiti nel ciclo (.1)

                    err_sol = abs((moving_averages[-1]-moving_averages[-2-jump_index]))/moving_averages[-1]
                    nested_error_list.append(err_sol)


                    if len(nested_error_list) > 1+jump_index:
                        val_nested_err = abs(nested_error_list[-1]-nested_error_list[-2-jump_index])

                    if err_sol <= err_rel and val_nested_err <= err_rel_nest:

                        # Per essere verificata la condizione di output serve che sia l'errore relativo tra due valori consecutivi di media
                        # che l'errore relativo tra gli errori relativi siano verificati

                        if printNrep == "y":
                            print(f"All Done!\nNrep = {Nrep}")
                        else:
                            pass

                        return moving_averages[-1]
                
                else:
                    pass

                val_media = []
                val_temp = []

            Nrep += 1