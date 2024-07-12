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

import pybox_v1 as pybox
import pybox_comfyui

from pybox_comfyui import UI_INTERRUPT
from pybox_comfyui import Color
from pybox_comfyui import LayerIn
from pybox_comfyui import LayerOut


COMFYUI_WORKFLOW_NAME = "ComfyUI ZDepth Marigold"
COMFYUI_OPERATOR_NAME = "zdepth_marigold"

UI_DENOISE_STEPS = "Denoise Steps"
UI_NREPEAT = "N Repeat"
UI_REGULARIZER_STRENGTH = "Regularizer Strength"
UI_REDUCTION_METHOD = "Reduction Method"
UI_MAX_ITER = "Max Iter"
UI_TOL = "Tol"
UI_INVERT = "Invert"
UI_KEEP_MODEL_LOADED = "Keep Model Loaded"
UI_NREPEAT_BATCH_SIZE = "N Repeat Batch Size"
UI_USE_FP16 = "Use FP16"
UI_SCHEDULER = "Scheduler"
UI_NORMALIZE = "Normalize"

DEFAULT_DENOISE_STEPS = 10
DEFAULT_N_REPEAT = 10
DEFAULT_REGULARIZER_STRENGTH = 0.020
DEFAULT_REDUCTION_METHOD = "median"
DEFAULT_MAX_ITER = 5
DEFAULT_TOL = 0.001
DEFAULT_INVERT = True
DEFAULT_KEEP_MODEL_LOADED = True
DEFAULT_NREPEAT_BATCH_SIZE = 2
DEFAULT_USE_FP16 = True
DEFAULT_SCHEDULER = "DDIMScheduler"
DEFAULT_NORMALIZE = True


