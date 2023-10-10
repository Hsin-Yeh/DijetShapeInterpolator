#!/usr/bin/env python

from argparse import ArgumentParser
import numpy as np


def main():
    # usage description
    usage = "Example: ./extractShapes.py -i InputShapes_RSGqq_PU30_Spring15.root"

    # input parameters
    parser = ArgumentParser(description='Script extracting resonance shapes from an input ROOT file and printing them in a format used by the interpolation code',epilog=usage)

    parser.add_argument("-n", "--narrow_input_file", dest="narrow_input_file", required=True,
                        help="Narrow Input file",
                        metavar="NARROW_INPUT_FILE")

    parser.add_argument("-m", "--medium_input_file", dest="medium_input_file", required=True,
                        help="Medium Input file",
                        metavar="MEDIUM_INPUT_FILE")

    parser.add_argument("-w", "--wide_input_file", dest="wide_input_file", required=True,
                        help="Wide Input file",
                        metavar="WIDE_INPUT_FILE")

    parser.add_argument("--mass", dest="mass", required=True,
                        help="Interpolate mass",
                        metavar="INTERPOLATE_MASS")

    parser.add_argument("-d", "--dir", dest="dir",
                        default='',
                        help="Path to TDirectory containing histograms (This parameter is optional (default: %(default)s)",
                        metavar="DIR")

    parser.add_argument("--debug", dest="debug", default=False, action="store_true", help="Debug printout")

    args = parser.parse_args()

    input_files = {}
    shapes = {}
    binxcenters = []

    # import ROOT stuff
    from ROOT import TFile, TH1F, TH1D
    # open input file
    input_files[0] = TFile(args.narrow_input_file)
    input_files[1] = TFile(args.medium_input_file)
    input_files[2] = TFile(args.wide_input_file)

    nEntries = input_files[0].GetListOfKeys().GetEntries()

    # loop over histograms in the input ROOT file
    mass = args.mass
    hName = "h_gg_" + mass
    if args.debug: print "Extracting shapes for m =", mass, "GeV..."

    for iwidth, input_file in enumerate(input_files):
        histo = input_files[iwidth].Get(hName)

        if args.debug: print "Extracting shapes for width =", iwidth

        bincontents = []

        for i in range(1,histo.GetNbinsX()+1):
            bincontents.append(histo.GetBinContent(i))
            if len(binxcenters) < histo.GetNbinsX():
                binxcenters.append(histo.GetBinCenter(i))

        normbincontents = np.array(bincontents)
        normbincontents = normbincontents/np.sum(normbincontents)

        if iwdith == 0: width = 0.00014
        elif iwdith == 1: width = 0.014
        elif iwdith == 2: width = 0.056

        shapes[width] = normbincontents.tolist()

    if args.debug: print ""
    if args.debug: print "Extracted shapes:"
    if args.debug: print ""
    print "shapes = {\n"
    for key, value in sorted(shapes.items()):
        print("  {} : {},".format(key, value))
        print ""
    print "}"
    print ""
    print "binxcenters =", binxcenters
    print ""


if __name__ == '__main__':
    main()
