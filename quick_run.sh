#!/bin/bash
#
# Script rápido para executar na VM do Google Cloud
# Execute este script após fazer SSH na VM
#

echo "====== Configuração Rápida WRF - Mato Grosso ======"
echo "Data: 06/03/2021 12Z (15Z-00Z)"
echo "Região: Chapada dos Guimarães - MT (3km)"
echo "===================================================="

# Verificar se os diretórios WRF/WPS existem
if [ ! -d "/home/WRF" ] || [ ! -d "/home/WPS" ]; then
    echo "ERRO: WRF ou WPS não encontrados em /home/"
    echo "Por favor, instale o WRF/WPS primeiro"
    exit 1
fi

# Criar diretório de trabalho
export WORK_DIR=/home/wrf_run/MT_$(date +%Y%m%d_%H%M%S)
mkdir -p $WORK_DIR
cd $WORK_DIR

echo ""
echo "Diretório de trabalho: $WORK_DIR"

# Salvar os namelists diretamente
echo "Criando namelist.wps..."
cat > namelist.wps << 'EOF'
&share
 wrf_core = 'ARW',
 max_dom = 1,
 start_date = '2021-03-06_12:00:00',
 end_date   = '2021-03-07_00:00:00',
 interval_seconds = 10800,
 io_form_geogrid = 2,
/

&geogrid
 parent_id         =   1,
 parent_grid_ratio =   1,
 i_parent_start    =   1,
 j_parent_start    =   1,
 e_we              = 200,
 e_sn              = 200,
 geog_data_res     = 'default',
 dx                = 3000,
 dy                = 3000,
 map_proj          = 'mercator',
 ref_lat           = -15.45,
 ref_lon           = -55.75,
 truelat1          = -15.45,
 truelat2          = 0,
 stand_lon         = -55.75,
 geog_data_path    = '/home/WPS_GEOG/',
 opt_geogrid_tbl_path = './',
/

&ungrib
 out_format = 'WPS',
 prefix     = 'FILE',
/

&metgrid
 fg_name         = 'FILE',
 io_form_metgrid = 2,
 opt_metgrid_tbl_path = './',
/
EOF

echo "Criando namelist.input..."
cat > namelist.input << 'EOF'
&time_control
 run_days                            = 0,
 run_hours                           = 12,
 run_minutes                         = 0,
 run_seconds                         = 0,
 start_year                          = 2021,
 start_month                         = 03,
 start_day                           = 06,
 start_hour                          = 12,
 start_minute                        = 00,
 start_second                        = 00,
 end_year                            = 2021,
 end_month                           = 03,
 end_day                             = 07,
 end_hour                            = 00,
 end_minute                          = 00,
 end_second                          = 00,
 interval_seconds                    = 10800,
 input_from_file                     = .true.,
 history_interval                    = 60,
 frames_per_outfile                  = 1,
 restart                             = .false.,
 restart_interval                    = 720,
 io_form_history                     = 2,
 io_form_restart                     = 2,
 io_form_input                       = 2,
 io_form_boundary                    = 2,
 auxinput1_inname                    = "met_em.d<domain>.<date>",
 debug_level                         = 0,
/

&domains
 time_step                           = 15,
 time_step_fract_num                 = 0,
 time_step_fract_den                 = 1,
 max_dom                             = 1,
 e_we                                = 200,
 e_sn                                = 200,
 e_vert                              = 45,
 dzstretch_s                         = 1.1,
 p_top_requested                     = 5000,
 num_metgrid_levels                  = 34,
 num_metgrid_soil_levels             = 4,
 dx                                  = 3000,
 dy                                  = 3000,
 grid_id                             = 1,
 parent_id                           = 0,
 i_parent_start                      = 1,
 j_parent_start                      = 1,
 parent_grid_ratio                   = 1,
 parent_time_step_ratio              = 1,
 feedback                            = 0,
 smooth_option                       = 0,
/

&physics
 mp_physics                          = 8,
 cu_physics                          = 0,
 ra_lw_physics                       = 4,
 ra_sw_physics                       = 4,
 bl_pbl_physics                      = 2,
 sf_sfclay_physics                   = 2,
 sf_surface_physics                  = 2,
 radt                                = 3,
 bldt                                = 0,
 cudt                                = 0,
 icloud                              = 1,
 num_soil_layers                     = 4,
 num_land_cat                        = 21,
 sf_urban_physics                    = 0,
 prec_acc_dt                         = 60,
/

&fdda
/

&dynamics
 hybrid_opt                          = 2,
 w_damping                           = 1,
 diff_opt                            = 1,
 km_opt                              = 4,
 diff_6th_opt                        = 0,
 diff_6th_factor                     = 0.12,
 base_temp                           = 290.,
 damp_opt                            = 3,
 zdamp                               = 5000.,
 dampcoef                            = 0.2,
 khdif                               = 0,
 kvdif                               = 0,
 non_hydrostatic                     = .true.,
 moist_adv_opt                       = 1,
 scalar_adv_opt                      = 1,
 gwd_opt                             = 0,
/

&bdy_control
 spec_bdy_width                      = 5,
 spec_zone                           = 1,
 relax_zone                          = 4,
 specified                           = .true.,
 nested                              = .false.,
/

&grib2
/

&namelist_quilt
 nio_tasks_per_group = 0,
 nio_groups = 1,
/
EOF

echo ""
echo "Deseja executar o modelo agora? (s/n)"
read -r resposta

if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
    echo ""
    echo "Iniciando execução do modelo..."
    bash /workspace/run_wrf_mt.sh
else
    echo ""
    echo "Configuração salva em: $WORK_DIR"
    echo "Para executar mais tarde, rode:"
    echo "  cd $WORK_DIR && bash /workspace/run_wrf_mt.sh"
fi