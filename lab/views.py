from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Device
from .models import DevicePair
from .models import DeviceInterface
from .models import InterfaceMapper
from routerconfig.models import RouteSwitchConfig
from routerconfig.task import fetch_production_config
from datetime import datetime
import time


def devices(request):
    device_list = Device.objects.all()
    context = {
        'devices': device_list,
    }
    return render(request, 'lab/devices.html', context)

def device(request, device_id=None):
    device = Device.objects.get(id=device_id)
    interfaces = DeviceInterface.objects.filter(device=device)
    
    try:
        config = RouteSwitchConfig.objects.get(device=device)
        config = config.text
    except RouteSwitchConfig.DoesNotExist:
        config = str()

    if device.environment == "PROD":
        device_pair = DevicePair.objects.get(prod_device=device)
        other_device = device_pair.lab_device
        interface_maps = InterfaceMapper.objects.filter(prod_device__device__name=device.name)
    else:
        device_pair = DevicePair.objects.get(lab_device=device)
        other_device = device_pair.prod_device
        interface_maps = InterfaceMapper.objects.filter(lab_device__device__name=device.name)

    eligible_interfaces = DeviceInterface.objects.filter(device=other_device)

    if request.method == 'POST':
        if request.POST['name']:
            messages.success(request, f"{device.name} has been updated to {request.POST['name']}")
            device.name = request.POST['name']
        if request.POST['environment']:
            messages.success(request, f"{request.POST['environment']} has been updated on {device.name}")
            device.environment = request.POST['environment']
        if request.POST['os_type']:
            messages.success(request, f"{request.POST['os_type']} has been updated on {device.name}")
            device.os_type = request.POST['os_type']
        device.save()

    context = {
        'device': device,
        'interfaces': interfaces,
        'interface_maps': interface_maps,
        'eligible_interfaces': eligible_interfaces,
        'device_config': config
        }

    return render(request, 'lab/device.html', context)

def device_add(request):
    if request.method == 'POST':
        prod_device = Device.objects.create(
            name=request.POST['name'],
            environment="PROD",
            os_type=request.POST['os_type']
        )
        lab_device = Device.objects.create(
            name=request.POST['name'],
            environment="LAB",
            os_type=request.POST['os_type']
        )
        DevicePair.objects.create(prod_device=prod_device, lab_device=lab_device)

        messages.success(request, f"{request.POST['name']} has been created")

    return HttpResponseRedirect('/devices/')

def device_delete(request, device_id=None):
    device = Device.objects.get(id=device_id)

    if device.environment == "PROD":
        device_pair = DevicePair.objects.get(prod_device=device)
        other_device = device_pair.lab_device
    else:
        device_pair = DevicePair.objects.get(lab_device=device)
        other_device = device_pair.prod_device

    device_name = device.name

    device.delete()
    other_device.delete()
    messages.success(request, f"{device_name} has been deleted")
    return HttpResponseRedirect('/devices/')

def interface_add(request, device_id=None):
    device = Device.objects.get(id=device_id)
    if request.method == 'POST':
        DeviceInterface.objects.create(name=request.POST['name'], device=device)

    messages.success(request, f"interface {request.POST['name']} has been created on {device.name}")

    return HttpResponseRedirect(f"/devices/{device.id}/")

def interface_delete(request, device_id=None, interface_id=None):
    interface = DeviceInterface.objects.get(id=interface_id)
    interface_name = interface.name
    device = Device.objects.get(id=device_id)

    interface.delete()
    messages.success(request, f"{interface_name} deleted from {device.name}")

    return HttpResponseRedirect(f"/devices/{device.id}")

def interface_mapper_add(request, device_id=None):
    lab_interface = DeviceInterface.objects.get(id=request.POST['lab_device'])
    prod_interface = DeviceInterface.objects.get(id=request.POST['prod_device'])

    InterfaceMapper.objects.create(prod_device=prod_interface, lab_device=lab_interface)
    messages.success(
        request,
        f"mapped {prod_interface.device.name} - {prod_interface.name} to {lab_interface.device.name} - {lab_interface.name}"
    )
    return HttpResponseRedirect(f"/devices/{device_id}")

def interface_mapper_delete(request, device_id=None, interface_mapper_id=None):
    interface_map = InterfaceMapper.objects.get(id=interface_mapper_id)
    device = Device.objects.get(id=device_id)

    interface_map.delete()
    messages.success(request, f"interface map has been deleted for {device.name}")

    return HttpResponseRedirect(f"/devices/{device_id}")

def device_config(request, device_id=None):
    device = Device.objects.get(id=device_id)
    if request.method == "POST":

        if request.POST['command']:
            command = request.POST['command']
        else:
            command = "show running-config"

        if device.environment == "PROD":
            task = fetch_production_config.delay(
                device=device.name,
                username=request.POST['username'],
                password=request.POST['password'],
                device_type=device.os_type,
                command=command,
            )

        while task.state not in ["SUCCESS", "FAILURE"]:
            messages.info(request, f"fetching config for {device.name} - status: {task.state}")
            time.sleep(2)

        if task.successful():
            messages.success(request, f"config fetched for {device.name}")

            try:
                RouteSwitchConfig.objects.get(device=device)
                RouteSwitchConfig.objects.update(device=device, text=task.get())
            except RouteSwitchConfig.DoesNotExist:
                RouteSwitchConfig.objects.create(device=device, text=task.get(), created=datetime.now())
        else:
            messages.danger(request, f"error fetching config for {device.name}")


    return HttpResponseRedirect(f"/devices/{device_id}")