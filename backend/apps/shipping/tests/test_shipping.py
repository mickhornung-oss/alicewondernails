import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.admin.sites import AdminSite
from decimal import Decimal

from apps.shipping.models import ShippingZone, ShippingMethod, ShippingRateSnapshot
from apps.shipping.services import (
    ShippingError,
    get_available_shipping_methods,
    get_shipping_method,
    calculate_shipping_amount,
    build_shipping_snapshot,
)
from apps.shipping.admin import (
    ShippingZoneAdmin,
    ShippingMethodAdmin,
    ShippingRateSnapshotAdmin,
)


# ============================================================================
# ShippingZone Model Tests
# ============================================================================

@pytest.mark.django_db
class TestShippingZoneModel:
    """Tests für das ShippingZone-Modell."""
    
    def test_create_shipping_zone_minimal(self):
        """ShippingZone kann mit Mindestfeldern erstellt werden."""
        zone = ShippingZone.objects.create(
            name="Test Zone",
            code="TEST"
        )
        assert zone.pk is not None
        assert zone.name == "Test Zone"
        assert zone.code == "TEST"
        assert zone.countries == []
        assert zone.is_active is True
        assert zone.sort_order == 0
    
    def test_create_shipping_zone_with_countries(self):
        """ShippingZone speichert Ländercodes als Array."""
        countries = ["DE", "AT", "CH"]
        zone = ShippingZone.objects.create(
            name="EU Zone",
            code="EU",
            countries=countries
        )
        zone.refresh_from_db()
        assert zone.countries == countries
    
    def test_shipping_zone_code_unique(self):
        """ShippingZone.code muss eindeutig sein."""
        ShippingZone.objects.create(name="Zone A", code="DE")
        with pytest.raises(IntegrityError):
            ShippingZone.objects.create(name="Zone B", code="DE")
    
    def test_shipping_zone_str(self):
        """ShippingZone.__str__ gibt Name und Code zurück."""
        zone = ShippingZone.objects.create(name="Deutschland", code="DE")
        assert str(zone) == "Deutschland (DE)"
    
    def test_shipping_zone_is_active_default(self):
        """ShippingZone ist standardmäßig aktiv."""
        zone = ShippingZone.objects.create(name="Test", code="T")
        assert zone.is_active is True
    
    def test_shipping_zone_ordering(self):
        """ShippingZones werden nach sort_order und name geordnet."""
        zone_b = ShippingZone.objects.create(name="B Zone", code="B", sort_order=10)
        zone_a = ShippingZone.objects.create(name="A Zone", code="A", sort_order=5)
        zones = list(ShippingZone.objects.all())
        assert zones[0].code == "A"
        assert zones[1].code == "B"


# ============================================================================
# ShippingMethod Model Tests
# ============================================================================

