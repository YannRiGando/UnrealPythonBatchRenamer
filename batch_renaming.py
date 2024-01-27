import unreal
import math

editor_utility = unreal.EditorUtilityLibrary()
editor_assets = unreal.EditorAssetLibrary()

rename_pref = {
    unreal.HoudiniAsset : "HDA_",
    unreal.AnimBlueprint : "ABP_",
    unreal.EditorUtilityWidgetBlueprint : "EUW_",
    unreal.WidgetBlueprint : "WBP_",
    unreal.Blueprint : "BP_",
    unreal.PCGraph : "PCG_",
    # unreal.CurveBase : "CF_",
    unreal.Material : "M_",
    unreal.MaterialInstance : "MI_",
    unreal.MaterialInstanceConstant: "MI_",
    unreal.MaterialLayersFunctions : "ML_",
    unreal.MaterialFunctionMaterialLayerBlend : "MLB_",
    unreal.MaterialFunction : "MF_",
    unreal.TextureCube : "TC_",
    unreal.TextureRenderTarget2D : "RT_",
    unreal.Texture2D : "T_",
    unreal.AnimationAsset : "A_",
    unreal.AnimMontage : "AM_",
    unreal.BlendSpace : "BS_",
    unreal.NiagaraSystem : "FXS_",
    unreal.NiagaraEmitter : "FXE_",
    unreal.NiagaraScript : "FXF_",
    unreal.StaticMesh : "SM_",
    unreal.LevelInstance : "LI_", 
    unreal.World : "L_",
    unreal.LevelSequence : "LS_",
    # unreal.DataTable : "DT_",
    unreal.SoundWave : "SW_",
    unreal.PhysicsAsset : "PA_"
}

rename_suffix_tex = [
    "_N",
    "_M",
    "_BC"
]

# print(len(rename_pref))

def length(i):
    return len(i)


def name_preping(splitted_names):
    name=""
    if len(splitted_names) == 1:
        name = str(splitted_names[0])
        return name
    
    if len(splitted_names) > 1:
        splitted_names.sort(reverse = True, key=len)
        name = splitted_names[0]
        return name

def texture_management(asset, splited_name):
    suffix = ""
    is_normal_map = unreal.TextureCompressionSettings.TC_NORMALMAP
    is_mask_map = unreal.TextureCompressionSettings.TC_MASKS
    
    if asset.compression_settings is is_normal_map:
        suffix = rename_suffix_tex[0]
    elif "ORM" in splited_name:
        i = splited_name.index("ORM")
        suffix = "_" + splited_name[i]
    elif asset.srgb is True:
        suffix = rename_suffix_tex[2]
    elif asset.compression_settings is is_mask_map:
        suffix = rename_suffix_tex[1]
    return suffix

def static_mesh_management(asset):
    if "Module" in asset.get_name():
        suffix = ""
        box_size = asset.get_bounding_box().get_box_center_size()
        box = box_size[1].to_tuple()
        for i in range(len(box)):
            l = math.floor(box[i] * 0.01)
            suffix += "x" + str(l)
        suffix = "_" + suffix[1:] # regarder comment marche un slice

        return suffix

  
# y'avait une boucle qui servait rien c.f discord    
def generate_new_name_for_asset(asset_data, previous_names):
    full_name = ""
    main_name = ""  
    suffix = ""    
    prefix = rename_pref[type(asset_data)]
    base_name = asset_data.get_name()
    cut_name = base_name.split("_")
    main_name = name_preping(cut_name)
    
    if main_name in previous_names.keys():
        previous_names[main_name] += 1
        main_name += "_" + str(previous_names[main_name])
    else:
        # ajoute au dico syntax python
        previous_names[main_name] = 0

    if type(asset_data) is unreal.Texture2D:
        suffix = texture_management(asset_data, cut_name)
    if type(asset_data) is unreal.StaticMesh:
        suffix = static_mesh_management(asset_data)
    
            
    full_name = prefix + main_name + suffix
    # print(full_name)
    
    
    return full_name                                                
    

def rename_assets_at_path(asset_paths):
    previous_names = dict()
    
    for i in range(len(asset_paths)):
        # editor_assets.checkout_loaded_asset(assets_paths[i]) 
                                  
        asset_data = editor_assets.find_asset_data(asset_paths[i]).get_asset()
        asset_old_path = asset_data.get_path_name()
        asset_folder = unreal.Paths.get_path(asset_old_path)
    
        new_name = generate_new_name_for_asset(asset_data, previous_names)
        new_path = asset_folder + "/" + new_name # + add les digits
            
        rename_succes = unreal.EditorAssetLibrary.rename_asset(asset_old_path, new_path)
        if not rename_succes:
            unreal.log_warning("Could not rename " + asset_old_path)


def folder_selection():
    all_str = "/All"
    array_path = editor_utility.get_selected_folder_paths()
                              
    for i in range(len(array_path)):                                          
        main_path = array_path[i].removeprefix(all_str)        
        assets_path = editor_assets.list_assets(main_path)
        
        rename_assets_at_path(assets_path)

def run():
    folder_selection()
    
run()
