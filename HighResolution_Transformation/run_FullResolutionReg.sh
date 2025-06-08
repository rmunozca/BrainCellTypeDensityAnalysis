export SVN_REVISION=20180828
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/MCR/v93/bin/glnxa64:.
export ORIGINAL_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
#export LD_LIBRARY_PATH=/usr/local/MCR/v80/runtime/glnxa64:/usr/local/MCR/v80/bin/glnxa64:/usr/local/MCR/v80/sys/os/glnxa64:/usr/local/MCR/v80/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:/usr/local/MCR/v80/sys/java/jre/glnxa64/jre/lib/amd64/server:/usr/local/MCR/v80/sys/java/jre/glnxa64/jre/lib/amd64:$LD_LIBRARY_PATH
#export MCR80_DIRECTORY=/usr/local/MCR/v80
export INSTALL_PREFIX=`expr /usr/local/openSTP/V"$SVN_REVISION"`


# Detecting the current working directory and setting as it as the dataset home
export DATASET_HOME=`pwd`
DATASET_HOME=`echo $DATASET_HOME/`
echo "Setting DATASET_HOME=$DATASET_HOME"

export IMAGEFOLDER=`expr "$DATASET_HOME"stitchedImage_ch1/`
export IMAGE_SCALING_FACTOR=20

# Setting the dataset_prefix variable
export DATASET_PREFIX=${PWD##*/}
echo "Setting DATASET_PREFIX=$DATASET_PREFIX"

export WARPING_RIDECTORY=`expr "$DATASET_HOME"warping/`

export WARPING_IMAGE=`expr "$WARPING_RIDECTORY"*_ch2_p05.tif`
export REFERENCE_BRAIN=/data/rmunozca/BrainMap/BrainFeaturesTemplate_264_flip.tif

export ELASTIX_OUTPUT_DIR=`expr "$WARPING_RIDECTORY"/elastixOutput`
mkdir $ELASTIX_OUTPUT_DIR
export TRANSFORMIX_OUTPUT_DIR=`expr "$WARPING_RIDECTORY"/transformixOutput`
mkdir $TRANSFORMIX_OUTPUT_DIR

echo "Setting DATASET_PREFIX=$DATASET_PREFIX"
echo "Setting DATASET_PREFIX=$WARPING_RIDECTORY"
echo "Setting DATASET_PREFIX=$WARPING_IMAGE"
echo "Setting DATASET_PREFIX=$ELASTIX_OUTPUT_DIR"
echo "Setting DATASET_PREFIX=$INPUTVOLUMEFILE"

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/elastix/lib/
export ELASTIX=/usr/local/elastix/bin/elastix
export AFFINEPARFILE=/data/rmunozca/Registration_Parameters/Par0008affine.txt
export BSPLINEPARFILE=/data/rmunozca/Registration_Parameters/Par0018bspline.txt
export MCR_DIRECTORY=/usr/local/MCR/v93
$ELASTIX -threads 16 -m $WARPING_IMAGE -f $REFERENCE_BRAIN -p  $AFFINEPARFILE -p $BSPLINEPARFILE -out $ELASTIX_OUTPUT_DIR

export INPUTVOLUMEFILE=$WARPING_RIDECTORY/*ch1_p05.tif
export CREATEDEFORMATIONFILES=`expr "$INSTALL_PREFIX"/bin/run_createRegistrationValidationImagesTif.sh`

$CREATEDEFORMATIONFILES $MCR_DIRECTORY $WARPING_IMAGE

export xDEF=`expr "$DATASET_HOME"/xGrid.tif`
export yDEF=`expr "$DATASET_HOME"/yGrid.tif`
export zDEF=`expr "$DATASET_HOME"/zGrid.tif`

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/elastix/lib/
export TRANSFORMIX=/usr/local/elastix/bin/transformix

cd $ELASTIX_OUTPUT_DIR*
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

$TRANSFORMIX -threads 16 -in $yDEF -tp $parameters -out $TRANSFORMIX_OUTPUT_DIR
mv $TRANSFORMIX_OUTPUT_DIR/result.nrrd $WARPING_RIDECTORY/df_y.nrrd

$TRANSFORMIX -threads 16 -in $xDEF -tp $parameters -out $TRANSFORMIX_OUTPUT_DIR
mv $TRANSFORMIX_OUTPUT_DIR/result.nrrd $WARPING_RIDECTORY/df_x.nrrd
#/usr/local/c3d/bin/c3d $WARPING_RIDECTORY/df_x.nrrd -flip xy -o $WARPING_RIDECTORY/df_x.nrrd

$TRANSFORMIX -threads 16 -in $zDEF -tp $parameters -out $TRANSFORMIX_OUTPUT_DIR
mv $TRANSFORMIX_OUTPUT_DIR/result.nrrd $WARPING_RIDECTORY/df_z.nrrd

echo "Setting inputDir=$inputDir"
export OutputFullResDir=`expr "$IMAGEFOLDER"_register`
mkdir $OutputFullResDir
export CODEPATH=/data/palmer/registration

matlab -nosplash -nodesktop -r "$CODEPATH"/registerWholeBrain '$DATASET_HOME' $IMAGEFOLDER $IMAGE_SCALING_FACTOR;"


