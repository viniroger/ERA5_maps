#!/usr/bin/env python3.8.11
# -*- Coding: UTF-8 -*-

from helpers.era5 import ERA5

# Define type of map
fig_type = {
    'slpesp': 'Espessura 1000-500 (sombreado, mgp)\nPressão ao nível do mar (contorno, hPa)',
    'uvt850': 'Vento 850 hPa (vetor)\nT 850 hPa (contorno, °C)',
    'advt850': 'Z 850 hPa (contorno, mgp)\n-$V_g$.$∇_H$T 850hPa (sombreado, $X10^{-8}$ $s^{-2}$)',
    'vort500': 'Z 500 hPa (contorno, mgp)\n-$V_g$.$∇_p$$ζ_g$ 500hPa (sombreado, $X10^{-8}$ $s^{-2}$)',
    'omega': 'Z 500 hPa (contorno grosso, mgp)\nω 500 hPa (sombreado, $X10^{-5}$ Pa $s^{-1}$)',
    'uv250': 'Vento 250 hPa (vetores e linhas de corrente)',
}

# Extensions - llcrnrlat,urcrnrlat,llcrnrlon,urcrnrlon
ext = [-55,15,-85,-10]

# Open NC files and get data
ds_slp = ERA5.open_nc('input/slp.nc')
ds_levels = ERA5.open_nc('input/levels.nc')
lat, lon, size, times = ERA5.get_dimensions(ds_slp)

# Loop for all keys
for key in fig_type:
    print(f'PRODUCT {key}')
    # Loop for all times
    for t in range(size):
        print(f'- Generating image from {times[t]} -> {str(t)}')
        # Draw base map based at extent
        fig, bmap = ERA5.base_map(ext)
        # Plot specified map
        if key == 'slpesp':
            fig, cbar_val = ERA5.plot_slpesp(fig, bmap, ds_slp, ds_levels, lat, lon, t)
        elif key == 'uvt850':
            fig, cbar_val = ERA5.plot_uvt850(fig, bmap, ds_levels, lat, lon, t)
        elif key == 'advt850':
            fig, cbar_val = ERA5.plot_advt850(fig, bmap, ds_levels, lat, lon, t)
        elif key == 'vort500':
            fig, cbar_val = ERA5.plot_vort500(fig, bmap, ds_levels, lat, lon, t)
        elif key == 'omega':
            fig, cbar_val = ERA5.plot_omega(fig, bmap, ds_levels, lat, lon, t)
        elif key == 'uv250':
            fig, cbar_val = ERA5.plot_uv250(fig, bmap, ds_levels, lat, lon, t)
        # Plot Andes
        #fig = ERA5.plot_andes(fig, bmap)
        # Finalize/Close figure
        file_name = f'output/{key}_{str(t).zfill(3)}.png'
        ERA5.plot_fig(fig, cbar_val, file_name, fig_type[key], times[t])
        #exit()
    #exit()