@pytest.mark.django_db
class TestShippingMethodModel:
    """Tests für das ShippingMethod-Modell."""
    
    def setup_method(self):
        """Erstelle eine Test-Zone vor jedem Test."""
        self.zone = ShippingZone.objects.create(
            name="Deutschland",
            code="DE",
            countries=["DE"]
        )
    
    def test_create_shipping_method_minimal(self):
        """ShippingMethod kann mit Mindestfeldern erstellt werden."""
        method = ShippingMethod.objects.create(
            zone=self.zone,
            name="Standardversand",
            code="standard_de"
        )
        assert method.pk is not None
        assert method.zone == self.zone
        assert method.name == "Standardversand"
        assert method.code == "standard_de"
        assert method.base_price == Decimal("0.00")
        assert method.customer_group == "all"
        assert method.is_active is True
    
    def test_create_shipping_method_with_prices(self):
        """ShippingMethod speichert base_price und currency."""
        method = ShippingMethod.objects.create(
            zone=self.zone,
            name="Express",
            code="express_de",
            base_price=Decimal("9.99"),
            currency="EUR"
        )
        method.refresh_from_db()
        assert method.base_price == Decimal("9.99")
        assert method.currency == "EUR"
    
    def test_shipping_method_code_unique(self):
        """ShippingMethod.code muss eindeutig sein."""
        ShippingMethod.objects.create(zone=self.zone, name="M1", code="m1")
        with pytest.raises(IntegrityError):
            ShippingMethod.objects.create(zone=self.zone, name="M2", code="m1")
    
    def test_shipping_method_base_price_non_negative(self):
        """ShippingMethod.base_price darf nicht negativ sein."""
        method = ShippingMethod(
            zone=self.zone,
            name="Test",
            code="test",
            base_price=Decimal("-5.00")
        )
        with pytest.raises(IntegrityError):
            method.save()
    
    def test_shipping_method_customer_group_choices(self):
        """ShippingMethod.customer_group kann 'all', 'b2c' oder 'b2b' sein."""
        m_all = ShippingMethod.objects.create(zone=self.zone, name="All", code="all", customer_group="all")
        m_b2c = ShippingMethod.objects.create(zone=self.zone, name="B2C", code="b2c", customer_group="b2c")
        m_b2b = ShippingMethod.objects.create(zone=self.zone, name="B2B", code="b2b", customer_group="b2b")
        assert m_all.customer_group == "all"
        assert m_b2c.customer_group == "b2c"
        assert m_b2b.customer_group == "b2b"
    
    def test_shipping_method_estimated_days_valid(self):
        """estimated_max_days muss >= estimated_min_days sein."""
        # Valid
        method = ShippingMethod.objects.create(
            zone=self.zone,
            name="Test",
            code="test",
            estimated_min_days=3,
            estimated_max_days=5
        )
        assert method.estimated_min_days == 3
        assert method.estimated_max_days == 5
        
        # Invalid: max < min
        invalid_method = ShippingMethod(
            zone=self.zone,
            name="Invalid",
            code="invalid",
            estimated_min_days=5,
            estimated_max_days=3
        )
        with pytest.raises(IntegrityError):
            invalid_method.save()
    
    def test_shipping_method_str(self):
        """ShippingMethod.__str__ gibt Name und Zone-Code zurück."""
        method = ShippingMethod.objects.create(
            zone=self.zone,
            name="Standardversand",
            code="standard"
        )
        assert str(method) == "Standardversand (DE)"
    
    def test_shipping_method_zone_protection(self):
        """ShippingMethod.zone ist durch PROTECT geschützt."""
        method = ShippingMethod.objects.create(zone=self.zone, name="M", code="m")
        with pytest.raises(IntegrityError):
            self.zone.delete()


# ============================================================================
# ShippingRateSnapshot Model Tests
# ============================================================================

