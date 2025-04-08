function registerWholeBrain(inputDir, registrationScaleFactor, outputScaleFactor, channel, numOpticalSections)

zPtsDir = fullfile(inputDir, 'warping', 'df_z.nrrd');
[zPts, ~] = nrrdread(zPtsDir);
zPts = squeeze(zPts);
zDim = size(zPts,1);

yPtsDir = fullfile(inputDir, 'warping', 'df_y.nrrd');
[yPts, ~] = nrrdread(yPtsDir);
yPts = squeeze(yPts);
yDim = size(yPts,2) * registrationScaleFactor;

xPtsDir = fullfile(inputDir, 'warping', 'df_x.nrrd');
[xPts, ~] = nrrdread(xPtsDir);
xPts = squeeze(xPts);
xDim = size(xPts,3) * registrationScaleFactor;

minmax = zeros(2,zDim);

for i=1:zDim
   zPtsZ = squeeze(zPts(i, :,:));
   un = unique(zPtsZ);
   if(un(1) ~= 0)
        minmax(1,i) = un(1);
   elseif(length(un) > 1)
       minmax(1,i) = un(2);
   else
       minmax(1,i) = 1;
   end
   if(length(un) > 1)
       minmax(2,i) = max(max(zPtsZ));
   else
       minmax(2,i) = 1;
   end
end

re = regexp(inputDir, filesep, 'split');
re = re(length(re));
brainName = re{1};

parfor i=1:zDim
   xVals = squeeze(xPts(i,:,:));
   yVals = squeeze(yPts(i,:,:));
   zVals = squeeze(zPts(i,:,:));
   
   im = registerBrainSlice(inputDir, channel, numOpticalSections, registrationScaleFactor, xDim, yDim, minmax(1,i), minmax(2,i), xVals, yVals, zVals); 

   zs = floor(i / numOpticalSections);
   l = i - (zs * numOpticalSections) + 1;
   
   outputFile = fullfile(inputDir, sprintf('registeredImage_ch%d', channel), strcat(brainName, sprintf('_RegisteredImage_Z%03d_L%03d.tif', zs, l)));
   imwrite(uint16(im .* outputScaleFactor), outputFile, 'TIFF');   
end