#!/usr/bin/env python3.8.11
# -*- Coding: UTF-8 -*-

'''
Generic methods for python scripts
authors: Vinicius Roggério da Rocha and Lucas Alberto Fumagalli Coelho
github: @viniroger and @lucasfumagalli
version: 0.0.1
date: 2021-08-27
'''

import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset, num2date
from mpl_toolkits.basemap import Basemap
import scipy.ndimage as ndimage
import mygrads as mg

class ERA5():

    @staticmethod
    def open_nc(file_name):
        '''
        Open NetCDF file
        '''
        return Dataset(file_name)

    @staticmethod
    def get_dimensions(ds):
        '''
        Get latitudes, longitudes and times
        '''
        lat = ds.variables['latitude'][:]
        lon = ds.variables['longitude'][:]
        size = len(ds.variables['time'][:])
        time = ds.variables['time']
        dates = num2date(time[:], time.units, time.calendar)
        return lat, lon, size, dates

    @staticmethod
    def get_dt(day, month, year, i):
        '''
        Get date/time info and convert to datetime/string formats
        '''
        start_date = dt.datetime(int(year),int(month),int(day))
        dt_i = start_date + dt.timedelta(hours=i)
        dt_str = dt_i.strftime('%d/%m/%Y %HZ')
        return dt_i, dt_str

    @staticmethod
    def base_map(ext):
        '''
        Draw map based at extent and using:
        - shapefile with brazilian states borders
        - coastlines, borders and gridlines
        '''
        proj = 'cyl' # 'merc' # Mercator; 'cyl' for Equidistant Cylindrical Projection
        fig = plt.figure(figsize=(11,11))
        ax = fig.add_subplot(111)
        bmap = Basemap(projection=proj,llcrnrlat=ext[0],urcrnrlat=ext[1],llcrnrlon=ext[2],urcrnrlon=ext[3])
        bmap.drawlsmask(land_color='#DEDEDE',ocean_color='#D8FFFF',resolution='f',lakes=False,alpha=1,zorder=-4)
        bmap.drawparallels(np.arange( -90., 90.,5),labels=[1,0,0,0],fontsize=9,linewidth=0.75,dashes=[4, 2],color='#A3ACAC')
        bmap.drawmeridians(np.arange(-180.,180.,10),labels=[0,0,0,1],fontsize=9,linewidth=0.75,dashes=[4, 2],color='#A3ACAC')
        bmap.readshapefile('helpers/BR_UF_2019','BR_UF_2019',linewidth=0.5,color='#732B29')
        bmap.readshapefile('helpers/ne_10m_admin_0_countries','ne_10m_admin_0_countries',linewidth=0.5,color='#732B29')
        return fig, bmap

    @staticmethod
    def plot_slpesp(fig, bmap, ds_slp, ds_levels, lat, lon, t):
        '''
        Plot mean sea level pressure
        and difference between 1000 and 500 geopotential (thickness)
        '''
        # Prepare/Calculate values
        x, y = bmap(*np.meshgrid(lon,lat))
        z500 = (ds_levels.variables['z'][t,1,:,:])
        z1000 = (ds_levels.variables['z'][t,3,:,:])
        esp = (z500-z1000)/9.8
        esp = ndimage.gaussian_filter(esp, sigma=0, order=0)
        slp = (ds_slp.variables['msl'][t,:,:])
        slp = ndimage.gaussian_filter(slp, sigma=0, order=0)
        slp = slp/100 # convert to hPa

        # Thickness - Plot shadows and lines
        esp1 = bmap.contourf(x, y, esp, cmap= 'Spectral_r', levels=np.arange(4680,6240,120), alpha=0.6)
        esp3 = bmap.contour(x, y, esp, cmap= 'Spectral_r', linewidths=.7, levels=np.arange(4560,6120,120))
        labels2 = plt.clabel(esp3, fontsize=8, rightside_up=True, use_clabeltext=True, inline_spacing=0, fmt='%i')
        for i in labels2:
            i.set_rotation(0)
        # Thickness - Draw 5400 line at black
        esp2 = bmap.contour(x, y, esp, colors='k',linewidths=.9, levels=np.arange(5400,5450,50),zorder=100)
        labels2 = plt.clabel(esp2, fontsize=9, rightside_up=True, use_clabeltext=True, inline_spacing=0, fmt='%i')
        for i in labels2:
            i.set_rotation(0)
        # Pressure - Plot intermediate lines and main lines (with rotate values)
        pres2 = plt.contour(x, y, slp, cmap = 'hsv_r', linewidths=.7, levels=np.arange(int(np.min(slp)-2),int(np.max(slp)),4))
        pres = plt.contour(x, y, slp, cmap = 'hsv_r', linewidths=1.5, levels=np.arange(int(np.min(slp)),int(np.max(slp)),4))
        labels2 = plt.clabel(pres, fontsize=10, rightside_up=True, use_clabeltext=True, inline_spacing=0, fmt='%i')
        for i in labels2:
            i.set_rotation(0)
        return fig, esp1

    @staticmethod
    def plot_uvt850(fig, bmap, ds_levels, lat, lon, t):
        '''
        Plot wind and temperature at 850 hPa
        '''
        # Prepare/Calculate values
        x, y = bmap(*np.meshgrid(lon,lat))
        u = (ds_levels.variables['u'][t,2,:,:])
        v = (ds_levels.variables['v'][t,2,:,:])
        t850 = (ds_levels.variables['t'][t,2,:,:])
        t850 = t850-273.15

        # Temperature - Plot lines
        temp = plt.contour(x, y, t850, cmap = 'gist_rainbow_r', linewidths=1.5, levels=np.arange(-24,24,2))
        labels2 = plt.clabel(temp, fontsize=10, rightside_up=True, use_clabeltext=True, inline_spacing=0, fmt="%i")
        for i in labels2:
            i.set_rotation(0)
        #temp2 = plt.contour(x, y, t850, colors='#FF0028', linewidths=1.5, levels=np.arange(24,42,2))
        #labels2 = plt.clabel(temp2, fontsize=10, rightside_up=True, use_clabeltext=True, inline_spacing=0, fmt="%i")
        #for i in labels2:
        #    i.set_rotation(0)
        # Temperature - Plot black line
        temp3 = bmap.contour(x, y, t850, colors='k',linewidths=.9, levels=np.arange(0,1,1),zorder=100)
        labels2 = plt.clabel(temp3, fontsize=9, rightside_up=True, use_clabeltext=True, inline_spacing=0, fmt="%i")
        for i in labels2:
            i.set_rotation(0)
        # Wind - Plot vectors
        yy = np.arange(0, y.shape[0], 5)
        xx = np.arange(0, x.shape[1], 5)
        points = np.meshgrid(yy, xx)
        plt.quiver(x[points], y[points], u[points], v[points], color='#5F5F5F',width=0.0008, scale=700,  headwidth=5, headlength=6, pivot='middle',zorder=3 )
        #return fig, temp
        return fig, 'no_cbar'

    @staticmethod
    def plot_advt850(fig, bmap, ds_levels, lat, lon, t):
        '''
        Plot temperature advection at 850 hPa
        '''
        # Prepare/Calculate values
        x, y = bmap(*np.meshgrid(lon,lat))
        u = (ds_levels.variables['u'][t,2,:,:])
        v = (ds_levels.variables['v'][t,2,:,:])
        z = (ds_levels.variables['z'][t,2,:,:])
        z = z/9.8
        t850 = (ds_levels.variables['t'][t,2,:,:])
        t850 = t850-273.15
        adv = mg.hadv(u,v,t850,lat,lon)*1e4

        # Advection - Plot shadow
        cores = ['#440097','#440097','#4700A1','#4D11A2','#613BAD','#967BC7','#CFC3E5',
        '#FFFFFF00','#FCC9C9','#F98A95','#F4405E','#F4002E','#F30000','#D00000','#D00000','#D00000']
        levels = [-14,-12,-10, -8, -6,-4,-2,-1,1,2,4,6,8,10,12,14]
        tadv = plt.contourf(x, y, adv, colors=cores, levels=levels,zorder=-3)
        # Wind - Plot vectors
        yy = np.arange(0, y.shape[0], 5)
        xx = np.arange(0, x.shape[1], 5)
        points = np.meshgrid(yy, xx)
        plt.quiver(x[points], y[points], u[points], v[points], color='#5F5F5F',width=0.0008, scale=700, headwidth=5, headlength=6, pivot='middle', zorder=3)

        pres = bmap.contour(x, y, z, colors='k',linewidths=1., levels=np.arange(0,5000,20),zorder=-2)
        labels2=plt.clabel(pres, fontsize=9, rightside_up=True,use_clabeltext=True, inline_spacing=0, fmt="%i")
        for i in labels2:
            i.set_rotation(0)
        return fig, tadv

    @staticmethod
    def plot_vort500(fig, bmap, ds_levels, lat, lon, t):
        '''
        Plot vorticity at 500 hPa
        '''
        # Prepare/Calculate values
        x, y = bmap(*np.meshgrid(lon,lat))
        u = (ds_levels.variables['u'][t,1,:,:])
        v = (ds_levels.variables['v'][t,1,:,:])
        z = (ds_levels.variables['z'][t,1,:,:])
        z = z/9.8
        vort = mg.hcurl(u,v,lat,lon)
        adv = mg.hadv(u,v,vort,lat,lon)*1e8

        # Vorticity - Plot shadows and lines
        cores = ['#440097','#440097','#4700A1','#4D11A2','#613BAD','#967BC7','#CFC3E5',
        '#FFFFFF00','#FCC9C9','#F98A95','#F4405E','#F4002E','#F30000','#D00000','#D00000','#D00000']
        levels = [-12,-6,-5, -4, -3,-2,-1,-.5,.5,1,2,3,3.5,4,4.5,20]
        tadv = plt.contourf(x, y, adv, colors=cores, levels=levels, zorder=-3)
        pres = bmap.contour(x, y, z, colors='k',linewidths=1., levels=np.arange(0,10000,30), zorder=1)
        labels2 = plt.clabel(pres, fontsize=9, rightside_up=True, use_clabeltext=True, inline_spacing=0, fmt="%i")
        for i in labels2:
            i.set_rotation(0)
        return fig, tadv

    @staticmethod
    def plot_omega(fig, bmap, ds_levels, lat, lon, t):
        '''
        Plot omega at 500 hPa
        '''
        x, y= bmap(*np.meshgrid(lon,lat))
        w = (ds_levels.variables['w'][t,1,:,:])
        z = (ds_levels.variables['z'][t,1,:,:])
        z = z/9.8
        cores = ['#440097','#440097','#4700A1','#4D11A2','#613BAD','#967BC7','#CFC3E5',
        '#FFFFFF00','#FCC9C9','#F98A95','#F4405E','#F4002E','#F30000','#D00000','#D00000','#D00000']
        levels=[-12,-6,-5,-4,-3,-2,-1,-.5,.5,1,2,3,3.5,4,4.5,20]
        omega = plt.contourf(x, y, w, colors=cores, levels=levels, zorder=-1)
        hgt500 = bmap.contour(x, y, z, colors='k',linewidths=1., levels=np.arange(0,10000,30), zorder=0)
        labels=plt.clabel(hgt500, fontsize=10, rightside_up=True, use_clabeltext=True, inline_spacing=0, fmt="%i")
        for i in labels:
            i.set_rotation(0)
        return fig, omega

    @staticmethod
    def plot_uv250(fig, bmap, ds_levels, lat, lon, t):
        '''
        Plot wind at 250 hPa
        '''
        # Prepare/Calculate values
        x, y = bmap(*np.meshgrid(lon,lat))
        u = (ds_levels.variables['u'][t,0,:,:])
        v = (ds_levels.variables['v'][t,0,:,:])
        # Streamlines - not works with Mercator projection
        plt.streamplot(x, y, u, v)
        # Plot shadows and vectors
        yy = np.arange(0, y.shape[0], 5)
        xx = np.arange(0, x.shape[1], 5)
        points = np.meshgrid(yy, xx)
        plt.quiver(x[points], y[points], u[points], v[points], color='#5F5F5F', width=0.0008, scale=700, headwidth=5, headlength=6, pivot='middle',zorder=3)
        return fig, 'no_cbar'

    @staticmethod
    def plot_andes(fig, bmap):
        '''
        Cover Andes (above 2000 meters) with gray shadow
        '''
        file_oro = Dataset('helpers/orografia.nc')
        latr = file_oro.variables['latitude'][:]
        lonr = file_oro.variables['longitude'][:]
        xr, yr = bmap(*np.meshgrid(lonr,latr))
        r = (file_oro.variables['z'][0,:,:])
        r = r/10
        mask = plt.contourf(xr, yr, r, colors='dimgray', levels=np.arange(2000,10000,3000), zorder=5)
        return fig

    @staticmethod
    def cftime_to_str(d):
        '''
        Convert cftime.DatetimeGregorian to datetime and string
        '''
        dt1 = dt.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
        dt2 = dt1.strftime('%d/%m/%Y %HZ')
        return dt2

    @classmethod
    def plot_fig(self, fig, cbar_val, file_name, title1, time):
        '''
        Plot map and save figure
        '''
        dt_str = self.cftime_to_str(time)
        plt.title('\n'+title1+'\n', fontweight='bold',fontsize=10,loc='left', va='top')
        plt.title('\n\n'+dt_str, fontweight='bold',fontsize=10,loc='right', va='top')
        if cbar_val != 'no_cbar':
            cax = fig.add_axes([0.83, 0.25, 0.012, 0.5])
            fig.colorbar(cbar_val, shrink=.6, cax=cax)
        plt.margins(0,0)
        plt.savefig(file_name, bbox_inches='tight', dpi=300, transparent=False, pad_inches = 0)
        plt.close()