@pytest.mark.django_db
class TestShippingRateSnapshotModel:
    """Tests für das ShippingRateSnapshot-Modell."""
    
    def setup_method(self):
        """Erstelle Test-Daten."""
        self.zone = ShippingZone.objects.create(name="DE", code="DE", countries=["DE"])
        self.method = ShippingMethod.objects.create(
            zone=self.zone,
            name="Standard",
            code="standard",
            base_price=Decimal("5.99"),
            estimated_min_days=3,
            estimated_max_days=5
        )
    
    def test_create_snapshot_minimal(self):
        """ShippingRateSnapshot kann erstellt werden."""
        snapshot = ShippingRateSnapshot.objects.create(
            method=self.method,
            method_code="standard",
            method_name="Standard",
            zone_code="DE",
            zone_name="Deutschland",
            customer_group="b2c",
            amount=Decimal("5.99"),
            currency="EUR"
        )
        assert snapshot.pk is not None
        assert snapshot.method == self.method
        assert snapshot.amount == Decimal("5.99")
    
    def test_snapshot_amount_non_negative(self):
        """ShippingRateSnapshot.amount darf nicht negativ sein."""
        snapshot = ShippingRateSnapshot(
            method_code="test",
            method_name="Test",
            zone_code="T",
            zone_name="Test Zone",
            customer_group="b2c",
            amount=Decimal("-1.00"),
            currency="EUR"
        )
        with pytest.raises(IntegrityError):
            snapshot.save()
    
    def test_snapshot_method_can_be_null(self):
        """ShippingRateSnapshot.method kann NULL sein (bei Methoden-Löschung)."""
        snapshot = ShippingRateSnapshot.objects.create(
            method=None,
            method_code="deleted",
            method_name="Deleted Method",
            zone_code="DE",
            zone_name="Deutschland",
            customer_group="b2c",
            amount=Decimal("0.00"),
            currency="EUR"
        )
        assert snapshot.method is None
    
    def test_snapshot_str(self):
        """ShippingRateSnapshot.__str__ gibt Methode, Zone, Betrag zurück."""
        snapshot = ShippingRateSnapshot.objects.create(
            method=self.method,
            method_code="standard",
            method_name="Standard",
            zone_code="DE",
            zone_name="Deutschland",
            customer_group="b2c",
            amount=Decimal("5.99"),
            currency="EUR"
        )
        assert "Standard (Deutschland)" in str(snapshot)
        assert "5.99 EUR" in str(snapshot)
    
    def test_snapshot_ordering_by_created_at(self):
        """ShippingRateSnapshots werden nach created_at absteigend geordnet."""
        s1 = ShippingRateSnapshot.objects.create(
            method_code="m1",
            method_name="M1",
            zone_code="Z",
            zone_name="Zone",
            customer_group="b2c",
            amount=Decimal("1.00"),
            currency="EUR"
        )
        s2 = ShippingRateSnapshot.objects.create(
            method_code="m2",
            method_name="M2",
            zone_code="Z",
            zone_name="Zone",
            customer_group="b2c",
            amount=Decimal("2.00"),
            currency="EUR"
        )
        snapshots = list(ShippingRateSnapshot.objects.all())
        assert snapshots[0].pk == s2.pk
        assert snapshots[1].pk == s1.pk


# ============================================================================
# Shipping Services Tests
# ============================================================================

