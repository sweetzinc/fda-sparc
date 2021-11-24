# Processing and testing the FDA-SPARC dataset

This repo contains scripts to test the prcessing of FDA-SPARC dataset (for Guillermo's JNE paper) using `oct-cbort`.

If not using Spyder, the command line can be used to process from the `settings\editsettings.ini` file.

```
python -m oct D:\SPARC-FDA\SL2\OS1_D1 struct+angio+ps+hsv mgh 1-200

```
The datasets are located in `vlab-eye` local drive. 

## Standard workflow
1. Use `oct-cbort` to process optic axis and PS
2. Use Damon's OA correction (adapted by Ilyas) to use phantom ROIs to rotate the OAs and calculate theta
(`D:\SPARC-FDA\OA_HDF5`)