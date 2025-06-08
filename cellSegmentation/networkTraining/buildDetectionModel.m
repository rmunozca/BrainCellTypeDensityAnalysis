function lgraph = buildYOLOModel(inputSize, numClasses)
%BUILDYOLOMODEL Constructs a YOLOv2 object detector with ResNet-50
lgraph = yolov2Layers(inputSize, numClasses, 'resnet50');
end
