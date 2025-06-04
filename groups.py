#!/usr/bin/env python
'''
Sensor grouping module for VELO detector sensors.

This module provides explicit lists of sensors grouped by their properties.
'''

# Legend descriptions for each group are included in comments

# R-type sensors on A side
# Legend: "R-type, A-side"
sensors_r_side_a = [
    'PU01_AT', 'PU02_AB', 'VL01_AB', 'VL02_AT', 'VL03_AB', 'VL04_AT', 'VL05_AB',
    'VL06_AT', 'VL07_AB', 'VL08_AT', 'VL09_AB', 'VL10_AT', 'VL11_AB', 'VL12_AT',
    'VL13_AB', 'VL14_AT', 'VL15_AB', 'VL16_AT', 'VL19_AB', 'VL22_AT', 'VL23_AB',
    'VL24_AT', 'VL25_AB'
]

# R-type sensors on C side
# Legend: "R-type, C-side"
sensors_r_side_c = [
    'PU01_CT', 'PU02_CB', 'VL01_CB', 'VL02_CT', 'VL03_CB', 'VL04_CT', 'VL05_CB',
    'VL06_CT', 'VL07_CB', 'VL08_CT', 'VL09_CB', 'VL10_CT', 'VL11_CB', 'VL12_CT',
    'VL13_CB', 'VL14_CT', 'VL15_CB', 'VL16_CT', 'VL19_CB', 'VL22_CT', 'VL23_CB',
    'VL24_CT', 'VL25_CB'
]

# Phi-type sensors on A side
# Legend: "Phi-type, A-side"
sensors_phi_side_a = [
    'VL01_AT', 'VL02_AB', 'VL03_AT', 'VL04_AB', 'VL05_AT', 'VL06_AB', 'VL07_AT',
    'VL08_AB', 'VL09_AT', 'VL10_AB', 'VL11_AT', 'VL12_AB', 'VL13_AT', 'VL14_AB',
    'VL15_AT', 'VL16_AB', 'VL19_AT', 'VL22_AB', 'VL23_AT', 'VL24_AB', 'VL25_AT'
]

# Phi-type sensors on C side
# Legend: "Phi-type, C-side"
sensors_phi_side_c = [
    'VL01_CT', 'VL02_CB', 'VL03_CT', 'VL04_CB', 'VL05_CT', 'VL06_CB', 'VL07_CT',
    'VL08_CB', 'VL09_CT', 'VL10_CB', 'VL11_CT', 'VL12_CB', 'VL13_CT', 'VL14_CB',
    'VL15_CT', 'VL16_CB', 'VL19_CT', 'VL22_CB', 'VL23_CT', 'VL24_CB', 'VL25_CT'
]

# All R-type sensors
# Legend: "R-type sensors"
sensors_r = sensors_r_side_a + sensors_r_side_c

# All Phi-type sensors
# Legend: "Phi-type sensors"
sensors_phi = sensors_phi_side_a + sensors_phi_side_c

# All sensors on side A
# Legend: "Side A"
sensors_side_a = sensors_r_side_a + sensors_phi_side_a

# All sensors on side C
# Legend: "Side C"
sensors_side_c = sensors_r_side_c + sensors_phi_side_c

# All Top (T) sensors
# Legend: "Top (T) sensors"
sensors_type_t = [
    'PU01_AT', 'PU01_CT', 'VL01_AT', 'VL01_CT', 'VL02_AT', 'VL02_CT', 'VL03_AT', 'VL03_CT',
    'VL04_AT', 'VL04_CT', 'VL05_AT', 'VL05_CT', 'VL06_AT', 'VL06_CT', 'VL07_AT', 'VL07_CT',
    'VL08_AT', 'VL08_CT', 'VL09_AT', 'VL09_CT', 'VL10_AT', 'VL10_CT', 'VL11_AT', 'VL11_CT',
    'VL12_AT', 'VL12_CT', 'VL13_AT', 'VL13_CT', 'VL14_AT', 'VL14_CT', 'VL15_AT', 'VL15_CT',
    'VL16_AT', 'VL16_CT', 'VL19_AT', 'VL19_CT', 'VL22_AT', 'VL22_CT', 'VL23_AT', 'VL23_CT',
    'VL24_AT', 'VL24_CT', 'VL25_AT', 'VL25_CT'
]

# All Bottom (B) sensors
# Legend: "Bottom (B) sensors"
sensors_type_b = [
    'PU02_AB', 'PU02_CB', 'VL01_AB', 'VL01_CB', 'VL02_AB', 'VL02_CB', 'VL03_AB', 'VL03_CB',
    'VL04_AB', 'VL04_CB', 'VL05_AB', 'VL05_CB', 'VL06_AB', 'VL06_CB', 'VL07_AB', 'VL07_CB',
    'VL08_AB', 'VL08_CB', 'VL09_AB', 'VL09_CB', 'VL10_AB', 'VL10_CB', 'VL11_AB', 'VL11_CB',
    'VL12_AB', 'VL12_CB', 'VL13_AB', 'VL13_CB', 'VL14_AB', 'VL14_CB', 'VL15_AB', 'VL15_CB',
    'VL16_AB', 'VL16_CB', 'VL19_AB', 'VL19_CB', 'VL22_AB', 'VL22_CB', 'VL23_AB', 'VL23_CB',
    'VL24_AB', 'VL24_CB', 'VL25_AB', 'VL25_CB'
]

# Sensors grouped by z-position ranges
# Legend: "z < -200cm"
sensors_z_lt_m200 = [
    'PU01_AT', 'PU01_CT', 'PU02_AB', 'PU02_CB'
]

