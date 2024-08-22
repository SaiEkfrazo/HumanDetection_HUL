from django.db import models

class Plant(models.Model):
    class Meta:
        db_table = 'Plant'
    
    plant_name = models.CharField('Plant',max_length=100,blank=False,null=False,unique=True)
    # organization_name = models.ForeignKey(Organization,on_delete=models.CASCADE,null=False,blank=False)
    is_active = models.BooleanField('Is Active',default=True)

    def __str___(self):
        return self.plant_name if self.plant_name else ""

######### Object detection tables ###############

class Machines(models.Model):
    class Meta:
        db_table = 'Machines'
    name = models.CharField(max_length=100,blank=False,null=False)
    # organization = models.ForeignKey(Organization,on_delete=models.SET_NULL,blank=True,null=True)
    plant = models.ForeignKey(Plant,blank=True,on_delete=models.SET_NULL,null=True)
    color_code = models.CharField(max_length=100,blank=True,null=True)
    def __str__(self):
        return self.name if self.name else ""
    
class Areas(models.Model):
    class Meta:
        db_table = 'Areas'
    name = models.CharField(max_length=100,blank=False,null=False)
    color_code = models.CharField(max_length=100,blank=False,null=False)
    # organization = models.ForeignKey(Organization,on_delete=models.SET_NULL,blank=True,null=True)
    plant = models.ForeignKey(Plant,blank=True,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.name if self.name else ""
    
class Products(models.Model):  ##### Alerts Changed into Products ######
    class Meta:
        db_table = 'Products'
    name = models.CharField(max_length=100,blank=False,null=False)
    # organization = models.ForeignKey(Organization,on_delete=models.SET_NULL,blank=True,null=True)
    plant = models.ForeignKey(Plant,blank=True,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.name if self.name else ""
    

class Department(models.Model):
    class Meta:
        db_table = 'Department'
    name = models.CharField(max_length=100,blank=False,null=False)
    # organization = models.ForeignKey(Organization,on_delete=models.CASCADE,blank=True,null=True)
    plant = models.ForeignKey(Plant,blank=True,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name if self.name else ""

class StoppageType(models.Model):
    class Meta:
        db_table = 'Stoppage'
    name = models.CharField(max_length=100,blank=True,null=True)
    is_active = models.BooleanField(default=True)

class Khamgaon(models.Model): ### For human detection ###
    class Meta:
        db_table = 'Khamgaon'

    machines = models.ForeignKey(Machines,on_delete=models.CASCADE,null=True,blank=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey(Products,on_delete=models.CASCADE,null=True,blank=True)
    areas = models.ForeignKey(Areas,on_delete=models.CASCADE,blank=True,null=True)
    image = models.CharField(max_length=250,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,blank=True,null=True)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)
    duration = models.FloatField(null=True,blank=True)
    type_of_stoppage = models.ForeignKey(StoppageType,on_delete=models.CASCADE,null=True,blank=True)

class LiquidPlant(models.Model): # liquid means comfort sachet plant
    class Meta:
        db_table = 'LiquidPlant'

    machines = models.ForeignKey(Machines,on_delete=models.CASCADE,null=False,blank=False)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=False,blank=False)
    product = models.ForeignKey(Products,on_delete=models.CASCADE,null=False,blank=False)
    areas = models.ForeignKey(Areas,on_delete=models.CASCADE,blank=False,null=False)
    image = models.CharField(max_length=250,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,blank=False,null=False)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)

class ShampooPlant(models.Model):  ## shampoo plant 
    class Meta:
        db_table = 'ShampooPlant'

    machines = models.ForeignKey(Machines,on_delete=models.CASCADE,null=False,blank=False)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=False,blank=False)
    product = models.ForeignKey(Products,on_delete=models.CASCADE,null=False,blank=False)
    areas = models.ForeignKey(Areas,on_delete=models.CASCADE,blank=False,null=False)
    image = models.CharField(max_length=250,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,blank=False,null=False)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)


class RootCauseAnalysis(models.Model):
    class Meta:
        db_table = 'Root Cause Analysis'
    
    area = models.ForeignKey(Areas,on_delete=models.CASCADE,null=True,blank=True)
    rca1 = models.CharField(max_length=255,null=True,blank=True)
    rca2 = models.CharField(max_length=255,null=True,blank=True)
    rca3 = models.CharField(max_length=255,null=True,blank=True)
    rca4 = models.CharField(max_length=255,null=True,blank=True)
    rca5 = models.CharField(max_length=255,null=True,blank=True)
    rca6 = models.CharField(max_length=255,null=True,blank=True)



# Machine parameters models  

class MachineTemperatures(models.Model):
    class Meta:
        db_table = 'MachineTemperatures'
    machine=models.ForeignKey(Machines,on_delete=models.CASCADE,blank=False,null=False)
    horizontal = models.CharField(max_length=100,blank=True,null=True)
    teeth= models.BooleanField(blank=True,null=True,default=False)
    coder = models.BooleanField(default=False,blank=True,null=True)
    vertical = models.CharField(max_length=1000,blank=True,null=True)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,null=True,blank=True)


class MachineParameters(models.Model):
    class Meta:
        db_table = 'MachineParameters'
    parameter = models.CharField(max_length=200,blank=False,null=False)
    color_code = models.CharField(max_length=100,blank=False, null=False)

    def __str__(self):
        return self.parameter if self.parameter else None

class MachineParametersGraph(models.Model):
    class Meta:
        db_table = 'MachineParametersGraph'
    machine_parameter = models.ForeignKey(MachineParameters,on_delete=models.SET_NULL,blank=True,null=True)
    params_count = models.CharField(max_length=200,blank=True,null=True)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,null=True,blank=True)


class AreaNotification(models.Model):
    class Meta:
        db_table = 'AreaNotification'
    area = models.ForeignKey(Areas,on_delete=models.CASCADE,null=False,blank=False)
    notification_text = models.TextField(null=True,blank=True)    
    recorded_date_time = models.CharField(max_length=100,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,null=False,blank=False)

#### system status model ####

class SystemStatus(models.Model):
    class Meta:
        db_table = 'SystemStatus'
    
    machine = models.ForeignKey(Machines,on_delete=models.CASCADE,null=False,blank=False)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,null=False,blank=False)
    system_status = models.BooleanField('System Status',default=True)



class Dashboard(models.Model):
    class Meta:
        db_table = 'Dashboard'
    machines = models.ForeignKey(Machines, on_delete=models.CASCADE,null=True,blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE,null=True,blank=True)
    areas = models.ForeignKey(Areas, on_delete=models.CASCADE,null=True,blank=True)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE,null=True,blank=True)
    recorded_date_time = models.CharField(max_length=255)  # Store date and time as string
    total_duration = models.FloatField(default=0)  # Count of occurrences
    type_of_stoppage = models.ForeignKey(StoppageType,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        db_table = 'Dashboard'
        indexes = [
            models.Index(fields=['recorded_date_time']),                        # Index on recorded_date_time
        ]

class DownTimeAnalysis(models.Model):
    class Meta:
        db_table = "DownTimeAnalysis"
    machine_stop_time = models.CharField(max_length=100,blank=True,null=True)
    machine_stop_duration = models.CharField(max_length=100,blank=True,null=True)
    gate = models.CharField(max_length=100,blank=True,null=True)
    gate_open_duration = models.CharField(max_length=100,blank=False,null=False)
    areas = models.ForeignKey(Areas,blank=True,null=True,on_delete=models.SET_NULL)
    area_duration = models.CharField(max_length=100,blank=True,null=True)