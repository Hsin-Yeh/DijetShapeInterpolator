#!/usr/bin/env python

import sys, os
from argparse import ArgumentParser
from array import array
import numpy as np


# class storing input shape info
class ShapeStorage:
    def __init__(self, shapes, binxcenters):
        self.shapes = shapes
        self.binxcenters = binxcenters

        if len(self.shapes) < 2:
           print "** ERROR: ** Need at least 2 input shapes, %i provided. Aborting."%(len(self.shapes))
           sys.exit(1)
        nbins = []
        nbins.append(len(self.binxcenters))
        for key in self.shapes.keys():
            norm = sum(self.shapes[key])
            if abs(norm - 1.) > 0.01:
                print "** ERROR: ** Input shape for m =", key, "GeV not normalized. Make sure the input shapes are normalized to unity. Aborting."
                sys.exit(3)
            nbins.append(len(self.shapes[key]))
        if len(set(nbins)) > 1:
           print "** ERROR: ** Numbers of bins for different input shapes and the number of bin centers are not all identical. Aborting."
           sys.exit(2)


def LineShapePDF(shapes, mass, histo):
    # import ROOT
    from ROOT import Math

    x = shapes.binxcenters
    #print(x[0],x[-1])
    y = np.array([])
    if mass in shapes.shapes.keys():
        y = np.array(shapes.shapes[mass])
    else:
        input_masses = shapes.shapes.keys()
        # print(input_masses)
        min_mass = min(input_masses)
        max_mass = max(input_masses)
        ml = mass
        yl = np.array([])
        mh = mass
        yh = np.array([])
        if mass < min_mass:
            print "** WARNING: ** Attempting to extrapolate below the lowest input mass. The extrapolated shape(s) might not be reliable."
            m_temp = input_masses
            m_temp.sort()
            ml = m_temp[0]
            mh = m_temp[1]
        elif mass > max_mass:
            print "** WARNING: ** Attempting to extrapolate above the highest input mass. The extrapolated shape(s) might not be reliable."
            m_temp = input_masses
            m_temp.sort(reverse=True)
            ml = m_temp[1]
            mh = m_temp[0]
        else:
            ml = max([ m for m in input_masses if m<mass ])
            mh = min([ m for m in input_masses if m>mass ])
        print(ml,mh)


        yl = np.array(shapes.shapes[ml])
        yh = np.array(shapes.shapes[mh])

        y = ((yh - yl)/float(mh-ml))*float(mass - ml) + yl
        # print(y,yl,yh)

    # define interpolator
    interpolator = Math.Interpolator(len(x))
    interpolator.SetData(len(x), array('d',x), array('d',y.tolist()))

    for i in range(1, histo.GetNbinsX()+1):
        xcenter = histo.GetBinCenter(i)/float(mass)
        # print(xcenter
        if xcenter > shapes.binxcenters[0] and xcenter < shapes.binxcenters[-1]:

            xlow = histo.GetXaxis().GetBinLowEdge(i)/float(mass)
            if xlow < shapes.binxcenters[0]: xlow = shapes.binxcenters[0]
            xhigh = histo.GetXaxis().GetBinUpEdge(i)/float(mass)
            if xhigh > shapes.binxcenters[-1]: xhigh = shapes.binxcenters[-1]

            integral = interpolator.Integ(xlow, xhigh)
            # print(xlow,xhigh,integral)
            histo.SetBinContent( i, (integral if integral >= 0. else 0.) )
        else:
            histo.SetBinContent(i, 0.)

    histo.Scale( 1./histo.Integral() )


