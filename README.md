# BSRLC
Baltic Sea Region Land Cover scripts

# Requirements 
- FORCE ARD data in Fold-by-month format (FBD) in the **FORCE_datacube_fbm**. In each tile, it muss contain the following bands:
  + {year}-{year}_001-365_HL_TSA_LNDLG_BLU_FBW.tif
  + {year}-{year}_001-365_HL_TSA_LNDLG_GRN_FBW.tif
  + {year}-{year}_001-365_HL_TSA_LNDLG_NDV_FBW.tif
  + {year}-{year}_001-365_HL_TSA_LNDLG_NIR_FBW.tif
  + {year}-{year}_001-365_HL_TSA_LNDLG_RED_FBW.tif
  + {year}-{year}_001-365_HL_TSA_LNDLG_SAV_FBW.tif
  + {year}-{year}_001-365_HL_TSA_LNDLG_SW1_FBW.tif
  + {year}-{year}_001-365_HL_TSA_LNDLG_SW2_FBW.tif
- {year} must be singular year (eg. 2015-2015) not two different years (eg. 2014-2015) 
 

# 1. Creat the python environment via conda
```python
conda create --name BSRLC --file req.txt
```

# 2. Activate environment
```python
conda activate BSRLC
``` 

# 3. Run the mapping from pretrained models
For example, to predict maps for tile **X0068_Y0035** in year **2015**, run:
```python
python mapping.py --tile X0068_Y0035 --year 2015
``` 

The results are stored in the **Maps** directory with the same datacube structure as the **FORCE_datacube_fbm**.
