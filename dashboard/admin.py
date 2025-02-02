from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from .models import *

admin.site.register(Khamgaon)

@admin.register(RootCauseAnalysis)
class RootCauseAnalysisAdmin(ImportExportModelAdmin):
    list_display = ('id', 'area', 'rca1', 'rca2', 'rca3','rca4','rca5','rca6')

@admin.register(Areas)
class AreasAdmin(ImportExportModelAdmin):
    list_display = ('id','name','color_code','plant')

@admin.register(Machines)
class MachineAdmin(ImportExportModelAdmin):
    list_display = ('id','name', 'plant','color_code')  


@admin.register(StoppageType)
class StoppageAdmin(ImportExportModelAdmin):
    list_display = ('id','name', 'is_active')  

@admin.register(Products)
class ProductsAdmin(ImportExportModelAdmin):
    list_display = ('id','name', 'plant') 

@admin.register(Department)
class DepartmentsAdmin(ImportExportModelAdmin):
    list_display = ('id','name', 'plant') 

@admin.register(Plant)
class PlantAdmin(ImportExportModelAdmin):
    list_display = ('id','plant_name', 'is_active')  

@admin.register(MachineTemperatures)
class MachineTemperaturesAdmin(ImportExportModelAdmin):
    list_display = ('machine', 'horizontal', 'teeth', 'coder', 'vertical', 'recorded_date_time', 'plant')


@admin.register(MachineParametersGraph)
class MachineParametersGraphAdmin(ImportExportModelAdmin):
    list_display = ('machine_parameter', 'params_count', 'recorded_date_time', 'plant')
    

@admin.register(MachineParameters)
class MachineParametersAdmin(ImportExportModelAdmin):
    list_display = ('parameter', 'color_code')


admin.site.register(AreaNotification)


@admin.register(SystemStatus)
class PlantAdmin(ImportExportModelAdmin):
    list_display = ('id','machine','plant', 'system_status')

@admin.register(Dashboard)
class DashboardAdmin(ImportExportModelAdmin):
    list_display = ('id','machines',"department","product","recorded_date_time","total_duration","shift")