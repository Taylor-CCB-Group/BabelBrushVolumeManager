import os
import csv
import nibabel as nib
import matplotlib.pyplot as plt
from PIL import Image
from shutil import copyfile

save_folders = [ "Nii","Volume Presets","Brushes", "Points", "Tips","Tools","Transfers", "Objects", "Layouts", "Exports", "Scene", "Videos" ]
file_endings  = [".nii", ".vpre", ".bru", ".pnts", ".tip", ".tool", ".png", ".mve", ".obj", ".lay", ".csv", ".sce", ".cus", ".nvid" ]
log_headers= ["Image Name","Pixel Width","Pixel Height","Pixel Depth","Pixel Unit","Image width","Image height","channels","slices","frames"]


class BabelBrushVolumeHub(object):
    """A Class representing the hub.
    Attributes:
        base_folder (str): The base folder for the hub.
        volumes (list): A list of dictionaries describing the indexed nii files (volumes).
    """
    
    def __init__(self,base_folder=None,listener=None):      
        """Creates a new Hub 
        Args:
            base_folder (str,optional): The folder containing the hub.
            listener (function, optional): A function which accepts a string , messages will
               passed to this function.
        """
        self.listener=listener
        self.volumes=[]
        self.base_folder = base_folder
        if base_folder:
            self.open_hub(base_folder)
       
          
    def open_hub(self,base_folder):
        """Loads a new hub, any data associated with the old hub will be expunged
        Args:
            base_folder (str): The folder containing the hub
        """
        
        self.base_folder=base_folder
        #chcek folder and subfolders exist
        if not os.path.exists(base_folder):
            raise Exception("{} does not exist".format(base_folder))
        for name in save_folders:
            folder= os.path.join(base_folder,name)
            if not os.path.exists(folder):
                raise Exception ("{} subfolder does not exist".format(folder))
            
                
        self.nii_folder = os.path.join(base_folder,"nii")
        log_file = os.path.join(self.nii_folder,"Log.csv")
        if not os.path.exists(log_file):
            raise Exception ("The log file {} does not exist".format(log_file))
        
        self.volumes=[]
        with open(log_file) as f:
            reader = csv.DictReader(f)
            #for name in log_headers:
            #    if not name in reader.fieldnames:
            #        raise Exception("Cannot read log file")
            for row in reader:
               
                file_name = os.path.split(row["Image Name"])[1]
                if not os.path.exists(file_name):
                    pass          
                tn_file= os.path.join(self.nii_folder,"Thumbnails","Resources",file_name+"_thumb.jpg")
                stub= file_name.split(".")[0]
                row["thumbnail"]=self._create_list_thumbnail(tn_file,stub)
                row["_stub"]=stub
                self.volumes.append(row)
                    
    
    
    def delete_volume(self,index):
        """Deletes the volume (removes the local nii file, thumbnails and the log entry)
        Args:
            index(int): The index (in the volumes attribute) of the volume to be deleted    
        """
        volume =self.volumes[index]
        log_file= os.path.join(self.nii_folder,"Log.csv")
        inp = open(log_file)
        lines= inp.read().split("\n")
        inp.close()
        outp =open(log_file,"w")
        for line in lines:
            if not line:
                continue
            if line.startswith(volume["Image Name"]):
                continue
            outp.write(line+"\n")
        outp.close()
        os.remove(volume["Image Name"])
        stub = volume["_stub"]
        list_thumbnail = os.path.join(self.nii_folder,"Thumbnails",stub+"_tn.jpg")
        file_name = os.path.split(volume["Image Name"])[1]
        tn_file= os.path.join(self.nii_folder,"Thumbnails","Resources",file_name+"_thumb.jpg")
        os.remove(list_thumbnail)
        os.remove(tn_file)
        print("hello")
        del self.volumes[index]
        
        
    def index_nii_file(self,nii_file):
        """Copies the nii file to the hub directry, calculates metrics and adds to the log and     
        Args:
            nii_file(str): The index (in the volumes attribute) of the volume to be deleted    
        """
        #get tge file name
        file_name =  os.path.split(nii_file)[1]
        stub =file_name.split(".")[0]
        
        #load the file
        self._send_message("loading nii fie")
        epi_img = nib.load(nii_file)
           
        #get the metrics
        self._send_message("Obtaining metrics")  
        epi_img_data= epi_img.get_fdata()
        h= epi_img.get_header()
        
        #gets the height, width and slices
        dims= h.get_data_shape()
        if len(dims)==4:
            frames=dims[3]
        else:
            frames=1   
        width=dims[1]
        height=dims[0]
        slices=dims[2]
        
        # get pixel height/width and depth (in mm)
        vox = h.get_zooms()
        
        #!!!!need to work out chanels
        channels=1
       
        #copy to the users folder
        self._send_message("Copying File")  
        new_location = os.path.join(self.nii_folder,file_name)
        copyfile(nii_file,new_location)
        
        #write to logfile
        self._send_message("Saving to logfile")
        log_file = open (os.path.join(self.nii_folder,"Log.csv"),"a")
        info = "{},{},{},{},{},{},{},{},{},{}\n"
        info =info.format(new_location,vox[0]*1000,vox[1]*1000,vox[2]*1000,"microns",width,height,channels,slices,frames)
        log_file.write(info)
        log_file.close()
        
        #create main thumbnail  (the one babel uses)
        self._send_message("Creating Thumbnails")
        tn_file= os.path.join(self.nii_folder,"Thumbnails","Resources",file_name+"_thumb.jpg")
        plt.imsave(tn_file,epi_img_data[:,:,27],format="jpg")
        
        #create the thumbnail used b
        list_tn=self._create_list_thumbnail(tn_file, stub)
       
        #add to internal list
        row={
            "thumbnail":list_tn,
            "_stub":stub,
            "Image Name":new_location
            
        }
        self.volumes.append(row)
    
    
    def _create_list_thumbnail(self,original,stub):       
        #creates a thumbnail suitible for display in wx list box
        list_thumbnail = os.path.join(self.nii_folder,"Thumbnails",stub+"_tn.jpg")
        if not os.path.exists(list_thumbnail):        
            im = Image.open(original)
            im.thumbnail((60,64))
            #im.save(list_thumbnail)
            
            old_size = im.size

            new_size = (60, 64)
            new_im = Image.new("RGB", new_size,(255,255,255))
            pos=[0,0]
            if old_size[0]!=60:
                pos[0]=int((60-old_size[0])/2)
            if old_size[1]!=64:
                pos[1]=int((64-old_size[1])/2)
                   
            new_im.paste(im, (pos[0],pos[1]))

            new_im.save(list_thumbnail)
        return list_thumbnail
        
    def _send_message(self,msg):
        if self.listener:
            self.listener(msg)


def create_directory_structure(directory):
    """Creates all the sub folders and files required for the hub     
    Args:
        directory(str): the base directory of the hub (should be empty)  
    """
    for folder in save_folders:
        f = os.path.join(directory,folder)
        os.makedirs(f)
    resources = os.path.join(directory,"Nii","Thumbnails","Resources")
    os.makedirs(resources)
    log_file = os.path.join(directory,"Nii","Log.csv")
    outp=open(log_file,"w")
    outp.write(",".join(log_headers)+"\n")
    outp.close()        





        