import wolf
from tasks import sgz, ascat2sgz_seg, sgz_format_maf

def workflow(
    pair_id,
    hapaseg_tonly_merged_maf,
    ascat_segments,
    tumor_LogR,
    tumor_BAF,
    ascat_qc,
    workspace=None,
    entity_type=None,
    entity_name=None,
    docker='gcr.io/broad-getzlab-workflows/sgz:v21',
):
    ascat2sgz_seg_results = ascat2sgz_seg(
        inputs=dict(            
            sample_id=pair_id,
            ascat_segments=ascat_segments,
            tumor_baf=tumor_LogR,
            tumor_log_r=tumor_BAF,
            ascat_qc=ascat_qc,
        ),
        docker=docker,
    )
    sgz_format_maf_results = sgz_format_maf(
        inputs = dict(
            sample_id=pair_id
            hapaseg_tonly_merged_maf=hapaseg_tonly_merged_maf
        ),
        docker=docker,
    )
    
    sgz_results = sgz(
        inputs = dict(
            sample_id=pair_id, 
            cna_txt=ascat2sgz_seg_results['ascat2sgz_seg'],
            mut_txt=sgz_format_maf_results['hapaseg_tonly_merged_maf2sgz_fn']
        ),
        docker=docker,
    )
    
    output_dict = {
        "ascat2sgz_seg": ascat2sgz_seg_results['ascat2sgz_seg'],
        "hapaseg_tonly_merged_maf2sgz_fn": sgz_format_maf_results["hapaseg_tonly_merged_maf2sgz_fn"],
        "sgz_annot_hapaseg_tonly_merged_maf2sgz_fn": sgz_results["sgz_mut_txt"]
    }
    
    if workspace is not None:
        sync_task = wolf.fc.SyncToWorkspace(
            nameworkspace = workspace,
            entity_type = entity_type,
            entity_name = entity_name,
            attr_map = output_dict
        )
        
    return output_dict
    
    
    