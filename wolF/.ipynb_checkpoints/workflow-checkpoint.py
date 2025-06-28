import wolf
import prefect
from .tasks import sgz, ascat2sgz_seg, sgz_format_maf


split_maf_task = wolf.ImportTask(
    "git@github.com:getzlab/tonly2.git",
    commit="0aa47e8",
    main_task="split_maf"
)

gather_tonly_mafs_task = wolf.ImportTask(
    "git@github.com:getzlab/tonly2.git",
    commit="0aa47e8",
    main_task="gather_tonly_mafs"
)

def workflow(
    pair_id,
    put_som_annot_maf, 
    ascat_segments,
    tumor_LogR,
    tumor_BAF,
    ascat_qc,
    batch_size=25000,
    workspace=None,
    entity_type=None,
    entity_name=None,
    docker='gcr.io/broad-getzlab-workflows/sgz:v27',
    sync_prefix=""
):
    ascat2sgz_seg_results = ascat2sgz_seg(
        inputs=dict(            
            sample_id=pair_id,
            ascat_segments=ascat_segments,
            tumor_baf=tumor_BAF,
            tumor_log_r=tumor_LogR,
            ascat_qc=ascat_qc,
        ),
        docker=docker,
    )
    
    sgz_format_maf_results = sgz_format_maf(
        inputs = dict(
            sample_id=pair_id,
            put_som_annot_maf=put_som_annot_maf
        ),
        docker=docker,
    )
    
    split_maf_task_results = split_maf_task(
        inputs=dict(
            sample_id=pair_id, 
            maf_file=sgz_format_maf_results['maf2sgz_fn'], # hapaseg is a legacy name
            batch_size=batch_size, 
        )
    )
    
    sgz_results = sgz(
        inputs = dict(
            sample_id=pair_id, 
            cna_txt=ascat2sgz_seg_results['ascat2sgz_seg'],
            mut_txt=split_maf_task_results['split_mafs']
        ),
        docker=docker,
    )

    @prefect.task
    def atleast1d(x):
        return [x] if (not isinstance(x, list)) and x is not None else x

    # if split maf only produces a single maf, make it a list
    sgz_mut_txts = atleast1d(sgz_results['sgz_mut_txt'])
    
    gather_tonly_mafs_task_results = gather_tonly_mafs_task(
        inputs=dict(
            sample_id=pair_id, 
            tonly_annot_maf_files=[sgz_mut_txts], 
        )
    )
    
    output_dict = {
        f"{sync_prefix}SGZ_ascat2sgz_seg": ascat2sgz_seg_results['ascat2sgz_seg'],
        f"{sync_prefix}SGZ_format_maf2sgz_fn": sgz_format_maf_results["maf2sgz_fn"], # legacy run
        f"{sync_prefix}SGZ_annot_maf2sgz_fn": gather_tonly_mafs_task_results["merged_maf"]
    }
    
    if workspace is not None:
        sync_task = wolf.fc.SyncToWorkspace(
            nameworkspace = workspace,
            entity_type = entity_type,
            entity_name = entity_name,
            attr_map = output_dict
        )
        
    return output_dict
    
    
    