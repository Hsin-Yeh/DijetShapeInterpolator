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

def LineShapePDF(shapes_narrow, shapes_wide, width, mass, histo):
    # import ROOT
    from ROOT import Math

    x = shapes_narrow.binxcenters
    #print(x[0],x[-1])
    y = np.array([])

    yl = np.array([])
    yh = np.array([])
    yl = shapes_narrow.shapes[mass]
    yh = shapes_wide.shapes[mass]

    wh = 0.2
    wl = 0.01
    y = ((yh - yl)/float(wh-wl))*float(width - wl) + yl
    # print(y,yl,yh)

    # define interpolator
    interpolator = Math.Interpolator(len(x))
    interpolator.SetData(len(x), array('d',x), array('d',y.tolist()))

    for i in range(1, histo.GetNbinsX()+1):
        xcenter = histo.GetBinCenter(i)/float(mass)
        # print(xcenter
        if xcenter > shapes_narrow.binxcenters[0] and xcenter < shapes_narrow.binxcenters[-1]:

            xlow = histo.GetXaxis().GetBinLowEdge(i)/float(mass)
            if xlow < shapes_narrow.binxcenters[0]: xlow = shapes_narrow.binxcenters[0]
            xhigh = histo.GetXaxis().GetBinUpEdge(i)/float(mass)
            if xhigh > shapes_narrow.binxcenters[-1]: xhigh = shapes_narrow.binxcenters[-1]

            integral = interpolator.Integ(xlow, xhigh)
            # print(xlow,xhigh,integral)
            histo.SetBinContent( i, (integral if integral >= 0. else 0.) )
        else:
            histo.SetBinContent(i, 0.)

    histo.Scale( 1./histo.Integral() )

