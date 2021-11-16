import subprocess
import multiprocessing

class Launcher_s:

    def __init__(self,*s):

        self.ndim = 3
        self.xsize, self.ysize, self.zsize = 15,15,15
        
        self.rho = 3
        self.kb = 1
        self.T = 1/self.kb
        self.rc = 1
        self.rcD = 1.38
        self.s = s
        self.a = 265
        self.dt = 0.03
        self.sigma = 3
        self.nBeads = (self.xsize*self.ysize*self.zsize)*self.rho

        self.neql = 1.0e4
        self.nrun = 1000*10

        self.Nev = 1
        self.Nrep = 1000
        self.Nfreq = 1000

    def generateTxt(self):

        list_filename = []

        for s_val in self.s:

            filename = f"in.Sh_prova_{s_val}"

            with open(filename,"w") as setup:

                setup.write(    "# LAMMPS input script Shardlow's ODEs integration\n"
                                "# DPD simple fluid Schmidt number evaluation\n\n\n"
                                "units       lj\n"
                            f"variable    ndim      equal {self.ndim}\n\n\n"
                                "# Box size\n\n"
                            f"variable    xsize     equal {self.xsize}\n"
                            f"variable    ysize     equal {self.ysize}\n"
                            f"variable    zsize     equal {self.zsize}\n\n\n"
                                "# DPD parameters\n\n"
                            f"variable    rho       equal {self.rho}\n"
                            f"variable    kb        equal {self.kb}\n"
                            f"variable    T         equal {self.T}\n"
                            f"variable    rc        equal {self.rc}\n"
                            f"variable    rcD       equal {self.rcD}\n"
                            f"variable    s         equal {s_val}\n"
                            f"variable    a         equal {self.a}\n"
                            f"variable    dt        equal {self.dt}\n"
                            f"variable    sigma     equal {self.sigma}\n"
                            f"variable    nBeads    equal {self.nBeads}\n\n\n"
                                "# Simulation parameters\n\n"
                                "timestep     ${dt}\n"
                                "dimension    ${ndim} \n"
                            f"variable    neql      equal {self.neql}\n"
                            f"variable    nrun      equal {self.nrun}\n\n\n"
                                "# Post-processing correlation function parameters\n\n"
                            f"variable    Nev  equal {self.Nev}    # correlation length\n"
                            f"variable    Nrep equal {self.Nrep}     # sample interval\n"
                            f"variable    Nfreq  equal {self.Nfreq}   # dump interval\n\n\n"
                                "# Create simulation box\n\n"
                                "boundary     p p p\n"
                                "atom_style   atomic\n"
                                "comm_modify  vel yes\n"
                                "newton       on\n"
                                "lattice      none 1\n"
                                "region       box block 0 ${xsize} 0 ${ysize} 0 ${zsize}\n" 
                                "create_box   1 box\n"
                                "create_atoms 1 random ${nBeads}  126775  box\n\n\n"
                                "# Define masses and interaction coefficient\n\n"
                                "pair_style   dpdext/fdt ${T} ${rc} 123455\n"
                                "mass         1 1.0\n"
                                "pair_coeff   1 1 ${a} ${sigma} ${sigma} ${s} ${s} ${rcD}\n"
                                "velocity all create ${T} 4928 mom yes dist gaussian\n\n"
                                "fix 1 all shardlow\n"
                                "fix 2 all nve\n"
                                "thermo ${Nfreq}\n"
                                "run ${neql}\n\n"
                                "write_restart  dpd_fluid.restart0\n\n\n"
                                "#Post-processing:\n"
                                "#Green-Kubo viscosity calculation settings\n\n"
                                "reset_timestep 0\n"
                                "variable pxy equal pxy\n"
                                "variable pxz equal pxz\n"
                                "variable pyz equal pyz\n"
                                "variable V   equal vol\n"
                                "variable K   equal 1/(${kb}*$T)*$V*${Nev}*${dt}\n"
                                "fix              SS all ave/correlate ${Nev} ${Nrep} ${Nfreq} &\n"
                                "                v_pxy v_pxz v_pyz type auto file time_cor.txt_${s} ave running\n\n"
                                "variable v11 equal trap(f_SS[3])*${K}\n"
                                "variable v22 equal trap(f_SS[4])*${K}\n"
                                "variable v33 equal trap(f_SS[5])*${K}\n\n"
                                "thermo_style custom step temp press v_v11 v_v22 v_v33\n"
                                "thermo ${Nfreq}\n"
                                "run ${nrun}\n")

            list_filename.append(filename)

        self.list = list_filename

    def launchSims(self,core_numbers):

        def sims(fname):
            command = f"mpirun -np {core_numbers} lmp_mpi -in {fname}"
            subprocess.run(command,shell="True")

        processes = []

        for fname in self.list:
            p = multiprocessing.Process(target=sims, args=[fname])
            p.start()
            processes.append(p)

        for process in processes:
            process.join()

########################################################################################################################

