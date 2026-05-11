from django.db.models import Q

from .models import ShippingMethod, ShippingZone, ShippingRateSnapshot


class ShippingError(Exception):
    """Exception für Versand-Fehler."""
    pass


def get_available_shipping_methods(country_code="DE", customer_group="b2c"):
    """
    Gibt verfügbare Versandmethoden für ein Land und eine Kundengruppe zurück.
    
    Argumente:
    - country_code: ISO-Ländercode (z.B. "DE", "AT")
    - customer_group: "b2c" oder "b2b"
    
    Rückgabewert:
    - QuerySet von ShippingMethod
    
    Filterung:
    - nur aktive Zonen
    - nur aktive Methoden
    - Zone muss country_code enthalten
    - Methode muss für Kundengruppe verfügbar sein (all oder exakt)
    """
    
    if customer_group not in ["b2c", "b2b"]:
        raise ShippingError(f"Invalid customer_group: {customer_group}")
    
    # Finde Zonen, die das Land enthalten und aktiv sind
    zones = ShippingZone.objects.filter(
        is_active=True,
        countries__contains=[country_code]
    )
    
    if not zones.exists():
        return ShippingMethod.objects.none()
    
    # Finde Methoden in diesen Zonen, die für die Kundengruppe verfügbar sind
    methods = ShippingMethod.objects.filter(
        Q(zone__in=zones),
        Q(is_active=True),
        Q(customer_group="all") | Q(customer_group=customer_group)
    ).order_by('sort_order', 'name')
    
    return methods


def get_shipping_method(code, customer_group="b2c", country_code="DE"):
    """
    Findet eine spezifische Versandmethode und validiert Zugangsrechte.
    
    Argumente:
    - code: eindeutiger Code der Methode
    - customer_group: "b2c" oder "b2b"
    - country_code: ISO-Ländercode
    
    Rückgabewert:
    - ShippingMethod Objekt
    
    Raises:
    - ShippingError: wenn Methode nicht gefunden oder nicht erlaubt
    """
    
    if customer_group not in ["b2c", "b2b"]:
        raise ShippingError(f"Invalid customer_group: {customer_group}")
    
    try:
        method = ShippingMethod.objects.get(code=code, is_active=True)
    except ShippingMethod.DoesNotExist:
        raise ShippingError(f"Shipping method '{code}' not found or not active")
    
    # Prüfe Kundengruppe
    if method.customer_group not in ["all", customer_group]:
        raise ShippingError(
            f"Shipping method '{code}' not available for customer group '{customer_group}'"
        )
    
    # Prüfe Zone/Land
    if country_code not in method.zone.countries:
        raise ShippingError(
            f"Shipping method '{code}' not available for country '{country_code}'"
        )
    
    if not method.zone.is_active:
        raise ShippingError(
            f"Shipping zone for method '{code}' is not active"
        )
    
    return method


def calculate_shipping_amount(method):
    """
    Berechnet Versandkosten für eine Methode.
    
    Argumente:
    - method: ShippingMethod Objekt
    
    Rückgabewert:
    - Dezimalzahl mit Versandkosten
    
    Hinweis:
    - Aktuell einfache Rückgabe von base_price
    - Keine Gewichtslogik
    - Keine Warenwertlogik
    - Keine Rabatte
    - Keine Versandkostenfrei-Regel
    """
    
    return method.base_price


def build_shipping_snapshot(method, customer_group="b2c"):
    """
    Erstellt einen Snapshot einer Versandmethode für spätere Verwendung.
    
    Argumente:
    - method: ShippingMethod Objekt
    - customer_group: "b2c" oder "b2b"
    
    Rückgabewert:
    - ShippingRateSnapshot Objekt
    """
    
    if customer_group not in ["b2c", "b2b"]:
        raise ShippingError(f"Invalid customer_group: {customer_group}")
    
    amount = calculate_shipping_amount(method)
    
    snapshot = ShippingRateSnapshot.objects.create(
        method=method,
        method_code=method.code,
        method_name=method.name,
        zone_code=method.zone.code,
        zone_name=method.zone.name,
        customer_group=customer_group,
        amount=amount,
        currency=method.currency,
        estimated_min_days=method.estimated_min_days,
        estimated_max_days=method.estimated_max_days,
    )
    
    return snapshot
