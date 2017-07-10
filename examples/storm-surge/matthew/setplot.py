from __future__ import absolute_import
from __future__ import print_function

import os

import numpy
import matplotlib.pyplot as plt
import datetime, time

import clawpack.visclaw.colormaps as colormap
import clawpack.visclaw.gaugetools as gaugetools
import clawpack.clawutil.data as clawutil
import clawpack.amrclaw.data as amrclaw
import clawpack.geoclaw.data as geodata
import pandas as pd


import clawpack.geoclaw.surge.plot as surgeplot

try:
    from setplotfg import setplotfg
except:
    setplotfg = None

import csv
import locale


def setplot(plotdata=None):
    """"""

    if plotdata is None:
        from clawpack.visclaw.data import ClawPlotData
        plotdata = ClawPlotData()

    # clear any old figures,axes,items data
    plotdata.clearfigures()
    plotdata.format = 'ascii'

    # Load data from output
    clawdata = clawutil.ClawInputData(2)
    clawdata.read(os.path.join(plotdata.outdir, 'claw.data'))
    physics = geodata.GeoClawData()
    physics.read(os.path.join(plotdata.outdir, 'geoclaw.data'))
    surge_data = geodata.SurgeData()
    surge_data.read(os.path.join(plotdata.outdir, 'surge.data'))
    friction_data = geodata.FrictionData()
    friction_data.read(os.path.join(plotdata.outdir, 'friction.data'))

    # Load storm track
    track = surgeplot.track_data(os.path.join(plotdata.outdir, 'fort.track'))

    # Calculate landfall time
    # Landfall 2016/10/7 6 a.m.
    landfall_dt = datetime.datetime(2016, 10, 7, 6) - \
           datetime.datetime(2016, 1, 1, 0)
    landfall = landfall_dt.days * 24.0 * 60**2 + landfall_dt.seconds

    # Set afteraxes function
    def surge_afteraxes(cd):
        surgeplot.surge_afteraxes(cd, track, landfall, plot_direction=False,
                                  kwargs={"markersize": 4})

    # Color limits
    surface_limits = [physics.sea_level - 5.0, physics.sea_level + 5.0]
    surface_ticks = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    surface_labels = [str(value) for value in surface_ticks]
    speed_limits = [0.0, 3.0]
    speed_ticks = [0, 1, 2, 3]
    speed_labels = [str(value) for value in speed_ticks]
    wind_limits = [0, 64]
    pressure_limits = [933, 1013]
    friction_bounds = [0.01, 0.04]

    def add_custom_colorbar_ticks_to_axes(axes, item_name, ticks,
                                          tick_labels=None):
        """Adjust colorbar ticks and labels"""
        axes.plotitem_dict[item_name].colorbar_ticks = ticks
        axes.plotitem_dict[item_name].colorbar_tick_labels = tick_labels

    def gulf_after_axes(cd):
        # plt.subplots_adjust(left=0.08, bottom=0.04, right=0.97, top=0.96)
        surge_afteraxes(cd)

    def latex_after_axes(cd):
        # plt.subplot_adjust()
        surge_afteraxes(cd)

    def friction_after_axes(cd):
        # plt.subplots_adjust(left=0.08, bottom=0.04, right=0.97, top=0.96)
        plt.title(r"Manning's $n$ Coefficient")
        # surge_afteraxes(cd)

    # ==========================================================================
    #   Plot specifications
    # ==========================================================================
    regions = {"Gulf": {"xlimits": (clawdata.lower[0], clawdata.upper[0]),
                        "ylimits": (clawdata.lower[1], clawdata.upper[1])}}

    for (name, region_dict) in regions.iteritems():

        # Surface Figure
        plotfigure = plotdata.new_plotfigure(name="Surface - %s" % name)
        plotfigure.kwargs = {"figsize": [4,6]}
        plotaxes = plotfigure.new_plotaxes()
        plotaxes.title = "Surface"
        plotaxes.xlimits = regions['Gulf']['xlimits']
        plotaxes.ylimits = regions['Gulf']['ylimits']
        plotaxes.afteraxes = surge_afteraxes

        surgeplot.add_surface_elevation(plotaxes, bounds=surface_limits)
        surgeplot.add_land(plotaxes)
        plotaxes.plotitem_dict['surface'].amr_patchedges_show = [0] * 10
        plotaxes.plotitem_dict['land'].amr_patchedges_show = [0] * 10
        add_custom_colorbar_ticks_to_axes(plotaxes, 'surface', surface_ticks,
                                          surface_labels)

        # Speed Figure
        plotfigure = plotdata.new_plotfigure(name="Currents - %s" % name)
        plotfigure.kwargs = {"figsize": [4,6]}
        plotaxes = plotfigure.new_plotaxes()
        plotaxes.title = "Currents"
        plotaxes.xlimits = regions['Gulf']['xlimits']
        plotaxes.ylimits = regions['Gulf']['ylimits']
        plotaxes.afteraxes = surge_afteraxes

        surgeplot.add_speed(plotaxes, bounds=speed_limits)
        surgeplot.add_land(plotaxes)
        plotaxes.plotitem_dict['speed'].amr_patchedges_show = [0] * 10
        plotaxes.plotitem_dict['land'].amr_patchedges_show = [0] * 10
        add_custom_colorbar_ticks_to_axes(plotaxes, 'speed', speed_ticks,
                                          speed_labels)

    #
    # Friction field
    #
    plotfigure = plotdata.new_plotfigure(name='Friction')
    plotfigure.kwargs = {"figsize": [4,6]}
    plotfigure.show = friction_data.variable_friction and True

    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = regions['Gulf']['xlimits']
    plotaxes.ylimits = regions['Gulf']['ylimits']
    # plotaxes.title = "Manning's N Coefficient"
    plotaxes.afteraxes = friction_after_axes
    # plotaxes.scaled = True

    surgeplot.add_friction(plotaxes, bounds=friction_bounds)
    plotaxes.plotitem_dict['friction'].amr_patchedges_show = [0] * 10
    plotaxes.plotitem_dict['friction'].colorbar_label = "$n$"

    #
    #  Hurricane Forcing fields
    #
    # Pressure field
    plotfigure = plotdata.new_plotfigure(name='Pressure')
    plotfigure.kwargs = {"figsize": [4,6]}
    plotfigure.show = surge_data.pressure_forcing and True

    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = region_dict["xlimits"]
    plotaxes.ylimits = region_dict["ylimits"]
    plotaxes.title = "Pressure Field"
    plotaxes.afteraxes = surge_afteraxes
    # plotaxes.scaled = True
    surgeplot.add_pressure(plotaxes, bounds=pressure_limits)
    surgeplot.add_land(plotaxes)

    # Wind field
    plotfigure = plotdata.new_plotfigure(name='Wind Speed')
    plotfigure.kwargs = {"figsize": [4,6]}
    plotfigure.show = surge_data.wind_forcing and True

    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = region_dict["xlimits"]
    plotaxes.ylimits = region_dict["ylimits"]
    plotaxes.title = "Wind Field"
    plotaxes.afteraxes = surge_afteraxes
    # plotaxes.scaled = True
    surgeplot.add_wind(plotaxes, bounds=wind_limits)
    surgeplot.add_land(plotaxes)

    # ========================================================================
    #  Figures for gauges
    # ========================================================================

    plotfigure = plotdata.new_plotfigure(name='Gauge Surfaces', figno=300,
                                         type='each_gauge')
    plotfigure.kwargs = {"figsize": [4,6]}
    plotfigure.show = True
    plotfigure.clf_each_gauge = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = [-3, 2]
    # plotaxes.xlabel = "Days from landfall"
    # plotaxes.ylabel = "Surface (m)"
    plotaxes.ylimits = [-1, 5]
    plotaxes.title = 'Surface'

    def gauge_afteraxes(cd):

        axes = plt.gca()
        surgeplot.plot_landfall_gauge(cd.gaugesoln, axes, landfall=landfall)

        
        columns = ['Time', 'Difference']
        if (cd.gaugeno == 1):
            data = pd.read_csv('/Users/anonymous/clawpack_src/clawpack-v5.4.1rc-beta/geoclaw/examples/storm-surge/matthew/gaugeVirginiaKey.csv', header=None, names=columns)
        elif (cd.gaugeno == 2):
            data = pd.read_csv('/Users/anonymous/clawpack_src/clawpack-v5.4.1rc-beta/geoclaw/examples/storm-surge/matthew/gaugeLakeWorthPier.csv', header=None, names=columns)
        elif (cd.gaugeno == 3):
            data = pd.read_csv('/Users/anonymous/clawpack_src/clawpack-v5.4.1rc-beta/geoclaw/examples/storm-surge/matthew/gaugeTridentPier.csv', header=None, names=columns)
        elif (cd.gaugeno == 4):
            data = pd.read_csv('/Users/anonymous/clawpack_src/clawpack-v5.4.1rc-beta/geoclaw/examples/storm-surge/matthew/gaugeMayport.csv', header=None, names=columns)
        elif (cd.gaugeno == 5):
            data = pd.read_csv('/Users/anonymous/clawpack_src/clawpack-v5.4.1rc-beta/geoclaw/examples/storm-surge/matthew/gaugeDamesPoint.csv', header=None, names=columns)
        else:
            data = pd.read_csv('/Users/anonymous/clawpack_src/clawpack-v5.4.1rc-beta/geoclaw/examples/storm-surge/matthew/gaugeFernandinaBeach.csv', header=None, names=columns)
        converted = []
        tide = []
        for x in data.Time:
            if (x != 'Time'):
                datetime_object = datetime.datetime.strptime(x, '%x  %H:%M')
                t = datetime_object - landfall_dt
                second = (time.mktime(t.timetuple())) - time.mktime(datetime.datetime(2016, 1, 1, 1, 0).timetuple())
                day = second / (60.0**2 * 24.0)
                converted.append(day)

        for y in data.Difference:
            if (y != 'Difference'):
                tide.append(float(y))
        offset = numpy.mean(tide[:70])
        plt.plot(converted, tide - offset)
        # plt.hold(False)                
        

        # Fix up plot - in particular fix time labels
        axes.set_title('Station %s' % cd.gaugeno)
        axes.set_xlabel('Days relative to landfall')
        axes.set_ylabel('Surface (m)')
        axes.set_xlim([-3, 2])
        axes.set_ylim([-1, 5])
        axes.set_xticks([-3, -2, -1, 0, 1, 2])
        axes.set_xticklabels([r"-3", r"$-2$", r"$-1$", r"$0$", r"$1$", r"$2$"])
        axes.grid(True)
    

    plotaxes.afteraxes = gauge_afteraxes

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'

    # Plot real data as red curve:
    # gauge_report = pd.read_csv('/Users/anonymous/clawpack_src/clawpack-v5.4.1rc-beta/geoclaw/examples/storm-surge/matthew/gaugeReportHour.csv')    

    #plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    #plotitem.show = True
        

        

    # plotitem.plot_var = gaugeReal
    # print ("hello")
    # plotitem.plotstyle = 'g-'

    # plotaxes.afteraxes = gaugeReal


    #
    #  Gauge Location Plot
    #
    def gauge_location_afteraxes(cd):
        plt.subplots_adjust(left=0.12, bottom=0.68, right=0.97, top=0.87)
        surge_afteraxes(cd)
        gaugetools.plot_gauge_locations(cd.plotdata, gaugenos='all',
                                        format_string='ko', add_labels=True)

    plotfigure = plotdata.new_plotfigure(name="Gauge Locations")

    plotfigure.show = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Gauge Locations'
    plotaxes.scaled = True
    plotaxes.xlimits = [-82, -79.5]
    plotaxes.ylimits = [25.5, 30.5]
    plotaxes.afteraxes = gauge_location_afteraxes
    surgeplot.add_surface_elevation(plotaxes, bounds=surface_limits)
    add_custom_colorbar_ticks_to_axes(plotaxes, 'surface', surface_ticks,
                                      surface_labels)
    surgeplot.add_land(plotaxes)
    plotaxes.plotitem_dict['surface'].amr_patchedges_show = [0] * 10
    plotaxes.plotitem_dict['land'].amr_patchedges_show = [0] * 10

    # -----------------------------------------
    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    # plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_framenos = 'none'          # list of frames to print
    plotdata.print_gaugenos = [3, 4, 5, 6]            # list of gauges to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?
    plotdata.parallel = True                 # parallel plotting

    return plotdata