def main():
    # usage description
    # usage = "Example: ./getResonanceShapes.py -i inputs/input_shapes_qq_13TeV_PU20_Phys14.py -f qq --massrange 400 10000 100 -o ResonanceShapes_qq_13TeV_PU20_Phys14.root"
    usage = "Example: ./getResonanceShapes.py -i inputs/input_shapes_qq_13TeV_PU20_Phys14.py inputs/input_shapes_qq_13TeV_PU20_Phys14.py -f qq --widthrange 0.05 0.2 0.05 -o ResonanceShapes_qq_13TeV_PU20_Phys14.root"


    # input parameters
    parser = ArgumentParser(description='Resonance shape interpolation code based on vertical template morphing',epilog=usage)

    parser.add_argument("-n", "--input_shapes_narrow", dest="input_shapes_narrow", required=True,
                        help="Narrow Input shapes",
                        metavar="INPUT_SHAPES_NARROW")

    parser.add_argument("-w", "--input_shapes_wide", dest="input_shapes_wide", required=True,
                        help="Wide Input shapes",
                        metavar="INPUT_SHAPES_WIDE")

    parser.add_argument("-o", "--output_file", dest="output_file", required=True,
                        help="Output ROOT file",
                        metavar="OUTPUT_FILE")

    parser.add_argument("-m", "--mass", dest="mass", required=True,
                        help="Mass",
                        metavar="MASS")

    parser.add_argument("-f", "--final_state", dest="final_state", required=True,
                        help="Final state (e.g. qq, qg, gg)",
                        metavar="FINAL_STATE")
    parser.add_argument("--fineBinning", dest="fineBinning", default=False, action="store_true", help="Use fine, 1-GeV binning")

    parser.add_argument("--storePDF", dest="storePDF", default=False, action="store_true", help="Also store a 1-GeV-binned PDF")

    parser.add_argument("--storeCDF", dest="storeCDF", default=False, action="store_true", help="Also store a 1-GeV-binned CDF")

    width_group = parser.add_mutually_exclusive_group(required=False)
    width_group.add_argument("--width",
                            type=float,
                            nargs = '*',
                            default = 0.05,
                            help="Width can be specified as a single value or a whitespace separated list (default: %(default)s)"
                            )
    width_group.add_argument("--widthrange",
                            type=float,
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

    # input shapes
    #print(os.path.dirname(args.input_shapes))
    sys.path.insert(0, os.path.dirname(args.input_shapes_narrow))
    #print(os.path.basename(args.input_shapes).replace(".py",""))
    input_shapes_narrow = __import__(os.path.basename(args.input_shapes_narrow).replace(".py",""))

    sys.path.insert(0, os.path.dirname(args.input_shapes_wide))
    input_shapes_wide = __import__(os.path.basename(args.input_shapes_wide).replace(".py",""))

    #========================================
    #EBEE
    #binBoundaries["kMpl001"] = [500, 510, 520, 531, 542, 553, 564, 576, 588, 600, 612, 625, 638, 651, 664, 678, 692, 706, 721, 736, 751, 766, 782, 798, 815, 832, 849, 867, 884, 903, 922, 941, 960, 980, 1000, 1021, 1042, 1064, 1086, 1109, 1132, 1155, 1179, 1204, 1229, 1254, 1280, 1307, 1334, 1362, 1390, 1419, 1449, 1479, 1510, 1541, 1573, 1606, 1640, 1674, 1709, 1744, 1781, 1818, 1856, 1895, 1934, 1975, 2016, 2058, 2101, 2145, 2189, 2235, 2282, 2330, 2378, 2428, 2479, 2530, 2583, 2637, 2692, 2749, 2806, 2865, 2925, 2986, 3048, 3112, 3177, 3244, 3312, 3381, 3452, 3524, 3598, 3673, 3750, 3828, 3909, 3990, 4074, 4159, 4246, 4335, 4426, 4519, 4613, 4710, 4809, 4909, 5012, 5117, 5224, 5334, 5446, 5560, 5676, 5795, 5917, 6041, 6167, 6297, 6429, 6563, 6701, 6841, 6985, 7131, 7281, 7433, 7589, 7748, 7911, 8077, 8246, 8419, 8596, 8776, 8960, 9148, 9340, 9536, 9735, 9940, 10148, 10361, 10578, 10800, 11027, 11258, 11494, 11735, 11982, 12233, 12490, 12752, 13019, 13292, 13571, 13856, 14000]

    #binBoundaries["kMpl01"] = [500, 512, 525, 538, 551, 565, 579, 593, 608, 623, 639, 655, 671, 688, 705, 722, 740, 759, 778, 797, 817, 838, 858, 880, 902, 924, 947, 971, 995, 1020, 1045, 1072, 1098, 1126, 1154, 1183, 1212, 1242, 1273, 1305, 1338, 1371, 1405, 1440, 1476, 1513, 1551, 1590, 1629, 1670, 1712, 1754, 1798, 1843, 1889, 1936, 1985, 2034, 2085, 2137, 2191, 2245, 2301, 2359, 2418, 2478, 2540, 2603, 2669, 2735, 2804, 2874, 2945, 3019, 3094, 3172, 3251, 3332, 3415, 3501, 3588, 3678, 3770, 3864, 3960, 4059, 4161, 4265, 4371, 4481, 4593, 4707, 4825, 4945, 5069, 5196, 5326, 5459, 5595, 5735, 5878, 6025, 6176, 6330, 6488, 6650, 6817, 6987, 7162, 7341, 7524, 7712, 7905, 8102, 8305, 8513, 8725, 8943, 9167, 9396, 9631, 9872, 10118, 10371, 10630, 10896, 11168, 11448, 11734, 12027, 12328, 12636, 12952, 13275, 13607, 13947, 14000]

    #binBoundaries["kMpl01"] = [500, 524, 550, 578, 606, 635, 666, 699, 732, 767, 804, 842, 882, 924, 968, 1013, 1060, 1110, 1162, 1216, 1272, 1331, 1393, 1457, 1524, 1594, 1667, 1743, 1823, 1906, 1993, 2083, 2178, 2277, 2380, 2487, 2600, 2717, 2839, 2967, 3101, 3240, 3385, 3537, 3696, 3861, 4034, 4215, 4403, 4600, 4805, 5019, 5243, 5477, 5721, 5975, 6241, 6518, 6808, 7111, 7426, 7756, 8100, 8460, 8835, 9226, 9635, 10062, 10508, 10973, 11459, 11966, 12495, 13048, 13625, 14000]


    # initialize shape storage
    shapes_narrow = ShapeStorage(input_shapes_narrow.shapes,input_shapes_narrow.binxcenters)
    shapes_wide = ShapeStorage(input_shapes_wide.shapes,input_shapes_wide.binxcenters)

    #shapes = ShapeStorage(shapes,binxcenters)

    # mass points for which resonance shapes will be produced
    widths = []

    if args.widthrange != None:
        MIN, MAX, STEP = args.widthrange
        widths = range(MIN, MAX+STEP, STEP)
    elif args.width != None:
        widths = args.width

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
    widths.sort()

    # output ROOT file
    output = TFile(args.output_file,"RECREATE")

    for width in widths:

       print "Producing %s shape for width = %f GeV"%(args.final_state, float(width))

       histname = "h_" + args.final_state + "_" + str(float(width))

       h_shape = ( TH1D(histname, args.final_state + " Resonance Shape", 1750, 0, 14000) if args.fineBinning else TH1D(histname, args.final_state + " Resonance Shape", len(binBoundaries[args.coup])-1, array('d',binBoundaries[args.coup])) )
       #h_shape = ( TH1D(histname, args.final_state + " Resonance Shape", 14000, 0, 14000) if args.fineBinning else TH1D(histname, args.final_state + " Resonance Shape", 2800, 0, 14000) )
       h_shape.SetXTitle("DiPhotonMass [GeV]")
       h_shape.SetYTitle("Probability")

       # interpolate resonance shape
       LineShapePDF(shapes_narrow, shapes_wide, width, args.mass, h_shape);

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
