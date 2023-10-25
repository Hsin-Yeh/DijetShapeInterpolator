#!/usr/bin/env python3

import ROOT
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--width','-w',default=-1,type=int)
parser.add_argument('--mass','-m',default=-1,type=int)
parser.add_argument('--cat','-c',default="EBEB",type=str)
parser.add_argument('--year','-y',default="2018",type=str)
parser.add_argument('--systematics','-s',default="nom",type=str)
parser.add_argument('--signame','-n',default="grav",type=str)
args = parser.parse_args()

def main():
    if (args.width == -1): widths = [14, 361, 707, 1054, 1400, 2450, 3500, 4550, 5600]
    else: widths = [args.width]
    if (args.mass == -1): masses = [600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 4000, 4100, 4200, 4300, 4400, 4500, 4600, 4700, 4800, 4900]
    else: masses = [args.mass]

    if (args.signame=="grav"): signame="RSGravitonToGammaGamma"
    elif (args.signame=="grav"): signame="GluGluSpin0ToGammaGamma"
    cats = ["EBEB","EBEE"]
    years = ["2016","2017","2018"]
    systematics = ["nom","energyScaleStatUp","energyScaleSystUp","energyScaleGainUp","energySigmaUp","energyScaleStatDown","energyScaleSystDown",
                   "energyScaleGainDown","energySigmaDown","SFScaleUp","SFScaleDown","PUScaleUp","PUScaleDown"]
    for year in years:
        for cat in cats:
            for width in widths:
                for systematic in systematics:
                    print("Merging %s %s %s %s"%(year, cat, width, systematic))
                    if (systematic=="nom"): out_filename = 'signal_shapes/ResonanceShapes_InputShapes_%s_%s_%s_%s.root'%(signame,width,cat,year)
                    else: out_filename = 'signal_shapes/ResonanceShapes_InputShapes_%s_%s_%s_%s_%s.root'%(signame,width,cat,year,systematic)
                    outfile = ROOT.TFile(out_filename, 'RECREATE')
                    for mass in masses:
                        if (systematic=="nom"): in_filename = 'signal_shapes/width_InputShapes_%s_%s_%s_%iGeV.root'%(signame,cat,year,mass)
                        else: in_filename = 'signal_shapes/width_InputShapes_%s_%s_%s_%s_%iGeV.root'%(signame,cat,year,systematic,mass)
                        infile = ROOT.TFile(in_filename)
                        histo = infile.Get('h_gg_%s'%(width))
                        histo.SetName('h_gg_%s'%(mass))
                        outfile.cd()
                        histo.Write()

if __name__ == "__main__":
    main()