class ComfyuiZDMG(pybox_comfyui.ComfyUIBaseClass):
    operator_name = COMFYUI_OPERATOR_NAME
    operator_layers = [LayerIn.FRONT, LayerOut.RESULT]
    
    version = 1
    
    workflow_denoise_steps_idx = -1
    workflow_nrepeat_idx = -1
    workflow_regularizer_strength_idx = -1
    workflow_reduction_method_idx = -1
    workflow_max_iter_idx = -1
    workflow_tol_idx = -1
    workflow_invert_idx = -1
    workflow_keep_model_loaded_idx = -1
    workflow_nrepeat_batch_size_idx = -1
    workflow_use_fp16_idx = -1
    workflow_scheduler_idx = -1
    workflow_normalize_idx = -1
    
    denoise_steps = DEFAULT_DENOISE_STEPS
    n_repeat = DEFAULT_N_REPEAT
    regularizer_strength = DEFAULT_REGULARIZER_STRENGTH
    reduction_method = DEFAULT_REDUCTION_METHOD
    max_iter = DEFAULT_MAX_ITER
    tol = DEFAULT_TOL
    invert = DEFAULT_INVERT
    keep_model_loaded = DEFAULT_KEEP_MODEL_LOADED
    n_repeat_batch_size = DEFAULT_NREPEAT_BATCH_SIZE
    use_fp16 = DEFAULT_USE_FP16
    scheduler = DEFAULT_SCHEDULER
    normalize = DEFAULT_NORMALIZE

    schedulers = ["DDIMScheduler", 
                "DDPMScheduler",
                "PNDMScheduler",
                "DEISMultiSpepScheduler"]
    
    reduction_methods = ["median", 
                        "mean"]

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
            "Server & Workflow", "", "Parameters", "", "Action"
            )
        pages.append(page)
        self.set_ui_pages_array(pages)
        
        col = 0
        self.set_ui_host_info(col)
        
        self.set_ui_workflow_path(col, self.workflow_dir, self.workflow_path)
        
        col = 1
        denoise_steps = pybox.create_float_numeric(
            UI_DENOISE_STEPS, 
            value=self.denoise_steps, 
            default=10, 
            min=0, max=100, inc=1,
            row=0, col=col, tooltip="Denoise steps",
            )
        self.add_global_elements(denoise_steps)
        
        nrepeat = pybox.create_float_numeric(
            UI_NREPEAT, 
            value=self.n_repeat, 
            default=10, 
            min=0, max=100, inc=1,
            row=1, col=col, tooltip="N Repeat",
            )
        self.add_global_elements(nrepeat)
        
        max_iter = pybox.create_float_numeric(
            UI_MAX_ITER, 
            value=self.max_iter, 
            default=5, 
            min=0, max=100, inc=1,
            row=2, col=col, tooltip="Maximum number of iterations",
            )
        self.add_global_elements(max_iter)
        
        col = 2
        regularizer_strength = pybox.create_float_numeric(
            UI_REGULARIZER_STRENGTH, 
            value=self.regularizer_strength, 
            default=10, 
            min=0, max=100, inc=1,
            row=0, col=col, tooltip="Regularizer strength",
            )
        self.add_global_elements(regularizer_strength)
        
        tol = pybox.create_float_numeric(
            UI_TOL, 
            value=self.tol, 
            default=0.001, 
            min=0, max=1, inc=0.001,
            row=1, col=col, tooltip="Tolerance",
            )
        self.add_global_elements(tol)
        
        reduction_methods_list = pybox.create_popup(
            UI_REDUCTION_METHOD, 
            self.reduction_methods, 
            value=self.reduction_methods.index(self.reduction_method), 
            default=0, 
            row=2, col=col, tooltip="Reduction method"
            )
        self.add_global_elements(reduction_methods_list)
        
        scheduler = pybox.create_popup(
            UI_SCHEDULER, 
            self.schedulers, 
            value=self.schedulers.index(self.scheduler), 
            default=0, 
            row=3, col=col, tooltip="Scheduler"
            )
        self.add_global_elements(scheduler)
        
        col = 3
        use_fp16 = pybox.create_toggle_button(
            UI_USE_FP16, 
            self.use_fp16, 
            default=True,
            row=0, col=col, tooltip="Use FP16"
            )
        self.add_global_elements(use_fp16)
        
        invert = pybox.create_toggle_button(
            UI_INVERT, 
            self.invert, 
            default=True,
            row=1, col=col, tooltip="Invert"
            )
        self.add_global_elements(invert)
        
        keep_model_loaded = pybox.create_toggle_button(
            UI_KEEP_MODEL_LOADED, 
            self.keep_model_loaded, 
            default=True,
            row=2, col=col, tooltip="Keep model loaded"
            )
        self.add_global_elements(keep_model_loaded)
        
        normalize = pybox.create_toggle_button(
            UI_NORMALIZE, 
            self.normalize, 
            default=True,
            row=3, col=col, tooltip="Normalize"
            )
        self.add_global_elements(normalize)
        
        col = 4
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
        pass
    
    ###################################
    # Workflow
    
    def load_workflow(self):
        with open(self.workflow_path) as f:
            print("Loading Workflow")
            self.workflow = json.load(f)
            self.workflow_id_to_class_type = {id: details['class_type'] for id, details in self.workflow.items()}
            # load & save 
            self.workflow_load_exr_front_idx = self.get_workflow_index('LoadEXR')
            wf_ids_to_classes = self.workflow_id_to_class_type.items()
            save_exr_nodes = [(key, self.workflow.get(key)["inputs"]) for key, value in wf_ids_to_classes if value == 'SaveEXR']
            self.workflow_save_exr_result_idx = [key for (key, attr) in save_exr_nodes if attr["filename_prefix"] == "Result"][0]
            # paramaters
            self.workflow_marigold_depth_estimation_idx = self.get_workflow_index('MarigoldDepthEstimation')
            self.denoise_steps = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["denoise_steps"]
            self.n_repeat = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["n_repeat"]
            self.regularizer_strength = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["regularizer_strength"]
            self.reduction_method = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["reduction_method"]
            self.max_iter = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["max_iter"]
            self.tol = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["tol"]
            self.invert = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["invert"]
            self.keep_model_loaded = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["keep_model_loaded"]
            self.n_repeat_batch_size = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["n_repeat_batch_size"]
            self.use_fp16 = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["use_fp16"]
            self.scheduler = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["scheduler"]
            self.normalize = self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["normalize"]
            
            self.out_frame_pad = self.workflow.get(self.workflow_save_exr_result_idx)["inputs"]["frame_pad"]
    
    
    def set_workflow_denoise_steps(self):
        if self.workflow:  
            self.denoise_steps = int(self.get_global_element_value(UI_DENOISE_STEPS))
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["denoise_steps"] = self.denoise_steps
            print(f'Workflow Denoise steps: {self.denoise_steps}')
    
    
    def set_workflow_nrepeat(self):
        if self.workflow:  
            self.n_repeat = int(self.get_global_element_value(UI_NREPEAT))
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["n_repeat"] = self.n_repeat
            print(f'Workflow N Repeat: {self.n_repeat}')
    
    
    def set_workflow_reduction_method(self):
        if self.workflow:  
            self.reduction_method = self.reduction_methods[int(self.get_global_element_value(UI_REDUCTION_METHOD))]
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["reduction_method"] = self.reduction_method
            print(f'Workflow Reduction method: {self.reduction_method}')
    
    
    def set_workflow_regularizer_strength(self):
        if self.workflow:  
            self.regularizer_strength = self.get_global_element_value(UI_REGULARIZER_STRENGTH)
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["regularizer_strength"] = self.regularizer_strength
            print(f'Workflow Regularizer strength: {self.regularizer_strength}')
    
    
    def set_workflow_max_iter(self):
        if self.workflow:  
            self.max_iter = int(self.get_global_element_value(UI_MAX_ITER))
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["max_iter"] = self.max_iter
            print(f'Workflow Max iter: {self.max_iter}')
    
    
    def set_workflow_tol(self):
        if self.workflow:  
            self.tol = self.get_global_element_value(UI_TOL)
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["tol"] = self.tol
            print(f'Workflow Tolerance: {self.tol}')
    

    def set_workflow_invert(self):
        if self.workflow:  
            self.invert = self.get_global_element_value(UI_INVERT)
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["invert"] = self.invert
            print(f'Workflow Invert: {self.invert}')
    
    
    def set_workflow_keep_model_loaded(self):
        if self.workflow:  
            self.keep_model_loaded = self.get_global_element_value(UI_KEEP_MODEL_LOADED)
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["keep_model_loaded"] = self.keep_model_loaded
            print(f'Workflow Keep model loaded: {self.keep_model_loaded}')
    
    
    def set_workflow_n_repeat_batch_size(self):
        if self.workflow:  
            self.n_repeat_batch_size = int(self.get_global_element_value(UI_KEEP_MODEL_LOADED))
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["n_repeat_batch_size"] = self.n_repeat_batch_size
            print(f'Workflow N Repeat batch size: {self.n_repeat_batch_size}')
    
    
    def set_workflow_use_fp16(self):
        if self.workflow:  
            self.use_fp16 = self.get_global_element_value(UI_USE_FP16)
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["use_fp16"] = self.use_fp16
            print(f'Workflow Use FP16: {self.use_fp16}')
    
    
    def set_workflow_scheduler(self):
        if self.workflow:  
            self.scheduler = self.schedulers[int(self.get_global_element_value(UI_SCHEDULER))]
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["scheduler"] = self.scheduler
            print(f'Workflow Scheduler: {self.scheduler}')
            
    
    def set_workflow_normalize(self):
        if self.workflow:  
            self.normalize = self.get_global_element_value(UI_NORMALIZE)
            self.workflow.get(self.workflow_marigold_depth_estimation_idx)["inputs"]["normalize"] = self.normalize
            print(f'Workflow Normalize: {self.normalize}')
            
    
    def workflow_setup(self):
        self.set_workflow_denoise_steps()
        self.set_workflow_nrepeat()
        self.set_workflow_reduction_method()
        self.set_workflow_regularizer_strength()
        self.set_workflow_max_iter()
        self.set_workflow_tol()
        self.set_workflow_invert()
        self.set_workflow_keep_model_loaded()
        self.set_workflow_n_repeat_batch_size()
        self.set_workflow_use_fp16()
        self.set_workflow_scheduler()
        self.set_workflow_normalize()
        
        self.set_workflow_load_exr_filepath()
        self.set_workflow_save_exr_filename_prefix(layers=self.operator_layers)
    
    
    
def _main(argv):
    print("____________________")
    print("Loading ComfyUI JSON Pybox")
    print("____________________")
    
    # Load the json file, make sure you have read access to it
    p = ComfyuiZDMG(argv[0])
    # Call the appropriate function
    p.dispatch()
    # Save file
    p.write_to_disk(argv[0])
    
    print("____________________")
    print("Writing ComfyUI JSON Pybox")
    print("____________________")

if __name__ == "__main__":
    _main(sys.argv[1:])
    