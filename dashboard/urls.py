from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from .delete_images import DeleteRecordsByDateAPIView

router = DefaultRouter()
# router.register('designation', DesignationAPIView, basename='Designation')
# router.register('organization',OrganizationAPIView,basename='Organization')
router.register('plant', PlantAPIView, basename='plant')
###### object detection urls #######
router.register('machine',MachineAPIView,basename='Machines')
router.register('product',ProductAPIView,basename='Products')
router.register('department',DepartmentAPIView,basename='Department')
router.register('area',AreaAPIView,basename='Defect')
router.register('dashboard',DashboardAPIView,basename='Dashboard')
router.register('reports',ReportsAPIView,basename='Reports')
router.register('ai-smart',AISmartAPIView,basename='AISmartView')
router.register('area-notifications',AreaNotificationAPIView,basename="Defect Notifications")
router.register('system-status',SystemStatusAPIView,basename="System Status")
router.register('stoppage',StoppageAPIView,basename='Stoppage')
router.register('stoppage-graph',StoppageGraphAPIView,basename='StoppageGraph')
router.register('downtime-analysis', DownTimeAnalysisViewSet, basename='downtime-analysis')
router.register('downtime-graph',DownTimeAnalysisAggregatedViewSet,basename='downtimegraph')
# router.register('defct-vs-machine', DefectVSProduction, basename='plant-data')

urlpatterns= [
    # path('dashboard/',CreateDashboardAPIView.as_view(),name='CreateDashboard'),
    # path('reports/',ReportsAPIView.as_view(),name='Reports'),
    # path('dashboard/',DashboardAPIView.as_view(),name='Dashboard'),
    path('dashboard/<int:plant_id>/<int:pk>/', DashboardAPIView.as_view({'delete': 'destroy'}), name='dashboard-detail'),
    path('machine_temprature/',MachineTemperaturesAPIView.as_view(),name='Machine Temperature'),
    path('machine_temp_graph/',MachineTemperatureGraphView.as_view(),name='MachineGraph'),
    path('params_graph/',MachineParametersGraphView.as_view(),name='machineparametersgraph'),
    path('', include(router.urls)),
    path('delete_by_date/',DeleteRecordsByDateAPIView.as_view())
]