"""
Physical parameters for the Hamburg model simulation.

This file contains all physical constants and parameters used in the
Hamburg model for leakage current simulation.
"""

# Physical constants
KB = 8.617333262145e-5  # Boltzmann constant in eV/K
T_REF = 294.15  # Reference temperature in K

# Hamburg model parameters
E_I_STAR = 1.30  # Energy in eV
ALPHA_I = 1.23e-17  # Current-related damage rate in A/cm
ALPHA_0_STAR = 7.07e-17  # Current-related damage coefficient in A/cm
BETA = 3.29e-18  # Second order damage coefficient in A/cm
E_I = 1.11  # Activation energy in eV
K_0I = 1.2e13  # Frequency factor in s^-1
T_0 = 1.0  # Reference time in days
V = 0.805  # Bias voltage in V
E_EFF = 1.20  # Effective activation energy in eV

class Parameters:
    """Container for simulation parameters.
    
    This class holds all the physical constants and parameters needed for the
    Hamburg model simulation of leakage current.
    """
    def __init__(self):
        self.kb = KB
        self.T_ref = T_REF
        self.E_I_star = E_I_STAR
        self.alpha_I = ALPHA_I
        self.alpha_0_star = ALPHA_0_STAR
        self.beta = BETA
        self.E_I = E_I
        self.k_0I = K_0I
        self.t_0 = T_0
        self.V = V
        self.E_eff = E_EFF
