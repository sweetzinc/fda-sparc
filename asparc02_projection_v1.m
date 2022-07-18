% (20220204)Copled from vlab-ofdi\a0b_angioProjection.m for RatBurn batch
% angiography projection
% addpath 'C:\Users\Triband\Dropbox (MIT)\dropboxMatlab\codeCleanUp'
addpath('C:\Users\vlab_eye\Documents\local_repo\vlab-ofdi');

%%
% % directory = 'Z:\OFDIData\user.Stephanie\[p.Claudio]\[p.Claudio][s.test09][06-21-2017_14-29-53]';
% % [~,fileID,~] = fileparts(getPath4ext(directory,'ofb'));
% % fullfile_ofdiWEIGHT = getPath4namestr(directory, 'weight8.mgh');
% % fullfile_ofdiANGIO = getPath4namestr(directory, 'angiography8.mgh');
% 
directory = 'D:\OFDIData\user.Ilyas\[p.pig_nh_5mm_pr]\[p.pig_nh_5mm_pr][s.2_prestim_X40_Y20][04-06-2022_10-25-42]';
fileID = '[p.pig_nh_5mm_pr][s.2_prestim_X40_Y20][04-06-2022_10-25-42]'
fullfile_ofdiWEIGHT = getPath4namestr(directory, 'ofdiWEIGHT.mgh');
fullfile_ofdiANGIO = getPath4namestr(directory, 'angioMin.mgh');

% batch_dir = 'F:\[p.CombBurn]';
batch_dir = 'F:\[p.CombBurn11]';
listing = dir(batch_dir)

% for ii= 3:length(listing) %[3,4,6,7,8,9] %
%     fileID = listing(ii).name
%     directory = fullfile(batch_dir, fileID, 'Processed');
% 
%     fullfile_ofdiWEIGHT = getPath4namestr(directory, 'weight.mgh');
%     fullfile_ofdiANGIO = getPath4namestr(directory, 'angio.mgh');

clear opt
    % Define projection parameters and create an option structure opt
    index = [400 800]; %[515 690];%[250 850];%[280 800];%%[300 900]+15;
%     load('angioCmap.mat'); %  
% %     load('hotCmap.mat'); cMap = hotCmap;
% %     cMap = colormap('gray');
    cMap = ones(64,3);
    opacity = 0.05;
    black = 31;%%16;%64; % mean+std 
    scale = 400;%35;%220;
    attenuation = 0.2;%0.5;
    cMapP = 1.0;%1.5;
    weight = [128, 250]; %[59 160];%[60 128]; % mean+std, % mean-std
    slices = 1:1184;%1:3552;%1714;%1:1184;%800:1200;%
    isTrial = ( numel(slices)==1 );
    monitorFlag = 1; %( numel(slices)==1 ); % takes either 0 (false) or 1(true)
    if contains(fullfile_ofdiANGIO,'mrcdv')
        saveString = 'mrcdv';
    else
        saveString = '';%'mrcdv';
    end

    opt = v2struct(fullfile_ofdiANGIO, fullfile_ofdiWEIGHT, ...
        index, opacity, black, scale, attenuation, cMap, cMapP, weight, ...
        slices, monitorFlag, saveString);
    
%     opt = v2struct(index, opacity, black, scale, attenuation, cMap, cMapP, weight, slices, monitorFlag);

    [ projection, cMapExp ] = ...
        angioProjection( fullfile(directory), fileID, opt );
    
    if (numel(slices)>100)
    figure(); imshow(projection,[0 2^16]);  colorbar;
    title(fileID);
    end
    
% end %for ii=3:length(listing)
