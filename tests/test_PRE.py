import pytest
import MDAnalysis
import os
import sys
import numpy as np
from DEERpredict.PRE import PREpredict
import pandas as pd

def load_precalcPREs(path,labels,tau_c,Cbeta):
    CB = '_CB' if Cbeta else ''
    data = {}
    for label in labels:
        resnums, data[label] = np.loadtxt(path+'/PRE_1nti_{:g}-{:d}{:s}.dat'.format(tau_c,label,CB),unpack=True)
    df = pd.DataFrame(data,index=resnums)
    df.rename_axis('residue', inplace=True)
    df.rename_axis('label', axis='columns',inplace=True)
    return resnums, df

def load_calcPREs(path,labels):
    data = {}
    for label in labels:
        resnums, data[label], _ = np.loadtxt(path+'/res-{:d}.dat'.format(label),unpack=True)
    df = pd.DataFrame(data, index=resnums)
    df.rename_axis('residue', inplace=True)
    df.rename_axis('label', axis='columns',inplace=True)
    return resnums, df

def calcIratio(path,tau_c,args):
    u, label, tau_t, r_2, Cbeta = args
    PRE = PREpredict(u, label, log_file = path+'/log',
          temperature = 298, Z_cutoff = 0.2, Cbeta = Cbeta, atom_selection = 'H')
    PRE.run(output_prefix = path+'/calcPREs/res', tau_c = tau_c*1e-09, tau_t = tau_t*1e-9,
            k = 1.23e16, r_2 = r_2, wh = 750, delay = 10e-3)

def test_PRE():
    if not os.path.isdir('tests/data/ACBP/calcPREs'):
        os.mkdir('tests/data/ACBP/calcPREs')
    u = MDAnalysis.Universe('tests/data/ACBP/1nti.pdb')
    labels = [17,36,46,65,86]
    for Cbeta in [True,False]:
        for tau_c in [0.1,1]: 
            tau_t = tau_c if tau_c < 0.5 else 0.5
            for label in labels:
                calcIratio('tests/data/ACBP',tau_c,[u, label, tau_t, 12.6, Cbeta])
            resnums, precalcPREs = load_precalcPREs('tests/data/ACBP/precalcPREs',labels,tau_c,Cbeta)
            resnums, calcPREs = load_calcPREs('tests/data/ACBP/calcPREs',labels)
        assert np.power(precalcPREs-calcPREs,2).sum().sum() < 0.3