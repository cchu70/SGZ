import wolf

sgz_docker = 'gcr.io/broad-getzlab-workflows/sgz:v21'

class sgz(wolf.Task):
    
    inputs = {
        'sample_id': None,
        'cna_txt': None,
        'mut_txt': None,
    }
    
    script = "python /app/fmiSGZ.py ${mut_txt} ${cna_txt} -o ${sample_id}"
    
    output_patterns = {
        "sgz_mut_txt": "*.fmi.sgz.full.txt"
    }
    
    docker = sgz_docker
    resources = {"cpus-per-task": 4, "mem" : "8G"}
    

class ascat2sgz_seg(wolf.Task):
    inputs = {
        'sample_id': None,
        'ascat_segments': None,
        'tumor_baf': None,
        'tumor_log_r': None,
        'ascat_qc': None,
    }
    
    script = """
        python /app/convert_ascat2sgz.py \
            --sample_id ${sample_id} \
            --ascat_segments ${ascat_segments}  \
            --tumor_log_r ${tumor_log_r}  \
            --tumor_baf ${tumor_baf} \
            --ascat_qc ${ascat_qc} 
    """
    
    output_patterns = {
        'ascat2sgz_seg': '*.ascat2SGZ.tsv'
    }
    
    docker = sgz_docker
    resources = {"cpus-per-task": 4, "mem" : "8G"}
    
class sgz_format_maf(wolf.Task):
    
    inputs = {
        'sample_id': None, 
        'hapaseg_tonly_merged_maf': None
    }
    
    script = "python /app/format_maf2sgz.py --sample_id ${sample_id} --hapaseg_tonly_merged_maf ${hapaseg_tonly_merged_maf}"
    
    output_patterns = {
        'hapaseg_tonly_merged_maf2sgz_fn': '*.hapaseg_tonly_merged_maf2sgz.tsv'
    }
    
    docker = sgz_docker
    resources = {"cpus-per-task": 4, "mem" : "8G"}