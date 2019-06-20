# snakemake --cores 15 --snakefile Snakefile_forcecall -npr

from os.path import join
METADATA_DIR = config["metadata_dir"]
GENOME = 'hg38'

comparisons = [("WTCHG_538916_221156", "WTCHG_538916_217108"),  #Zcw only Chip vs Input
              ("WTCHG_538916_223180", "WTCHG_538916_220144"), #Cotransfected Chip vs Cotransfected Input
              ("WTCHG_538916_223180", "WTCHG_538916_221156"),  #Chip vs Chip with Prdm9
              ("WTCHG_538916_224192", "WTCHG_538916_221156"), # vs chimpPrdm9
              ("SRA_Altemose2015_SRR5627146", "SRA_Altemose2015_SRR5627143"), # hPrdm9 vs Input
              ("SRA_Altemose2015_SRR5627147", "SRA_Altemose2015_SRR5627143"), # hPrdm9 V5 vs Input (HA)
              ("SRA_Altemose2015_SRR5627146_AND_SRA_Altemose2015_SRR5627147", "SRA_Altemose2015_SRR5627143"), # hPrdm9 HA & V5 vs Input (HA)
              ("SRA_Altemose2015_SRR5627144", "SRA_Altemose2015_SRR5627143"), # cPrdm9 vs (h) Input
              ("SRA_Altemose2015_SRR5627152_AND_SRA_Altemose2015_SRR5627153", "SRA_Altemose2015_SRR5627143"), #SRR5627153 ! # H3K4 peaks wPrdm9
              ("SRA_Altemose2015_SRR5627149", "SRA_Altemose2015_SRR5627143"), # H3K36 peaks wPprdm9
              ("SRA_Altemose2015_SRR5627150", "SRA_Altemose2015_SRR5627142"), # untransfected H3K4 peaks
              ("SRA_Altemose2015_SRR5627148", "SRA_Altemose2015_SRR5627142")] # untransfected H3K36 peaks

comparisons = [("WTCHG_538916_221156", "WTCHG_538916_217108"),  #Zcw only Chip vs Input
              ("WTCHG_538916_223180", "WTCHG_538916_220144"), #Cotransfected Chip vs Cotransfected Input


              ("WTCHG_538916_223180", "WTCHG_538916_221156"),  #Chip with Prdm9 vs Chip
              ("WTCHG_538916_224192", "WTCHG_538916_221156"), # chimpPrdm9 vs chip

              # Human
              ("SRA_Altemose2015_SRR5627138_AND_SRA_Altemose2015_SRR5627139", "SRA_Altemose2015_SRR5627140"), # hPrdm9-Nterm vs Input
              ("SRA_Altemose2015_SRR5627146", "SRA_Altemose2015_SRR5627143"), # hPrdm9 HA vs Input
              ("SRA_Altemose2015_SRR5627147", "SRA_Altemose2015_SRR5627143"), # hPrdm9 V5 vs Input (HA)
              ("SRA_Altemose2015_SRR5627146_AND_SRA_Altemose2015_SRR5627147", "SRA_Altemose2015_SRR5627143"), # hPrdm9-Cterm HA & V5 vs Input (HA)

              # Chimp
              ("SRA_Altemose2015_SRR5627145", "SRA_Altemose2015_SRR5627143"), # cPrdm9 V5 vs Input (HA)
              ("SRA_Altemose2015_SRR5627144", "SRA_Altemose2015_SRR5627143"), # cPrdm9 HA vs (h) Input
              ("SRA_Altemose2015_SRR5627145_AND_SRA_Altemose2015_SRR5627144", "SRA_Altemose2015_SRR5627143"), # cPrdm9 V5 & HA vs Input (HA)

              # Histone Mods
              ("SRA_Altemose2015_SRR5627152_AND_SRA_Altemose2015_SRR5627153", "SRA_Altemose2015_SRR5627143"), # H3K4 peaks wPrdm9
              ("SRA_Altemose2015_SRR5627149", "SRA_Altemose2015_SRR5627143"), # H3K36 peaks wPprdm9
              ("SRA_Altemose2015_SRR5627150", "SRA_Altemose2015_SRR5627142"), # untransfected H3K4 peaks
              ("SRA_Altemose2015_SRR5627148", "SRA_Altemose2015_SRR5627142")] # untransfected H3K36 peaks

