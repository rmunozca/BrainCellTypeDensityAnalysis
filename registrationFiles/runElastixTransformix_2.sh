export FIXED_IMAGE=/mnt/brainmapstore/rmunozca/celltypes/ImagesForFigures/cellTypes/registration/BrainFeaturesTemplate_flip_25um_264.tif
export MOVING_IMAGE=/mnt/brainmapstore/rmunozca/celltypes/Ramesh/MotorCortexMeeting/180629_AB_Gad2Ai75374108_processed/warping/180629_AB_Gad2Ai75374108_processed_ch2_p05_processed.tif

export AFFINEPARFILE=/data/rmunozca/Registration_Parameters/Par0000affine_rmc.txt
export BSPLINEPARFILE=/data/rmunozca/Registration_Parameters/Par0000bspline_rmc.txt

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/elastix/lib/
export ELASTIX=/usr/local/elastix/bin/elastix
export ELASTIX_OUTPUT_DIR=elastixOutput_2
mkdir $ELASTIX_OUTPUT_DIR

$ELASTIX -threads 24 -m $MOVING_IMAGE -f $FIXED_IMAGE -p $AFFINEPARFILE -p $BSPLINEPARFILE -out $ELASTIX_OUTPUT_DIR


export inputImage=/mnt/brainmapstore/rmunozca/celltypes/Ramesh/MotorCortexMeeting/annotationAtlas.tif

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/elastix/lib/
export TRANSFORMIX=/usr/local/elastix/bin/transformix

cd elastixOutput_2*
cp TransformParameters.0.txt TransformParameters_labels.0.txt
cp TransformParameters.1.txt TransformParameters_labels.1.txt
sed -i 's/TransformParameters.0.txt/TransformParameters_labels.0.txt/g' TransformParameters_labels.1.txt
sed -i 's/FinalBSplineInterpolationOrder 3/FinalBSplineInterpolationOrder 0/g' TransformParameters_labels.1.txt
sed -i 's/(ResultImageFormat "mhd")/(ResultImageFormat "nrrd")/g' TransformParameters_labels.0.txt
sed -i 's/(ResultImageFormat "mhd")/(ResultImageFormat "nrrd")/g' TransformParameters_labels.1.txt
sed -i 's/(ResultImagePixelType "short")/(ResultImagePixelType "float")/g' TransformParameters_labels.0.txt
sed -i 's/(ResultImagePixelType "short")/(ResultImagePixelType "float")/g' TransformParameters_labels.1.txt

cd -

export parameters=`expr "$ELASTIX_OUTPUT_DIR"/TransformParameters_labels.1.txt`
export transformixoutputdir=transformixOutput_2
mkdir $transformixoutputdir

$TRANSFORMIX -threads 16 -in $inputImage -tp $parameters -out $transformixoutputdir

