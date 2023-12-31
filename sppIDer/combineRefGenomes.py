#!/usr/bin/env python
import sys, subprocess, argparse
from Bio import SeqIO

################################################################
# This script will create the combination reference genome and all additional files needed to run the full sppIDer script.
#
#Program Requirements: bwa, samtools
#Input: output name prefix, text file key of genome names, and optional desired minimum length of contigs included (default is to keep all contigs)
#The text file key must be a tab seperated list of unique name for each genome and the actual fasta name for that genome, e.g.
#Saccharomyces_cerevisaie   S288c.fasta
#Saccharomyces_paradoxus    GCA_002079055.1.fasta
#
################################################################

#JFW edit: runs everything in the current directory
workingDir = "./" 

parser = argparse.ArgumentParser(description="Combine desired reference genomes")
parser.add_argument('--out', help="Output prefix, required", required=True)
parser.add_argument('--key', help="Key to reference genomes, required", required=True)
parser.add_argument('--trim', help="Trim any contigs smaller than this value (for genomes in many small contigs)", default=0)
args = parser.parse_args()
comboGenomeName = args.out
listName = args.key
trimLength = int(args.trim)

#Replace paths
comboTotalLen = 0
lengthFile = open(workingDir + "comboLength_" + comboGenomeName + ".txt", 'w')
lengthFile.write(comboGenomeName + "\tTrimmed contigs >" + str(trimLength)+"\n")
outGenome = open(workingDir + comboGenomeName, 'w')
list = open(listName, 'r')
lines = list.readlines()
for line in lines:
    line = line.strip().split('\t')
    uniID = line[0]
    genomeName = line[1]
    sumGenomeLen = 0
    counter = 0
    fasta = open(genomeName, 'r')
    for seq_record in SeqIO.parse(fasta, "fasta"):
        #print(len(seq_record.seq))
        if len(seq_record.seq)>=trimLength:
            outGenome.write(">"+uniID+"-"+str(counter+1)+"\n")
            outGenome.write(str(seq_record.seq)+"\n")
            lengthFile.write(uniID+"-"+str(counter+1)+"\t"+str(len(seq_record.seq))+"\n")
            sumGenomeLen += len(seq_record.seq)
            counter += 1
    comboTotalLen = comboTotalLen + sumGenomeLen
    strGenomeLen = ''
    if sumGenomeLen > 1000000000:
        genomeLen = sumGenomeLen / 1000000000
        mbRemain = sumGenomeLen - (genomeLen * 1000000000)
        Mb = mbRemain / 1000000
        kbRemain = mbRemain - (Mb * 1000000)
        Kb = kbRemain / 1000
        bpRemain = kbRemain - (Kb * 1000)
        strGenomeLen = str(genomeLen) + "-Gb " + str(Mb) + "-Mb " + str(Kb) + "-Kb " + str(bpRemain)+ "-bp"
    elif sumGenomeLen>1000000:
        genomeLen = sumGenomeLen/1000000
        kbRemain = sumGenomeLen - (genomeLen * 1000000)
        Kb = kbRemain / 1000
        bpRemain = kbRemain - (Kb * 1000)
        strGenomeLen = str(genomeLen) + "-Mb " + str(Kb) + "-Kb " + str(bpRemain)+ "-bp"
    elif sumGenomeLen>1000:
        genomeLen = sumGenomeLen/1000
        bpRemain = sumGenomeLen - (genomeLen * 1000)
        strGenomeLen = str(genomeLen)+"-Kb " + str(bpRemain)+ "-bp"
    else:
        strGenomeLen = str(sumGenomeLen) + "-bp"
    lengthFile.write(uniID + "-totalGenome\t" + strGenomeLen + "\n")
strComboLen = ''
if comboTotalLen > 1000000000:
    comboLen = comboTotalLen/1000000000
    mbRemain = comboTotalLen - (comboLen*1000000000)
    Mb = mbRemain/1000000
    kbRemain = mbRemain - (Mb*1000000)
    Kb = kbRemain/1000
    bpRemain = kbRemain - (Kb*1000)
    strComboLen = str(comboLen) + "-Gb " + str(Mb) + "-Mb " + str(Kb) + "-Kb " + str(bpRemain)+ "-bp"
elif comboTotalLen>1000000:
    comboLen = comboTotalLen/1000000
    kbRemain = comboTotalLen - (comboLen * 1000000)
    Kb = kbRemain / 1000
    bpRemain = kbRemain - (Kb * 1000)
    strComboLen = str(comboLen) + "-Mb " + str(Kb) + "-Kb " + str(bpRemain)+ "-bp"
elif comboTotalLen>1000:
    comboLen = comboTotalLen/1000
    bpRemain = comboTotalLen - (comboLen * 1000)
    strComboLen = str(comboLen)+"-Kb " + str(bpRemain)+ "-bp"
else:
    strComboLen = str(comboTotalLen) + "-bp"
lengthFile.write("Combo-totalGenome\t" + strComboLen + "\n")

outGenome.close()
lengthFile.close()

subprocess.call(["bwa", "index", comboGenomeName])
subprocess.call(["samtools", "faidx", comboGenomeName])