# Legend: "z = [-200cm,-100cm]"
sensors_z_m200_m100 = [
    'VL01_AT', 'VL01_AB', 'VL01_CT', 'VL01_CB',
    'VL02_AT', 'VL02_AB', 'VL02_CT', 'VL02_CB',
    'VL03_AT', 'VL03_AB', 'VL03_CT', 'VL03_CB'
]

# Legend: "z = [-100cm,0cm]"
sensors_z_m100_0 = [
    'VL04_AT', 'VL04_AB', 'VL04_CT', 'VL04_CB',
    'VL05_AT', 'VL05_AB', 'VL05_CT', 'VL05_CB',
    'VL06_AT', 'VL06_AB', 'VL06_CT', 'VL06_CB'
]

# Legend: "z = [0cm,100cm]"
sensors_z_0_100 = [
    'VL07_AT', 'VL07_AB', 'VL07_CT', 'VL07_CB',
    'VL08_AT', 'VL08_AB', 'VL08_CT', 'VL08_CB',
    'VL09_AT', 'VL09_AB', 'VL09_CT', 'VL09_CB',
    'VL10_AT', 'VL10_AB', 'VL10_CT', 'VL10_CB'
]

# Legend: "z = [100cm,200cm]"
sensors_z_100_200 = [
    'VL11_AT', 'VL11_AB', 'VL11_CT', 'VL11_CB',
    'VL12_AT', 'VL12_AB', 'VL12_CT', 'VL12_CB',
    'VL13_AT', 'VL13_AB', 'VL13_CT', 'VL13_CB'
]

# Legend: "z = [200cm,300cm]"
sensors_z_200_300 = [
    'VL14_AT', 'VL14_AB', 'VL14_CT', 'VL14_CB',
    'VL15_AT', 'VL15_AB', 'VL15_CT', 'VL15_CB',
    'VL16_AT', 'VL16_AB', 'VL16_CT', 'VL16_CB'
]

# Legend: "z = [300cm,500cm]"
sensors_z_300_500 = [
    'VL19_AT', 'VL19_AB', 'VL19_CT', 'VL19_CB'
]

# Legend: "z = [500cm,700cm]"
sensors_z_500_700 = [
    'VL22_AT', 'VL22_AB', 'VL22_CT', 'VL22_CB',
    'VL23_AT', 'VL23_AB', 'VL23_CT', 'VL23_CB',
    'VL24_AT', 'VL24_AB', 'VL24_CT', 'VL24_CB'
]

# Legend: "z ≥ 700cm"
sensors_z_ge_700 = [
    'VL25_AT', 'VL25_AB', 'VL25_CT', 'VL25_CB'
]

# VL02_CT sensors only
# Legend: "VL02_CT"
vl02_ct_sensors = ['VL02_CT']

# All sensors
# Legend: "All sensors"
all_sensors = sensors_side_a + sensors_side_c

# Dictionary mapping group variables to legend texts
legend_texts = {
    'sensors_r_side_a': "R-type, A-side",
    'sensors_r_side_c': "R-type, C-side",
    'sensors_phi_side_a': "Phi-type, A-side",
    'sensors_phi_side_c': "Phi-type, C-side",
    'sensors_r': "R-type sensors",
    'sensors_phi': "Phi-type sensors",
    'sensors_side_a': "Side A",
    'sensors_side_c': "Side C",
    'sensors_type_t': "Top (T) sensors",
    'sensors_type_b': "Bottom (B) sensors",
    'sensors_z_lt_m200': "z < -200cm",
    'sensors_z_m200_m100': "z = [-200cm,-100cm]",
    'sensors_z_m100_0': "z = [-100cm,0cm]",
    'sensors_z_0_100': "z = [0cm,100cm]",
    'sensors_z_100_200': "z = [100cm,200cm]",
    'sensors_z_200_300': "z = [200cm,300cm]",
    'sensors_z_300_500': "z = [300cm,500cm]",
    'sensors_z_500_700': "z = [500cm,700cm]",
    'sensors_z_ge_700': "z ≥ 700cm",
    'vl02_ct_sensors': "VL02_CT"
}

# Grouping mode definitions
# For each grouping mode, we define:
# - title: Title for the legend
# - groups: List of tuples (sensor_list, group_label, index_for_color)
group_modes = {
    'side': {
        'title': "Sensors by Side",
        'groups': [
            (sensors_side_a, "Side A", 0),
            (sensors_side_c, "Side C", 1)
        ]
    },
    'type': {
        'title': "Sensors by Type",
        'groups': [
            (sensors_r, "R-type", 0),
            (sensors_phi, "Phi-type", 1)
        ]
    },
    'tb': {
        'title': "Sensors by Position (Top/Bottom)",
        'groups': [
            (sensors_type_t, "- (T)", 0),
            (sensors_type_b, "- (B)", 1)
        ]
    },
    'z_position': {
        'title': "Sensors by Z Position",
        'groups': [
            (sensors_z_lt_m200, "z < -200cm", 0),
            (sensors_z_m200_m100, "z = [-200cm,-100cm]", 1),
            (sensors_z_m100_0, "z = [-100cm,0cm]", 2),
            (sensors_z_0_100, "z = [0cm,100cm]", 3),
            (sensors_z_100_200, "z = [100cm,200cm]", 4),
            (sensors_z_200_300, "z = [200cm,300cm]", 5),
            (sensors_z_300_500, "z = [300cm,500cm]", 6),
            (sensors_z_500_700, "z = [500cm,700cm]", 7),
            (sensors_z_ge_700, "z ≥ 700cm", 8)
        ]
    },
    'none': {
        'title': "All Sensors",
        'groups': []
    }
}
