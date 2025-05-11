from datetime import date
from decimal import Decimal

from circuits.models import Circuit, CircuitType, Provider, ProviderAccount
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from django.contrib.contenttypes.models import ContentType
from netbox.choices import ColorChoices
from tenancy.models import Tenant
from utilities.testing import ViewTestCases

from netbox_contract.models import (
    AccountingDimension,
    Contract,
    ContractAssignment,
    ContractType,
    Invoice,
    InvoiceLine,
    ServiceProvider,
    StatusChoices,
)


# Create test provider
Provider.objects.create(name='Provider A', slug='provider-a')

# create test tenant
Tenant.objects.create(name='Tenant 1', slug='tenant-1')

# Create test service provider
ServiceProvider.objects.create(name='Service Provider A', slug='service-provider-a')

# Create test contract types
contract_types = ContractType.objects.bulk_create([
    ContractType(name='Contract Type 1', description='Description for type 1', color=ColorChoices.COLOR_BLUE),
    ContractType(name='Contract Type 2', description='Description for type 2', color=ColorChoices.COLOR_RED),
])

for contract_type in contract_types:
    contract_type.save()

# Create three Contracts
contract1 = Contract.objects.create(
    name='Contract1',
    contract_type=ContractType.objects.get(name='Contract Type 1'),
    external_partie_object_type=ContentType.objects.get_for_model(Provider),
    external_partie_object_id=Provider.objects.get(slug='provider-a').id,
    internal_partie='default',
    status=StatusChoices.STATUS_ACTIVE,
    start_date=date(2025, 1, 1),
    end_date=date(2025, 12, 31),
    currency='usd',
    yrc=Decimal(1000),
    invoice_frequency=1
)

contract2 = Contract.objects.create(
    name='Contract2',
    contract_type=ContractType.objects.get(name='Contract Type 2'),
    external_partie_object_type=ContentType.objects.get_for_model(Provider),
    external_partie_object_id=Provider.objects.get(slug='provider-a').id,
    internal_partie='default',
    status=StatusChoices.STATUS_ACTIVE,
    start_date=date(2025, 1, 1),
    end_date=date(2025, 12, 31),
    currency='usd',
    yrc=Decimal(1000),
    invoice_frequency=1
)

contract3 = Contract.objects.create(
    name='Contract3',
    external_partie_object_type=ContentType.objects.get_for_model(Provider),
    external_partie_object_id=Provider.objects.get(slug='provider-a').id,
    internal_partie='default',
    status=StatusChoices.STATUS_ACTIVE,
    start_date=date(2025, 1, 1),
    end_date=date(2025, 12, 31),
    currency='usd',
    yrc=Decimal(1000),
    invoice_frequency=1
)

# Create test assignements
assignements = ContractAssignment.objects.bulk_create([
    ContractAssignment(
        content_type=ContentType.objects.get_for_model(Device),
        content_object=device1,
        contract=contract1
    ),
    ContractAssignment(
        content_type=ContentType.objects.get_for_model(Circuit),
        content_object=circuit1,
        contract=contract2
    )
])

for assignement in assignements:
    assignement.save()

# Create test invoices
invoices = Invoice.objects.bulk_create([
    Invoice(number='Invoice1', template=False, date=date(2025, 1, 25),
            period_start=date(2025, 1, 1), period_end=date(2025, 1, 31),
            currency='usd', amount=Decimal(100)),
    Invoice(number='Invoice2', template=False, date=date(2025, 2, 25),
            period_start=date(2025, 2, 1), period_end=date(2025, 2, 28),
            currency='usd', amount=Decimal(100)),
    Invoice(number='Invoice3', template=False, date=date(2025, 3, 25),
            period_start=date(2025, 3, 1), period_end=date(2025, 3, 31),
            currency='usd', amount=Decimal(100))
])

# associate invoices to contract
for invoice in invoices:
    invoice.save()
    invoice.contracts.add(contract1)

 
# Create test invoice lines

invoice_lines = InvoiceLine.objects.bulk_create([
    InvoiceLine(invoice=invoices[0], currency='usd', amount=Decimal(50)),
    InvoiceLine(invoice=invoices[0], currency='usd', amount=Decimal(50)),
])

for invoice_line in invoice_lines:
    invoice_line.save()


# Create test dimensions
dimensions = AccountingDimension.objects.bulk_create([
    AccountingDimension(name='account', value='account1', status=StatusChoices.STATUS_ACTIVE),
    AccountingDimension(name='account', value='account2', status=StatusChoices.STATUS_ACTIVE),
])

for dimension in dimensions:
    dimension.save()

 

# Create test providers
providers = ServiceProvider.objects.bulk_create([
    ServiceProvider(name='Provider 1', slug='provider-1'),
    ServiceProvider(name='Provider 2', slug='provider-2'),
])

for provider in providers:
    provider.save()


