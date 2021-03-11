# -*- coding: utf-8 -*-

"""
Post_ImportRaster.py
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Leandro França'
__date__ = '2021-03-10'
__copyright__ = '(C) 2020, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsApplication,
                       QgsRasterLayer,
                       QgsCoordinateReferenceSystem)

from lftools.geocapt.imgs import Imgs
import os
from pathlib import Path
from qgis.PyQt.QtGui import QIcon

class ImportRaster(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()

    def translate(self, string):
        return QCoreApplication.translate('Processing', string)

    def tr(self, *string):
        # Traduzir para o portugês: arg[0] - english (translate), arg[1] - português
        if self.LOC == 'pt':
            if len(string) == 2:
                return string[1]
            else:
                return self.translate(string[0])
        else:
            return self.translate(string[0])

    def createInstance(self):
        return ImportRaster()

    def name(self):
        return 'importraster'

    def displayName(self):
        return self.tr('Import Raster', 'Importar Raster')

    def group(self):
        return self.tr('PostGIS')

    def groupId(self):
        return 'postgis'

    def tags(self):
        return self.tr('postgis,postgresql,database,BD,DB,import,raster,overview,tiling').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/postgis.png'))

    def shortHelpString(self):
        txt_en = '''This tool allows you to load a raster layer into a PostGIS database.'''
        txt_pt = """Esta ferramenta permite carregar uma camada raster para dentro de um banco de dados PostGIS."""
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/tutorial/post_importraster.jpg') +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(txt_en, txt_pt) + footer

    RASTER = 'RASTER'
    DATABASE = 'DATABASE'
    SCHEMA = 'SCHEMA'
    TABLE = 'TABLE'
    HOST = 'HOST'
    PORT = 'PORT'
    USER = 'USER'
    VERSION = 'VERSION'
    TYPE = 'TYPE'
    NAMECOL = 'NAMECOL'
    TILING = 'TILING'
    OVERVIEW = 'OVERVIEW'
    versions = ['9.6', '10', '11', '12', '13']

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RASTER,
                self.tr('Raster layer', 'Camada Raster'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.DATABASE,
                self.tr('Database', 'Banco de dados')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.SCHEMA,
                self.tr('Schema', 'Schema'),
                defaultValue = 'public'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.TABLE,
                self.tr('Table', 'Tabela')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.HOST,
                self.tr('Host', 'Host'),
                defaultValue = 'localhost'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PORT,
                self.tr('Port', 'Porta'),
                defaultValue = '5432'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.USER,
                self.tr('User', 'Usuário'),
                defaultValue = 'postgres'
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.VERSION,
                self.tr('PostgreSQL version', 'Versão do PostgreSQL'),
				options = self.versions,
                defaultValue= 1
            )
        )

        tipos = ['d: Drops and creates a table',
                 'a: Appends data to an existing table',
                 'c: Creates a new table',
                 'p: Turns on prepare mode']

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Options', 'Opções'),
				options = tipos,
                defaultValue= 2
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.NAMECOL,
            self.tr('Create column with raster name', 'Criar coluna com nome do raster'),
            defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.TILING,
                self.tr('Tiling'),
                defaultValue = '100x100'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.OVERVIEW,
                self.tr('Overviews'),
                defaultValue = '2,4'
            )
        )



    def processAlgorithm(self, parameters, context, feedback):

        raster = self.parameterAsRasterLayer(
            parameters,
            self.RASTER,
            context
        )
        if raster is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.RASTER))


        database = self.parameterAsString(
            parameters,
            self.DATABASE,
            context
        )
        if not database or database == '' or ' ' in database:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DATABASE))


        schema = self.parameterAsString(
            parameters,
            self.SCHEMA,
            context
        )

        table = self.parameterAsString(
            parameters,
            self.TABLE,
            context
        )
        if not table or table == '' or ' ' in table:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TABLE))

        host = self.parameterAsString(
            parameters,
            self.HOST,
            context
        )

        port = self.parameterAsString(
            parameters,
            self.PORT,
            context
        )

        version = self.parameterAsEnum(
            parameters,
            self.VERSION,
            context
        )
        version = self.versions[version]

        user = self.parameterAsString(
            parameters,
            self.USER,
            context
        )

        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )
        tipo = ['-d ', '-a ', '-c ', '-p '][tipo]

        namecol = self.parameterAsBool(
            parameters,
            self.USER,
            context
        )
        namecol = '-F ' if namecol else ''

        tiling = self.parameterAsString(
            parameters,
            self.TILING,
            context
        )
        if len(tiling)>2 and 'x' in tiling:
            tiling = '-t {} '.format(tiling)
        else:
            tiling = ''

        ovr = self.parameterAsString(
            parameters,
            self.OVERVIEW,
            context
        )
        if ovr or ovr != '' or ' ' in ovr:
            ovr = '-l {} '.format(ovr)
        else:
            ovr = ''

        # Preparando parâmetros
        projection = raster.crs().authid().split(":")[1]
        projection = ' -s ' + projection + ' '
        raster_path = raster.dataProvider().dataSourceUri()
        comando = 'raster2pgsql' + projection + tiling + tipo + namecol + ovr + '-I -C -M "'+ raster_path + '" ' + schema +'.'+ table + ' | psql -U '+user+' -d '+database+' -h '+host+' -p '+port
        feedback.pushInfo('\n' + self.tr('Command: ','Comando: ') + comando)

        # Procurando arquivo psql
        win64 = 'C:/Program Files (x86)/PostgreSQL/'+version+'/bin'
        win32 = 'C:/Program Files/PostgreSQL/'+version+'/bin'
        mac = '/Library/PostgreSQL/'+version+'/bin/'
        if os.path.isdir(win64):
            os.chdir(win64)
        elif os.path.isdir(win32):
            os.chdir(win32)
        elif os.path.isdir(mac):
            os.chdir(mac)
        else:
            raise QgsProcessingException(self.tr('Make sure your PostgreSQL version is correct!', 'Verifique se a versão do seu PostgreSQL está correta!'))

        feedback.pushInfo('\n' + self.tr('Importing raster into the database...', 'Importando raster para o banco de dados...'))
        result = os.system(comando)

        if result==0:
            feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
            feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        else:
            feedback.pushInfo(self.tr('There was a problem while executing the command. Please check the input parameters.',
                                      'Houve algum problema durante a execução do comando. Por favor, verifique os parâmetros de entrada.'))

        return {}
