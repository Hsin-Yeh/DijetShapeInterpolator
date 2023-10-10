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

def LineShapePDF(shapes, mass, width, histo):
    # import ROOT
    from ROOT import Math

    x = shapes.binxcenters
    #print(x[0],x[-1])
    y = np.array([])
    if width in shapes.shapes.keys():
        y = np.array(shapes.shapes[width])
    else:
        input_widthes = shapes.shapes.keys()
        # print(input_widthes)
        min_width = min(input_widthes)
        max_width = max(input_widthes)
        wl = width
        yl = np.array([])
        wh = width
        yh = np.array([])
        if width < min_width:
            print "** WARNING: ** Attempting to extrapolate below the lowest input width. The extrapolated shape(s) might not be reliable."
            w_temp = input_widthes
            w_temp.sort()
            wl = w_temp[0]
            wh = w_temp[1]
        elif width > max_width:
            print "** WARNING: ** Attempting to extrapolate above the highest input width. The extrapolated shape(s) might not be reliable."
            w_temp = input_widthes
            w_temp.sort(reverse=True)
            wl = w_temp[1]
            wh = w_temp[0]
        else:
            wl = max([ w for w in input_widthes if w<width ])
            wh = min([ w for w in input_widthes if w>width ])
        print(wl,wh)


        yl = np.array(shapes.shapes[wl])
        yh = np.array(shapes.shapes[wh])

        y = ((yh - yl)/float(wh-wl))*float(width - wl) + yl
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

    parser.add_argument("-f", "--final_state", dest="final_state", required=True,
                        help="Final state (e.g. qq, qg, gg)",
                        metavar="FINAL_STATE")
    parser.add_argument("--fineBinning", dest="fineBinning", default=False, action="store_true", help="Use fine, 1-GeV binning")

    parser.add_argument("--doWidthInterp", dest="doWidthInterp", default=False, action="store_true", help="Store ratio histos")

    parser.add_argument("--storePDF", dest="storePDF", default=False, action="store_true", help="Also store a 1-GeV-binned PDF")

    parser.add_argument("--storeCDF", dest="storeCDF", default=False, action="store_true", help="Also store a 1-GeV-binned CDF")

    width_group = parser.add_mutually_exclusive_group(required=False)
    width_group.add_argument("--width",
                            type=int,
                            nargs = '*',
                            default = 1000,
                            help="Width can be specified as a single value or a whitespace separated list (default: %(default)s)"
                            )
    width_group.add_argument("--widthrange",
                            type=int,
                            nargs = 3,
                            help="Define a range of widthes to be produced. Format: min max step",
                            metavar = ('MIN', 'MAX', 'STEP')
                            )
    width_group.add_argument("--widthlist",
                            help = "List containing width information"
                            )

    args = parser.parse_args()

    # import ROOT
    from ROOT import TFile, TH1D

    sys.path.insert(0, os.path.dirname(args.input_shapes))

    input_shapes = __import__(os.path.basename(args.input_shapes).replace(".py",""))

    binBoundaries = {}
    binBoundaries["kMpl001"] = [500, 506, 513, 519, 526, 533, 540, 547, 554, 561, 568, 575, 583, 590, 598, 605, 613, 621, 629, 637, 645, 653, 662, 670, 679, 687, 696, 705, 714, 723, 732, 741, 751, 760, 770, 779, 789, 799, 809, 820, 830, 840, 851, 862, 872, 883, 894, 906, 917, 929, 940, 952, 964, 976, 988, 1001, 1013, 1026, 1038, 1051, 1064, 1078, 1091, 1105, 1119, 1132, 1147, 1161, 1175, 1190, 1205, 1219, 1235, 1250, 1265, 1281, 1297, 1313, 1329, 1346, 1362, 1379, 1396, 1413, 1431, 1449, 1466, 1485, 1503, 1521, 1540, 1559, 1578, 1598, 1617, 1637, 1657, 1678, 1698, 1719, 1740, 1762, 1783, 1805, 1827, 1850, 1873, 1895, 1919, 1942, 1966, 1990, 2014, 2039, 2064, 2089, 2115, 2141, 2167, 2193, 2220, 2247, 2275, 2303, 2331, 2359, 2388, 2417, 2447, 2477, 2507, 2537, 2568, 2600, 2631, 2663, 2696, 2729, 2762, 2795, 2830, 2864, 2899, 2934, 2970, 3006, 3042, 3079, 3117, 3155, 3193, 3232, 3271, 3311, 3351, 3392, 3433, 3475, 3517, 3560, 3603, 3647, 3691, 3736, 3781, 3827, 3873, 3920, 3968, 4016, 4065, 4114, 4164, 4214, 4265, 4317, 4369, 4422, 4476, 4530, 4585, 4640, 4696, 4753, 4811, 4869, 4928, 4987, 5048, 5109, 5171, 5233, 5296, 5360, 5425, 5491, 5557, 5624, 5692, 5761, 5831, 5901, 5973, 6045, 6118, 6192, 6267, 6342, 6419, 6496, 6575, 6654, 6734, 6816, 6898, 6981, 7066, 7151, 7237, 7325, 7413, 7502, 7593, 7684, 7777, 7871, 7966, 8062, 8159, 8258, 8357, 8458, 8560, 8663, 8768, 8873, 8980, 9089, 9198, 9309, 9421, 9535, 9650, 9766, 9884, 10003, 10123, 10245, 10369, 10494, 10620, 10748, 10877, 11008, 11141, 11275, 11411, 11548, 11687, 11828, 11971, 12115, 12261, 12408, 12558, 12709, 12862, 13017, 13173, 13332, 13492, 13655, 13819, 13985, 14000]
    binBoundaries["kMpl01"] = [500, 509, 518, 528, 538, 548, 558, 568, 579, 589, 600, 611, 622, 634, 645, 657, 669, 681, 694, 707, 719, 732, 746, 759, 773, 787, 801, 816, 830, 845, 860, 876, 892, 908, 924, 940, 957, 974, 992, 1009, 1027, 1046, 1064, 1083, 1102, 1122, 1142, 1162, 1183, 1204, 1225, 1247, 1269, 1291, 1314, 1337, 1361, 1385, 1409, 1434, 1459, 1485, 1511, 1537, 1564, 1592, 1619, 1648, 1677, 1706, 1736, 1766, 1797, 1828, 1860, 1893, 1926, 1959, 1993, 2028, 2064, 2099, 2136, 2173, 2211, 2249, 2288, 2328, 2368, 2410, 2451, 2494, 2537, 2581, 2626, 2671, 2718, 2765, 2812, 2861, 2910, 2961, 3012, 3064, 3117, 3171, 3225, 3281, 3338, 3395, 3454, 3513, 3574, 3636, 3698, 3762, 3827, 3893, 3960, 4028, 4097, 4167, 4239, 4312, 4386, 4462, 4538, 4616, 4696, 4776, 4858, 4942, 5027, 5113, 5201, 5290, 5381, 5473, 5567, 5662, 5759, 5858, 5958, 6061, 6164, 6270, 6377, 6487, 6598, 6711, 6826, 6943, 7061, 7182, 7305, 7430, 7557, 7687, 7818, 7952, 8088, 8226, 8367, 8510, 8656, 8804, 8954, 9107, 9263, 9421, 9582, 9746, 9912, 10082, 10254, 10429, 10607, 10788, 10972, 11160, 11350, 11544, 11741, 11942, 12146, 12353, 12564, 12778, 12996, 13218, 13443, 13673, 13906, 14000]
    binBoundaries["kMpl02"] = [500, 523, 547, 572, 598, 625, 653, 683, 713, 745, 778, 812, 848, 885, 924, 964, 1005, 1049, 1094, 1141, 1190, 1241, 1293, 1348, 1405, 1465, 1527, 1591, 1658, 1727, 1800, 1875, 1953, 2034, 2119, 2207, 2298, 2393, 2492, 2595, 2702, 2813, 2929, 3050, 3175, 3305, 3440, 3581, 3728, 3880, 4038, 4203, 4374, 4553, 4738, 4931, 5131, 5339, 5556, 5782, 6016, 6260, 6514, 6777, 7052, 7337, 7634, 7942, 8263, 8597, 8944, 9305, 9680, 10070, 10477, 10899, 11338, 11795, 12270, 12764, 13277, 13812, 14000]
    binBoundaries["0p014"] = binBoundaries["kMpl001"]
    binBoundaries["1p4"] = binBoundaries["kMpl01"]
    binBoundaries["5p6"] = binBoundaries["kMpl02"]


    # initialize shape storage
    shapes = ShapeStorage(input_shapes.shapes,input_shapes.binxcenters)
    # width points for which resonance shapes will be produced
    widths = []

    if args.widthrange != None:
        MIN, MAX, STEP = args.widthrange
        widths = range(MIN, MAX+STEP, STEP)
    elif args.widthlist != None:
        # A width list was provided
        print  "Will create width list according to", args.widthdict
        widthlist = __import__(args.widthlist.replace(".root.py",""))
        widths = widthlist.widths
    else:
        widths = [14, 707, 1400, 3500, 5600]

    # sort widths
    widths.sort()

    # output ROOT file
    output = TFile(args.output_file,"RECREATE")

    for width in widths:

       print "Producing %s shape for width = %i"%(args.final_state, float(width))

       histname = "h_" + args.final_state + "_" + str(int(width))

       h_shape = TH1D(histname, args.final_state + " Resonance Shape", 1750, 0, 14000)
       # interpolate resonance shape
       LineShapePDF(shapes, 1000, width, h_shape);

       h_shape.SetXTitle("DiPhotonMass [GeV]")
       h_shape.SetYTitle("Probability")
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
