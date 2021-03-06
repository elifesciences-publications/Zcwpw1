
from os.path import join

configfile: 'pipelines/config.yml'

METADATA_DIR = config["metadata_dir"]

sample, strand, gz = glob_wildcards("data/dmc1/ssDNA_{sample}_rep1_type1_filtered_only_rmdup.chrALL.{strand}prime.{gz}")

rule all:
    input:
        "results/dmc1/DMC1_SSDS_plot.rds",
        "results/dmc1/DMC1_stratified.rds"

# Manual Step:
# combine seperate chromosome files into one
# cat ssDNA_ZCWPW1_HOM_260619_rep1_type1_filtered_only_rmdup.chr*.5prime.bedgraph.gz > ssDNA_ZCWPW1_HOM_260619_rep1_type1_filtered_only_rmdup.chrALL.5prime.bedgraph.gz
# 
# cat ssDNA_ZCWPW1_HOM_260619_rep1_type1_filtered_only_rmdup.chr*.3prime.bedgraph.gz > ssDNA_ZCWPW1_HOM_260619_rep1_type1_filtered_only_rmdup.chrALL.3prime.bedgraph.gz
# 
# cat WT/ssDNA_B6_Sample1_Brick2012_rep1_type1_filtered_only_rmdup.chr*.3prime.bedgraph > WT/ssDNA_B6_Sample1_Brick2012_rep1_type1_filtered_only_rmdup.chrALL.3prime.bedgraph 
# 
# cat WT/ssDNA_B6_Sample1_Brick2012_rep1_type1_filtered_only_rmdup.chr*.5prime.bedgraph > WT/ssDNA_B6_Sample1_Brick2012_rep1_type1_filtered_only_rmdup.chrALL.5prime.bedgraph 


rule gzip:
  input:
    "{sample}"
  output:
    "{sample}.gz"
  shell:
    "gzip -k {input}"


rule clean:
  # remove odd chromosomes
  # reomve Mitochondria, Sex
  # convert chr1 to 1
  input:
    "data/dmc1/ssDNA_{sample}_rep1_type1_filtered_only_rmdup.chrALL.{strand}prime.bedgraph.gz"
  output:
    "data/dmc1/ssDNA_{sample}_rep1_type1_filtered_only_rmdup.chrALLclean.{strand}prime.bedgraph"
  shell:
    """
    zgrep -v '_' {input} | grep -vP 'M|X|Y' | sed 's/chr//' > {output}
    """


rule bedtoBigWig:
  #
  # compress to bigwig for faster downstream processing
  #
  input:
    "data/dmc1/ssDNA_{sample}_rep1_type1_filtered_only_rmdup.chrALLclean.{strand}prime.bedgraph"
  output:
    "data/dmc1/{sample}_{strand}prime.bigWig"
  params:
    join("../",METADATA_DIR, "mm10_sizes.chrom")
  shell:
    """
    bedGraphToBigWig {input} {params} {output}
    """


rule averageProfile:
  input:
    sample="data/dmc1/{sample}_{strand}prime.bigWig",
    b6="data/dmc1/B6.bed",
    ko="data/dmc1/KO.bed"
  output:
    b6="data/dmc1/{sample}_{strand}prime_atB6.tsv",
    b6m="data/dmc1/{sample}_{strand}prime_atB6.bwm",
    ko="data/dmc1/{sample}_{strand}prime_atKO.tsv"
  params:
    a=5000,
    b=5000
  shell:
    """
    bwtool aggregate {params.a}:{params.b} {input.b6} {input.sample} {output.b6} -fill=0
    bwtool aggregate {params.a}:{params.b} {input.ko} {input.sample} {output.ko} -fill=0
    
    bwtool matrix -fill=0 -decimals=1 -tiled-averages=5 {params.a}:{params.b} {input.b6} {input.sample} {output.b6m}
    """


rule beds:
  # create bed file from composite file form Anjali
  #1 = chr (20 = X?)
  #4 = allele (B6, KO, or UNK)
  #5 = hshared
  #10 = motif center pos
  input:
    b6="data/dmc1/B6_composite.txt",
    ko="data/dmc1/KO.txt"
  output:
    ko="data/dmc1/KO.bed",
    b6="data/dmc1/B6.bed",
    b6f="data/dmc1/B6_composite_filtered.bed"
  shell:
    """
    awk -v OFS='\t' '$10=sprintf("%.0f",$10) {{if($1 != "20" && $5=="0" && $4=="B6") print $1,$10,$10,"0","0","+";}}'  {input.b6} > {output.b6}
    awk -v OFS='\t' '$10=sprintf("%.0f",$10) {{if($1 != "20" && $5=="0" && $4=="B6") print $0;}}'  {input.b6} > {output.b6f}
    awk -v OFS='\t' '{{if($1 != "20") print $1,$2,$2,"0","0","+";}}'  {input.ko} | tail -n +2 > {output.ko}
    """

rule spo11:
  input:
    bg="data/dmc1/B6_Spo11.bedgraph",
    b6="data/dmc1/B6.bed"
  output:
    out='data/dmc1/B6_Spo11_atB6.bwm'
  shell:
    """
    sed 's/chr//' data/dmc1/B6_Spo11.bedgraph > data/dmc1/B6_Spo11_clean.bedgraph
    zgrep -v '_' data/dmc1/B6_Spo11.bedgraph | grep -vP 'M|X|Y' | sed 's/chr//' > data/dmc1/B6_Spo11_clean.bedgraph
    bedGraphToBigWig data/dmc1/B6_Spo11_clean.bedgraph ../../single-cell/sequencing/metadata/mm10_sizes.chrom data/dmc1/B6_Spo11.bedgraph.bigWig
    bwtool matrix -fill=0 -decimals=1 -tiled-averages=5 5000:5000 {output.b6} data/dmc1/B6_Spo11.bedgraph.bigWig {output.out}
    """

rule plotdmc1:
  input:
    'data/dmc1/B6_Spo11_atB6.bwm',
    "data/dmc1/B6_composite_filtered.bed",
    "data/dmc1/B6_composite.txt",
    expand("data/dmc1/{sample}_{strand}prime_atB6.tsv", sample=set(sample), strand=set(strand)),
    expand("data/dmc1/{sample}_{strand}prime_atKO.tsv", sample=set(sample), strand=set(strand))
  output:
    "results/dmc1/DMC1_SSDS.pdf",
    "results/dmc1/DMC1_SSDS_plot.rds",
    "results/dmc1/DMC1_stratified-1.pdf",
    "results/dmc1/DMC1_stratified.rds"
  shell:
    """
    Rscript pipelines/plotDMC1.R
    R -e "knitr::knit('analysis/dmc1_stratification.Rmd', 'results/dmc1_stratification.md')"
    R -e "knitr::knit('analysis/dmc1.Rmd', 'results/dmc1.md')"
    """