@pytest.mark.django_db
class TestShippingServices:
    """Tests für Shipping-Services."""
    
    def setup_method(self):
        """Erstelle Test-Daten."""
        # Zone für Deutschland
        self.zone_de = ShippingZone.objects.create(
            name="Deutschland",
            code="DE",
            countries=["DE"]
        )
        
        # Zone für EU (ohne DE)
        self.zone_eu = ShippingZone.objects.create(
            name="Restliche EU",
            code="EU",
            countries=["AT", "CH"],
            sort_order=10
        )
        
        # Zone inaktiv
        self.zone_inactive = ShippingZone.objects.create(
            name="Inaktive Zone",
            code="INACTIVE",
            countries=["XX"],
            is_active=False
        )
        
        # Versandmethoden für DE
        self.method_all_de = ShippingMethod.objects.create(
            zone=self.zone_de,
            name="Standard (all)",
            code="standard_all",
            customer_group="all",
            base_price=Decimal("5.99")
        )
        
        self.method_b2c_de = ShippingMethod.objects.create(
            zone=self.zone_de,
            name="B2C Standard",
            code="standard_b2c",
            customer_group="b2c",
            base_price=Decimal("3.99")
        )
        
        self.method_b2b_de = ShippingMethod.objects.create(
            zone=self.zone_de,
            name="B2B Standard",
            code="standard_b2b",
            customer_group="b2b",
            base_price=Decimal("0.00")
        )
        
        # Versandmethode für EU
        self.method_eu = ShippingMethod.objects.create(
            zone=self.zone_eu,
            name="EU Standard",
            code="standard_eu",
            customer_group="all",
            base_price=Decimal("9.99"),
            is_active=True
        )
        
        # Inaktive Versandmethode
        self.method_inactive = ShippingMethod.objects.create(
            zone=self.zone_de,
            name="Inaktiv",
            code="inactive",
            customer_group="all",
            is_active=False
        )
    
    def test_get_available_methods_germany_b2c(self):
        """get_available_shipping_methods filtert richtig für DE B2C."""
        methods = get_available_shipping_methods(country_code="DE", customer_group="b2c")
        codes = set(m.code for m in methods)
        # Sollte nur aktive Methoden für DE B2C enthalten
        assert "standard_all" in codes  # all-Methode
        assert "standard_b2c" in codes  # b2c-Methode
        assert "standard_b2b" not in codes  # b2b-Methode
        assert "inactive" not in codes  # inaktive Methode
    
    def test_get_available_methods_germany_b2b(self):
        """get_available_shipping_methods filtert richtig für DE B2B."""
        methods = get_available_shipping_methods(country_code="DE", customer_group="b2b")
        codes = set(m.code for m in methods)
        assert "standard_all" in codes
        assert "standard_b2c" not in codes
        assert "standard_b2b" in codes
    
    def test_get_available_methods_eu_country(self):
        """get_available_shipping_methods findet EU-Methoden."""
        methods = get_available_shipping_methods(country_code="AT", customer_group="b2c")
        codes = set(m.code for m in methods)
        assert "standard_eu" in codes
        assert "standard_all" not in codes  # DE-Methode
    
    def test_get_available_methods_unknown_country(self):
        """get_available_shipping_methods gibt empty QuerySet für unbekanntes Land."""
        methods = get_available_shipping_methods(country_code="XX", customer_group="b2c")
        assert methods.count() == 0
    
    def test_get_available_methods_invalid_customer_group(self):
        """get_available_shipping_methods wirft Fehler für ungültige Kundengruppe."""
        with pytest.raises(ShippingError):
            get_available_shipping_methods(country_code="DE", customer_group="invalid")
    
    def test_get_available_methods_ordering(self):
        """get_available_shipping_methods ordnet nach sort_order und name."""
        methods = list(get_available_shipping_methods(country_code="DE", customer_group="b2c"))
        # Beide haben sort_order=0, daher nach name geordnet
        names = [m.name for m in methods]
        assert names == sorted(names)
    
    def test_get_shipping_method_found(self):
        """get_shipping_method findet eine gültige Methode."""
        method = get_shipping_method(code="standard_all", customer_group="b2c", country_code="DE")
        assert method.code == "standard_all"
    
    def test_get_shipping_method_not_found(self):
        """get_shipping_method wirft Fehler wenn Methode nicht existiert."""
        with pytest.raises(ShippingError):
            get_shipping_method(code="nonexistent", customer_group="b2c", country_code="DE")
    
    def test_get_shipping_method_wrong_customer_group(self):
        """get_shipping_method wirft Fehler für falsche Kundengruppe."""
        with pytest.raises(ShippingError):
            get_shipping_method(code="standard_b2c", customer_group="b2b", country_code="DE")
    
    def test_get_shipping_method_wrong_country(self):
        """get_shipping_method wirft Fehler für falsches Land."""
        with pytest.raises(ShippingError):
            get_shipping_method(code="standard_all", customer_group="b2c", country_code="AT")
    
    def test_get_shipping_method_inactive_method(self):
        """get_shipping_method wirft Fehler für inaktive Methode."""
        with pytest.raises(ShippingError):
            get_shipping_method(code="inactive", customer_group="b2c", country_code="DE")
    
    def test_get_shipping_method_inactive_zone(self):
        """get_shipping_method wirft Fehler wenn Zone inaktiv ist."""
        method = ShippingMethod.objects.create(
            zone=self.zone_inactive,
            name="Test",
            code="test_inactive_zone",
            is_active=True
        )
        with pytest.raises(ShippingError):
            get_shipping_method(code="test_inactive_zone", customer_group="b2c", country_code="XX")
    
    def test_calculate_shipping_amount(self):
        """calculate_shipping_amount gibt base_price zurück."""
        amount = calculate_shipping_amount(self.method_all_de)
        assert amount == Decimal("5.99")
    
    def test_calculate_shipping_amount_free(self):
        """calculate_shipping_amount kann kostenlos sein."""
        amount = calculate_shipping_amount(self.method_b2b_de)
        assert amount == Decimal("0.00")
    
    def test_build_shipping_snapshot_creates_record(self):
        """build_shipping_snapshot erstellt einen ShippingRateSnapshot."""
        snapshot = build_shipping_snapshot(self.method_all_de, customer_group="b2c")
        assert snapshot.pk is not None
        assert snapshot.method == self.method_all_de
        assert snapshot.method_code == "standard_all"
        assert snapshot.method_name == "Standard (all)"
        assert snapshot.zone_code == "DE"
        assert snapshot.customer_group == "b2c"
        assert snapshot.amount == Decimal("5.99")
        assert snapshot.currency == "EUR"
    
    def test_build_shipping_snapshot_captures_estimated_days(self):
        """build_shipping_snapshot speichert estimated_days."""
        method = ShippingMethod.objects.create(
            zone=self.zone_de,
            name="Express",
            code="express_de",
            estimated_min_days=1,
            estimated_max_days=2
        )
        snapshot = build_shipping_snapshot(method, customer_group="b2c")
        assert snapshot.estimated_min_days == 1
        assert snapshot.estimated_max_days == 2
    
    def test_build_shipping_snapshot_invalid_customer_group(self):
        """build_shipping_snapshot wirft Fehler für ungültige Kundengruppe."""
        with pytest.raises(ShippingError):
            build_shipping_snapshot(self.method_all_de, customer_group="invalid")


