function createSubImgs(rawdir, labeldir, outputdir, loutputdir, numSubimgs, xSize, ySize)
%CREATESUBIMGS Generates labeled image patches from full-resolution images
%   createSubImgs(rawdir, labeldir, outputdir, loutputdir, numSubimgs, xSize, ySize)
%
%   Inputs:
%     rawdir      - Directory with raw .tif images
%     labeldir    - Directory with label .tif images
%     outputdir   - Directory to save extracted raw image patches
%     loutputdir  - Directory to save extracted label image patches
%     numSubimgs  - Number of sub-images per original image
%     xSize       - Patch width
%     ySize       - Patch height

if ~isfolder(outputdir); mkdir(outputdir); end
if ~isfolder(loutputdir); mkdir(loutputdir); end

rawfiles = dir(fullfile(rawdir, '*.tif'));
labelfiles = dir(fullfile(labeldir, '*.tif'));

parfor i = 1:length(rawfiles)
    img = imread(fullfile(rawfiles(i).folder, rawfiles(i).name));
    limg = imread(fullfile(labelfiles(i).folder, labelfiles(i).name));

    for j = 1:numSubimgs
        % Find a random labeled patch (non-zero label)
        valid = false;
        while ~valid
            indxX = randi([1 + xSize, size(img, 1) - xSize]);
            indxY = randi([1 + ySize, size(img, 2) - ySize]);
            if limg(indxX, indxY) > 0
                valid = true;
            end
        end

        % Extract and save patches
        subRaw = img(indxX - xSize + 1:indxX, indxY - ySize + 1:indxY);
        subLbl = limg(indxX - xSize + 1:indxX, indxY - ySize + 1:indxY);

        [~, baseName, ~] = fileparts(rawfiles(i).name);
        outName = sprintf('%s_patch_%d.tif', baseName, j);

        imwrite(subRaw, fullfile(outputdir, outName));
        imwrite(subLbl, fullfile(loutputdir, outName));
    end
end
end
