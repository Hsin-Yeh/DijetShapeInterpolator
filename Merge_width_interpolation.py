#!/usr/bin/env python3

import ROOT
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--width','-w',default="14",type=str)
parser.add_argument('--cat','-c',default="EBEB",type=str)
parser.add_argument('--year','-y',default="2018",type=str)
parser.add_argument('--systematics','-s',default="nom",type=str)
args = parser.parse_args()

def main():
    widths = [14, 707, 1400, 3500, 5600]
    cats = ["EBEB","EBEE"]
    years = ["2016","2017","2018"]
    systematics = ["nom","energyScaleStatUp","energyScaleSystUp","energyScaleGainUp","energySigmaUp","energyScaleStatDown","energyScaleSystDown",
                   "energyScaleGainDown","energySigmaDown","SFScaleUp","SFScaleDown","PuScaleUp","PuScaleDown"]
    for year in years:
        for cat in cats:
            for width in widths:
                for systematic in systematics:
                    print("Merging %s %s %s %s",year, cat, width, systematic)
                    if (systematic=="nom"): out_filename = 'ResonanceShapes_InputShapes_RSGravitonToGammaGamma_%s_%s_%s.root'%(width,cat,year)
                    else: out_filename = 'ResonanceShapes_InputShapes_RSGravitonToGammaGamma_%s_%s_%s_%s.root'%(width,cat,year,systematic)
                    outfile = ROOT.TFile(out_filename, 'RECREATE')
                    for mass in range(600,5000,100):
                        if (systematic=="nom"): in_filename = 'width_interpolated_shapes/width_InputShapes_RSGravitonToGammaGamma_%s_%s_%iGeV.root'%(cat,year,mass)
                        else: in_filename = 'width_interpolated_shapes/width_InputShapes_RSGravitonToGammaGamma_%s_%s_%s_%iGeV.root'%(cat,year,systematic,mass)
                        infile = ROOT.TFile(in_filename)
                        histo = infile.Get('h_gg_%s'%(width))
                        histo.SetName('h_gg_%s'%(mass))
                        outfile.cd()
                        histo.Write()

if __name__ == "__main__":
    main()
