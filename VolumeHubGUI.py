import wx,sys,subprocess,os,time
from BabelBrushVolumeHub import BabelBrushVolumeHub,create_directory_structure


class VolumeList(wx.ListCtrl):
    def __init__(self, parent,volume_hub):
        wx.ListCtrl.__init__(
            self, parent, -1,
            style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES
            )

        self.volume_hub=volume_hub
        self.il = wx.ImageList(60,64)
        
        for item in volume_hub.volumes:
            item["_image_index"]=self.il.Add(wx.Bitmap(item["thumbnail"],wx.BITMAP_TYPE_JPEG))
        
        
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        

        self.InsertColumn(0, "Thumb")
        self.InsertColumn(1, "Volume")
        self.InsertColumn(2, "File")
     
        self.SetColumnWidth(0, 60)
        self.SetColumnWidth(1, 80)
        self.SetColumnWidth(2, 150)

        self.SetItemCount(len(volume_hub.volumes))
     
       
        
    
    def item_added(self):
        
        last_added= self.volume_hub.volumes[-1]
        last_added["_image_index"]=self.il.Add(wx.Bitmap(last_added["thumbnail"],wx.BITMAP_TYPE_JPEG))
        self.SetItemCount(len(self.volume_hub.volumes))

    def hub_changed(self):
        self.il.RemoveAll()
        for item in self.volume_hub.volumes:
            item["_image_index"]=self.il.Add(wx.Bitmap(item["thumbnail"],wx.BITMAP_TYPE_JPEG))
        self.SetItemCount(len(self.volume_hub.volumes))
        self.Refresh()

  
    def OnGetItemText(self, item, col):
        if col==1:
            return self.volume_hub.volumes[item]["_stub"]
        elif col==2:
            return self.volume_hub.volumes[item]["Image Name"]
        return ""

    def OnGetItemImage(self, item):
        if item >=  len(self.volume_hub.volumes):
            return None
        return self.volume_hub.volumes[item]["_image_index"]
        




