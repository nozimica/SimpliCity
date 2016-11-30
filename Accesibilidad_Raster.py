# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Accesibilidad_Raster
                                 A QGIS plugin
 Calcula accesibilidad
                              -------------------
        begin                : 2016-02-01
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Tomas Cox
        email                : tcox2@uc.cl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QTableWidget, QTableWidgetItem, QFont
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Accesibilidad_Raster_dialog import Accesibilidad_RasterDialog
import os.path

# getting current project's name
from qgis.core import *

class AccRasGui(object):
    def __init__(self, dlgObj, workingPath):
        self.counter = -1
        self.workingPath = workingPath
        self.defsFileName = os.path.abspath(os.path.join(self.workingPath, 'simsFile.txt'))
        self.dlgObj = dlgObj
        self.dlgObj.testLineEdit.clear()

        # add event for button "btnAddSimParams"
        self.dlgObj.btnAddSimParams.clicked.connect(self.eventAddSimParams)
        self.dlgObj.btnDelSimParams.clicked.connect(self.eventDelSimParams)

        self.columnLabels = [u'Capa origen', u'Col origen', u'Capa destino', u'Col destino', u'Vecindad', u'Tipo de cálculo', u'Fórmula', u'Peso min', u'T corte', u'Exp tiempo', u'Elasticidad']
        self.colNames = ['origName', 'origFieldName', 'destName', 'destFieldName', 'vicinity', 'calcType', 'formType', 'minWeightDest', 'maxTimeCalc', 'expTime', 'elasticity', 'sideLength', 'sizeX', 'sizeY']
        fnt = QFont()
        fnt.setPointSize(8)
        #fnt.setFamily("Arial")
        self.dlgObj.tblSimParams.setFont(fnt)
        self.dlgObj.tblSimParams.setColumnCount(len(self.columnLabels))
        self.dlgObj.tblSimParams.setHorizontalHeaderLabels(self.columnLabels)

        # try to load simulation definitions from file
        try:
            defsFileSize = os.path.getsize(self.defsFileName)
        except:
            defsFileSize = -1
        if defsFileSize > 0:
            dataFromFile = self.getSimulationDefinitions()
            for row_k in dataFromFile:
                self.counter += 1
                self.dlgObj.tblSimParams.setRowCount(self.counter + 1)
                colIdx = 0
                for key_h in self.colNames[0:11]:
                    self.dlgObj.tblSimParams.setItem(self.counter, colIdx, QTableWidgetItem(str(row_k[key_h])))
                    colIdx += 1
            self.dlgObj.tblSimParams.resizeColumnsToContents()


    def eventAddSimParams(self):
        self.counter += 1
        self.dlgObj.tblSimParams.setRowCount(self.counter + 1)
        self.dlgObj.testLineEdit.setText("tested... %s" % self.counter)
        # gather the elements in this row
        elemsList = [
                self.dlgObj.cboxOrigLayerName.currentText()
                , self.dlgObj.cboxOrigLayerFieldName.currentText()
                , self.dlgObj.cboxDestLayerName.currentText()
                , self.dlgObj.cboxDestLayerFieldName.currentText()
                , self.dlgObj.comboBox_tipo_acc_2.currentText()
                , self.dlgObj.comboBox_tipo_acc.currentText()
                , self.dlgObj.comboBox_tipo_formula.currentText()
                , self.dlgObj.txtMinWeightDest.text()
                , self.dlgObj.txtMaxTimeCalc.text()
                , self.dlgObj.txtExpTime.text()
                , self.dlgObj.txtElasticity.text()]

        colIdx = 0
        for elem_j in elemsList:
            self.dlgObj.tblSimParams.setItem(self.counter, colIdx, QTableWidgetItem(str(elem_j)))
            colIdx += 1
        self.dlgObj.tblSimParams.resizeColumnsToContents()

    def eventDelSimParams(self):
        self.counter -= 1
        self.dlgObj.tblSimParams.setRowCount(self.counter + 1)

    def eventOkButton(self):
        varsDict = {}
        # common data for all rows in table
        """varsDict['origName'] = self.dlgObj.cboxOrigLayerName.currentText()
        varsDict['destName'] = self.dlgObj.cboxDestLayerName.currentText()
        varsDict['origFieldName'] = self.dlgObj.cboxOrigLayerFieldName.currentText()
        varsDict['destFieldName'] = self.dlgObj.cboxDestLayerFieldName.currentText()
        varsDict['calcType'] = self.dlgObj.comboBox_tipo_acc.currentText()
        varsDict['formType'] = self.dlgObj.comboBox_tipo_formula.currentText()
        varsDict['expTime'] = float(self.dlgObj.txtExpTime.text())
        varsDict['elasticity'] = float(self.dlgObj.txtElasticity.text())
        varsDict['maxTimeCalc'] = float(self.dlgObj.txtMaxTimeCalc.text())
        varsDict['minWeightDest'] = float(self.dlgObj.txtMinWeightDest.text())
        varsDict['vicinity'] = self.dlgObj.comboBox_tipo_acc_2.currentText()
        """
        varsDict['sideLength'] = int(self.dlgObj.lineLadoCeldas.text())
        varsDict['sizeX'] = int(self.dlgObj.lineCeldasX.text())
        varsDict['sizeY'] = int(self.dlgObj.lineCeldasY.text())

        with open(self.defsFileName, 'w') as fp:
            for i in xrange(self.counter + 1):
                dataRow = []
                for j in xrange(len(self.columnLabels)):
                    #print self.dlgObj.tblSimParams.item(i, j).text()
                    dataRow.append(self.dlgObj.tblSimParams.item(i, j).text())
                dataRow.append(str(varsDict['sideLength']))
                dataRow.append(str(varsDict['sizeX']))
                dataRow.append(str(varsDict['sizeY']))
                fp.write("||".join(dataRow) + "\n")

    def getSimulationDefinitions(self):
        simsArr = []
        with open(self.defsFileName, 'r') as fp:
            for line in fp:
                dataRow_i = line.strip().split("||")
                dataDict_i = dict(zip(self.colNames, dataRow_i))
                # fix nontextual fields
                dataDict_i['expTime'] = float(dataDict_i['expTime'])
                dataDict_i['elasticity'] = float(dataDict_i['elasticity'])
                dataDict_i['maxTimeCalc'] = float(dataDict_i['maxTimeCalc'])
                dataDict_i['minWeightDest'] = float(dataDict_i['minWeightDest'])
                dataDict_i['sideLength'] = int(dataDict_i['sideLength'])
                dataDict_i['sizeX'] = int(dataDict_i['sizeX'])
                dataDict_i['sizeY'] = int(dataDict_i['sizeY'])
                simsArr.append(dataDict_i)
        return simsArr

