"""
Make sure the python interpreter for Spyder is the conda environment for `oct-cbort` library.
That conda environment must also have `spyder-kernels` installed.

ref. https://github.com/spyder-ide/spyder/wiki/Working-with-packages-and-environments-in-Spyder 

Stephanie Nam (snam@alum.mit.edu)
"""

#Import required system libraries for file management
import sys,importlib,os

pc_path = 'C:\\Users\\vlab_eye\\Documents\\local_repo' #
# pc_path = 'C:\\Users\\UCL-SPARC\\Documents\\GitHub'
# Provide path to oct-cbort library
module_path = os.path.abspath(os.path.join(pc_path, 'oct-cbort'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
# Import oct-cbort library
from oct import *

# ASN libs
module_path2=os.path.abspath(os.path.join(pc_path, 'asnlibs'))
if module_path2 not in sys.path:
    sys.path.append(module_path2)
from mgh_io import MGHio
from asndev_analysis import mark_line
import asnlib_mplset
# Import additional libraries
import shutil, time


#%% Load data
# session_name = '[p.Chicken052621][s.SANsChicken_smallV][05-26-2021_13-11-59]'
# path_dir = os.path.join(os.getcwd(), 'example_data', session_name)
# path_dir = 'C:\\Users\\UCL-SPARC\\Downloads\\OS1_D1'
# path_dir = 'D:\\SPARC-FDA\\SL2\\OS1_D1'
# path_dir = 'D:\\SPARC-FDA\\SL2\\OS1_D7'
# path_dir = 'D:\\SPARC-FDA\\Control_nostim\\Ctrl_D1'
path_dir = 'D:\\SPARC-FDA\\Control_nostim\\Ctrl_D7'

b_change_editsetting = True
data = Load(directory = path_dir)
data.loadFringe(frame=1300)

#%% Tomogram processing : complex tomogram, k-space fringe, stokes vectors  
data.reconstructionSettings['processState'] = 'struct+angio+ps+hsv+oa'#'+kspace+stokes'
if b_change_editsetting:
    data.reconstructionSettings['spectralBinning'] = True
    # data.reconstructionSettings['depthIndex'] = [500,2000] # [1100,1500]#(phantom) # [0, 0]
    data.reconstructionSettings['binFract'] = 3
    # data.reconstructionSettings['demodSet'] = [0.4, 0.0, 1.0, 0.0, 0.0, 0.0]
    
if b_change_editsetting:
    data.processOptions['maskOutput'] = False
    data.processOptions['projState'] = 'hsv'
    data.processOptions['OOPAveraging'] = True
    data.processOptions['correctSystemOA'] = False


tom = Tomogram(mode='heterodyne')
outtom = tom.reconstruct(data=data)
for key,val in outtom.items():
    data.processedData[key] = outtom[key]
    
    
print("outtom.keys() >> ", outtom.keys())
plt.imshow(cp.asnumpy(cp.log10(cp.abs(outtom['tomch1'][:,:]))), aspect ='auto', cmap='gray')
plt.imshow(cp.asnumpy(cp.log10(cp.abs(outtom['tomch2'][:,:]))), aspect ='auto', cmap='gray')

print("outtom['tomch1'].shape >> ", outtom['tomch1'].shape)
print("outtom['sv1'].shape >> ", outtom['sv1'].shape)
if outtom['k1'] is not None:
    print("outtom['k1'].shape >> ", outtom['k1'].shape)

#%% Structure processing
# data.structureSettings['contrastLowHigh'] = [0,195]# [-50, 160]
struct_obj = Structure(mode='log')
struct_out = struct_obj.reconstruct(data=data)
for key,val in struct_out.items():
    data.processedData[key] = struct_out[key]
    
print("struct_out.keys() >> ", struct_out.keys())
plt.imshow(cp.asnumpy(struct_out['struct']), aspect ='auto', cmap='gray')


#%% PS processing
if b_change_editsetting:
    data.psSettings['zOffset'] = 5 # this is deltaZ for differential calculation
    data.psSettings['oopFilter']  = 2
    data.psSettings['xFilter'] = 11
    data.psSettings['zFilter']  = 1
    data.psSettings['dopThresh'] = 0.9
    data.psSettings['maxRet'] = 100
    data.psSettings['binFract'] = data.reconstructionSettings['binFract']
    # data.psSettings['thetaOffset'] = -int(151/256*180)
    data.hsvSettings['maskThresholds'] = np.array([230, 15, 45])
    data.hsvSettings['structWeight'] = np.array([40, 180])
    data.hsvSettings['dopWeight'] = np.array([200, 250])
    data.hsvSettings['retWeight'] = np.array([5,180])
    data.hsvSettings['thetaRef'] = -int(151/256*180)
    

print(data.psSettings)
ps = Polarization('sym') # Polarization('sb')
outps = ps.reconstruct(data=data)
for key,val in outps.items():
    data.processedData[key] = outps[key]
    
print("outps.keys() >> ", outps.keys())

fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(221)
ax.imshow(data.processedData['dop'], cmap='gray', aspect='auto')
ax = fig.add_subplot(222)
ax.imshow(data.processedData['ret'], cmap='gray', aspect='auto')
ax = fig.add_subplot(223)
ax.imshow(data.processedData['theta'], aspect='auto')
ax = fig.add_subplot(224)
ax.imshow(data.processedData['oa'], aspect='auto')
plt.show()


SVF1, SVF2, SVN1, SVN2, QUV1, QUV2 = filtNormStokes(data.processedData['sv1'],
                                                    data.processedData['sv2'],
                                                    stokesFilter=ps.filter)

if b_change_editsetting:
    print("Settings changed in Spyder")
else:
    print("Saved edit settings used")

# sys.exit()
#%% Process and save the whole volume
# Set up logging to print on Spyder console
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.__dict__

# Initialize the post processor. 
# Write editsettings.ini file and copy to the settings folder
data.reconstructionMode = {'tom': 'heterodyne', 
                            'struct': 'log', 
                            'angio': 'cdv', 
                            'ps': 'sym'}


data.generateEditSettings()
src = os.path.join(path_dir, 'editsettings.ini')
dst = os.path.join(path_dir, 'Processed', 'spyder_used_editsettings.ini')
shutil.copy(src, dst)

# The data object still contains the settings parameters defined above carry over.
processor = Post()
processor.processFrameRange(data, procState='struct+ps+hsv+angio+oa', procAll=True, writeState=True)
                            # procAll=False, startFrame=1000, endFrame=1200, writeState=True)

sys.exit()
#%%
"""
import napari

# Looking at QUV (filtered and normalized)
viewer = napari.Viewer()
viewer.add_image(cp.asnumpy(SVN1), name='SVN1', rgb=False, contrast_limits=(-1,1), colormap='viridis' )
viewer.add_image(cp.asnumpy(SVN2), name='SVN2', rgb=False, contrast_limits=(-1,1), colormap='viridis' )
viewer.add_image(data.processedData['oa'][:,:,:,None], name='oa', rgb=False, colormap='plasma' )


viewer2 = napari.Viewer()
viewer2.add_image(cp.asnumpy( data.processedData['dop']/255), name='dop', contrast_limits=(0,1), rgb=False)
viewer2.add_image(cp.asnumpy( data.processedData['struct']/255), name='nlog_struct', contrast_limits=(0,1), rgb=False)
viewer2.add_image(cp.asnumpy(data.processedData['ret']/255), name='ret', contrast_limits=(0,1), rgb=False)


viewer3 = napari.Viewer()

%matplotlib qt 
"""


#%%
disp_z =  np.arange(100) + 120 # np.arange(645,700) #
disp_x = np.array([412])

disp_SVN1 = cp.asnumpy(SVN1[disp_z, disp_x, :,  (data.psSettings['binFract']-1)])
disp_SVN2 = cp.asnumpy(SVN2[disp_z, disp_x, :,  (data.psSettings['binFract']-1)])

fig = plt.figure()
ax = plt.axes(projection='3d')

r = 1
phi, theta = np.mgrid[0.0:np.pi:100j, 0.0:2.0*np.pi:100j]
x = r*np.sin(phi)*np.cos(theta)
y = r*np.sin(phi)*np.sin(theta)
z = r*np.cos(phi)
ax.plot_surface(x, y, z,  rstride=1, cstride=1, color='c', alpha=0.1, linewidth=0)

# Data for a three-dimensional line
pdict_line1 = {'linewidth':0.5, 'color':'red'}
pdict_line2 = {'linewidth':0.5, 'color':'blue'}
# Use colormaps `winter` and `autumn` that start with blue and red
ax.plot3D(disp_SVN1[:,0], disp_SVN1[:,1], disp_SVN1[:,2], **pdict_line1)
ax.plot3D(disp_SVN2[:,0], disp_SVN2[:,1], disp_SVN2[:,2], **pdict_line2)

# Data for three-dimensional scattered points
ax.scatter3D(disp_SVN1[:,0], disp_SVN1[:,1], disp_SVN1[:,2], c=disp_z, cmap='autumn')
ax.scatter3D(disp_SVN2[:,0], disp_SVN2[:,1], disp_SVN2[:,2], c=disp_z, cmap='winter')


fig, ax = plt.subplots(1,1)
ax.imshow(cp.asnumpy(struct_out['struct']), aspect ='auto', cmap='gray')

ax = mark_line(ax, (disp_z[[0,-1]], disp_x), orientation_dim=1)


#%% Intensity for input states 1 and 2
intensity1 = 10*np.log10(np.clip(cp.asnumpy(data.processedData['sv1'][:,:,0,:]), 1e-6, None)) #SVF1[:,:,0,1]
intensity2 = 10*np.log10(np.clip(cp.asnumpy(data.processedData['sv2'][:,:,0,:]), 1e-6, None)) #SVF2[:,:,0,1]


intensityXod = np.clip(np.abs(cp.asnumpy(outtom['tomch1'][:,1::2])), 1e-6, None)[:,:,None]
intensityYod = np.clip(np.abs(cp.asnumpy(outtom['tomch2'][:,1::2])), 1e-6, None)[:,:,None]
intensityXev = np.clip(np.abs(cp.asnumpy(outtom['tomch1'][:,0::2])), 1e-6, None)[:,:,None]
intensityYev = np.clip(np.abs(cp.asnumpy(outtom['tomch2'][:,0::2])), 1e-6, None)[:,:,None]


intensity = (intensityXod + intensityYod + intensityXev + intensityYev)/4


log_intensity_disp = 10*np.log10(np.concatenate(
    (intensity, intensityXod, intensityYod, intensityXev, intensityYev), axis=2))
list_intendity_str_disp = ['intensity', 
                           'intensityXod', 'intensityYod', 
                           'intensityXev', 'intensityYev']

list_ps_str_disp = ['struct', 'dop', 'ret', 'theta', 'oa']


fig, axes = plt.subplots(1,5, figsize=(10,8))
for q, ax in enumerate(axes):
    ax.imshow(data.processedData[list_ps_str_disp[q]])
    ax.set_title(list_ps_str_disp[q])
fig.tight_layout()


fig, axes = plt.subplots(1,5, figsize=(10,5))
for q, ax in enumerate(axes):
    ax.imshow(log_intensity_disp[:,:,q], cmap='gray')
    ax.set_title(list_intendity_str_disp[q])
fig.tight_layout()


"""
import napari

# Looking at QUV (filtered and normalized)
viewer = napari.Viewer()
viewer.add_image(log_intensity_disp, name='log_intensity_disp', rgb=False, colormap='gray', contrast_limits=(0,60))

"""
#%%
disp_x_tomo = 1000*2
fringeXev = cp.asnumpy(data.ch1[:,disp_x_tomo])
fringeXod = cp.asnumpy(data.ch1[:,disp_x_tomo+1])
fringeYev = cp.asnumpy(data.ch2[:,disp_x_tomo])
fringeYod = cp.asnumpy(data.ch2[:,disp_x_tomo+1])

fringe = np.vstack((fringeXod, fringeYod, fringeXev, fringeYev))
list_fringe_disp = ['fringeXod', 'fringeYod', 'fringeXev', 'fringeYev']
fig, axes = plt.subplots(4,1, sharey=True, sharex=True, figsize=(5,8))
for q, ax in enumerate(axes):
    ax.plot(fringe[q,:], label=list_fringe_disp[q])
    ax.set_title(list_fringe_disp[q])
fig.tight_layout()