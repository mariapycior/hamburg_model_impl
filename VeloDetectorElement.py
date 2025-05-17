class VeloDetectorElement():
    """ ------------------------------------------------------------------- """
    """  Can return information regarding sensor number, sensor position    """
    """  and sensor type R = 1, Phi = 0                                     """
    """ ------------------------------------------------------------------- """

    def __init__(self):
        self.__members__ = {
            'Type'      : 'VeloDetectorElement'
            ,'__Velo_Det__'  : { }
        }
        self.__createMap__()
        self._HV_CHANNEL = 0
        self._SENSOR = 1
        self._Z = 2
        self._SENSOR_TYPE = 3

    def __createMap__(self):
        # -> header data have format as follow: maXX/chXX
        #    map will relate hardware channels with labels and sensors
        # ----------------------
        # -> side C, HV_Board00
        self.__members__['__Velo_Det__']['PU01_CT','HV']= ['ma06/ch00', 129, -300., 1]
        self.__members__['__Velo_Det__']['PU02_CB','HV'] = ['ma06/ch01', 131, -220., 1]
        self.__members__['__Velo_Det__']['VL01_CT','HV'] = ['ma06/ch02', 65, -160., 0]
        self.__members__['__Velo_Det__']['VL01_CB','HV'] = ['ma06/ch03', 1, -160., 1]
        self.__members__['__Velo_Det__']['VL02_CT','HV'] = ['ma06/ch04', 3, -130., 1]
        self.__members__['__Velo_Det__']['VL02_CB','HV'] = ['ma06/ch05', 67, -130., 0]
        self.__members__['__Velo_Det__']['VL03_CT','HV'] = ['ma06/ch06', 69, -100., 0]
        self.__members__['__Velo_Det__']['VL03_CB','HV'] = ['ma06/ch07', 5, -100., 1]
        # -> side C, HV_Board01
        self.__members__['__Velo_Det__']['VL04_CT','HV'] = ['ma07/ch00', 7, 70., 1]
        self.__members__['__Velo_Det__']['VL04_CB','HV'] = ['ma07/ch01', 71, -70.,0]
        self.__members__['__Velo_Det__']['VL05_CT','HV'] = ['ma07/ch02', 73, -40., 0]
        self.__members__['__Velo_Det__']['VL05_CB','HV'] = ['ma07/ch03', 9, -40., 1]
        self.__members__['__Velo_Det__']['VL06_CT','HV'] = ['ma07/ch04', 11, -10., 1]
        self.__members__['__Velo_Det__']['VL06_CB','HV'] = ['ma07/ch05', 75, -10., 0]
        self.__members__['__Velo_Det__']['VL07_CT','HV'] = ['ma07/ch06', 77, 20., 0]
        self.__members__['__Velo_Det__']['VL07_CB','HV'] = ['ma07/ch07', 13, 20., 1]
        # -> side C, HV_Board02
        self.__members__['__Velo_Det__']['VL08_CT','HV'] = ['ma08/ch00', 15, 50., 1]
        self.__members__['__Velo_Det__']['VL08_CB','HV'] = ['ma08/ch01', 79, 50., 0]
        self.__members__['__Velo_Det__']['VL09_CT','HV'] = ['ma08/ch02', 81, 80., 0]
        self.__members__['__Velo_Det__']['VL09_CB','HV'] = ['ma08/ch03', 17, 80., 1]
        self.__members__['__Velo_Det__']['VL10_CT','HV'] = ['ma08/ch04', 19, 80., 1]
        self.__members__['__Velo_Det__']['VL10_CB','HV'] = ['ma08/ch05', 83, 110., 0]
        self.__members__['__Velo_Det__']['VL11_CT','HV'] = ['ma08/ch06', 85, 140., 0]
        self.__members__['__Velo_Det__']['VL11_CB','HV'] = ['ma08/ch07', 21, 140., 1]
        # -> side C, HV_Board03
        self.__members__['__Velo_Det__']['VL12_CT','HV'] = ['ma09/ch00', 23, 170., 1]
        self.__members__['__Velo_Det__']['VL12_CB','HV'] = ['ma09/ch01', 87, 170., 0]
        self.__members__['__Velo_Det__']['VL13_CT','HV'] = ['ma09/ch02', 89, 200., 0]
        self.__members__['__Velo_Det__']['VL13_CB','HV'] = ['ma09/ch03', 25, 200., 1]
        self.__members__['__Velo_Det__']['VL14_CT','HV'] = ['ma09/ch04', 27, 230., 1]
        self.__members__['__Velo_Det__']['VL14_CB','HV'] = ['ma09/ch05', 91, 230., 0]
        self.__members__['__Velo_Det__']['VL15_CT','HV'] = ['ma09/ch06', 93, 260., 0]
        self.__members__['__Velo_Det__']['VL15_CB','HV'] = ['ma09/ch07', 29, 260., 1]
        # -> side C, HV_Board04
        self.__members__['__Velo_Det__']['VL16_CT','HV'] = ['ma10/ch00', 31, 290., 1]
        self.__members__['__Velo_Det__']['VL16_CB','HV'] = ['ma10/ch01', 95, 290., 0]
        self.__members__['__Velo_Det__']['VL19_CT','HV'] = ['ma10/ch02', 97, 450., 0]
        self.__members__['__Velo_Det__']['VL19_CB','HV'] = ['ma10/ch03', 33, 450., 1]
        self.__members__['__Velo_Det__']['VL22_CT','HV'] = ['ma10/ch04', 35, 600., 1]
        self.__members__['__Velo_Det__']['VL22_CB','HV'] = ['ma10/ch05', 99, 600., 0]
        self.__members__['__Velo_Det__']['VL23_CT','HV'] = ['ma10/ch06', 101, 650., 0]
        self.__members__['__Velo_Det__']['VL23_CB','HV'] = ['ma10/ch07', 37, 650., 1]
        # -> side C, HV_Board05
        self.__members__['__Velo_Det__']['VL24_CT','HV'] = ['ma11/ch00', 39, 700., 1]
        self.__members__['__Velo_Det__']['VL24_CB','HV'] = ['ma11/ch01', 103, 700., 0]
        self.__members__['__Velo_Det__']['VL25_CT','HV'] = ['ma11/ch02', 105, 750., 0]
        self.__members__['__Velo_Det__']['VL25_CB','HV'] = ['ma11/ch03', 41, 750., 1]
        # ----------------------
        # -> side A, HV_Board00
        self.__members__['__Velo_Det__']['PU01_AT','HV'] = ['ma00/ch00', 130, -315., 1]
        self.__members__['__Velo_Det__']['PU02_AB','HV'] = ['ma00/ch01', 128, -235., 1]
        self.__members__['__Velo_Det__']['VL01_AT','HV'] = ['ma00/ch02', 64, -175., 0]
        self.__members__['__Velo_Det__']['VL01_AB','HV'] = ['ma00/ch03', 0, -175., 1]
        self.__members__['__Velo_Det__']['VL02_AT','HV'] = ['ma00/ch04', 2, -145., 1]
        self.__members__['__Velo_Det__']['VL02_AB','HV'] = ['ma00/ch05', 66, -145., 0]
        self.__members__['__Velo_Det__']['VL03_AT','HV'] = ['ma00/ch06', 68, -115., 0]
        self.__members__['__Velo_Det__']['VL03_AB','HV'] = ['ma00/ch07', 4, -115., 1]
        # -> side A, HV_Board01
        self.__members__['__Velo_Det__']['VL04_AT','HV'] = ['ma01/ch00', 6, -85., 1]
        self.__members__['__Velo_Det__']['VL04_AB','HV'] = ['ma01/ch01', 70, -85., 0]
        self.__members__['__Velo_Det__']['VL05_AT','HV'] = ['ma01/ch02', 72, -55., 0]
        self.__members__['__Velo_Det__']['VL05_AB','HV'] = ['ma01/ch03', 8, -55., 1]
        self.__members__['__Velo_Det__']['VL06_AT','HV'] = ['ma01/ch04', 10, -25., 1]
        self.__members__['__Velo_Det__']['VL06_AB','HV'] = ['ma01/ch05', 74, -25., 0]
        self.__members__['__Velo_Det__']['VL07_AT','HV'] = ['ma01/ch06', 76, 5., 0]
        self.__members__['__Velo_Det__']['VL07_AB','HV'] = ['ma01/ch07', 12, 5., 1]
        # -> side A, HV_Board02
        self.__members__['__Velo_Det__']['VL08_AT','HV'] = ['ma02/ch00', 14, 35., 1]
        self.__members__['__Velo_Det__']['VL08_AB','HV'] = ['ma02/ch01', 78, 35., 0]
        self.__members__['__Velo_Det__']['VL09_AT','HV'] = ['ma02/ch02', 80, 65., 0]
        self.__members__['__Velo_Det__']['VL09_AB','HV'] = ['ma02/ch03', 16, 65., 1]
        self.__members__['__Velo_Det__']['VL10_AT','HV'] = ['ma02/ch04', 18, 95., 1]
        self.__members__['__Velo_Det__']['VL10_AB','HV'] = ['ma02/ch05', 82, 95., 0]
        self.__members__['__Velo_Det__']['VL11_AT','HV'] = ['ma02/ch06', 84, 125., 0]
        self.__members__['__Velo_Det__']['VL11_AB','HV'] = ['ma02/ch07', 20, 125., 1]
        # -> side C, HV_Board03
        self.__members__['__Velo_Det__']['VL12_AT','HV'] = ['ma03/ch00', 22, 155., 1]
        self.__members__['__Velo_Det__']['VL12_AB','HV'] = ['ma03/ch01', 86, 155., 0]
        self.__members__['__Velo_Det__']['VL13_AT','HV'] = ['ma03/ch02', 88, 185., 0]
        self.__members__['__Velo_Det__']['VL13_AB','HV'] = ['ma03/ch03', 24, 185., 1]
        self.__members__['__Velo_Det__']['VL14_AT','HV'] = ['ma03/ch04', 26, 215., 1]
        self.__members__['__Velo_Det__']['VL14_AB','HV'] = ['ma03/ch05', 90, 215., 0]
        self.__members__['__Velo_Det__']['VL15_AT','HV'] = ['ma03/ch06', 92, 245., 0]
        self.__members__['__Velo_Det__']['VL15_AB','HV'] = ['ma03/ch07', 28, 245., 1]
        # -> side A, HV_Board04
        self.__members__['__Velo_Det__']['VL16_AT','HV'] = ['ma04/ch00', 30, 275., 1]
        self.__members__['__Velo_Det__']['VL16_AB','HV'] = ['ma04/ch01', 94, 305., 0]
        self.__members__['__Velo_Det__']['VL19_AT','HV'] = ['ma04/ch02', 96, 435., 0]
        self.__members__['__Velo_Det__']['VL19_AB','HV'] = ['ma04/ch03', 32, 435., 1]
        self.__members__['__Velo_Det__']['VL22_AT','HV'] = ['ma04/ch04', 34, 585., 1]
        self.__members__['__Velo_Det__']['VL22_AB','HV'] = ['ma04/ch05', 98, 585., 0]
        self.__members__['__Velo_Det__']['VL23_AT','HV'] = ['ma04/ch06', 100, 635., 0]
        self.__members__['__Velo_Det__']['VL23_AB','HV'] = ['ma04/ch07', 36, 635., 1]
        # -> side A, HV_Board05
        self.__members__['__Velo_Det__']['VL24_AT','HV'] = ['ma05/ch00', 38, 685., 1]
        self.__members__['__Velo_Det__']['VL24_AB','HV'] = ['ma05/ch01', 102, 685., 0]
        self.__members__['__Velo_Det__']['VL25_AT','HV'] = ['ma05/ch02', 104, 735., 0]
        self.__members__['__Velo_Det__']['VL25_AB','HV'] = ['ma05/ch03', 40, 735., 1]

        #NTC 01
        
        self.__members__['__Velo_Det__']['PU01_CT','NTC01'] = ['VeloCTempBoard1/AI/NTC_03', 129, -300., 1]
        self.__members__['__Velo_Det__']['PU02_CB','NTC01'] = ['VeloCTempBoard1/AI/NTC_07', 131, -220., 1]
        self.__members__['__Velo_Det__']['VL01_CT','NTC01'] = ['VeloCTempBoard1/AI/NTC_11', 65, -160., 0]
        self.__members__['__Velo_Det__']['VL01_CB','NTC01'] = ['VeloCTempBoard1/AI/NTC_15', 1, -160., 1]
        self.__members__['__Velo_Det__']['VL02_CT','NTC01'] = ['VeloCTempBoard1/AI/NTC_19', 3, -130., 1]
        self.__members__['__Velo_Det__']['VL02_CB','NTC01'] = ['VeloCTempBoard1/AI/NTC_23', 67, -130., 0]
        self.__members__['__Velo_Det__']['VL03_CT','NTC01'] = ['VeloCTempBoard1/AI/NTC_27', 69, -100., 0]
        self.__members__['__Velo_Det__']['VL03_CB','NTC01'] = ['VeloCTempBoard1/AI/NTC_31', 5, -100., 1]
        # -> side C, HV_Board01
        
        self.__members__['__Velo_Det__']['VL04_CT','NTC01'] = ['VeloCTempBoard1/AI/NTC_35', 7, 70., 1]
        self.__members__['__Velo_Det__']['VL04_CB','NTC01'] = ['VeloCTempBoard1/AI/NTC_39', 71, -70.,0]
        self.__members__['__Velo_Det__']['VL05_CT','NTC01'] = ['VeloCTempBoard1/AI/NTC_43', 73, -40., 0]
        self.__members__['__Velo_Det__']['VL05_CB','NTC01'] = ['VeloCTempBoard1/AI/NTC_47', 9, -40., 1]
        self.__members__['__Velo_Det__']['VL06_CT','NTC01'] = ['VeloCTempBoard1/AI/NTC_51', 11, -10., 1]
        self.__members__['__Velo_Det__']['VL06_CB','NTC01'] = ['VeloCTempBoard1/AI/NTC_55', 75, -10., 0]
        self.__members__['__Velo_Det__']['VL07_CT','NTC01'] = ['VeloCTempBoard1/AI/NTC_59', 77, 20., 0]
        self.__members__['__Velo_Det__']['VL07_CB','NTC01'] = ['VeloCTempBoard1/AI/NTC_63', 13, 20., 1]
        # -> side C, HV_Board02
        self.__members__['__Velo_Det__']['VL08_CT','NTC01'] = ['VeloCTempBoard2/AI/NTC_03', 15, 50., 1]
        self.__members__['__Velo_Det__']['VL08_CB','NTC01'] = ['VeloCTempBoard2/AI/NTC_07', 79, 50., 0]
        self.__members__['__Velo_Det__']['VL09_CT','NTC01'] = ['VeloCTempBoard2/AI/NTC_11', 81, 80., 0]
        self.__members__['__Velo_Det__']['VL09_CB','NTC01'] = ['VeloCTempBoard2/AI/NTC_15', 17, 80., 1]
        self.__members__['__Velo_Det__']['VL10_CT','NTC01'] = ['VeloCTempBoard2/AI/NTC_19', 19, 80., 1]
        self.__members__['__Velo_Det__']['VL10_CB','NTC01'] = ['VeloCTempBoard2/AI/NTC_23', 83, 110., 0]
        self.__members__['__Velo_Det__']['VL11_CT','NTC01'] = ['VeloCTempBoard2/AI/NTC_27', 85, 140., 0]
        self.__members__['__Velo_Det__']['VL11_CB','NTC01'] = ['VeloCTempBoard2/AI/NTC_31', 21, 140., 1]
        # -> side C, HV_Board03
        self.__members__['__Velo_Det__']['VL12_CT','NTC01'] = ['VeloCTempBoard2/AI/NTC_35', 23, 170., 1]
        self.__members__['__Velo_Det__']['VL12_CB','NTC01'] = ['VeloCTempBoard2/AI/NTC_39', 87, 170., 0]
        self.__members__['__Velo_Det__']['VL13_CT','NTC01'] = ['VeloCTempBoard2/AI/NTC_43', 89, 200., 0]
        self.__members__['__Velo_Det__']['VL13_CB','NTC01'] = ['VeloCTempBoard2/AI/NTC_47', 25, 200., 1]
        self.__members__['__Velo_Det__']['VL14_CT','NTC01'] = ['VeloCTempBoard2/AI/NTC_51', 27, 230., 1]
        self.__members__['__Velo_Det__']['VL14_CB','NTC01'] = ['VeloCTempBoard2/AI/NTC_55', 91, 230., 0]
        self.__members__['__Velo_Det__']['VL15_CT','NTC01'] = ['VeloCTempBoard2/AI/NTC_59', 93, 260., 0]
        self.__members__['__Velo_Det__']['VL15_CB','NTC01'] = ['VeloCTempBoard2/AI/NTC_63', 29, 260., 1]
        # -> side C, HV_Board04
        self.__members__['__Velo_Det__']['VL16_CT','NTC01'] = ['VeloCTempBoard3/AI/NTC_03', 31, 290., 1]
        self.__members__['__Velo_Det__']['VL16_CB','NTC01'] = ['VeloCTempBoard3/AI/NTC_07', 95, 290., 0]
        self.__members__['__Velo_Det__']['VL19_CT','NTC01'] = ['VeloCTempBoard3/AI/NTC_11', 97, 450., 0]
        self.__members__['__Velo_Det__']['VL19_CB','NTC01'] = ['VeloCTempBoard3/AI/NTC_15', 33, 450., 1]
        self.__members__['__Velo_Det__']['VL22_CT','NTC01'] = ['VeloCTempBoard3/AI/NTC_19', 35, 600., 1]
        self.__members__['__Velo_Det__']['VL22_CB','NTC01'] = ['VeloCTempBoard3/AI/NTC_23', 99, 600., 0]
        self.__members__['__Velo_Det__']['VL23_CT','NTC01'] = ['VeloCTempBoard3/AI/NTC_27', 101, 650., 0]
        self.__members__['__Velo_Det__']['VL23_CB','NTC01'] = ['VeloCTempBoard3/AI/NTC_31', 37, 650., 1]
        # -> side C, HV_Board05
        self.__members__['__Velo_Det__']['VL24_CT','NTC01'] = ['VeloCTempBoard3/AI/NTC_35', 39, 700., 1]
        self.__members__['__Velo_Det__']['VL24_CB','NTC01'] = ['VeloCTempBoard3/AI/NTC_39', 103, 700., 0]
        self.__members__['__Velo_Det__']['VL25_CT','NTC01'] = ['VeloCTempBoard3/AI/NTC_43', 105, 750., 0]
        self.__members__['__Velo_Det__']['VL25_CB','NTC01'] = ['VeloCTempBoard3/AI/NTC_47', 41, 750., 1]
        # ----------------------

        # -> side A, HV_Board00
        self.__members__['__Velo_Det__']['PU01_AT','NTC01'] = ['VeloATempBoard1/AI/NTC_03', 130, -315., 1]
        self.__members__['__Velo_Det__']['PU02_AB','NTC01'] = ['VeloATempBoard1/AI/NTC_07', 128, -235., 1]
        self.__members__['__Velo_Det__']['VL01_AT','NTC01'] = ['VeloATempBoard1/AI/NTC_11', 64, -175., 0]
        self.__members__['__Velo_Det__']['VL01_AB','NTC01'] = ['VeloATempBoard1/AI/NTC_15', 0, -175., 1]
        self.__members__['__Velo_Det__']['VL02_AT','NTC01'] = ['VeloATempBoard1/AI/NTC_19', 2, -145., 1]
        self.__members__['__Velo_Det__']['VL02_AB','NTC01'] = ['VeloATempBoard1/AI/NTC_23', 66, -145., 0]
        self.__members__['__Velo_Det__']['VL03_AT','NTC01'] = ['VeloATempBoard1/AI/NTC_27', 68, -115., 0]
        self.__members__['__Velo_Det__']['VL03_AB','NTC01'] = ['VeloATempBoard1/AI/NTC_31', 4, -115., 1]
        # -> side A, HV_Board01
        self.__members__['__Velo_Det__']['VL04_AT','NTC01'] = ['VeloATempBoard1/AI/NTC_35', 6, -85., 1]
        self.__members__['__Velo_Det__']['VL04_AB','NTC01'] = ['VeloATempBoard1/AI/NTC_39', 70, -85., 0]
        self.__members__['__Velo_Det__']['VL05_AT','NTC01'] = ['VeloATempBoard1/AI/NTC_43', 72, -55., 0]
        self.__members__['__Velo_Det__']['VL05_AB','NTC01'] = ['VeloATempBoard1/AI/NTC_47', 8, -55., 1]
        self.__members__['__Velo_Det__']['VL06_AT','NTC01'] = ['VeloATempBoard1/AI/NTC_51', 10, -25., 1]
        self.__members__['__Velo_Det__']['VL06_AB','NTC01'] = ['VeloATempBoard1/AI/NTC_55', 74, -25., 0]
        self.__members__['__Velo_Det__']['VL07_AT','NTC01'] = ['VeloATempBoard1/AI/NTC_59', 76, 5., 0]
        self.__members__['__Velo_Det__']['VL07_AB','NTC01'] = ['VeloATempBoard1/AI/NTC_63', 12, 5., 1]
        # -> side A, HV_Board02
        self.__members__['__Velo_Det__']['VL08_AT','NTC01'] = ['VeloATempBoard2/AI/NTC_03', 14, 35., 1]
        self.__members__['__Velo_Det__']['VL08_AB','NTC01'] = ['VeloATempBoard2/AI/NTC_07', 78, 35., 0]
        self.__members__['__Velo_Det__']['VL09_AT','NTC01'] = ['VeloATempBoard2/AI/NTC_11', 80, 65., 0]
        self.__members__['__Velo_Det__']['VL09_AB','NTC01'] = ['VeloATempBoard2/AI/NTC_15', 16, 65., 1]
        self.__members__['__Velo_Det__']['VL10_AT','NTC01'] = ['VeloATempBoard2/AI/NTC_19', 18, 95., 1]
        self.__members__['__Velo_Det__']['VL10_AB','NTC01'] = ['VeloATempBoard2/AI/NTC_23', 82, 95., 0]
        self.__members__['__Velo_Det__']['VL11_AT','NTC01'] = ['VeloATempBoard2/AI/NTC_27', 84, 125., 0]
        self.__members__['__Velo_Det__']['VL11_AB','NTC01'] = ['VeloATempBoard2/AI/NTC_31', 20, 125., 1]
        # -> side C, HV_Board03
        self.__members__['__Velo_Det__']['VL12_AT','NTC01'] = ['VeloATempBoard2/AI/NTC_35', 22, 155., 1]
        self.__members__['__Velo_Det__']['VL12_AB','NTC01'] = ['VeloATempBoard2/AI/NTC_39', 86, 155., 0]
        self.__members__['__Velo_Det__']['VL13_AT','NTC01'] = ['VeloATempBoard2/AI/NTC_43', 88, 185., 0]
        self.__members__['__Velo_Det__']['VL13_AB','NTC01'] = ['VeloATempBoard2/AI/NTC_47', 24, 185., 1]
        self.__members__['__Velo_Det__']['VL14_AT','NTC01'] = ['VeloATempBoard2/AI/NTC_51', 26, 215., 1]
        self.__members__['__Velo_Det__']['VL14_AB','NTC01'] = ['VeloATempBoard2/AI/NTC_55', 90, 215., 0]
        self.__members__['__Velo_Det__']['VL15_AT','NTC01'] = ['VeloATempBoard2/AI/NTC_59', 92, 245., 0]
        self.__members__['__Velo_Det__']['VL15_AB','NTC01'] = ['VeloATempBoard2/AI/NTC_63', 28, 245., 1]
        # -> side A, HV_Board04
        self.__members__['__Velo_Det__']['VL16_AT','NTC01'] = ['VeloATempBoard3/AI/NTC_03', 30, 275., 1]
        self.__members__['__Velo_Det__']['VL16_AB','NTC01'] = ['VeloATempBoard3/AI/NTC_07', 94, 305., 0]
        self.__members__['__Velo_Det__']['VL19_AT','NTC01'] = ['VeloATempBoard3/AI/NTC_11', 96, 435., 0]
        self.__members__['__Velo_Det__']['VL19_AB','NTC01'] = ['VeloATempBoard3/AI/NTC_15', 32, 435., 1]
        self.__members__['__Velo_Det__']['VL22_AT','NTC01'] = ['VeloATempBoard3/AI/NTC_19', 34, 585., 1]
        self.__members__['__Velo_Det__']['VL22_AB','NTC01'] = ['VeloATempBoard3/AI/NTC_23', 98, 585., 0]
        self.__members__['__Velo_Det__']['VL23_AT','NTC01'] = ['VeloATempBoard3/AI/NTC_27', 100, 635., 0]
        self.__members__['__Velo_Det__']['VL23_AB','NTC01'] = ['VeloATempBoard3/AI/NTC_31', 36, 635., 1]
        # -> side A, HV_Board05
        self.__members__['__Velo_Det__']['VL24_AT','NTC01'] = ['VeloATempBoard3/AI/NTC_35', 38, 685., 1]
        self.__members__['__Velo_Det__']['VL24_AB','NTC01'] = ['VeloATempBoard3/AI/NTC_39', 102, 685., 0]
        self.__members__['__Velo_Det__']['VL25_AT','NTC01'] = ['VeloATempBoard3/AI/NTC_43', 104, 735., 0]
        self.__members__['__Velo_Det__']['VL25_AB','NTC01'] = ['VeloATempBoard3/AI/NTC_47', 40, 735., 1]

        # NTC00

       

    @property
    def HV_CHANNEL(self):
        return ( self._HV_CHANNEL )

    @property
    def SENSOR(self):
        return ( self._SENSOR )

    @property
    def Z(self):
        return ( self._Z )

    @property
    def SENSOR_TYPE(self):
        return ( self._SENSOR_TYPE )

    # -> translate sensor name to hv module channel
    def sensor_name2channel(self, name):
        return ( self.__members__['__Velo_Det__'][name][self.HV_CHANNEL] )

    # -> get sensor number for a given sensor name
    def sensor_name2sensor_number(self, name):
        return ( self.__members__['__Velo_Det__'][name][self.SENSOR] )

    # -> get z position for a given sensor name
    def sensor_name2sensor_z(self, name):
        return ( self.__members__['__Velo_Det__'][name][self.Z] )

    # -> get sensor type for a given sensor name
    def sensor_name2sensor_type(self, name):
        return ( self.__members__['__Velo_Det__'][name][self.SENSOR_TYPE] )
    
    # -> get sensor name for a given sensor number
    def sensor_number2sensor_name(self,number):
        for key, value in self.__members__['__Velo_Det__'].items():
            if number == value[1]:
                return key[0]
    # -> get sensor name for a given sensor number
    def channel2sensor_name(self,channel):
        for key, value in self.__members__['__Velo_Det__'].items():
            if channel == value[0]:
                return key[0]
    
    def get_keys(self):
        keys = []
        for key, value in self.__members__["__Velo_Det__"].items():
            # Extract the sensor number from the third element (index 1) of the value list
            keys.append(key[0])
        keys = list(set(keys))
        return keys

