addpath('C:\Users\vlab_eye\Documents\local_repo\vlab-ofdi')

% path of the folder containing all acquired data and  
directory = 'D:\OFDIData\user.Ilyas\[p.pig_nh_5mm_pr]\[p.pig_nh_5mm_pr][s.2_prestim_X40_Y20][04-06-2022_10-25-42]';

slices = 512:514; %(1:1184);%(300:300);
zoomFactor = 4;%4;
monitorBscan = 512; %512;
monitorAline = 0;
flipUpDown = 1;
tomoOpt = v2struct(slices, zoomFactor, monitorBscan, monitorAline, flipUpDown);
% ofdiTOMOGRAPHYclean(directory,tomoOpt);

tomoOpt_gpu = tomoOpt;
tomoOpt_gpu.gpuFlag = 0;
[xXfilename, xYfilename] = ofdiTOMOGRAPHYclean_gpu(directory,tomoOpt_gpu); 
%%%>> will need to change REF_lowhigh values when using gpu code.

sprintf('xXfilename = %s \n', xXfilename)

%%
slices = 1:3;%1:1;
meta5tomo = [0 3 5920 1024 3];
monitorBscan = 1;
REF_lowhigh = [-10 90];
% nZpixels = 

structOpt = v2struct(slices,meta5tomo,monitorBscan, REF_lowhigh);
ofdiSTRUCTUREclean(directory,structOpt);

%%
REF_lowhigh = [10 40];
angioOpt = v2struct(slices,meta5tomo,monitorBscan,REF_lowhigh);
ofdiANGIOGRAPHYclean(directory,angioOpt);