class Accesibilidad_Raster:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Accesibilidad_Raster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        #thisShapeName = QgsProject.instance().fileName()
        self.thisShapeURI = ""
        self.thisShapeDirname = ""
        self.thisShapeName = ""
        if (QgsMapLayerRegistry.instance().mapLayers().values()):
            self.thisShapeURI = QgsMapLayerRegistry.instance().mapLayers().values()[-1].dataProvider().dataSourceUri().split("|")[0]
            self.thisShapeDirname = os.path.dirname(self.thisShapeURI)
            self.thisShapeName = os.path.basename(self.thisShapeURI)
            self.thisShapeNameNoext = os.path.splitext(self.thisShapeName)[0]
            self.thisShapeDest = self.thisShapeNameNoext
        else:
            self.thisShapeNameNoext = "No shapefile loaded."
            self.thisShapeDest = ""

        self.dlg = Accesibilidad_RasterDialog()
        self.guiMngr = AccRasGui(self.dlg, self.thisShapeDirname)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Accesibilidad Raster')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Accesibilidad_Raster')
        self.toolbar.setObjectName(u'Accesibilidad_Raster')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Accesibilidad_Raster', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Accesibilidad_Raster/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Accesibilidad Raster'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Accesibilidad Raster'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""

        # TODO: create new file
        #p2 = os.path.join(os.path.dirname(__file__), "newFile.shp")
        #self.createNewShp(p2)

        # Run the dialog event loop
        capas = self.iface.legendInterface().layers()
        lista_capas = []
        for item in capas:
            lista_capas.append(item.name())

        self.dlg.cboxOrigLayerName.addItems(lista_capas)
        self.dlg.cboxDestLayerName.addItems(lista_capas)
        # TODO: check the features for each layer being selected in the cbox above
        fieldsList = [f.name() for f in capas[0].fields()]
        self.dlg.cboxOrigLayerFieldName.addItems(fieldsList)
        self.dlg.cboxDestLayerFieldName.addItems(fieldsList)
        # set default fields
        self.dlg.cboxOrigLayerFieldName.setCurrentIndex(fieldsList.index(u'VELPROM'))
        self.dlg.cboxDestLayerFieldName.setCurrentIndex(fieldsList.index(u'prueba_acc'))

        # show the dialog
        self.dlg.show()

        Se_apreto_Aceptar = self.dlg.exec_()
        # See if OK was pressed

        if Se_apreto_Aceptar:
            import numpy as np
            import datetime
            print '############ALGORTIMO PARA CALCULO DE ACCESIBILIDAD################################'
            print '%s : INICIA PROCESO' % datetime.datetime.now().time()

            ## obtiene la informacion ingresada por el usuario###
            self.guiMngr.eventOkButton()

            con_info_ingresada_en_codigo = 0  ## indica si se va a calcular con input de usuario (QGIS) o con arrays ingresados por codigo (acc en serie)
            
            ## INVOCA FUNCION MAIN CON LA INFO ENTREGADA POR USUARIO ##
            if con_info_ingresada_en_codigo == 0:
                # get simulation data from file
                simDefinitions = self.guiMngr.getSimulationDefinitions()
                cant_accesibilidades = len(simDefinitions)
                for idx, varsDict in enumerate(simDefinitions):
                    #print varsDict
                    self.Funcion_Main(lista_capas,capas,varsDict,idx+1,cant_accesibilidades)

            ## INVOCA FUNCION MAIN CON LA INFO DETALLADA EN EL CODIGO A CONTINUACION ##
            if con_info_ingresada_en_codigo == 1:
                cant_accesibilidades = 11
                varsDict['sizeX'] = 175
                varsDict['sizeY'] = 175
                varsDict['sideLength'] = 500
                varsDict['vicinity'] = "Ortogonal"
                varsDict['origName'] = "Velocidades"
                varsDict['origFieldName'] = "hog_por_ano_por_celda"
                varsDict['calcType'] = "Mas Cercano"
                varsDict['formType'] = "Promedio Ponderado"
                varsDict['expTime'] = 1
                varsDict['elasticity'] = -0.05
                varsDict['maxTimeCalc'] = 100000
                varsDict['minWeightDest'] = 175

                ########### OJO QEU PUEDEN HABER INDICES EN CERO!!!!!!!!!!!!!##############################
                columna_velocidades = ["VELPR_0104","VELPR_05","VELPR_0607","VELPR_0607","VEL_PR_08","VELPR_09ad","VELPR_09ad","VELPR_09ad","VELPR_09ad","VELPR_09ad","VELPR_09ad"]  
                columna_destinos = ["TOT2004","TOT2005","TOT2006","TOT2007","TOT2008","TOT2009","TOT2010","TOT2011","TOT2012","TOT2013","TOT2014"]  
                for i in range (0,cant_accesibilidades):
                    varsDict['origFieldName'] = columna_velocidades[i]
                    varsDict['destFieldName'] = columna_destinos[i]
                    self.Funcion_Main(lista_capas,capas,varsDict,i,cant_accesibilidades)

            print '%s : TERMINA PROCESO' % datetime.datetime.now().time()

    def Funcion_Main(self,lista_capas,capas,varsDict,cont_archivo_escritura,cant_accesibilidades):
        print 'PROCESO: %s de %s' %(cont_archivo_escritura,cant_accesibilidades)
        ## obtiene la informacion de la capa ###############
        listas_vel_y_destinos = self.Obtiene_info_de_capa(lista_capas,capas,varsDict)
        lista_velocidades = listas_vel_y_destinos[0]
        lista_destinos = listas_vel_y_destinos[1]

        ## crea matrices ####################################### self.crea_matrices(varsDict,lista_velocidades,lista_destinos)
        import numpy as np
        matriz_tiempo_cruce = np.array([[0.0000000 for x in range(varsDict['sizeX'])] for y in range(varsDict['sizeY'])],dtype='f')
        matriz_destinos = np.array([[0 for x in range(varsDict['sizeX'])] for y in range(varsDict['sizeY'])])
        cont = 0
        for y in range (varsDict['sizeY']):
            for x in range (varsDict['sizeX']):
                matriz_tiempo_cruce[y,x] = (float(varsDict['sideLength']) / 1000) / (float(lista_velocidades[cont]) / 60)
                if lista_destinos[cont] >= varsDict['minWeightDest']: matriz_destinos[y,x] = lista_destinos[cont]
                else: matriz_destinos[y,x] = 0
                cont += 1

        ## CALCULA ACCESIBILIDAD ###############################
        matriz_tiempo_acumulado_total = self.calcula_tiempo_acumulado_total(matriz_tiempo_cruce,matriz_destinos,varsDict)

        self.escribe_csv_accesibilidad_total(matriz_tiempo_acumulado_total, "tiempo_acumulado%s.csv" % cont_archivo_escritura)

 ################################################ TERMINA FX DE PLUGIN (RUN). EMPIEZAN LAS DE ACCESIBILIDAD #########################################

    def Obtiene_info_de_capa(self,lista_capas,capas,varsDict):
        import numpy as np
        ## obtiene objeto Grilla Vectorial que especifico usuario #######
        CapaVelocidades = 'no encontrado'
        CapaDestinos = 'no encontrado'
        cont = 0
        for item in lista_capas:
            if varsDict['origName'] == item:
                CapaVelocidades = capas[cont]
            if varsDict['destName'] == item: 
                CapaDestinos = capas[cont]
            cont += 1

        ## se obtienen listas de velocidades y destinos de Celdas #######
        iterador_Celdas_Velocidades = CapaVelocidades.getFeatures()
        iterador_Celdas_Destinos = CapaDestinos.getFeatures()
        lista_velocidades = []
        lista_destinos = []
        for item in iterador_Celdas_Velocidades:
            lista_velocidades.append(item[varsDict['origFieldName']])
        for item in iterador_Celdas_Destinos:
            lista_destinos.append(item[varsDict['destFieldName']])

        return (lista_velocidades,lista_destinos)

    def calcula_tiempo_acumulado_total(self,matriz_tiempo_cruce,matriz_destinos,varsDict):   
        import numpy as np
        import datetime
        ## matriz que almacena valores de accesibilidad final ##
        matriz_tiempo_acumulado_total = np.array([[0.0000000 for x in range(varsDict['sizeX'])] for y in range(varsDict['sizeY'])],dtype='f')
        lista_con_matrices_tiempos_por_destinos = [] ## lista con las matrices de tiempos por cada destino, solo usado para escribir csv con tiempos.

        ## genera lista con destinos ##
        lista_destinos = []
        lista_pesos_por_destino = []
        for y in range (varsDict['sizeY']):
            for x in range (varsDict['sizeX']):
                if matriz_destinos[y,x] > 0: 
                    lista_destinos.append([y,x])
                    lista_pesos_por_destino.append(matriz_destinos[y,x])   

        if varsDict['calcType'] == 'Todos los Destinos':         
            ## recorre lista de destinos y calcula tiempo acumulado para cada uno, luego va sumando a matriz de tiempo acum total
            total_destinos = len(lista_destinos)
            cont = 0
            for item in lista_destinos:
                print '%s: CALCULANDO A DESTINO: %s (%s de %s)' % (datetime.datetime.now().time(),item,cont + 1,total_destinos)
                ## calcula para un tiempo especifico
                lista_destinos_con_un_destino = [item]
                matriz_t_acum_un_dest = self.calcula_tiempo_un_destino(matriz_tiempo_cruce,varsDict,lista_destinos_con_un_destino)
                lista_con_matrices_tiempos_por_destinos.append(matriz_t_acum_un_dest)
       
                ## suma los tiempos a una matriz de tiempos totales, aplicando formulas a eleccion de usuario     
                if varsDict['formType'] == 'Promedio Ponderado':
                    total_pesos_destinos = sum(lista_pesos_por_destino)
                    for y in range (varsDict['sizeY']):
                        for x in range (varsDict['sizeX']):
                            if matriz_t_acum_un_dest[y,x] == 10000000 : pass
                            else: matriz_tiempo_acumulado_total[y,x] = matriz_tiempo_acumulado_total[y,x] + matriz_t_acum_un_dest[y,x] * (float(lista_pesos_por_destino[cont]) / float(total_pesos_destinos))

                if varsDict['formType'] == 'Gravitacional':
                    for y in range (varsDict['sizeY']):
                        for x in range (varsDict['sizeX']):
                            if matriz_t_acum_un_dest[y,x] == 10000000 : pass
                            else: matriz_tiempo_acumulado_total[y,x] = matriz_tiempo_acumulado_total[y,x] + (lista_pesos_por_destino[cont] /  matriz_t_acum_un_dest[y,x]**varsDict['expTime'])       

                if varsDict['formType'] == 'Exponencial Negativa':
                    total_pesos_destinos = sum(lista_pesos_por_destino)
                    for y in range (varsDict['sizeY']):
                        for x in range (varsDict['sizeX']):
                            if matriz_t_acum_un_dest[y,x] == 10000000 : pass
                            else: matriz_tiempo_acumulado_total[y,x] = matriz_tiempo_acumulado_total[y,x] + (1 / (2.718281**(varsDict['elasticity'] * matriz_t_acum_un_dest[y,x])))*(float(lista_pesos_por_destino[cont]) / float(total_pesos_destinos) )

                cont += 1


        if varsDict['calcType'] == 'Mas Cercano':
            print '%s: CALCULANDO DESTINO MAS CERCANO' % datetime.datetime.now().time()
            ## calcula para la lista con todos los destinos
            matriz_t_acum_un_dest = self.calcula_tiempo_un_destino(matriz_tiempo_cruce,varsDict,lista_destinos)

            ## a partir de la matriz con los tiempos al destino mas cercano, se calcula la accesbilidad con formula gravitacional
            if varsDict['formType'] == 'Gravitacional': 
                for y in range (varsDict['sizeY']):
                    for x in range (varsDict['sizeX']):
                        if matriz_t_acum_un_dest[y,x] == 10000000 : pass
                        else: matriz_tiempo_acumulado_total[y,x] = 1 /  matriz_t_acum_un_dest[y,x]**varsDict['expTime']

            ## a partir de la matriz con los tiempos al destino mas cercano, se calcula la accesbilidad con formula exponencial negativa
            if varsDict['formType'] == 'Exponencial Negativa':
                for y in range (varsDict['sizeY']):
                    for x in range (varsDict['sizeX']):
                        if matriz_t_acum_un_dest[y,x] == 10000000 : pass
                        else: matriz_tiempo_acumulado_total[y,x] = (1 / (2.718281**(varsDict['elasticity'] * matriz_t_acum_un_dest[y,x])))
            ## nota: si se elige promedio ponderado, se deja la matriz tiempo acumulado tal cual (el tiempo al mas cercano queda en minutos)

            if varsDict['formType'] == 'Promedio Ponderado':
                total_pesos_destinos = sum(lista_pesos_por_destino)
                for y in range (varsDict['sizeY']):
                    for x in range (varsDict['sizeX']):
                        if matriz_t_acum_un_dest[y,x] == 10000000 : pass
                        else: matriz_tiempo_acumulado_total[y,x] = matriz_t_acum_un_dest[y,x]

        if varsDict['calcType'] == 'Todos los Destinos':
            self.escribe_csv_tiempos_por_destino(lista_con_matrices_tiempos_por_destinos,'tiempos_por_destino.csv', varsDict)


        return matriz_tiempo_acumulado_total

    def calcula_tiempo_un_destino(self,matriz_tiempo_cruce,varsDict,lista_destinos): 
        import datetime
        import copy
        import numpy as np 

        ## crea matrices de calculo
        matriz_t_acum_un_dest = np.array([[10000000.000000 for x in range(varsDict['sizeX'])] for y in range(varsDict['sizeY'])],dtype='f')
        matriz_celda_cerrada = np.array([[0 for x in range(varsDict['sizeX'])] for y in range(varsDict['sizeY'])])
        celdas_frontera = []

        ## crea pivote a partir de lista de destinos. El primero es pivote, los demas destinos (si es que hay mas) quedan como celdas frontera y se cierran
        ya_hay_un_pivote = 0
        for item in lista_destinos:
            matriz_t_acum_un_dest[item[0],item[1]] = 1
            if ya_hay_un_pivote == 0: 
                pivote = [item[0],item[1]]
                ya_hay_un_pivote = 1
            else: 
                celdas_frontera.append([item[0],item[1]])
                matriz_celda_cerrada[item[0],item[1]] = 1

        ############################## CICLO CALCULO DE TIEMPO ACUMULADO A UN DESTINO ######################
        todas_cerradas = 0
        ya_no_hay_celdas_front = 0
        cont2 = 0
        while todas_cerradas == 0 and ya_no_hay_celdas_front == 0 and cont2 < 40000 :

            matriz_celda_cerrada[pivote[0],pivote[1]] = 1

            ## crea lista con celdas vecinas a pivote y elimina las que se salen de la matriz
            vecinos_orto_pivote = [[pivote[0] - 1,pivote[1]],[pivote[0] + 1,pivote[1]],[pivote[0],pivote[1] - 1],[pivote[0],pivote[1] + 1]]
            if varsDict['vicinity'] == 'Ortogonal y Diagonal': vecinos_diago_pivote = [[pivote[0] - 1,pivote[1] - 1],[pivote[0] + 1,pivote[1] + 1],[pivote[0] + 1,pivote[1] - 1],[pivote[0] - 1,pivote[1] + 1]]

            ## suma tiempos a los vecinos del pivote que no estan cerrados y que tienen tiempo acumulado mayor al del pivote ##

            tiempo_acum_pivote = matriz_t_acum_un_dest[pivote[0],pivote[1]] ##se crea esta variable para no tener que llamar a la matriz 2 veces
            tiempo_cruce_pivote = matriz_tiempo_cruce[pivote[0],pivote[1]] ##se crea esta variable para no tener que llamar a la matriz 2 veces

            for item in vecinos_orto_pivote:
                if item[0] >= 0 and item[0] < varsDict['sizeY'] and item[1] >= 0 and item[1] < varsDict['sizeX']:
                    if matriz_t_acum_un_dest[item[0],item[1]] > tiempo_acum_pivote + tiempo_cruce_pivote and tiempo_acum_pivote + tiempo_cruce_pivote <= varsDict['maxTimeCalc'] and matriz_celda_cerrada[item[0],item[1]] == 0:      
                        matriz_t_acum_un_dest[item[0],item[1]] = tiempo_acum_pivote + tiempo_cruce_pivote
                        celdas_frontera.append([item[0],item[1]])

            if varsDict['vicinity'] == 'Ortogonal y Diagonal':
                for item in vecinos_diago_pivote:
                    if item[0] >= 0 and item[0] < varsDict['sizeY'] and item[1] >= 0 and item[1] < varsDict['sizeX']:
                        if matriz_t_acum_un_dest[item[0],item[1]] > tiempo_acum_pivote + tiempo_cruce_pivote * 1.41 and tiempo_acum_pivote + tiempo_cruce_pivote *1.41 <= varsDict['maxTimeCalc'] and matriz_celda_cerrada[item[0],item[1]] == 0:                    
                            matriz_t_acum_un_dest[item[0],item[1]] = tiempo_acum_pivote + tiempo_cruce_pivote * 1.41 
                            celdas_frontera.append([item[0],item[1]])


            todas_cerradas = 1         
            for y in range (varsDict['sizeY']):
                for x in range (varsDict['sizeX']):
                    #if matriz_celda_cerrada[y,x] == 0 and matriz_t_acum_un_dest[y,x] <> 10000000:
                    if matriz_celda_cerrada[y,x] == 0:
                        todas_cerradas = 0         
                        break
                if todas_cerradas == 0: break

            ## encuentra celda frontera con el menor tiempo acumulado y la designa pivote ##
            min_tiempo = 1000000000
            index_pivote = -1 
            cont3 = 0
            celda_con_tiempo_menor = []
            for item in celdas_frontera:
                if matriz_t_acum_un_dest[item[0],item[1]] < min_tiempo: 
                    min_tiempo = matriz_t_acum_un_dest[item[0],item[1]]
                    celda_con_tiempo_menor = [item[0],item[1]]
                    index_pivote = cont3
                cont3 += 1
            #print celdas_frontera
            pivote = celda_con_tiempo_menor
            if todas_cerradas == 0 and len(celdas_frontera) > 0: celdas_frontera.pop(index_pivote)
            cont2 += 1
        
            if len(celdas_frontera) == 0 : ya_no_hay_celdas_front = 1
       
        return matriz_t_acum_un_dest

    def escribe_csv_accesibilidad_total(self,matriz_atributo,nombre_archivo):
        ## escribe texto en archivo csv #######
        p = os.path.join(self.thisShapeDirname, nombre_archivo)
        file = open(p,'w')
        os.path.abspath(file.name)
        file.write("ID,acces")     
        cont = 0
        for item in matriz_atributo:
            for item2 in item:
                file.write("\n%s" % cont ) 
                file.write(",%s" % item2 )
                cont += 1
        file.close()

    def escribe_csv_tiempos_por_destino(self,lista_con_matrices_tiempos_por_destinos, nombre_archivo, varsDict):

        ## escribe texto en archivo csv #######
        p = os.path.join(self.thisShapeDirname, nombre_archivo)
        file = open(p,'w')
        os.path.abspath(file.name)

        file.write("ID")
        cont = 0
        for item in lista_con_matrices_tiempos_por_destinos:
            file.write(",%s" %cont)
            cont+= 1
 
        cont = 0
        for y in range (varsDict['sizeY']):
            for x in range (varsDict['sizeX']):
                file.write("\n%s" % cont ) 
                for item in lista_con_matrices_tiempos_por_destinos:
                    file.write(",%s" % item[y,x] )
                cont += 1
        file.close()

        p2 = os.path.join(self.thisShapeDirname, "%st" % nombre_archivo)
        archivo2 = open(p2,'w')
        os.path.abspath(archivo2.name)
        archivo2.write('"integer"')
        for item in lista_con_matrices_tiempos_por_destinos:
            archivo2.write(',"real"')
        archivo2.close() 

    def createNewShp(self, outputFilename):
        layer = self.iface.activeLayer()
        provider = layer.dataProvider()
        fields = provider.fields()
        writer = QgsVectorFileWriter(outputFilename, "CP1250", fields, provider.geometryType(), provider.crs(), "ESRI Shapefile")
        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        while provider.nextFeature(inFeat):
            point = inFeat.geometry().asPoint()
            inGeom = inFeat.geometry()
            outFeat.setGeometry(inFeat.geometry() )
            outFeat.setAttributeMap(inFeat.attributeMap() )
            writer.addFeature( outFeat )
        del writer
        newlayer = QgsVectorLayer(outputFilename, "Output", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(newlayer)

