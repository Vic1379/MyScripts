import os
from osgeo import gdal
from tqdm import tqdm

# Source Image to True and False color variants, Translate Params from XML file
PATH_SRC = 'C:\\SRC'
PATH_PAR = 'C:\\PARAMS'
PATH_OUT_TRUE = 'C:\\OUT_TRUE'
PATH_OUT_FALSE = 'C:\\OUT_FALSE'

for file in tqdm(os.listdir(PATH_SRC)):
    src = os.path.join(PATH_SRC, file)

    # Parse Source file such as "KV6_29261_31279_01_KANOPUS_20240405_021418_021445.SCN01.PMS.L2.tif"
    info, scn, _, _, _ = file.split('.')
    n1, n2, _, _, _, date, _, _ =  info.split('_')
    core = '_'.join([n1, n2, date, scn])
    
    # Read corresponding Params files such as "KV6_29261_20240405_SCN01_true.xml"
    with open(os.path.join(PATH_PAR, core+'_true.xml')) as f:
        pars_true = f.read().replace('/', '') # for "start" and "end" tags to match
    with open(os.path.join(PATH_PAR, core+'_false.xml')) as f:
        pars_false = f.read().replace('/', '')

    # Split by appropriate tags, ODD elements are Params!
    pars_true_min, pars_true_max = pars_true.split('<min>'), pars_true.split('<max>')
    pars_false_min, pars_false_max = pars_false.split('<min>'), pars_false.split('<max>')

    # TRUE STATS
    min1_true, min2_true, min3_true = pars_true_min[1], pars_true_min[3], pars_true_min[5]
    max1_true, max2_true, max3_true = pars_true_max[1], pars_true_max[3], pars_true_max[5]
    # FALSE STATS
    min4_false, min1_false, min2_false = pars_false_min[1], pars_false_min[3], pars_false_min[5]
    max4_false, max1_false, max2_false = pars_false_max[1], pars_false_max[3], pars_false_max[5]
    
    if not os.path.isdir(PATH_OUT_TRUE):
        os.makedirs(PATH_OUT_TRUE)
    if not os.path.isdir(PATH_OUT_FALSE):
        os.makedirs(PATH_OUT_FALSE)
    out_true = os.path.join(PATH_OUT_TRUE, core+'_true.tif')
    out_false = os.path.join(PATH_OUT_FALSE, core+'_false.tif')

    # GDAL Translate example usage
    co = ['TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256', 'BIGTIFF=IF_SAFER',
        'COPY_SRC_OVERVIEWS=YES', 'COMPRESS=LZW', 'PREDICTOR=1']
    scale_t = [(min1_true, max1_true), (min2_true, max2_true), (min3_true, max3_true)]
    scale_f = [(min1_false, max1_false), (min2_false, max2_false), (1, 188), (min4_false, max4_false)]
    gdal.Translate(out_true, src, format='GTiff', creationOptions=co, scaleParams=scale_t, bandList=[1, 2, 3])
    gdal.Translate(out_false, src, format='GTiff', creationOptions=co, scaleParams=scale_f)
