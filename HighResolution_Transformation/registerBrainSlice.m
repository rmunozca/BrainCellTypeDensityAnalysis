function zEndSlice = registerBrainSlice(inputDir, channel, numOpticalSections, scaleFactor, xDim, yDim, zStart, zEnd, xVals, yVals, zVals)

zEndSlice = zeros(yDim, xDim);

radius = scaleFactor*3;
gaussian = fspecial('gaussian',2*radius+1,scaleFactor);

for zz=zStart:zEnd
    
    zs = floor(zz / numOpticalSections);
    l = zz - (zs * numOpticalSections) + 1;
    
    zFile = fullfile(inputDir, sprintf('stitchedImage_ch%d', channel), sprintf('StitchedImage_Z%03d_L%03d.tif', zs, l));
    zSlice = imread(zFile);
    zSlice = imrotate(zSlice,-90);
    
    [yRows, xCols, ~] = find(zVals == (zz));
    
    for r=1:length(yRows)
        
        xDF = (scaleFactor*(xVals(yRows(r),xCols(r))));
        yDF = (scaleFactor*(yVals(yRows(r),xCols(r))));

        xl = max(1, xDF - radius);
        xr = min(size(zSlice,2), xDF + radius);
        yl = max(1, yDF - radius);
        yr = min(size(zSlice,1), yDF + radius);
        
        if(length(xl:xr) == size(gaussian,2))
            xlm = 1;
            xrm = size(gaussian,2);
        else
            if(xl == 1)
                xlm = size(gaussian,2) - xr + 1;
                xrm = size(gaussian,2);
            else
                xlm = 1;
                xrm = size(zSlice,2) - xl + 1;
            end
        end
        if(length(yl:yr) == size(gaussian,1))
            ylm = 1;
            yrm = size(gaussian,1);
        else
            if(yl == 1)
                ylm = size(gaussian,1) - yr + 1;
                yrm = size(gaussian,1);
            else
                ylm = 1;
                yrm = size(zSlice,1) - yl + 1;
            end
        end
        
        sliceX = xl:xr;
        sliceY = yl:yr;
        maskX = xlm:xrm;
        maskY = ylm:yrm;

        zSliceArea = zSlice(yl:yr, xl:xr);
        gMaskArea = gaussian(ylm:yrm, xlm:xrm);
        
        gzArea = double(zSliceArea) .* gMaskArea;
        
        for j=1:length(sliceX)
            for k=1:length(sliceY)
                x = (scaleFactor*xCols(r) + maskX(j) - radius - 1);
                y = (scaleFactor*yRows(r) + maskY(k) - radius - 1);
                
                val = gzArea(k,j);
                
                if(x <= 0 || y <= 0 || x > size(zEndSlice,2) || y > size(zEndSlice,1))
                    continue;
                end
                
                zEndSlice(y,x) = zEndSlice(y,x) + val;
            end
        end
    end
end
zEndSlice = zEndSlice .* scaleFactor;