# ============================================================================
# Admin Tests
# ============================================================================

@pytest.mark.django_db
class TestShippingAdmin:
    """Tests für Admin-Interfaces."""
    
    def setup_method(self):
        """Erstelle Test-Daten."""
        self.site = AdminSite()
        
        self.zone = ShippingZone.objects.create(
            name="Test Zone",
            code="TEST",
            countries=["DE"]
        )
        
        self.method = ShippingMethod.objects.create(
            zone=self.zone,
            name="Test Method",
            code="test"
        )
        
        self.snapshot = ShippingRateSnapshot.objects.create(
            method=self.method,
            method_code="test",
            method_name="Test",
            zone_code="TEST",
            zone_name="Test Zone",
            customer_group="b2c",
            amount=Decimal("5.99"),
            currency="EUR"
        )
    
    def test_shipping_zone_admin_registered(self):
        """ShippingZoneAdmin ist registriert."""
        admin = ShippingZoneAdmin(ShippingZone, self.site)
        assert admin is not None
    
    def test_shipping_method_admin_registered(self):
        """ShippingMethodAdmin ist registriert."""
        admin = ShippingMethodAdmin(ShippingMethod, self.site)
        assert admin is not None
    
    def test_shipping_rate_snapshot_admin_registered(self):
        """ShippingRateSnapshotAdmin ist registriert."""
        admin = ShippingRateSnapshotAdmin(ShippingRateSnapshot, self.site)
        assert admin is not None
    
    def test_snapshot_admin_no_add_permission(self):
        """ShippingRateSnapshotAdmin erlaubt kein Hinzufügen."""
        admin = ShippingRateSnapshotAdmin(ShippingRateSnapshot, self.site)
        assert admin.has_add_permission(None) is False
    
    def test_snapshot_admin_no_change_permission(self):
        """ShippingRateSnapshotAdmin erlaubt keine Änderungen."""
        admin = ShippingRateSnapshotAdmin(ShippingRateSnapshot, self.site)
        assert admin.has_change_permission(None, self.snapshot) is False
    
    def test_snapshot_admin_no_delete_permission(self):
        """ShippingRateSnapshotAdmin erlaubt kein Löschen."""
        admin = ShippingRateSnapshotAdmin(ShippingRateSnapshot, self.site)
        assert admin.has_delete_permission(None, self.snapshot) is False