class BabelBrushVolumeManager(wx.Frame): 
            
    def __init__(self,base_folder=None):
        parent = None
        title = "BabelBrush Manager"
        super(BabelBrushVolumeManager, self).__init__(parent, title = title,size=(1000,600))    
        
        label_font=  wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        info_font= wx.Font(16,wx.FONTFAMILY_SWISS,wx.NORMAL, wx.NORMAL)
            
        #splt top bottom
        outer_box=wx.BoxSizer(wx.VERTICAL)
        top_box=wx.BoxSizer(wx.HORIZONTAL)
        outer_box.Add(top_box,0,wx.ALL|wx.EXPAND,10)
        
        #top bar
        folder_label=wx.StaticText(self,label="Hub Folder:")
        folder_label.SetFont(label_font)
        top_box.Add(folder_label,0,wx.RIGHT,15)
        
        self.hub_label = wx.StaticText(self,size=(300,40))
        top_box.Add(self.hub_label)
        
        change_folder_button = wx.Button(self,-1,"Open")
        change_folder_button.Bind(wx.EVT_BUTTON,self.change_hub)
        top_box.Add(change_folder_button,0,wx.ALL,3)
        
        new_folder_button = wx.Button(self,-1,"Create New")
        new_folder_button.Bind(wx.EVT_BUTTON,self.create_new_hub)
        top_box.Add(new_folder_button,0,wx.ALL,3)
        
        self.launch_button = wx.Button(self,-1,"Launch Babel Brush")
        self.launch_button.Bind(wx.EVT_BUTTON,self.launch_babel)
        top_box.Add(self.launch_button,0,wx.ALL,3)
        
        main_box= wx.BoxSizer(wx.HORIZONTAL)
        outer_box.Add(main_box,1,wx.EXPAND)
       
        #spli left right
        left_box= wx.BoxSizer(wx.VERTICAL)
        main_box.Add(left_box,1,wx.EXPAND|wx.ALL,5)
        right_box = wx.BoxSizer(wx.VERTICAL)     
        main_box.Add(right_box,1,wx.EXPAND|wx.ALL,5)
        
        
        list_box_menu= wx.BoxSizer(wx.HORIZONTAL)
        list_label=wx.StaticText(self,label="Volumes")
        list_label.SetFont(label_font)
        list_box_menu.Add(list_label,1,wx.ALL,5)
        
        
        self.index_button = wx.Button(self,-1,"Add nii file")
        self.index_button.Bind(wx.EVT_BUTTON,self.addIndex)
        
        self.del_button= wx.Button(self,-1,"Delete")
        self.del_button.Bind(wx.EVT_BUTTON,self.delete_volume)
        list_box_menu.Add(self.index_button,0,wx.ALL,5)
        list_box_menu.Add(self.del_button,0,wx.ALL,5)
        right_box.Add(list_box_menu,0)
        
        main_left_box= wx.BoxSizer(wx.VERTICAL)
        bottom_left_box=wx.BoxSizer(wx.VERTICAL)
        left_box.Add(main_left_box,4,wx.EXPAND|wx.ALL)
        left_box.Add(bottom_left_box,1,wx.EXPAND|wx.ALL)
        
        
        main_left_box.Add(-1,-1)
        log_label=wx.StaticText(self,label="Log")
        log_label.SetFont(label_font)
        
        self.log_text = wx.TextCtrl(self,style = wx.TE_MULTILINE|wx.TE_RICH)
        #self.log_text.Disable()
        self.log_text.SetBackgroundColour(wx.LIGHT_GREY)   
        bottom_left_box.Add(log_label,0,wx.EXPAND|wx.ALL)
        bottom_left_box.Add(self.log_text,-1,wx.EXPAND|wx.ALL)
        self.hub_label.SetFont(info_font)
        
        
        self.babel_hub = BabelBrushVolumeHub(None,self.write_message)
        self.index_button.Disable()
        self.del_button.Disable()
        self.launch_button.Disable()
        self.hub_label.SetLabel("None")
            
            
        self.volume_list = VolumeList(self,self.babel_hub)
        right_box.Add(self.volume_list,1,wx.EXPAND) 
        self.SetSizer(outer_box) 
        self.SetAutoLayout(True) 
        self.Show(True)
        if base_folder:
            self.change_to_hub(base_folder)
    
    def launch_babel(self,event):
        exe_folder = os.path.realpath(os.path.dirname(sys.argv[0]))
        try:
            exe = os.path.join(exe_folder,"Babel Brush.exe")
            subprocess.Popen([exe,"--hub_folder",self.babel_hub.base_folder])
            sys.exit(0)
        except Exception as e:
            self.write_message("Unable to run {}".format(exe),True)
            
        
    
    def delete_volume(self,event):
        index  = self. volume_list.GetFirstSelected()
        self.babel_hub.delete_volume(index)
        self.volume_list.SetItemCount(len(self.volume_list.volume_hub.volumes))
       
    
    def addIndex(self,event):
       
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile="",
            wildcard="*.nii",
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            try:
                self.babel_hub.index_nii_file(paths[0])
            except Exception as e:
                self.write_message("Cannot process {}. Is it .nii file".format(paths[0]))
                self.write_message(str(e),True)
                return
           
            self.volume_list.item_added()
            self.write_message("Indexed {}".format(paths[0]))
            
        dlg.Destroy()
        
    
    def create_new_hub(self,event):
        dlg = wx.DirDialog(
            self, message="Choose a Directory",
            style=wx.FD_OPEN 
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                create_directory_structure(path)
                self.write_message("Created directory structure")
            except Exception as e:
                self.write_message(str(e),True)
                self.write_message("Unable to create new hub",True)
            
            self.change_to_hub(path)
           
            
            
        dlg.Destroy()
    
    
    def write_message(self,msg,error=False):
        if error:
            self.log_text.SetDefaultStyle(wx.TextAttr(wx.RED,wx.LIGHT_GREY))
        self.log_text.AppendText(msg+"\n")
        self.log_text.SetDefaultStyle(wx.TextAttr(wx.BLACK,wx.LIGHT_GREY))   
     
    def change_hub(self,event):
        dlg = wx.DirDialog(
            self, message="Choose a Directory",
            style=wx.FD_OPEN 
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.change_to_hub(path)
            
            
        dlg.Destroy()
    
    
    def change_to_hub(self,path):
        try:
            self.babel_hub.open_hub(path)
            self.volume_list.hub_changed()
            self.hub_label.SetLabel(path)
            self.index_button.Enable()
            self.del_button.Enable()
            self.launch_button.Enable()
            self.write_message("Opened {}".format(path))
            
        
        except Exception as e:
            self.write_message("Could not open {}".format(path),True)
            self.write_message(str(e),True)
            
         
    
ex = wx.App() 
BabelBrushVolumeManager(os.path.join(os.path.expanduser("~"),"Documents","Babel")) 
ex.MainLoop()


