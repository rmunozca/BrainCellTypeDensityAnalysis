function trainingData = loadDetectionTrainingData(imageDir, labelDir)
%LOADDETECTIONTRAININGDATA Load images and bounding boxes from .mat label files

% Get list of label files
labelFiles = dir(fullfile(labelDir, '*.mat'));
bboxData = {};
imageFilenames = {};

for k = 1:length(labelFiles)
    labelPath = fullfile(labelDir, labelFiles(k).name);
    labelStruct = load(labelPath);

    % Assumes labelStruct contains 'bbox' and 'filename'
    bboxData{end+1,1} = labelStruct.bbox;
    imageFilenames{end+1,1} = fullfile(imageDir, labelStruct.filename);
end

bboxTbl = table(imageFilenames, bboxData, 'VariableNames', {'imageFilename', 'cell'});
trainingData = objectDetectorTrainingData(bboxTbl, 'ReadFcn', @imread);
end
