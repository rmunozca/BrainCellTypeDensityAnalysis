function outputNetwork = trainDetectionNetwork(imageDir, labelDir)
%TRAINDETECTIONNETWORK Main function to train YOLOv2 object detector

if ~isfolder(imageDir)
    error('Image directory does not exist: %s', imageDir);
end
if ~isfolder(labelDir)
    error('Label directory does not exist: %s', labelDir);
end

trainingData = loadDetectionTrainingData(imageDir, labelDir);
inputSize = [224 224 3];
numClasses = width(trainingData) - 1;
lgraph = buildYOLOModel(inputSize, numClasses);
options = getTrainingOptions();

outputNetwork = trainYOLOv2ObjectDetector(trainingData, lgraph, options);
end