comparisons = [("SRA_Altemose2015_SRR5627138_AND_SRA_Altemose2015_SRR5627139", "SRA_Altemose2015_SRR5627140"),# YFP Nterm
                ("SRA_Altemose2015_SRR5627141", "SRA_Altemose2015_SRR5627140")] # YFP Nterm H3K4me3

forcecallAT = "SRA_Altemose2015_SRR5627138_AND_SRR5627139_vs_SRA_Altemose2015_SRR5627140"
forcecallAT = "SRA_Altemose2015_SRR5627146_AND_SRA_Altemose2015_SRR5627147_vs_SRA_Altemose2015_SRR5627143"
forcecallAT = "SRA_Altemose2015_SRR5627138_AND_SRA_Altemose2015_SRR5627139_vs_SRA_Altemose2015_SRR5627140.flank150"
forcecallAT = "genome.windows.100wide.100slide.bed"
forcecallAT = "qPCR_regions_for_validation.bed"

rule all:
  input:
    ["peaks/ForceCalledPeaks_{chip}_vs_{control}_AT_{at}.bed".format(
        chip = chip_id,
        control = control_id, at=forcecallAT) for chip_id, control_id in comparisons]


def get_chips(wildcards):
  if "_AND_" in wildcards.chip:
    two_samples = wildcards.chip.split("_AND_")
    return(list([f'MAPeakCaller/Fragment_Position_{two_samples[0]}.sorted.bed',
                f'MAPeakCaller/Fragment_Position_{two_samples[1]}.sorted.bed']))
  else:
    return(list([f'MAPeakCaller/Fragment_Position_{wildcards.chip}.sorted.bed.PR1',
                f'MAPeakCaller/Fragment_Position_{wildcards.chip}.sorted.bed.PR2']))


rule estconst:
  input:
    chips = get_chips ,
    control="MAPeakCaller/Fragment_Position_{control}.sorted.bed",
    chrsizes=join(METADATA_DIR, "hg38_sizes.chrom"),
  output:
    c="peaks/Constants.{chip}_vs_{control}.tsv",
  threads:
    3
  shell:
    """
    Rscript EstimateConstants.R \
	    peaks/ \
	    {input.chrsizes} \
	    {input.chips[0]} \
	    {input.chips[1]} \
      {input.control} \
      22 \
      {output.c}
    """



rule extend_peaks:
  input:
    forcepos="peaks/SingleBasePeaks.{forcecallAT}.p0.000001.sep250.ALL.bed",
    chrsizes=join(METADATA_DIR, "hg38_sizes.chrom")
  output:
    "peaks/SingleBasePeaks.{forcecallAT}.flank{flank}.p0.000001.sep250.ALL.bed"
  threads:
    1
  shell:
    """
    # bedtools doesn't like the header so use tail -n +2
    tail {input.forcepos} -n +2 | bedtools slop -i - -g {input.chrsizes} -b {wildcards.flank} > {output}
    """

rule call_peaks:
  input:
    chips = get_chips ,
    control="MAPeakCaller/Fragment_Position_{control}.sorted.bed",
    chrsizes=join(METADATA_DIR, "hg38_sizes.chrom"),
    forcepos= lambda wc: "forcepeaks/{forcecallAT}" if(".bed" in wc.forcecallAT) else "peaks/SingleBasePeaks.{forcecallAT}.p0.000001.sep250.ALL.bed",
    consts="peaks/Constants.{chip}_vs_{control}.tsv"
  output:
    p="peaks/ForceCalledPeaks_{chip}_vs_{control}_AT_{forcecallAT}.bed"
  threads:
    3
  shell:
    """
    Rscript ForceCallPeaks.R \
	    peaks/ \
	    {input.chips[0]} \
	    {input.chips[1]} \
      {input.control} \
      {input.consts} \
      {input.forcepos} \
      22 \
      {output.p}
    """

