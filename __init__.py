# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Accesibilidad_Raster
                                 A QGIS plugin
 Calcula accesibilidad
                             -------------------
        begin                : 2016-02-01
        copyright            : (C) 2016 by Tomas Cox
        email                : tcox2@uc.cl
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Accesibilidad_Raster class from file Accesibilidad_Raster.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Accesibilidad_Raster import Accesibilidad_Raster
    return Accesibilidad_Raster(iface)
