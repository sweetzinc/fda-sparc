
# Dev history notes:
2021-11-22
Add the random scripts (rand01, rand02) - i.e. unrelated to project - that I used to make the processing and folder organizations easier

2021-11-18
Investigated MATLAB script to generate HSV projection using Damon's code `D:\SPARC-FDA\OA_HDF5\After_Damon_SNoaxisReconstruction_exe_batch.m`. It is extremely important that ROIs are selected correctly in `getPhantomOAI.m`. Looking at the selected frames can help. 

2021-11-16
implement batch processing (test11)

2021-11-01
streamlined processing on spyder (test10)



# Files:
### FDASPARC_test_nosb
    no spectral binning, primarily analyzing the fringes, strangeness in the raw stokes data that cause the "sandwich-like banding" of the optic axis in the nerve.
### test10 
    single dataset processing, streamlined processing on spyder.
### test11
    batch process the Raw data