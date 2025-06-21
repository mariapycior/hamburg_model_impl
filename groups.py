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
#6ecf840a-7742-4098-80c1-a1c441c6e040

# Sensors grouped by z-position ranges (using absolute values)
# Legend: "0 ≤ |z| ≤ 50mm"
sensors_z_0_50 = [
    'VL08_AT',  # z = 35mm
    'VL08_AB',  # z = 35mm
    'VL08_CT',  # z = 50mm
    'VL08_CB',  # z = 50mm
    'VL05_CT',  # z = 40mm
    'VL05_CB',  # z = 40mm
    'VL06_AT',  # z = 25mm
    'VL06_AB',  # z = 25mm
    'VL06_CT',  # z = 10mm
    'VL06_CB',  # z = 10mm
    'VL07_AT',  # z = 5mm
    'VL07_AB',  # z = 5mm
    'VL07_CT',  # z = 20mm
    'VL07_CB'   # z = 20mm
]

# Legend: "50mm < |z| ≤ 100mm"
sensors_z_50_100 = [
    'VL05_AT',  # z = 55mm
    'VL05_AB',  # z = 55mm
    'VL04_AT',  # z = 85mm
    'VL04_AB',  # z = 85mm
    'VL04_CT',  # z = 70mm
    'VL04_CB',  # z = 70mm
    'VL09_AT',  # z = 65mm
    'VL09_AB',  # z = 65mm
    'VL09_CT',  # z = 80mm
    'VL09_CB',  # z = 80mm
    'VL10_AT',  # z = 95mm
    'VL10_AB',  # z = 95mm
    'VL10_CT',  # z = 80mm
    'VL10_CB'   # z = 80mm
]

# Legend: "100mm < |z| ≤ 200mm"
sensors_z_100_200 = [
    'VL01_AT',  # z = 175mm
    'VL01_AB',  # z = 175mm
    'VL01_CT',  # z = 160mm
    'VL01_CB',  # z = 160mm
    'VL02_AT',  # z = 145mm
    'VL02_AB',  # z = 145mm
    'VL02_CT',  # z = 130mm
    'VL02_CB',  # z = 130mm
    'VL03_AT',  # z = 115mm
    'VL03_AB',  # z = 115mm
    'VL03_CT',  # z = 100mm
    'VL03_CB',  # z = 100mm
    'VL11_AT',  # z = 125mm
    'VL11_AB',  # z = 125mm
    'VL11_CT',  # z = 140mm
    'VL11_CB',  # z = 140mm
    'VL12_AT',  # z = 155mm
    'VL12_AB',  # z = 155mm
    'VL12_CT',  # z = 170mm
    'VL12_CB',  # z = 170mm
    'VL13_AT',  # z = 185mm
    'VL13_AB',  # z = 185mm
    'VL13_CT',  # z = 200mm
    'VL13_CB',  # z = 200mm
]

# Legend: "200mm < |z| ≤ 400mm"
sensors_z_200_400 = [
    'VL14_AT',  # z = 215mm
    'VL14_AB',  # z = 215mm
    'VL14_CT',  # z = 230mm
    'VL14_CB'   # z = 230mm
    'VL15_AT',  # z = 245mm
    'VL15_AB',  # z = 245mm
    'VL15_CT',  # z = 260mm
    'VL15_CB',  # z = 260mm
    'VL16_AT',  # z = 275mm
    'VL16_AB',  # z = 305mm
    'VL16_CT',  # z = 290mm
    'VL16_CB'   # z = 290mm
]

# Legend: "400mm < |z| ≤ 700mm"
sensors_z_400_700 = [
    'VL19_AT',  # z = 435mm
    'VL19_AB',  # z = 435mm
    'VL19_CT',  # z = 450mm
    'VL19_CB',  # z = 450mm
    'VL22_AT',  # z = 585mm
    'VL22_AB',  # z = 585mm
    'VL22_CT',  # z = 600mm
    'VL22_CB',  # z = 600mm
    'VL23_AT',  # z = 635mm
    'VL23_AB',  # z = 635mm
    'VL23_CT',  # z = 650mm
    'VL23_CB'   # z = 650mm
    'VL24_AT',  # z = 685mm
    'VL24_AB',  # z = 685mm
]

# Legend: "|z| > 700mm"
sensors_z_gt_700 = [

    'VL24_CT',  # z = 700mm
    'VL24_CB',  # z = 700mm
    'VL25_AT',  # z = 735mm
    'VL25_AB',  # z = 735mm
    'VL25_CT',  # z = 750mm
    'VL25_CB'   # z = 750mm
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
    'sensors_side_a': "Side A",
    'sensors_side_c': "Side C",
    'sensors_type_t': "Top (T) sensors",
    'sensors_type_b': "Bottom (B) sensors",
    'sensors_z_0_50': "0 ≤ |z| ≤ 50mm",
    'sensors_z_50_100': "50mm < |z| ≤ 100mm",
    'sensors_z_100_200': "100mm < |z| ≤ 200mm",
    'sensors_z_200_400': "200mm < |z| ≤ 400mm",
    'sensors_z_400_700': "400mm < |z| ≤ 700mm",
    'sensors_z_gt_700_abs': "|z| > 700mm"
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
        'title': "Sensors by Position (T/B)",
        'groups': [
            (sensors_type_t, "- (T)", 0),
            (sensors_type_b, "- (B)", 1)
        ]
    },
    'z_position': {
        'title': "Sensors by Z Position",
        'groups': [
            (sensors_z_0_50, legend_texts['sensors_z_0_50'], 0),
            (sensors_z_50_100, legend_texts['sensors_z_50_100'], 1),
            (sensors_z_100_200, legend_texts['sensors_z_100_200'], 2),
            (sensors_z_200_400, legend_texts['sensors_z_200_400'], 3),
            (sensors_z_400_700, legend_texts['sensors_z_400_700'], 4),
            (sensors_z_gt_700, "|z| > 700mm", 5)  # lub legend_texts['sensors_z_gt_700_abs'] jeśli zmienisz nazwę zmiennej
        ]

    },
    'none': {
        'title': "All Sensors",
        'groups': []
    }
}
