% implement rejection-based motion artifact suppression
% work with .ofd files (using ofdiTOMOGRAPHY on frame to frame basis


clear all; %close all; clc;

addpath('C:\Users\vlab_eye\Documents\local_repo\vlab-ofdi')
% momDirectory = 'Z:\OFDIData\user.Stephanie\[p.PNStim]';
% listDirectory = dir(momDirectory);

% for iDirectory = [20:47]
% directory = fullfile(momDirectory, listDirectory(iDirectoray).name);
directory = 'D:\OFDIData\user.Ilyas\[p.pig_nh_5mm_pr]\[p.pig_nh_5mm_pr][s.2_prestim_X40_Y20][04-06-2022_10-25-42]';

[~,fileID,~] = fileparts(getPath4ext(directory,'ofb'));

% original dataset parameters
    scanInfo = loadScanInfo(directory);
    aqSettings = loadAqSettings(directory);
        nZpixels = aqSettings.nSamples; %aqSettings.zPixels;
        nAlinesToProcTomo = scanInfo.nAlinesToProcTomo;
        nFrames = scanInfo.nFrames;
        imgWidth = scanInfo.imgWidthStr;
        nMeasurements = scanInfo.imgDepthStr;
    nSegments = 4;

% construct all possible pairs, to be done only once, hence not in loop
pairA = []; pairB = [];
for delta =  1:(nMeasurements)
    for iA = 1:(nMeasurements-delta)
        iB = iA + delta; pairA = [pairA,iA]; pairB = [pairB,iB];
    end
end
nPairs = numel(pairA);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% set parameters
slices = 512; %1:nFrames;                                                                                                                                                  
measurements = 1:nMeasurements;
segments = 1:nSegments;

cBlack = 0.3;
cPairs = 3;
haveScatFiles = sum(getPath4namestr(directory, [num2str(nFrames), '].scatxX.mgh']))>1; % already have full volume scatX and scatY
monitorFalg = ~(numel(slices)>1);
monitorAllPairs = true;
writeVolume =(length(slices)==nFrames);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

tomoOpt.flipUpDown = true;
tomoOpt.monitorBscan = false;%slices;
if writeVolume
    meta5angio = [0 0 imgWidth nZpixels numel(slices)];
    angioFfile = fullfile(directory, [fileID, '.angioNew.mgh']);
    writeMgh('clear', meta5angio, angioFfile);
end

for iFrame = slices
    iFrame
    
tomoOpt.slices = iFrame; 
%slices in the optional structure is different because of how the function is set up.
if haveScatFiles
    scatX_fullfile = getPath4namestr(directory, [num2str(nFrames), '].scatxX.mgh']);
    scatY_fullfile = getPath4namestr(directory, [num2str(nFrames), '].scatxY.mgh']);
            readScatOpt.iFrame = iFrame;
else
    [scatX_fullfile, scatY_fullfile] = ofdiTOMOGRAPHYclean_gpu(directory, tomoOpt);
    readScatOpt.iFrame = 1;
    readScatOpt.metadata = [0 3 nAlinesToProcTomo nZpixels nFrames];

end
    
% read scatX and Y, resape them into measurement seperated volumes        
        readScatOpt.metadata = readMetaMgh(scatY_fullfile);
    scatXmgh = readMgh(scatX_fullfile,readScatOpt);
    scatYmgh = readMgh(scatY_fullfile,readScatOpt);

    scatXreshape = reshape(scatXmgh, [],imgWidth);
    temp = reshape(scatXreshape',imgWidth,[],nMeasurements);
    scatXreshape = permute(temp,[2 1 3]); 
    scatYreshape = reshape(scatYmgh, [],imgWidth);
    temp = reshape(scatYreshape',imgWidth,[],nMeasurements);
    scatYreshape = permute(temp,[2 1 3]); 

%     if false % monitor scat readings
%     figure(10); 
%     imagesc(20*log10(abs(scatXmgh(:,:,1)))); %colormap('gray'); 
%     colorbar;
%     end
    
% calculate angio for all pairs & ratioBlack % cBlack = 0.3;
blackRatio = zeros(nPairs, nSegments);
    for iPair = 1:nPairs
        frameAX = scatXreshape(:,:, pairA(iPair));
        frameBX = scatXreshape(:,:, pairB(iPair));
        [intensityAveFrameX, absZsumFrameX] = computeAngioFrames(frameAX,frameBX);
        %intensityAveFrameX = 0.5*(abs(frameAX).^2 + abs(frameBX).^2);
        frameAY = scatYreshape(:,:, pairA(iPair));
        frameBY = scatYreshape(:,:, pairB(iPair));
        [intensityAveFrameY, absZsumFrameY] = computeAngioFrames(frameAY,frameBY);
        %intensityAveFrameY = 0.5*(abs(frameAY).^2 + abs(frameBY).^2);
        
            isXbig = (intensityAveFrameX>intensityAveFrameY);
            intensityAveFrame = intensityAveFrameX.*isXbig + intensityAveFrameY.*~isXbig;
            absZsumFrame = absZsumFrameX.*isXbig + absZsumFrameY.*~isXbig;
        angioTemp = sqrt(1-absZsumFrame./intensityAveFrame);

        intensityAveVol(:,:,iPair) = intensityAveFrame;
        absZsumVol(:,:,iPair) = absZsumFrame;
        
        if monitorAllPairs % monitor all differential pairs
        figure(11); subplot(7,3,iPair);
        imagesc(angioTemp, [0 1]); %colormap('gray'); 
        colorbar;
        title(mat2str([iFrame, iPair, nPairs]));
        end
        
        temp = reshape(angioTemp,nZpixels*(imgWidth/nSegments),nSegments);
        blackRatio(iPair, :) = sum(temp<cBlack, 1)/(nZpixels*(imgWidth/nSegments));
    end %iPair

    
% now get angio image using the best few pairs for each segment % cPairs = 2;
angio = zeros(nZpixels, imgWidth);
pairsInfo = [iFrame];
pairsArray = zeros(length(slices), 1+cPairs*nSegments);
    for iSegment = 1:nSegments
        [~, sortIndex] = sort(blackRatio(:, iSegment),1,'descend');
        alines = (imgWidth/nSegments)*(iSegment-1)+[1:(imgWidth/nSegments)];
        num = zeros(nZpixels,(imgWidth/nSegments));
        den = zeros(nZpixels,(imgWidth/nSegments));
        pairs = sortIndex(1:cPairs);
        for iPair = pairs(:)'
            num = num + absZsumVol(:,alines,iPair);
            den = den + intensityAveVol(:,alines,iPair);
        end
        angio(:,alines) = sqrt(1-num./den);
        pairsInfo = [pairsInfo(:); sortIndex(1:cPairs)];
        
    end % iSegment
    pairsArray(iFrame - slices(1) +1, :) = pairsInfo;
    if monitorFalg % monitor surface detection
        
        angioReadOpt.iFrame = iFrame;
        angioBefore = readMgh(getPath4namestr(directory,'angiography8.mgh'),angioReadOpt);
        figure(12); 
        subplot(2,1,1); imagesc(angioBefore/255, [0 1]); colorbar; 
        title(['BEFORE, iFrame = ', num2str(iFrame)]);
            
        subplot(2,1,2); imagesc(angio, [0 1]); colorbar;
        title(['AFTER: ', mat2str(pairsInfo(:)')]);
    
    end
    if writeVolume
    writeMgh('append', meta5angio, angioFfile, uint8(angio.*255));
    end
end
if writeVolume
    save([directory, filesep, fileID, 'pairsArray.mat'], 'pairsArray');
end

% end % for iDirectory = 
