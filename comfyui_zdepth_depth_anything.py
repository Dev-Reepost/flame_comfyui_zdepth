##########################################################################
#
# Filename: comfyui_zdepth.py
#
# Author: Julien Martin
# Created: 2024-03
#
###########################################################################
from __future__ import print_function

import sys
import json
import webbrowser
from pathlib import Path

import pybox_v1 as pybox
import pybox_comfyui

from comfyui_client import COMFYUI_WORKING_DIR
from comfyui_client import find_models

from pybox_comfyui import UI_INTERRUPT
from pybox_comfyui import Color
from pybox_comfyui import LayerIn
from pybox_comfyui import LayerOut


COMFYUI_WORKFLOW_NAME = "ComfyUI ZDepth Depth Anything"
COMFYUI_OPERATOR_NAME = "zdepth_depth_anything"

COMFYUI_MODELS_DA_DIR_PATHS = [
    str(Path(COMFYUI_WORKING_DIR) / "models" / "depthanything")
    ]

DEFAULT_DA_MODEL = "depth_anything_v2_vitl_fp32.safetensors"

UI_MODELS_DA_LIST = "DA Model"


class ComfyuiZDDA(pybox_comfyui.ComfyUIBaseClass):
    operator_name = COMFYUI_OPERATOR_NAME
    operator_layers = [LayerIn.FRONT, LayerOut.RESULT]
    
    version = 1
    
    models = []
    model = ""
    
    workflow_model_idx = -1
    

    ###########################################################################
    # Overrided functions from pybox_comfyui.ComfyUIBaseClass
    
    
    def initialize(self):
        super().initialize()
        
        self.set_state_id("setup_ui")
        self.setup_ui()


    def setup_ui(self):
        super().setup_ui()
        
        self.set_state_id("execute")
    
    
    def execute(self):
        super().execute()
        
        if self.out_frame_requested():
                self.submit_workflow()
        
        if self.get_global_element_value(UI_INTERRUPT):
            self.interrupt_workflow()

        self.update_workflow_execution()
        self.update_outputs(layers=self.operator_layers)
    
    
    def teardown(self):
        super().teardown()
    
    
    ###########################################################################
    # Node-specific functions
    
    ###################################
    # UI
    
    def init_ui(self):
        
        # ComfyUI pages
        pages = []
        page = pybox.create_page(
            COMFYUI_WORKFLOW_NAME, 
            "Server & Workflow", "Model", "Action"
            )
        pages.append(page)
        self.set_ui_pages_array(pages)
        
        col = 0
        self.set_ui_host_info(col)
        
        self.set_ui_workflow_path(col, self.workflow_dir, self.workflow_path)
        
        col = 1
        models_list = pybox.create_popup(
            UI_MODELS_DA_LIST, 
            self.models, 
            value=self.models.index(self.model), 
            default=0, 
            row=0, col=col, tooltip="Depth Anything model to use"
            )
        self.add_global_elements(models_list)
        
        
        col = 2
        # ComfyUI workflow actions
        self.ui_version_row = 0
        self.ui_version_col = col
        self.set_ui_versions()
        
        self.set_ui_increment_version(row=1, col=col)

        self.set_ui_interrupt(row=2, col=col)
        
        self.ui_processing_color_row = 3
        self.ui_processing_color_col = col
        self.set_ui_processing_color(Color.GRAY, self.ui_processing)
    
    
    def set_models(self):
        self.models = find_models(COMFYUI_MODELS_DA_DIR_PATHS)
        self.model = DEFAULT_DA_MODEL
    
    
    ###################################
    # Workflow
    
    def load_workflow(self):
        with open(self.workflow_path) as f:
            print("Loading Workflow")
            self.workflow = json.load(f)
            self.workflow_id_to_class_type = {id: details['class_type'] for id, details in self.workflow.items()}
            # model 
            self.workflow_model_idx = self.get_workflow_index('DownloadAndLoadDepthAnythingV2Model')
            # load & save 
            self.workflow_load_exr_front_idx = self.get_workflow_index('LoadEXR')
            wf_ids_to_classes = self.workflow_id_to_class_type.items()
            save_exr_nodes = [(key, self.workflow.get(key)["inputs"]) for key, value in wf_ids_to_classes if value == 'SaveEXR']
            self.workflow_save_exr_result_idx = [key for (key, attr) in save_exr_nodes if attr["filename_prefix"] == "Result"][0]
            # paramaters
            self.out_frame_pad = self.workflow.get(self.workflow_save_exr_result_idx)["inputs"]["frame_pad"]
    
    
    def set_workflow_model(self):
        model_idx = self.get_global_element_value(UI_MODELS_DA_LIST)
        self.model = self.models[model_idx]
        print(f'Workflow DA model: {self.model}')
        self.workflow.get(self.workflow_model_idx)["inputs"]["model"] = self.model
            
    
    def workflow_setup(self):
        self.set_workflow_model()
        self.set_workflow_load_exr_filepath()
        self.set_workflow_save_exr_filename_prefix(layers=self.operator_layers)
    
    
def _main(argv):
    print("____________________")
    print("Loading ComfyUI JSON Pybox")
    print("____________________")
    
    # Load the json file, make sure you have read access to it
    p = ComfyuiZDDA(argv[0])
    # Call the appropriate function
    p.dispatch()
    # Save file
    p.write_to_disk(argv[0])
    
    print("____________________")
    print("Writing ComfyUI JSON Pybox")
    print("____________________")

if __name__ == "__main__":
    _main(sys.argv[1:])
    