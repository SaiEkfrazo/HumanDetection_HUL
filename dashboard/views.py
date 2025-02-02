from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import base64
import uuid
from django.core.files.base import ContentFile
import base64
import uuid
from django.conf import settings
from django.db.models import Max
from django.db.models.functions import Cast
from django.db.models import DateField
import os
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import connection
from datetime import datetime
from utils.digital_space import *
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import F
from django.db.models.functions import TruncDate
from django.db.models import Sum, Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import re
from django.core.files.storage import default_storage
from django.conf import settings
import os
from utils.custom_pagination import *
from django.db.models import Count
from datetime import timedelta, date
import re

# Create your views here.

CACHE_TIMEOUT = 300  # Cache timeout in seconds (1 minute)
CACHE_KEY = 'dashboard_data'


# import os
# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage
# import base64
# import uuid
# import re

class MachineAPIView(viewsets.ModelViewSet):
    queryset = Machines.objects.all()
    serializer_class = MachineSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=MachineSerializer,
        operation_summary="Create a Machine",
        responses={
            201: openapi.Response(description="Machine created successfully"),
            400: openapi.Response(description="Machine with this name already exists in this plant")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Machines.objects.filter(plant=plant, name=name).exists():
            return Response({'message': 'Machine with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({'message': 'Machine created successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=MachineSerializer,
        operation_summary="Update a Machine",
        responses={
            200: openapi.Response(description="Machine updated successfully"),
            400: openapi.Response(description="Machine with this name already exists in this plant")
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Machines.objects.exclude(id=instance.id).filter(plant=plant, name=name).exists():
            return Response({'message': 'Machine with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response({'message': 'Machine updated successfully'}, status=status.HTTP_200_OK)

    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='plant_name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter machines by plnat name'
            ),
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search machines by name'
            )
        ],
        operation_summary="List Machines",
        responses={200: MachineSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        plant_name = request.query_params.get('plant_name')
        search = request.query_params.get('key')
        queryset = self.get_queryset()

        if plant_name:
            plant_name = plant_name.strip()
            queryset = queryset.filter(plant__plant_name__icontains=plant_name)

        if search:
            search = search.strip()
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Machines list retrieved successfully', 'results': serializer.data})
    
    @swagger_auto_schema(
        operation_summary="Delete a Machine",
        responses={
            204: openapi.Response(description="Machine deleted successfully"),
            404: openapi.Response(description="Machine not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Machine deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class ProductAPIView(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ProductSerializers,
        operation_summary="Create an Alert",
        responses={
            201: openapi.Response(description="Alert created successfully"),
            400: openapi.Response(description="Alert with this name already exists in this plant")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Products.objects.filter(plant=plant, name=name).exists():
            return Response({'message': 'Alert with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({'message': 'Alert created successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=ProductSerializers,
        operation_summary="Update an Alert",
        responses={
            200: openapi.Response(description="Alert updated successfully"),
            400: openapi.Response(description="Alert with this name already exists in this plant")
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Products.objects.exclude(id=instance.id).filter(plant=plant, name=name).exists():
            return Response({'message': 'Alert with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response({'message': 'Alert updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='plant_name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter Products by plant name'
            ),
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search Products by name'
            )
        ],
        operation_summary="List Products",
        responses={200: ProductSerializers(many=True)}
    )
    def list(self, request, *args, **kwargs):
        plant_name = request.query_params.get('plant_name')
        search = request.query_params.get('key')
        queryset = self.get_queryset()

        if plant_name:
            plant_name = plant_name.strip()
            queryset = queryset.filter(plant__plant_name__icontains=plant_name)

        if search:
            search = search.strip()
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Machines list retrieved successfully', 'results': serializer.data})

    @swagger_auto_schema(
        operation_summary="Delete an Alert",
        responses={
            204: openapi.Response(description="Alert deleted successfully"),
            404: openapi.Response(description="Alert not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Alert deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class DepartmentAPIView(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=DepartmentSerializer,
        operation_summary="Create a Department",
        responses={
            201: openapi.Response(description="Department created successfully"),
            400: openapi.Response(description="Department with this name already exists in this plant")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Department.objects.filter(plant=plant, name=name).exists():
            return Response({'message': 'Department with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({'message': 'Department created successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=DepartmentSerializer,
        operation_summary="Update a Department",
        responses={
            200: openapi.Response(description="Department updated successfully"),
            400: openapi.Response(description="Department with this name already exists in this plant")
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Department.objects.exclude(id=instance.id).filter(plant=plant, name=name).exists():
            return Response({'message': 'Department with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response({'message': 'Department updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='plant_name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter departments by plant name'
            ),
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search departments by name'
            )
        ],
        operation_summary="List Departments",
        responses={200: DepartmentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        plant_name = request.query_params.get('plant_name')
        search = request.query_params.get('key')
        queryset = self.get_queryset()

        if plant_name:
            plant_name = plant_name.strip()
            queryset = queryset.filter(plant__plant_name__icontains=plant_name)

        if search:
            search = search.strip()
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Machines list retrieved successfully', 'results': serializer.data})

    @swagger_auto_schema(
        operation_summary="Delete a Department",
        responses={
            204: openapi.Response(description="Department deleted successfully"),
            404: openapi.Response(description="Department not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Department deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class AreaAPIView(viewsets.ModelViewSet):
    queryset = Areas.objects.all()
    serializer_class = AreasSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=AreasSerializers,
        operation_summary="Create a area",
        responses={
            201: openapi.Response(description="area created successfully"),
            400: openapi.Response(description="area with this name and color code already exists in this plant")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name').strip()
        color_code = serializer.validated_data.get('color_code').strip()

        if Areas.objects.filter(plant=plant, name=name).exists():
            return Response({'message': 'area with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        if Areas.objects.filter(plant=plant, color_code=color_code).exists():
            return Response({'message': 'area with this color code already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({'message': 'area created successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=AreasSerializers,
        operation_summary="Update a area",
        responses={
            200: openapi.Response(description="area updated successfully"),
            400: openapi.Response(description="area with this name and color code already exists in this plant")
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')
        color_code = serializer.validated_data.get('color_code')

        if Areas.objects.exclude(id=instance.id).filter(plant=plant, name=name, color_code=color_code).exists():
            return Response({'message': 'area with this name and color code already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response({'message': 'area updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='plant_name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter Areas by Plant name'
            ),
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search Areas by name'
            )
        ],
        operation_summary="List Areas",
        responses={200: AreasSerializers(many=True)}
    )
    def list(self, request, *args, **kwargs):
        plant_name = request.query_params.get('plant_name')
        search = request.query_params.get('key')
        queryset = self.get_queryset()

        if plant_name:
            plant_name = plant_name.strip()
            queryset = queryset.filter(plant__plant_name__icontains=plant_name)

        if search:
            search = search.strip()
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Machines list retrieved successfully', 'results': serializer.data})
    
    @swagger_auto_schema(
        operation_summary="Delete a area",
        responses={
            204: openapi.Response(description="area deleted successfully"),
            404: openapi.Response(description="area not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'area deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
####### Plant API View #######

class PlantAPIView(viewsets.ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        # manual_parameters=[
        # openapi.Parameter(
        #     name='organization_id',
        #     in_=openapi.IN_QUERY,
        #     type=openapi.TYPE_STRING,
        #     description='Give the Organization id to see all the plants in the organization'
        # )
        # ],
        operation_summary="List all Plants",
        responses={200: PlantSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        # organization_id = request.query_params.get('organization_id')
        # if not request.user.is_superuser:
        #     return Response({'message':'You are not allowed to view these.'}, status=status.HTTP_403_FORBIDDEN)
        # if organization_id:
        #     queryset = self.get_queryset().filter(organization_name_id=organization_id)
        # else:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Plants list retrieved successfully', 'results': serializer.data})
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            
            properties={
                'plant_name': openapi.Schema(type=openapi.TYPE_STRING),
                # 'organization_name': openapi.Schema(type=openapi.TYPE_INTEGER),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
            required=['is_active','plant_name']
        ),
        operation_summary="Create a Plant",

    )
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'message': 'Only superuser is permitted to create plant'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if a plant with the same name already exists
        plant_name = request.data.get('plant_name')
        if Plant.objects.filter(plant_name=plant_name).exists():
            return Response({'message': 'A plant with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': "Plant Created Successfully"}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_summary="Delete a Plant",
        operation_description="Delete a Plant based on its ID.",
        responses={204: "Plant deleted successfully"}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_superuser:
            return Response({'error': 'Only superuser is permitted to delete plant'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({'message': "Plant Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'plant_name': openapi.Schema(type=openapi.TYPE_STRING),
            # 'organization_name': openapi.Schema(type=openapi.TYPE_INTEGER),
            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
        },
        required=['is_active', 'plant_name']
    ),
    operation_summary="Update a Plant",
    responses={
        200: openapi.Response(
            description="Plant updated successfully",
            examples={
                "application/json": {
                    "message": "Plant updated successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad Request",
            examples={
                "application/json": {
                    "error": "A plant with the name already exists."
                }
            }
        )
    }
)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if the updated plant_name already exists
        plant_name = serializer.validated_data.get('plant_name')
        existing_plant = Plant.objects.exclude(id=instance.id).filter(plant_name=plant_name).first()
        if existing_plant:
            return Response({'error': f'A plant with the name "{plant_name}" already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response({'message': 'Plant updated successfully'}, status=status.HTTP_200_OK)

import os
from django.conf import settings
from django.core.files.storage import default_storage
import base64
import uuid
import re
from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache
from datetime import datetime, timedelta,time
from collections import defaultdict
from django.db import transaction

@method_decorator(csrf_exempt, name='dispatch')
class DashboardAPIView(viewsets.ModelViewSet):
    queryset = Khamgaon.objects.all()
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    MODEL_MAPPING = {
        1: Khamgaon,
        3: LiquidPlant,
        4: ShampooPlant,
    }

    @swagger_auto_schema(
        operation_summary="Create a Record",
        operation_description="Upload an image and store machine data",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'base64_image': openapi.Schema(type=openapi.TYPE_STRING, description='Base64 encoded image'),
                'machines_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Machine ID'),
                'areas_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Area ID'),
                'duration': openapi.Schema(type=openapi.TYPE_NUMBER, description='Duration in seconds'),
                'plant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Plant ID'),
                'recorded_date_time': openapi.Schema(type=openapi.TYPE_STRING, description='Recorded Date Time'),
                'type_of_stoppage': openapi.Schema(type=openapi.TYPE_INTEGER, description='Stoppage Type ID')  # Ensure this field is added

            },
            # required=['machines_id', 'areas_id', 'duration', 'plant_id', 'recorded_date_time']
        ),
        responses={
            201: openapi.Response(description="Record created successfully"),
            400: openapi.Response(description="Missing required fields or failed to upload image"),
            500: openapi.Response(description="Failed to save data")
        }
    )
    # @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     machines_id = request.data.get('machines_id', None)
    #     areas_id = request.data.get('areas_id', None)
    #     duration = request.data.get('duration', None)
    #     plant_id = request.data.get('plant_id', None)
    #     recorded_date_time = request.data.get('recorded_date_time', None)
    #     stoppage_type_id = request.data.get('type_of_stoppage', None)

    #     if not all([machines_id, areas_id, duration, plant_id, recorded_date_time, stoppage_type_id]):
    #         return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         # Determine the model to use based on the plant_id
    #         model = self.MODEL_MAPPING.get(plant_id)
    #         if not model:
    #             return Response({'error': 'Invalid plant_id provided.'}, status=status.HTTP_400_BAD_REQUEST)

    #         # Retrieve the StoppageType instance
    #         try:
    #             stoppage_type = StoppageType.objects.get(id=stoppage_type_id)
    #         except StoppageType.DoesNotExist:
    #             return Response({'error': 'Invalid type_of_stoppage ID provided.'}, status=status.HTTP_400_BAD_REQUEST)

    #         # Create a new record in the appropriate model (e.g., Khamgaon)
    #         record = model.objects.create(
    #             machines_id=machines_id,
    #             areas_id=areas_id,
    #             duration=duration,
    #             plant_id=plant_id,
    #             recorded_date_time=recorded_date_time,
    #             type_of_stoppage=stoppage_type
    #         )

    #         # Extract just the date from recorded_date_time for Dashboard entry
    #         recorded_date = recorded_date_time.split('T')[0]

    #         # Update or create the record in the Dashboard table
    #         dashboard_entry, created = Dashboard.objects.get_or_create(
    #             machines_id=machines_id,
    #             areas_id=areas_id,
    #             plant_id=plant_id,
    #             recorded_date_time=recorded_date,
    #             type_of_stoppage=stoppage_type,
    #             defaults={'total_duration': duration}
    #         )

    #         if not created:
    #             # If the record already exists, update the total_duration
    #             dashboard_entry.total_duration += duration
    #             dashboard_entry.save()

    #         return Response({'message': 'Record created successfully'}, status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         return Response({'error': f'Failed to save data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        machines_id = request.data.get('machines_id', None)
        areas_id = request.data.get('areas_id', None)
        duration = request.data.get('duration', None)
        plant_id = request.data.get('plant_id', None)
        recorded_date_time = request.data.get('recorded_date_time', None)
        stoppage_type_id = request.data.get('type_of_stoppage', None)

        if not all([machines_id, areas_id, duration, plant_id, recorded_date_time, stoppage_type_id]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Determine the model to use based on the plant_id
            model = self.MODEL_MAPPING.get(plant_id)
            if not model:
                return Response({'error': 'Invalid plant_id provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the StoppageType instance
            try:
                stoppage_type = StoppageType.objects.get(id=stoppage_type_id)
            except StoppageType.DoesNotExist:
                return Response({'error': 'Invalid type_of_stoppage ID provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # Parse recorded_date_time to extract date and time
            try:
                date_str, time_str = recorded_date_time.split('T')
                record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                record_time = datetime.strptime(time_str, '%H:%M:%S').time()
            except ValueError:
                return Response({'error': 'Invalid recorded_date_time format. Use YYYY-MM-DDTHH:MM:SS.'}, status=status.HTTP_400_BAD_REQUEST)

            # Define shift time ranges
            shifts = {
                'shift1': (time(23, 0), time(7, 0)),
                'shift2': (time(7, 0), time(15, 0)),
                'shift3': (time(15, 0), time(23, 0)),
            }

            # Determine the shift
            shift = None
            for shift_name, (start_time, end_time) in shifts.items():
                if start_time > end_time:  # Shift spans midnight
                    if (record_time >= start_time) or (record_time < end_time):
                        shift = shift_name
                        break
                else:
                    if (record_time >= start_time) and (record_time < end_time):
                        shift = shift_name
                        break

            if not shift:
                return Response({'error': 'Unable to determine shift for the provided recorded_date_time.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new record in the appropriate model (e.g., Khamgaon)
            record = model.objects.create(
                machines_id=machines_id,
                areas_id=areas_id,
                duration=duration,
                plant_id=plant_id,
                recorded_date_time=recorded_date_time,
                type_of_stoppage=stoppage_type,
                shift=shift
            )

            # Extract just the date from recorded_date_time for Dashboard entry
            recorded_date = date_str

            # Update or create the record in the Dashboard table
            dashboard_entry, created = Dashboard.objects.get_or_create(
                machines_id=machines_id,
                areas_id=areas_id,
                plant_id=plant_id,
                recorded_date_time=recorded_date,
                type_of_stoppage=stoppage_type,
                shift=shift,
                defaults={'total_duration': duration}
            )

            if not created:
                # If the record already exists, update the total_duration
                dashboard_entry.total_duration += duration
                dashboard_entry.save()

            return Response({'message': 'Record created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Failed to save data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('from_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        openapi.Parameter('to_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        openapi.Parameter('machine_id', openapi.IN_QUERY, description="Machine ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('department_id', openapi.IN_QUERY, description="Department ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('product_id', openapi.IN_QUERY, description="Product ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('area', openapi.IN_QUERY, description="Area ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('type_of_stoppage', openapi.IN_QUERY, description="Stoppage ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('shift', openapi.IN_QUERY, description="shift1,shift2,shift3", type=openapi.TYPE_STRING),

    ],
    operation_description="List area counts for a specific plant within the specified date range and filters",
    responses={
        200: openapi.Response(description="Records retrieved successfully"),
        400: openapi.Response(description="Missing or invalid parameters"),
        404: openapi.Response(description="Plant not found"),
        500: openapi.Response(description="Failed to retrieve records")
    },
    operation_summary="Dashboard Data"
    )
    def list(self, request, *args, **kwargs):
        plant_id = request.query_params.get('plant_id')
        from_date_str = request.query_params.get('from_date')
        to_date_str = request.query_params.get('to_date')
        machine_id = request.query_params.get('machine_id')
        department_id = request.query_params.get('department_id')
        product_id = request.query_params.get('product_id')
        area_id = request.query_params.get('area')
        stoppage_type = request.query_params.get('type_of_stoppage')
        shift = request.query_params.get('shift')  # Added shift filter

        if not plant_id:
            return Response({"message": "plant_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant_id = int(plant_id)
        except ValueError:
            return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
            if from_date and to_date and from_date > to_date:
                return Response({"message": "from_date cannot be after to_date."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"message": "Invalid date format provided. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if any filters are applied
        filters_applied = bool(machine_id or department_id or product_id or area_id or from_date or to_date or stoppage_type or shift)

        if not filters_applied:
            cache_key = f'{CACHE_KEY}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data, status=status.HTTP_200_OK)

        filter_criteria = {'plant_id': plant_id}
        if machine_id:
            filter_criteria['machines_id'] = machine_id
        if department_id:
            filter_criteria['department_id'] = department_id
        if product_id:
            filter_criteria['product_id'] = product_id
        if area_id:
            filter_criteria['areas_id'] = area_id
        if stoppage_type:
            filter_criteria['type_of_stoppage__id'] = stoppage_type
        if shift:
            filter_criteria['shift'] = shift  # Added shift filter

        queryset = Dashboard.objects.filter(**filter_criteria)
        response_data = {}
        areas_set = set()

        for record in queryset:
            if not record.recorded_date_time:
                continue

            try:
                record_date_str = record.recorded_date_time.split('T')[0]
                date = datetime.strptime(record_date_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            if (not from_date or from_date <= date) and (not to_date or date <= to_date):
                try:
                    area = Areas.objects.get(id=record.areas_id)
                    area_name = area.name
                except Areas.DoesNotExist:
                    area_name = None

                if area_name:
                    areas_set.add(area_name)

                if str(date) not in response_data:
                    response_data[str(date)] = {'total_duration': 0}

                if area_name not in response_data[str(date)]:
                    response_data[str(date)][area_name] = 0

                # Convert the duration from seconds to minutes and add to the total
                duration_in_minutes = record.total_duration  # Convert to minutes
                response_data[str(date)][area_name] += duration_in_minutes
                response_data[str(date)]['total_duration'] += duration_in_minutes

        response_data['areas'] = list(areas_set)

        # Cache the response data if no filters are applied
        if not filters_applied:
            cache.set(cache_key, response_data, timeout=CACHE_TIMEOUT)

        return Response(response_data, status=status.HTTP_200_OK)



@method_decorator(csrf_exempt, name='dispatch')
class ReportsAPIView(viewsets.ViewSet):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    MODEL_MAPPING = {
        1: Khamgaon,
        3: LiquidPlant,
        4: ShampooPlant,
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('from_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('to_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('machine_id', openapi.IN_QUERY, description="Machine ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('department_id', openapi.IN_QUERY, description="Department ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('product_id', openapi.IN_QUERY, description="Product ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('area', openapi.IN_QUERY, description="area", type=openapi.TYPE_INTEGER),
            openapi.Parameter('type_of_stoppage', openapi.IN_QUERY, description="Stoppage Id", type=openapi.TYPE_INTEGER),

        ],
        operation_description="List area counts for a specific plant within the specified date range and filters",
        responses={
            200: openapi.Response(description="Records retrieved successfully"),
            400: openapi.Response(description="Missing or invalid parameters"),
            404: openapi.Response(description="Plant not found"),
            500: openapi.Response(description="Failed to retrieve records")
        },
        operation_summary="Reports Data"
    )
    def list(self, request, *args, **kwargs):
        plant_id = request.query_params.get('plant_id', None)
        from_date_str = request.query_params.get('from_date', None)
        to_date_str = request.query_params.get('to_date', None)
        machine_id = request.query_params.get('machine_id', None)
        department_id = request.query_params.get('department_id', None)
        product_id = request.query_params.get('product_id', None)
        area_id = request.query_params.get('area', None)
        stoppage_type = request.query_params.get("type_of_stoppage", None)
        
        if not plant_id:
            return Response({"message": "plant_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant_id = int(plant_id)
        except ValueError:
            return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

        model = self.MODEL_MAPPING.get(plant_id)
        if not model:
            return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Prepare filter criteria
            filter_criteria = {}

            if machine_id:
                filter_criteria['machines__id'] = machine_id

            if department_id:
                filter_criteria['department__id'] = department_id

            if product_id:
                filter_criteria['product__id'] = product_id

            if area_id:
                filter_criteria['areas__id'] = area_id

            if stoppage_type:
                filter_criteria['type_of_stoppage__id'] = stoppage_type

            # Apply date range filters
            queryset = model.objects.filter(**filter_criteria)

            if from_date_str:
                queryset = queryset.filter(recorded_date_time__gte=f"{from_date_str}T00:00:00")

            if to_date_str:
                queryset = queryset.filter(recorded_date_time__lte=f"{to_date_str}T23:59:59")

            # Order by recorded_date_time in descending order to get latest records first
            queryset = queryset.order_by('-recorded_date_time')

            # Pagination
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            # Serialize paginated queryset to return all fields
            response_data = []
            for record in paginated_queryset:
                # Fetch related names
                machine_name = Machines.objects.get(id=record.machines_id).name if record.machines_id else None
                department_name = Department.objects.get(id=record.department_id).name if record.department_id else None
                product_name = Products.objects.get(id=record.product_id).name if record.product_id else None
                area_name = Areas.objects.get(id=record.areas_id).name if record.areas_id else None
                plant_name = model.__name__

                # Convert type_of_stoppage to its name
                type_of_stoppage_name = StoppageType.objects.get(id=record.type_of_stoppage_id).name if record.type_of_stoppage_id else None

                serialized_data = {
                    'id': record.id,
                    'machine': machine_name,
                    'department': department_name,
                    'product': product_name,
                    'area': area_name,
                    'image': record.image,
                    'plant': plant_name,
                    'recorded_date_time': record.recorded_date_time,
                    'downtime': record.duration,
                    'type_of_stoppage': type_of_stoppage_name
                }
                response_data.append(serialized_data)

            return paginator.get_paginated_response(response_data)

        except Exception as e:
            return Response({"message": f"Failed to retrieve records: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AISmartAPIView(viewsets.ViewSet):
    MODEL_MAPPING = {
        2: Khamgaon,
        3: LiquidPlant,
        4: ShampooPlant,
    }
    pagination_class = CustomPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('area_id', openapi.IN_QUERY, description="area ID", type=openapi.TYPE_INTEGER),
        ],
        operation_description="List area counts for a specific plant within the specified date range and filters",
        responses={
            200: openapi.Response(description="Records retrieved successfully"),
            400: openapi.Response(description="Missing or invalid parameters"),
            404: openapi.Response(description="Plant not found"),
            500: openapi.Response(description="Failed to retrieve records")
        },
        operation_summary="AI Smart View"
    )
    def list(self, request):
        plant_id = request.query_params.get('plant_id')
        area_id = request.query_params.get('area_id')

        if not plant_id or not area_id:
            return Response({'error': 'plant_id and area_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant_id = int(plant_id)
            area_id = int(area_id)
        except ValueError:
            return Response({'error': 'plant_id and area_id must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        model = self.MODEL_MAPPING.get(plant_id)
        if not model:
            return Response({'error': 'Invalid plant_id provided.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = model.objects.filter(areas_id=area_id).select_related('machines').order_by('-recorded_date_time').values('image', 'recorded_date_time', 'machines__name')

        # Apply pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Rename 'machines__name' to 'machine_name' in the result
        results = [
            {
                'image': record['image'],
                'recorded_date_time': record['recorded_date_time'],
                'machine_name': record['machines__name']
            }
            for record in paginated_queryset
        ]

        return paginator.get_paginated_response(results)
    

class MachineTemperaturesAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: MachineTemperaturesSerializer(many=True)},
    )
    def get(self, request):
        try:
            plant_id = request.query_params.get('plant_id')
            if plant_id:
                machine_ids = MachineTemperatures.objects.filter(plant_id=plant_id).values_list('machine_id', flat=True).distinct()
            else:
                machine_ids = MachineTemperatures.objects.values_list('machine_id', flat=True).distinct()

            latest_records = []
            for machine_id in machine_ids:
                if plant_id:
                    latest_record = MachineTemperatures.objects.filter(machine_id=machine_id, plant_id=plant_id).latest('recorded_date_time')
                else:
                    latest_record = MachineTemperatures.objects.filter(machine_id=machine_id).latest('recorded_date_time')

                serializer = MachineTemperaturesSerializer(latest_record)
                latest_records.append(serializer.data)

            return Response(latest_records)
        except MachineTemperatures.DoesNotExist:
            return Response({"message": "No machine records found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=MachineTemperaturesSerializer, responses={201: MachineTemperaturesSerializer})
    def post(self, request):
        serializer = MachineTemperaturesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MachineTemperatureGraphView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('machine_id', openapi.IN_QUERY, description="Machine ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: MachineTemperaturesSerializer(many=True)},
    )
    def get(self, request):
        machine_id = request.query_params.get('machine_id')
        plant_id = request.query_params.get('plant_id')

        filters = {}
        if machine_id:
            filters['machine_id'] = machine_id
        if plant_id:
            filters['plant_id'] = plant_id

        all_records = MachineTemperatures.objects.filter(**filters)

        serializer = MachineTemperaturesSerializer(all_records, many=True)
        return Response(serializer.data)


class MachineParametersGraphView(APIView):
    def get_date_only(self, date_time_str):
        date_time = datetime.fromisoformat(date_time_str)
        date_only = date_time.date()
        date_only_str = date_only.isoformat()
        return date_only_str

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: openapi.Response(description="Machine Parameters Graph", examples={
            "application/json": [
                {
                    "date_time": "2024-06-13",
                    "area_percentage": 10.5
                },
                {
                    "date_time": "2024-06-14",
                    "area_percentage": 20.0
                }
            ]
        })}
    )
    def get(self, request):
        plant_id = request.query_params.get('plant_id')

        filters = {}
        if plant_id:
            filters['plant_id'] = plant_id

        # Filter the queryset based on the plant_id only
        parameters_graph = MachineParametersGraph.objects.filter(**filters)
        
        # Aggregating counts per day
        date_aggregates = defaultdict(lambda: {'area_count': 0, 'total_production_count': 0})
        
        for graph in parameters_graph:
            date_only_str = graph.recorded_date_time[:10]  # Extracting date part
            if graph.machine_parameter.parameter == "Reject Counter":
                date_aggregates[date_only_str]['area_count'] += int(graph.params_count)
            elif graph.machine_parameter.parameter in ["Program Counter", "Machine Counter"]:
                date_aggregates[date_only_str]['total_production_count'] += int(graph.params_count)
        
        data = []
        for date_only_str, counts in date_aggregates.items():
            area_count = counts['area_count']
            total_production_count = counts['total_production_count']
            
            if total_production_count > 0:
                area_percentage = (area_count / total_production_count) * 1000000
            else:
                area_percentage = 0
            
            data.append({
                "date_time": date_only_str,
                "area_percentage": round(area_percentage, 2)
            })

        # Order the data by date
        data = sorted(data, key=lambda x: datetime.fromisoformat(x['date_time']))

        return Response({"results": data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['params_count', 'recorded_date_time', 'parameter', 'plant_id'],
        properties={
            'params_count': openapi.Schema(type=openapi.TYPE_STRING, description='Parameters count'),
            'recorded_date_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Recorded date and time'),
            'parameter': openapi.Schema(type=openapi.TYPE_INTEGER, description='Parameter ID'),
            'plant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Plant ID'),
        },
    ), responses={201: 'Created', 400: 'Bad Request', 404: 'Not Found'})

    def post(self, request):
        # Extract relevant data from the request and create or update a MachineParametersGraph object
        params_count = request.data.get('params_count')
        print('here')
        date_time_str = request.data.get('recorded_date_time')
        parameter_id = request.data.get('parameter')  # Assuming parameter_id is provided
        plant_id = request.data.get('plant_id')

        try:
            # Fetch the MachineParameters instance corresponding to the provided parameter_id
            parameter = MachineParameters.objects.get(pk=parameter_id)
            # Convert the given date_time to date only
            date_only_str = self.get_date_only(date_time_str)
            
            # Retrieve the existing record with the same date and parameter
            existing_graph = MachineParametersGraph.objects.filter(
                recorded_date_time__startswith=date_only_str, 
                machine_parameter=parameter,
                plant_id=plant_id
            ).first()

            if existing_graph:
                print('existing',existing_graph)
                # Update the existing record's params_count by adding the new value to the existing value
                existing_graph.params_count = F('params_count') + int(params_count)
                existing_graph.save(update_fields=['params_count'])  # Ensure that the field is updated in the database
                return Response({'message': 'MachineParametersGraph updated successfully'}, status=status.HTTP_200_OK)
            else:
                # Create a new MachineParametersGraph object
                graph = MachineParametersGraph.objects.create(
                    machine_parameter=parameter,
                    params_count=params_count,
                    recorded_date_time=date_time_str,
                    plant_id=plant_id
                )
                return Response({'message': 'MachineParametersGraph created successfully'}, status=status.HTTP_201_CREATED)
        except MachineParameters.DoesNotExist:
            return Response({'error': 'MachineParameters not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class AreaNotificationAPIView(viewsets.ViewSet):
    queryset = AreaNotification.objects.all()
    serializer_class = DefectNotificationSerializer

    @swagger_auto_schema(
        operation_summary='List All Notifications',
        manual_parameters=[
            openapi.Parameter(
                'plant_id',
                openapi.IN_QUERY,
                description="ID of the plant to filter notifications",
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    def list(self, request):
        plant_id = request.query_params.get('plant_id')
        if plant_id:
            queryset = self.queryset.filter(plant_id=plant_id).order_by('-recorded_date_time')
        else:
            queryset = self.queryset.none()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'results': serializer.data})



######### System status api ###########


class SystemStatusAPIView(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_description="Update the system status of a machine for a given plant.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'machine_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the machine'),
                'plant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the plant'),
                'system_status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='System status to set'),
            },
            required=['machine_id', 'plant_id', 'system_status']
        ),
        responses={
            200: SystemStatusSerializer,
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def create(self, request, *args, **kwargs):
        machine_id = request.data.get('machine_id')
        plant_id = request.data.get('plant_id')
        system_status_value = request.data.get('system_status')

        if not machine_id or not plant_id or system_status_value is None:
            return Response({'message': 'Machine ID, Plant ID, and System Status are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            machine = Machines.objects.get(id=machine_id)
            plant = Plant.objects.get(id=plant_id)
        except Machines.DoesNotExist:
            return Response({'message': 'Machine not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Plant.DoesNotExist:
            return Response({'message': 'Plant not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the SystemStatus record exists
        system_status, created = SystemStatus.objects.get_or_create(
            machine=machine,
            plant=plant,
            defaults={'system_status': system_status_value}  # Set the initial status if the record is created
        )

        if not created:
            # Update the system status if the record already exists
            system_status.system_status = system_status_value
            system_status.save()

        serializer = SystemStatusSerializer(system_status)
        return Response({"message":"System status updated successfully."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Retrieve system statuses for a specific plant based on plant_id.",
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="ID of the plant", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(
                description="System statuses retrieved successfully",
                schema=SystemStatusSerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "machine": 1,
                            "plant": 1,
                            "system_status": True
                        },
                        {
                            "machine": 2,
                            "plant": 1,
                            "system_status": False
                        }
                    ]
                }
            ),
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def list(self, request):
        plant_id = request.query_params.get('plant_id')

        if not plant_id:
            return Response({'message': 'plant_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({'message': 'Plant not found.'}, status=status.HTTP_404_NOT_FOUND)

        system_statuses = SystemStatus.objects.filter(plant=plant).select_related('machine')
        serializer = SystemStatusSerializer(system_statuses, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)



class StoppageAPIView(viewsets.ViewSet):
    queryset = StoppageType.objects.all()
    serializer_class = StoppageSerializer
    def list(self,request):
        serializer = StoppageSerializer(self.queryset,many=True)
        
        return Response({'results':serializer.data},status = status.HTTP_200_OK)
    
class StoppageGraphAPIView(viewsets.ViewSet):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Aggregated stoppage data by shifts and date",
                examples={
                    "application/json": {
                        "2024-08-13": {
                            "shift1": {
                                "major": 302,
                                "minor": 230
                            },
                            "shift2": {
                                "major": 150,
                                "minor": 120
                            },
                            "shift3": {
                                "major": 250,
                                "minor": 180
                            }
                        }
                    }
                }
            )
        }
    )
    def list(self, request):
        # Get all records
        records = Khamgaon.objects.all()
        
        # Initialize data structure
        data = defaultdict(lambda: {
            'shift1': {'major': 0, 'minor': 0},
            'shift2': {'major': 0, 'minor': 0},
            'shift3': {'major': 0, 'minor': 0}
        })

        # Helper function to determine shift based on time
        def get_shift(recorded_datetime):
            try:
                hour = int(recorded_datetime.split('T')[1].split(':')[0])
            except (IndexError, ValueError):
                print(f"Error extracting hour from {recorded_datetime}")
                return None
            if 23 <= hour or hour < 7:
                return 'shift1'
            elif 7 <= hour < 15:
                return 'shift2'
            elif 15 <= hour < 23:
                return 'shift3'
            return None

        # Process each record
        for record in records:
            date_key = record.recorded_date_time.split('T')[0]
            shift = get_shift(record.recorded_date_time)
            if shift:
                stoppage_type = record.type_of_stoppage
                if stoppage_type:
                    stoppage_counts = data[date_key][shift]
                    duration = record.duration if record.duration else 0
                    print(f"Processing record: date={date_key}, shift={shift}, stoppage_type={stoppage_type.name}, duration={duration}")
                    if stoppage_type.name == 'Major':
                        stoppage_counts['major'] += duration
                    elif stoppage_type.name == 'Minor':
                        stoppage_counts['minor'] += duration

        # Convert defaultdict to dict
        formatted_data = dict(data)
        print('Formatted data:', formatted_data)

        return Response(formatted_data, status=status.HTTP_200_OK)
    

class DownTimeAnalysisViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_summary="List downtime analysis records",
        operation_description="Retrieve a list of downtime analysis records with optional filters and pagination.",
        manual_parameters=[
            openapi.Parameter(
                'from_date',
                openapi.IN_QUERY,
                description="Start date for filtering records (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'to_date',
                openapi.IN_QUERY,
                description="End date for filtering records (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'areas',
                openapi.IN_QUERY,
                description="Filter by area ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                'gate',
                openapi.IN_QUERY,
                description="Filter by gate",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of downtime analysis records",
                examples={
                    'application/json': [
                        {
                            "id": 1,
                            "machine_stop_time": "2024-09-01T10:00:00",
                            "machine_stop_duration": "120",
                            "gate": "Gate 1",
                            "gate_open_duration": "15",
                            "area_duration": "45",
                            "area_name": "Area A"
                        },
                        # More example entries
                    ]
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    'application/json': {
                        "detail": "Bad request"
                    }
                }
            )
        }
    )
    def list(self, request):
        queryset = DownTimeAnalysis.objects.all()
        
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        area_id = request.query_params.get('areas')
        gate = request.query_params.get('gate')

        if from_date:
            queryset = queryset.filter(machine_stop_time__gte=f"{from_date}T00:00:00")
        if to_date:
            queryset = queryset.filter(machine_stop_time__lte=f"{to_date}T23:59:00")

        if area_id:
            queryset = queryset.filter(areas__id=area_id)
        
        if gate:
            queryset = queryset.filter(gate=gate)
        
        # Order by the latest machine_stop_time
        queryset = queryset.order_by('-machine_stop_time')
        
        # Apply pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Process results to include area_name
        results = []
        for item in paginated_queryset:
            data = {
                'id': item.id,
                'machine_stop_time': item.machine_stop_time,
                'machine_stop_duration': item.machine_stop_duration,
                'gate': item.gate,
                'gate_open_duration': item.gate_open_duration,
                'area_duration': item.area_duration,
                'area_name': item.areas.name if item.areas else None,  # Include area_name here
            }
            results.append(data)
        
        return paginator.get_paginated_response(results)

    @swagger_auto_schema(
        operation_summary="Create a new downtime analysis record",
        operation_description="Create a new downtime analysis record with the provided data.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'machine_stop_time': openapi.Schema(type=openapi.TYPE_STRING, description='Time when the machine stopped'),
                'machine_stop_duration': openapi.Schema(type=openapi.TYPE_STRING, description='Duration the machine was stopped'),
                'gate': openapi.Schema(type=openapi.TYPE_STRING, description='Gate identifier'),
                'gate_open_duration': openapi.Schema(type=openapi.TYPE_STRING, description='Duration the gate was open'),
                'areas': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the area where the downtime occurred'),
                'area_duration': openapi.Schema(type=openapi.TYPE_STRING, description='Duration of the downtime in the area')
            },
            required=['gate_open_duration'],  # Required fields
        ),
        responses={
            201: openapi.Response(
                description="Record created successfully",
                examples={
                    'application/json': {
                        "message": "Record Created Successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    'application/json': {
                        "detail": "Invalid data provided."
                    }
                }
            )
        }
    )
    def create(self, request):
        serializer = DownTimeAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Record Created Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.db import connection
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime, time as dt_time

class DownTimeAnalysisAggregatedViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_summary="Get aggregated downtime analysis data",
        operation_description="Retrieve aggregated downtime analysis data with optional filters.",
        manual_parameters=[
            openapi.Parameter(
                'from_date',
                openapi.IN_QUERY,
                description="Start date for filtering results (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'to_date',
                openapi.IN_QUERY,
                description="End date for filtering results (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'areas',
                openapi.IN_QUERY,
                description="Filter by area ID",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'gate',
                openapi.IN_QUERY,
                description="Filter by gate",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'shift',
                openapi.IN_QUERY,
                description="Filter by shift (shift1, shift2, shift3)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="Aggregated downtime analysis data",
                examples={
                    'application/json': {
                        "results": [
                            {
                                "date": "2024-08-27",
                                "total_max_machine_stop_duration": 120.0,
                                "total_max_gate_open_duration": 80.0,
                                "total_max_area_duration": 50.0
                            },
                            {
                                "date": "2024-08-28",
                                "total_max_machine_stop_duration": 90.0,
                                "total_max_gate_open_duration": 60.0,
                                "total_max_area_duration": 40.0
                            }
                            # More example entries
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    'application/json': {
                        "message": "Invalid date format provided. Use YYYY-MM-DD."
                    }
                }
            )
        }
    )
    def list(self, request):
        from_date_str = request.query_params.get('from_date')
        to_date_str = request.query_params.get('to_date')
        area_id = request.query_params.get('areas')
        gate = request.query_params.get('gate')
        shift = request.query_params.get('shift')

        # Validate dates
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
            if from_date and to_date and from_date > to_date:
                return Response({"message": "from_date cannot be after to_date."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"message": "Invalid date format provided. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Define shift times
        shifts = {
            'shift1': (dt_time(23, 0), dt_time(7, 0)),
            'shift2': (dt_time(7, 0), dt_time(15, 0)),
            'shift3': (dt_time(15, 0), dt_time(23, 0)),
        }

        # Base query
        query = """
        WITH MaxDurations AS (
            SELECT
                DATE(SUBSTRING(machine_stop_time, 1, 10)) AS date,
                MAX(CAST(SUBSTRING(machine_stop_duration, 1, LENGTH(machine_stop_duration)) AS UNSIGNED)) AS max_machine_stop_duration,
                MAX(CAST(SUBSTRING(gate_open_duration, 1, LENGTH(gate_open_duration)) AS UNSIGNED)) AS max_gate_open_duration,
                MAX(CAST(SUBSTRING(area_duration, 1, LENGTH(area_duration)) AS UNSIGNED)) AS max_area_duration
            FROM
                DownTimeAnalysis
            WHERE
                TRUE
        """

        # Add date filters
        if from_date:
            query += " AND DATE(SUBSTRING(machine_stop_time, 1, 10)) >= %s"
        if to_date:
            query += " AND DATE(SUBSTRING(machine_stop_time, 1, 10)) <= %s"

        # Add area filter
        if area_id:
            query += " AND areas_id = %s"

        # Add gate filter
        if gate:
            query += " AND gate = %s"

        # Add shift filter
        if shift and shift in shifts:
            shift_start, shift_end = shifts[shift]

            # Shift spans midnight, so handle in two parts
            if shift_start > shift_end:
                query += """
                AND (
                    (TIME(SUBSTRING(machine_stop_time, 12, 8)) BETWEEN %s AND '23:59:59')
                    OR
                    (TIME(SUBSTRING(machine_stop_time, 12, 8)) BETWEEN '00:00:00' AND %s)
                )
                """
            else:
                query += " AND TIME(SUBSTRING(machine_stop_time, 12, 8)) BETWEEN %s AND %s"

        query += """
            GROUP BY
                DATE(SUBSTRING(machine_stop_time, 1, 10)), SUBSTRING(machine_stop_time, 1, 19)
        )
        SELECT
            date,
            SUM(max_machine_stop_duration) AS total_max_machine_stop_duration,
            SUM(max_gate_open_duration) AS total_max_gate_open_duration,
            SUM(max_area_duration) AS total_max_area_duration
        FROM
            MaxDurations
        GROUP BY
            date;
        """

        # Prepare parameters for query
        params = []
        if from_date:
            params.append(from_date)
        if to_date:
            params.append(to_date)
        if area_id:
            params.append(area_id)
        if gate:
            params.append(gate)
        if shift and shift in shifts:
            shift_start, shift_end = shifts[shift]
            params.append(shift_start.strftime('%H:%M:%S'))
            if shift_start > shift_end:  # For shifts spanning midnight
                params.append(shift_end.strftime('%H:%M:%S'))
            else:
                params.append(shift_end.strftime('%H:%M:%S'))

        # Print the SQL query with parameters for debugging
        from django.db.backends.utils import truncate_name
        import re

        def substitute_params(query, params):
            """ Substitute parameters into the query for debugging. """
            param_iter = iter(params)
            def replace_placeholder(match):
                return str(next(param_iter))
            return re.sub(r'%s', replace_placeholder, query)

        print("SQL Query with values:", substitute_params(query, params))

        # Execute query
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        # Format results
        results = [
            {
                "date": row[0].strftime('%Y-%m-%d'),
                "total_max_machine_stop_duration": row[1],
                "total_max_gate_open_duration": row[2],
                "total_max_area_duration": row[3]
            }
            for row in rows
        ]

        return Response({"results": results}, status=status.HTTP_200_OK)
        