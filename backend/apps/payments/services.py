from django.utils import timezone
from django.db import models
from decimal import Decimal
from .models import PaymentMethod, PaymentTransaction, PaymentMethodSnapshot


class PaymentError(Exception):
    """Payment-spezifische Fehlerbehandlung."""
    pass


def get_available_payment_methods(customer_group="b2c"):
    """
    Gibt verfügbare Zahlungsmethoden für eine Kundengruppe zurück.
    
    Args:
        customer_group (str): "b2c" oder "b2b"
        
    Returns:
        QuerySet: Sortiert nach sort_order, name
        
    Raises:
        PaymentError: Bei ungültiger Kundengruppe
    """
    if customer_group not in ["b2c", "b2b"]:
        raise PaymentError(f"Invalid customer_group: {customer_group}")
    
    return PaymentMethod.objects.filter(
        is_active=True
    ).filter(
        models.Q(customer_group="all") | models.Q(customer_group=customer_group)
    ).order_by("sort_order", "name")


def get_payment_method(code, customer_group="b2c"):
    """
    Sucht eine aktive Zahlungsmethode nach Code und prüft Kundengruppe.
    
    Args:
        code (str): Eindeutiger Code der Zahlungsmethode
        customer_group (str): "b2c" oder "b2b"
        
    Returns:
        PaymentMethod: Die gefundene Methode
        
    Raises:
        PaymentError: Bei falscher Kundengruppe oder Methode nicht gefunden
    """
    if customer_group not in ["b2c", "b2b"]:
        raise PaymentError(f"Invalid customer_group: {customer_group}")
    
    try:
        method = PaymentMethod.objects.get(code=code, is_active=True)
    except PaymentMethod.DoesNotExist:
        raise PaymentError(f"Payment method not found: {code}")
    
    # Prüfe Kundengruppen-Kompatibilität
    if method.customer_group != "all" and method.customer_group != customer_group:
        raise PaymentError(
            f"Payment method {code} not available for customer group {customer_group}"
        )
    
    return method


def build_payment_method_snapshot(method, customer_group="b2c"):
    """
    Erstellt einen Snapshot einer Zahlungsmethode.
    
    Args:
        method (PaymentMethod): Die zu snapshottende Zahlungsmethode
        customer_group (str): "b2c" oder "b2b"
        
    Returns:
        dict: Snapshot mit Methoden-Informationen
    """
    return {
        "method_id": method.id,
        "method_code": method.code,
        "method_name": method.name,
        "provider": method.provider,
        "customer_group": customer_group,
    }


def create_payment_transaction(
    order=None,
    method=None,
    amount=None,
    currency="EUR",
    customer_group="b2c",
    payment_reference="",
    provider_reference="",
    metadata=None
):
    """
    Erstellt eine neue Zahlungstransaktion.
    
    Args:
        order: Optional, Order-Instanz
        method: Optional, PaymentMethod-Instanz
        amount (Decimal): Zahlungsbetrag (muss >= 0)
        currency (str): Währungscode, default EUR
        customer_group (str): "b2c" oder "b2b"
        payment_reference (str): Optionale Referenznummer
        provider_reference (str): Optionale Provider-Referenznummer
        metadata (dict): Optionale Metadaten
        
    Returns:
        PaymentTransaction: Die neue Transaktion
        
    Raises:
        PaymentError: Bei ungültigen Daten
    """
    if amount is None:
        raise PaymentError("amount is required")
    
    amount = Decimal(str(amount))
    if amount < Decimal("0"):
        raise PaymentError("amount must be non-negative")
    
    provider = "manual"
    if method:
        provider = method.provider
    
    if metadata is None:
        metadata = {}
    
    transaction = PaymentTransaction.objects.create(
        order=order,
        method=method,
        payment_reference=payment_reference,
        provider_reference=provider_reference,
        amount=amount,
        currency=currency,
        customer_group=customer_group,
        provider=provider,
        metadata=metadata,
        raw_response={},
    )
    
    return transaction


def mark_payment_paid(transaction):
    """
    Markiert eine Zahlungstransaktion als bezahlt.
    
    Args:
        transaction (PaymentTransaction): Die Transaktion
        
    Returns:
        PaymentTransaction: Die aktualisierte Transaktion
    """
    transaction.status = "paid"
    transaction.paid_at = timezone.now()
    transaction.save()
    return transaction


def mark_payment_failed(transaction):
    """
    Markiert eine Zahlungstransaktion als fehlgeschlagen.
    
    Args:
        transaction (PaymentTransaction): Die Transaktion
        
    Returns:
        PaymentTransaction: Die aktualisierte Transaktion
    """
    transaction.status = "failed"
    transaction.save()
    return transaction


def cancel_payment(transaction):
    """
    Storniert eine Zahlungstransaktion.
    
    Args:
        transaction (PaymentTransaction): Die Transaktion
        
    Returns:
        PaymentTransaction: Die aktualisierte Transaktion
    """
    transaction.status = "cancelled"
    transaction.cancelled_at = timezone.now()
    transaction.save()
    return transaction


def refund_payment(transaction):
    """
    Erstattet eine Zahlungstransaktion.
    
    Args:
        transaction (PaymentTransaction): Die Transaktion
        
    Returns:
        PaymentTransaction: Die aktualisierte Transaktion
    """
    transaction.status = "refunded"
    transaction.refunded_at = timezone.now()
    transaction.save()
    return transaction