def main():
    # usage description
    usage = "Example: ./getResonanceShapes.py -i inputs/input_shapes_qq_13TeV_PU20_Phys14.py -f qq --massrange 400 10000 100 -o ResonanceShapes_qq_13TeV_PU20_Phys14.root"

    # input parameters
    parser = ArgumentParser(description='Resonance shape interpolation code based on vertical template morphing',epilog=usage)

    parser.add_argument("-i", "--input_shapes", dest="input_shapes", required=True,
                        help="Input shapes",
                        metavar="INPUT_SHAPES")

    parser.add_argument("-o", "--output_file", dest="output_file", required=True,
                        help="Output ROOT file",
                        metavar="OUTPUT_FILE")

    parser.add_argument("-c", "--coup", dest="coup", required=True,
                        help="Coupling",
                        metavar="COUPLING")

    parser.add_argument("-f", "--final_state", dest="final_state", required=True,
                        help="Final state (e.g. qq, qg, gg)",
                        metavar="FINAL_STATE")
    parser.add_argument("--fineBinning", dest="fineBinning", default=False, action="store_true", help="Use fine, 1-GeV binning")

    parser.add_argument("--storePDF", dest="storePDF", default=False, action="store_true", help="Also store a 1-GeV-binned PDF")

    parser.add_argument("--storeCDF", dest="storeCDF", default=False, action="store_true", help="Also store a 1-GeV-binned CDF")

    mass_group = parser.add_mutually_exclusive_group(required=True)
    mass_group.add_argument("--mass",
                            type=int,
                            nargs = '*',
                            default = 1000,
                            help="Mass can be specified as a single value or a whitespace separated list (default: %(default)s)"
                            )
    mass_group.add_argument("--massrange",
                            type=int,
                            nargs = 3,
                            help="Define a range of masses to be produced. Format: min max step",
                            metavar = ('MIN', 'MAX', 'STEP')
                            )
    mass_group.add_argument("--masslist",
                            help = "List containing mass information"
                            )

    args = parser.parse_args()

    # import ROOT
    from ROOT import TFile, TH1D

    # input shapes
    #thedir = os.path.dirname(args.input_shapes)
    #sys.path.insert(0, thedir)
    #input_shapes = __import__(os.path.basename(args.input_shapes).replace(".py",""))
    #input_shapes = __import__(thedir + "." + os.path.basename(args.input_shapes).replace(".py",""))
    #import args.input_shapes
    
    #sys.path.append(os.path.abspath("/afs/cern.ch/work/a/apsallid/CMS/Hgg/exodiphotons/seconditeration/CMSSW_10_2_13/src/diphoton-analysis/DijetShapeInterpolator/inputs"))
    #sys.path.insert(0, os.path.dirname(args.input_shapes))

    #the_input_shapes = args.input_shapes.replace(".py","")
    #from the_input_shapes import *
    
    #input_shapes = __import__(args.input_shapes.replace(".py",""))
    #from inputs. import THINGS_YOU_WANT_TO_IMPORT_IN_A

    #os.system("python %s" %(os.path.dirname(args.input_shapes)) )
    #from inputs.import shapes, binxcenters
    #input_shapes = __import__(args.input_shapes.replace(".py",""))

    # input shapes
    #print(os.path.dirname(args.input_shapes))  
    sys.path.insert(0, os.path.dirname(args.input_shapes))
    #print(os.path.basename(args.input_shapes).replace(".py",""))  

    input_shapes = __import__(os.path.basename(args.input_shapes).replace(".py",""))

    binBoundaries = {}
    # Start from 230(330) GeV
    # binBoundaries["kMpl001"] = []
    # binBoundaries["kMpl01"] = []
    # binBoundaries["kMpl02"] = []
    binBoundaries["kMpl001"] = [500, 506, 513, 519, 526, 533, 540, 547, 554, 561, 568, 575, 583, 590, 598, 605, 613, 621, 629, 637, 645, 653, 662, 670, 679, 687, 696, 705, 714, 723, 732, 741, 751, 760, 770, 779, 789, 799, 809, 820, 830, 840, 851, 862, 872, 883, 894, 906, 917, 929, 940, 952, 964, 976, 988, 1001, 1013, 1026, 1038, 1051, 1064, 1078, 1091, 1105, 1119, 1132, 1147, 1161, 1175, 1190, 1205, 1219, 1235, 1250, 1265, 1281, 1297, 1313, 1329, 1346, 1362, 1379, 1396, 1413, 1431, 1449, 1466, 1485, 1503, 1521, 1540, 1559, 1578, 1598, 1617, 1637, 1657, 1678, 1698, 1719, 1740, 1762, 1783, 1805, 1827, 1850, 1873, 1895, 1919, 1942, 1966, 1990, 2014, 2039, 2064, 2089, 2115, 2141, 2167, 2193, 2220, 2247, 2275, 2303, 2331, 2359, 2388, 2417, 2447, 2477, 2507, 2537, 2568, 2600, 2631, 2663, 2696, 2729, 2762, 2795, 2830, 2864, 2899, 2934, 2970, 3006, 3042, 3079, 3117, 3155, 3193, 3232, 3271, 3311, 3351, 3392, 3433, 3475, 3517, 3560, 3603, 3647, 3691, 3736, 3781, 3827, 3873, 3920, 3968, 4016, 4065, 4114, 4164, 4214, 4265, 4317, 4369, 4422, 4476, 4530, 4585, 4640, 4696, 4753, 4811, 4869, 4928, 4987, 5048, 5109, 5171, 5233, 5296, 5360, 5425, 5491, 5557, 5624, 5692, 5761, 5831, 5901, 5973, 6045, 6118, 6192, 6267, 6342, 6419, 6496, 6575, 6654, 6734, 6816, 6898, 6981, 7066, 7151, 7237, 7325, 7413, 7502, 7593, 7684, 7777, 7871, 7966, 8062, 8159, 8258, 8357, 8458, 8560, 8663, 8768, 8873, 8980, 9089, 9198, 9309, 9421, 9535, 9650, 9766, 9884, 10003, 10123, 10245, 10369, 10494, 10620, 10748, 10877, 11008, 11141, 11275, 11411, 11548, 11687, 11828, 11971, 12115, 12261, 12408, 12558, 12709, 12862, 13017, 13173, 13332, 13492, 13655, 13819, 13985, 14000]
    binBoundaries["kMpl01"] = [500, 509, 518, 528, 538, 548, 558, 568, 579, 589, 600, 611, 622, 634, 645, 657, 669, 681, 694, 707, 719, 732, 746, 759, 773, 787, 801, 816, 830, 845, 860, 876, 892, 908, 924, 940, 957, 974, 992, 1009, 1027, 1046, 1064, 1083, 1102, 1122, 1142, 1162, 1183, 1204, 1225, 1247, 1269, 1291, 1314, 1337, 1361, 1385, 1409, 1434, 1459, 1485, 1511, 1537, 1564, 1592, 1619, 1648, 1677, 1706, 1736, 1766, 1797, 1828, 1860, 1893, 1926, 1959, 1993, 2028, 2064, 2099, 2136, 2173, 2211, 2249, 2288, 2328, 2368, 2410, 2451, 2494, 2537, 2581, 2626, 2671, 2718, 2765, 2812, 2861, 2910, 2961, 3012, 3064, 3117, 3171, 3225, 3281, 3338, 3395, 3454, 3513, 3574, 3636, 3698, 3762, 3827, 3893, 3960, 4028, 4097, 4167, 4239, 4312, 4386, 4462, 4538, 4616, 4696, 4776, 4858, 4942, 5027, 5113, 5201, 5290, 5381, 5473, 5567, 5662, 5759, 5858, 5958, 6061, 6164, 6270, 6377, 6487, 6598, 6711, 6826, 6943, 7061, 7182, 7305, 7430, 7557, 7687, 7818, 7952, 8088, 8226, 8367, 8510, 8656, 8804, 8954, 9107, 9263, 9421, 9582, 9746, 9912, 10082, 10254, 10429, 10607, 10788, 10972, 11160, 11350, 11544, 11741, 11942, 12146, 12353, 12564, 12778, 12996, 13218, 13443, 13673, 13906, 14000]
    binBoundaries["kMpl02"] = [500, 523, 547, 572, 598, 625, 653, 683, 713, 745, 778, 812, 848, 885, 924, 964, 1005, 1049, 1094, 1141, 1190, 1241, 1293, 1348, 1405, 1465, 1527, 1591, 1658, 1727, 1800, 1875, 1953, 2034, 2119, 2207, 2298, 2393, 2492, 2595, 2702, 2813, 2929, 3050, 3175, 3305, 3440, 3581, 3728, 3880, 4038, 4203, 4374, 4553, 4738, 4931, 5131, 5339, 5556, 5782, 6016, 6260, 6514, 6777, 7052, 7337, 7634, 7942, 8263, 8597, 8944, 9305, 9680, 10070, 10477, 10899, 11338, 11795, 12270, 12764, 13277, 13812, 14000]
    # binBoundaries["0p014"] = [500, 506, 512, 518, 524, 530, 536, 542, 548, 554, 561, 568, 575, 582, 589, 596, 603, 610, 617, 624, 631, 638, 646, 654, 662, 670, 678, 686, 694, 702, 710, 718, 726, 735, 744, 753, 762, 771, 780, 789, 798, 807, 817, 827, 837, 847, 857, 867, 877, 887, 898, 909, 920, 931, 942, 953, 964, 975, 987, 999, 1011, 1023, 1035, 1047, 1059, 1072, 1085, 1098, 1111, 1124, 1137, 1151, 1165, 1179, 1193, 1207, 1221, 1236, 1251, 1266, 1281, 1296, 1311, 1327, 1343, 1359, 1375, 1391, 1408, 1425, 1442, 1459, 1476, 1494, 1512, 1530, 1548, 1566, 1585, 1604, 1623, 1642, 1662, 1682, 1702, 1722, 1743, 1764, 1785, 1806, 1828, 1850, 1872, 1894, 1917, 1940, 1963, 1986, 2010, 2034, 2058, 2083, 2108, 2133, 2158, 2184, 2210, 2236, 2263, 2290, 2317, 2345, 2373, 2401, 2430, 2459, 2488, 2518, 2548, 2578, 2609, 2640, 2672, 2704, 2736, 2769, 2802, 2835, 2869, 2903, 2938, 2973, 3009, 3045, 3081, 3118, 3155, 3193, 3231, 3270, 3309, 3349, 3389, 3430, 3471, 3513, 3555, 3598, 3641, 3685, 3729, 3774, 3819, 3865, 3911, 3958, 4005, 4053, 4101, 4150, 4200, 4250, 4301, 4352, 4404, 4457, 4510, 4564, 4619, 4674, 4730, 4787, 4844, 4902, 4961, 5020, 5080, 5141, 5203, 5265, 5328, 5392, 5457, 5522, 5588, 5655, 5723, 5792, 5861, 5931, 6002, 6074, 6147, 6221, 6296, 6371, 6447, 6524, 6602, 6681, 6761, 6842, 6924, 7007, 7091, 7176, 7262, 7349, 7437, 7526, 7616, 7707, 7799, 7892, 7987, 8083, 8180, 8278, 8377, 8477, 8579, 8682, 8786, 8891, 8998, 9106, 9215, 9325, 9437, 9550, 9664, 9780, 9897, 10016, 10136, 10257, 10380, 10504, 10630, 10757, 10886, 11016, 11148, 11282, 11417, 11554, 11693, 11833, 11975, 12119, 12264, 12411, 12560, 12711, 12863, 13017, 13173, 13331, 13491, 13653, 13817, 13983, 14000]
    # binBoundaries["1p4"] = [500, 508, 517, 526, 535, 544, 553, 562, 571, 580, 590, 600, 610, 620, 630, 640, 650, 661, 672, 683, 694, 705, 716, 728, 740, 752, 764, 776, 788, 801, 814, 827, 840, 853, 866, 880, 894, 908, 922, 936, 951, 966, 981, 996, 1011, 1027, 1043, 1059, 1075, 1092, 1109, 1126, 1143, 1160, 1178, 1196, 1214, 1232, 1251, 1270, 1289, 1309, 1329, 1349, 1369, 1390, 1411, 1432, 1454, 1476, 1498, 1520, 1543, 1566, 1589, 1613, 1637, 1661, 1686, 1711, 1736, 1762, 1788, 1815, 1842, 1869, 1897, 1925, 1953, 1982, 2011, 2041, 2071, 2101, 2132, 2163, 2195, 2227, 2260, 2293, 2327, 2361, 2396, 2431, 2467, 2503, 2540, 2577, 2615, 2653, 2692, 2731, 2771, 2811, 2852, 2893, 2935, 2978, 3021, 3065, 3109, 3154, 3200, 3246, 3293, 3341, 3389, 3438, 3488, 3538, 3589, 3641, 3693, 3746, 3800, 3855, 3910, 3966, 4023, 4081, 4140, 4199, 4259, 4320, 4382, 4445, 4509, 4574, 4640, 4706, 4773, 4841, 4910, 4980, 5051, 5123, 5196, 5270, 5345, 5421, 5498, 5576, 5656, 5737, 5819, 5902, 5986, 6071, 6157, 6245, 6334, 6424, 6515, 6608, 6702, 6797, 6894, 6992, 7091, 7192, 7294, 7398, 7503, 7610, 7718, 7828, 7939, 8052, 8166, 8282, 8399, 8518, 8639, 8761, 8885, 9011, 9139, 9268, 9399, 9532, 9667, 9804, 9943, 10084, 10227, 10372, 10519, 10668, 10819, 10972, 11127, 11284, 11443, 11605, 11769, 11935, 12104, 12275, 12448, 12624, 12802, 12983, 13166, 13352, 13540, 13731, 13925, 14000]
    # binBoundaries["5p6"] = [500, 517, 534, 552, 570, 589, 608, 628, 649, 670, 692, 714, 737, 761, 785, 810, 836, 863, 890, 918, 947, 977, 1008, 1040, 1073, 1107, 1141, 1176, 1212, 1250, 1289, 1329, 1370, 1412, 1455, 1500, 1546, 1593, 1642, 1692, 1743, 1796, 1850, 1906, 1964, 2023, 2084, 2147, 2212, 2279, 2347, 2417, 2489, 2564, 2641, 2720, 2801, 2885, 2971, 3060, 3151, 3245, 3341, 3440, 3542, 3647, 3755, 3866, 3981, 4099, 4220, 4345, 4473, 4605, 4741, 4881, 5025, 5173, 5325, 5482, 5643, 5809, 5980, 6156, 6337, 6523, 6715, 6912, 7115, 7324, 7539, 7760, 7987, 8221, 8462, 8710, 8965, 9227, 9497, 9775, 10061, 10355, 10658, 10969, 11289, 11619, 11958, 12307, 12666, 13036, 13416, 13807, 14000]

    binBoundaries["0p014"] = binBoundaries["kMpl001"]
    binBoundaries["1p4"] = binBoundaries["kMpl01"]
    binBoundaries["5p6"] = binBoundaries["kMpl02"]

    #========================================
    #EBEE
    #binBoundaries["kMpl001"] = [500, 510, 520, 531, 542, 553, 564, 576, 588, 600, 612, 625, 638, 651, 664, 678, 692, 706, 721, 736, 751, 766, 782, 798, 815, 832, 849, 867, 884, 903, 922, 941, 960, 980, 1000, 1021, 1042, 1064, 1086, 1109, 1132, 1155, 1179, 1204, 1229, 1254, 1280, 1307, 1334, 1362, 1390, 1419, 1449, 1479, 1510, 1541, 1573, 1606, 1640, 1674, 1709, 1744, 1781, 1818, 1856, 1895, 1934, 1975, 2016, 2058, 2101, 2145, 2189, 2235, 2282, 2330, 2378, 2428, 2479, 2530, 2583, 2637, 2692, 2749, 2806, 2865, 2925, 2986, 3048, 3112, 3177, 3244, 3312, 3381, 3452, 3524, 3598, 3673, 3750, 3828, 3909, 3990, 4074, 4159, 4246, 4335, 4426, 4519, 4613, 4710, 4809, 4909, 5012, 5117, 5224, 5334, 5446, 5560, 5676, 5795, 5917, 6041, 6167, 6297, 6429, 6563, 6701, 6841, 6985, 7131, 7281, 7433, 7589, 7748, 7911, 8077, 8246, 8419, 8596, 8776, 8960, 9148, 9340, 9536, 9735, 9940, 10148, 10361, 10578, 10800, 11027, 11258, 11494, 11735, 11982, 12233, 12490, 12752, 13019, 13292, 13571, 13856, 14000]

    #binBoundaries["kMpl01"] = [500, 512, 525, 538, 551, 565, 579, 593, 608, 623, 639, 655, 671, 688, 705, 722, 740, 759, 778, 797, 817, 838, 858, 880, 902, 924, 947, 971, 995, 1020, 1045, 1072, 1098, 1126, 1154, 1183, 1212, 1242, 1273, 1305, 1338, 1371, 1405, 1440, 1476, 1513, 1551, 1590, 1629, 1670, 1712, 1754, 1798, 1843, 1889, 1936, 1985, 2034, 2085, 2137, 2191, 2245, 2301, 2359, 2418, 2478, 2540, 2603, 2669, 2735, 2804, 2874, 2945, 3019, 3094, 3172, 3251, 3332, 3415, 3501, 3588, 3678, 3770, 3864, 3960, 4059, 4161, 4265, 4371, 4481, 4593, 4707, 4825, 4945, 5069, 5196, 5326, 5459, 5595, 5735, 5878, 6025, 6176, 6330, 6488, 6650, 6817, 6987, 7162, 7341, 7524, 7712, 7905, 8102, 8305, 8513, 8725, 8943, 9167, 9396, 9631, 9872, 10118, 10371, 10630, 10896, 11168, 11448, 11734, 12027, 12328, 12636, 12952, 13275, 13607, 13947, 14000]

    #binBoundaries["kMpl01"] = [500, 524, 550, 578, 606, 635, 666, 699, 732, 767, 804, 842, 882, 924, 968, 1013, 1060, 1110, 1162, 1216, 1272, 1331, 1393, 1457, 1524, 1594, 1667, 1743, 1823, 1906, 1993, 2083, 2178, 2277, 2380, 2487, 2600, 2717, 2839, 2967, 3101, 3240, 3385, 3537, 3696, 3861, 4034, 4215, 4403, 4600, 4805, 5019, 5243, 5477, 5721, 5975, 6241, 6518, 6808, 7111, 7426, 7756, 8100, 8460, 8835, 9226, 9635, 10062, 10508, 10973, 11459, 11966, 12495, 13048, 13625, 14000]


    # initialize shape storage
    shapes = ShapeStorage(input_shapes.shapes,input_shapes.binxcenters)
    #shapes = ShapeStorage(shapes,binxcenters)

    # mass points for which resonance shapes will be produced
    masses = []

    if args.massrange != None:
        MIN, MAX, STEP = args.massrange
        masses = range(MIN, MAX+STEP, STEP)
    elif args.masslist != None:
        # A mass list was provided
        print  "Will create mass list according to", args.massdict
        masslist = __import__(args.masslist.replace(".root.py",""))
        masses = masslist.masses
    else:
        masses = args.mass

    '''    
    M_bins = {
        "kMpl001" : [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 4000, 5000],
        "kMpl01" : [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 3000, 3500, 4000, 4250, 4500, 4750, 5000, 5250, 5500, 5750, 6000, 6500, 7000, 8000],
        "kMpl02" : [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 3000, 3500, 4000, 4500, 4750, 5000, 5250, 5500, 5750, 6000, 6500, 7000, 8000],
        "0p014": [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 4000, 4500, 5000],
        "1p4": [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 3000, 3500, 4000, 4250, 4500, 4750, 5000],
        "5p6": [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 3000, 3500, 4000, 4500, 4750, 5000]
    }
    masses = M_bins[args.coup]
    '''


    # sort masses
    masses.sort()

    # output ROOT file
    output = TFile(args.output_file,"RECREATE")

    for mass in masses:

       print "Producing %s shape for m = %i GeV"%(args.final_state, int(mass))

       histname = "h_" + args.final_state + "_" + str(int(mass))

       h_shape = ( TH1D(histname, args.final_state + " Resonance Shape", 1750, 0, 14000) if args.fineBinning else TH1D(histname, args.final_state + " Resonance Shape", len(binBoundaries[args.coup])-1, array('d',binBoundaries[args.coup])) )
       #h_shape = ( TH1D(histname, args.final_state + " Resonance Shape", 14000, 0, 14000) if args.fineBinning else TH1D(histname, args.final_state + " Resonance Shape", 2800, 0, 14000) )
       h_shape.SetXTitle("DiPhotonMass [GeV]")
       h_shape.SetYTitle("Probability")

       # interpolate resonance shape
       LineShapePDF(shapes, mass, h_shape);

       output.cd()
       h_shape.Write()

       if args.storePDF or args.storeCDF:

           h_pdf = TH1D(histname + "_pdf", args.final_state + " Resonance Shape PDF", 14000, 0, 14000)
           h_cdf = TH1D(histname + "_cdf", args.final_state + " Resonance Shape CDF", 14000, 0, 14000)

           for i in range(1,h_shape.GetNbinsX()+1):

               bin_min = h_pdf.GetXaxis().FindBin(h_shape.GetXaxis().GetBinLowEdge(i)+0.5)
               bin_max = h_pdf.GetXaxis().FindBin(h_shape.GetXaxis().GetBinUpEdge(i)-0.5)
               bin_content = h_shape.GetBinContent(i)/float(bin_max-bin_min+1)
               for b in range(bin_min,bin_max+1):
                  h_pdf.SetBinContent(b, bin_content);

           for i in range(1,h_cdf.GetNbinsX()+1):

               bin_min = h_pdf.GetXaxis().FindBin(h_cdf.GetXaxis().GetBinLowEdge(i)+0.5)
               bin_max = h_pdf.GetXaxis().FindBin(h_cdf.GetXaxis().GetBinUpEdge(i)-0.5)

               curr = 0.;
               for b in range(bin_min,bin_max+1):
                  curr = curr + h_pdf.GetBinContent(b)

               prev = h_cdf.GetBinContent(i-1)
               h_cdf.SetBinContent(i, prev+curr)

           output.cd()
           if args.storePDF: h_pdf.Write()
           if args.storeCDF: h_cdf.Write()

    output.Close()


if __name__ == '__main__':
    main()
