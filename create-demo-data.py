from datetime import date
from decimal import Decimal

from circuits.models import Circuit, Provider
from dcim.models import Device
from django.contrib.contenttypes.models import ContentType
from netbox.choices import ColorChoices
from extras.scripts import Script

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


class CreateDemoData(Script):
    class Meta:
        name = "Create Netbox Contract demo data"
        description = "Create demo data for testing and development"
        field_order = []

    def run(self, data, commit):
        self.log_info("Creating demo data...")

        # Get test device and circuit from netbox test data
        device = Device.objects.get(id=1)
        circuit = Circuit.objects.get(id=1)

        # Create test service provider
        service_provider1 = ServiceProvider.objects.create(name='Service Provider A', slug='service-provider-a')

        # Create test contract types
        contract_types = ContractType.objects.bulk_create([
            ContractType(name='Telecom', description='Telecom contract', color=ColorChoices.COLOR_BLUE),
            ContractType(name='Maintenance', description='Maintenance contract', color=ColorChoices.COLOR_RED),
        ])

        for contract_type in contract_types:
            contract_type.save()

        # Create three Contracts
        device_contract = Contract.objects.create(
            name='MaintenanceContract1',
            contract_type=ContractType.objects.get(name='Maintenance'),
            external_party_object_type=ContentType.objects.get_for_model(ServiceProvider),
            external_party_object_id=service_provider1.id,
            internal_party='default',
            tenant=device.tenant,
            status=StatusChoices.STATUS_ACTIVE,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            currency='usd',
            yrc=Decimal(1500),
            invoice_frequency=12
        )

        circuit_contract = Contract.objects.create(
            name='TelecomContract1',
            contract_type=ContractType.objects.get(name='Telecom'),
            external_party_object_type=ContentType.objects.get_for_model(Provider),
            external_party_object_id=circuit.provider.id,
            internal_party='default',
            tenant=circuit.tenant,
            status=StatusChoices.STATUS_ACTIVE,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            currency='usd',
            mrc=Decimal(1000),
            invoice_frequency=1
        )

        # Create test assignments
        assignments = ContractAssignment.objects.bulk_create([
            ContractAssignment(
                content_type=ContentType.objects.get_for_model(Device),
                content_object=device,
                contract=device_contract
            ),
            ContractAssignment(
                content_type=ContentType.objects.get_for_model(Circuit),
                content_object=circuit,
                contract=circuit_contract
            )
        ])

        for assignment in assignments:
            assignment.save()

        # Create invoice templates
        maintenance_invoice_template = Invoice(number='dummy1', template=True, currency='usd', amount=Decimal(1500), comments='Maintenance contract template')
        telecom_invoice_template = Invoice(number='dummy2', template=True, currency='usd', amount=Decimal(1000), comments='Telecom contract template')

        # associate invoices to contract

        maintenance_invoice_template.save()
        maintenance_invoice_template.contracts.add(device_contract)

        telecom_invoice_template.save()
        telecom_invoice_template.contracts.add(circuit_contract)

        # Create test invoice lines
        maintenance_invoice_line = InvoiceLine(invoice=maintenance_invoice_template, currency='usd', amount=Decimal(1500))
        telecom_invoice_line = InvoiceLine(invoice=telecom_invoice_template, currency='usd', amount=Decimal(1000))


        for invoice_line in [maintenance_invoice_line, telecom_invoice_line]:
            invoice_line.save()


        # Create test dimensions
        account1 = AccountingDimension(name='account', value='account1', status=StatusChoices.STATUS_ACTIVE)
        account2 = AccountingDimension(name='account', value='account2', status=StatusChoices.STATUS_ACTIVE)
        cost_center1 = AccountingDimension(name='cost_center', value='cost_center1', status=StatusChoices.STATUS_ACTIVE)

        for dimension in [account1, account2, cost_center1]:
            dimension.save()

        maintenance_invoice_line.accounting_dimensions.add(account1)
        telecom_invoice_line.accounting_dimensions.add(account2)
        maintenance_invoice_line.accounting_dimensions.add(cost_center1)
        telecom_invoice_line.accounting_dimensions.add(cost_center1)

        # Create invoices
        invoices = Invoice.objects.bulk_create([
            Invoice(number='maintenance_invoice1', template=False, date=date(2025, 1, 25),
                    period_start=date(2025, 1, 1), period_end=date(2025, 12, 31),
                    currency='usd', amount=Decimal(1500)),
            Invoice(number='telecom_invoice1', template=False, date=date(2025, 1, 25),
                    period_start=date(2025, 1, 1), period_end=date(2025, 1, 31),
                    currency='usd', amount=Decimal(1000)),
        ])