class Launcher_dt:

    def __init__(self,dt,Neql,Nrep,N):

        self.ndim = 3
        self.xsize, self.ysize, self.zsize = 15,15,15
        
        self.rho = 3
        self.kb = 1
        self.T = 1/self.kb
        self.rc = 1
        self.rcD = 1.38
        self.s = 1
        self.a = 265
        self.dt = dt
        self.sigma = 3
        self.nBeads = (self.xsize*self.ysize*self.zsize)*self.rho

        self.neql = Neql
        self.nrun = Nrep*N

        self.Nev = 1
        self.Nrep = Nrep
        self.Nfreq = Nrep
        self.V = 15**3
    
    def initialize(self):
        filename_in = f"in_file.eql_{int(self.neql)}"

        with open(filename_in,"w") as setup:

            setup.write(    "# LAMMPS input script Shardlow's ODEs integration\n"
                            "# DPD simple fluid Schmidt number evaluation\n\n\n"
                            "units       lj\n"
                            f"variable    ndim      equal {self.ndim}\n\n\n"
                                "# Box size\n\n"
                            f"variable    xsize     equal {self.xsize}\n"
                            f"variable    ysize     equal {self.ysize}\n"
                            f"variable    zsize     equal {self.zsize}\n\n\n"
                                "# DPD parameters\n\n"
                            f"variable    rho       equal {self.rho}\n"
                            f"variable    kb        equal {self.kb}\n"
                            f"variable    T         equal {self.T}\n"
                            f"variable    rc        equal {self.rc}\n"
                            f"variable    rcD       equal {self.rcD}\n"
                            f"variable    s         equal {self.s}\n"
                            f"variable    a         equal {self.a}\n"
                            f"variable    dt        equal {self.dt}\n"
                            f"variable    sigma     equal {self.sigma}\n"
                            f"variable    nBeads    equal {self.nBeads}\n\n\n"
                                "# Simulation parameters\n\n"
                                "timestep     ${dt}\n"
                                "dimension    ${ndim} \n"
                            f"variable    neql      equal {self.neql}\n"
                                "# Create simulation box\n\n"
                                "boundary     p p p\n"
                                "atom_style   atomic\n"
                                "comm_modify  vel yes\n"
                                "newton       on\n"
                                "lattice      none 1\n"
                                "region       box block 0 ${xsize} 0 ${ysize} 0 ${zsize}\n" 
                                "create_box   1 box\n"
                                "create_atoms 1 random ${nBeads}  126775  box\n\n\n"
                                "# Define masses and interaction coefficient\n\n"
                                "pair_style   dpdext/fdt ${T} ${rc} 123455\n"
                                "mass         1 1.0\n"
                                "pair_coeff   1 1 ${a} ${sigma} ${sigma} ${s} ${s} ${rcD}\n"
                                "velocity all create ${T} 4928 mom yes dist gaussian\n\n"
                                "fix 1 all shardlow\n"
                                "fix 2 all nve\n"
                            f"thermo {self.Nfreq}\n"
                                "run ${neql}\n\n"
                            f"write_restart  out_file.eql_{int(self.neql)}\n\n\n")
                                
        self.filename_in = filename_in
        subprocess.run(f"mpirun -np 6 lmp_mpi -in {self.filename_in}",shell="True")

        print(f"\n\nTASK COMPLETED - NEW RESTART FILE GENERATED\nfilename: {filename_in}\n\n")

    def generateTxt_2(self,filename_in):

        filename = f"in.Sh_prova_dt_{self.dt}_Nrep_{self.Nrep}"

        with open(filename,"w") as setup:

            setup.write(        "#Post-processing:\n"
                                "#Green-Kubo viscosity calculation settings\n\n"

                            f"read_restart {filename_in}\n"

                            f"timestep     {self.dt}\n"

                            f"variable    neql      equal {self.neql}\n"
                                "comm_modify  vel yes\n"
                                "newton       on\n"
                                "lattice      none 1\n"
                            f"region       box block 0 {self.xsize} 0 {self.ysize} 0 {self.zsize}\n"

                            f"pair_style   dpdext/fdt {self.T} {self.rc} 123455\n"
                                "mass         1 1.0\n"
                            f"pair_coeff   1 1 {self.a} {self.sigma} {self.sigma} {self.s} {self.s} {self.rcD}\n"
                            f"velocity all create {self.T} 4928 mom yes dist gaussian\n\n"

                                "fix 1 all shardlow\n"
                                "fix 2 all nve\n"
                            f"thermo {self.Nfreq}\n"
                                
                                "reset_timestep 0\n"
                                "variable pxy equal pxy\n"
                                "variable pxz equal pxz\n"
                                "variable pyz equal pyz\n"
                                "variable V   equal vol\n"
                            f"variable K   equal 1/({self.kb}*{self.T})*{self.V}*{self.Nev}*{self.dt}\n"
                            f"fix              SS all ave/correlate {self.Nev} {self.Nrep} {self.Nfreq} &\n"
                            f"                v_pxy v_pxz v_pyz type auto file time_cor.txt_{self.s}_{self.Nrep} ave running\n\n"
                                "variable v11 equal trap(f_SS[3])*${K}\n"
                                "variable v22 equal trap(f_SS[4])*${K}\n"
                                "variable v33 equal trap(f_SS[5])*${K}\n\n"
                                "thermo_style custom step temp press v_v11 v_v22 v_v33\n"
                            f"thermo {self.Nfreq}\n"
                            f"run {self.nrun}\n")

        self.filename = filename


    def launchSims(self,core_numbers):

        command = f"mpirun -np {core_numbers} lmp_mpi -in {self.filename}"
        subprocess.run(command,shell="True")
