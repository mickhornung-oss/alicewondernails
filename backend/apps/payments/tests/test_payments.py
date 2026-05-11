from decimal import Decimal
from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from apps.payments.models import (
    PaymentMethod,
    PaymentTransaction,
    PaymentMethodSnapshot,
    PAYMENT_METHOD_PROVIDER_CHOICES,
)
from apps.payments.services import (
    PaymentError,
    get_available_payment_methods,
    get_payment_method,
    build_payment_method_snapshot,
    create_payment_transaction,
    mark_payment_paid,
    mark_payment_failed,
    cancel_payment,
    refund_payment,
)
from apps.payments.admin import (
    PaymentMethodAdmin,
    PaymentTransactionAdmin,
    PaymentMethodSnapshotAdmin,
)


class TestPaymentMethodModel(TestCase):
    """Tests für PaymentMethod Modell."""
    
    def setUp(self):
        self.method = PaymentMethod.objects.create(
            name="Credit Card",
            code="credit_card",
            provider="stripe",
            customer_group="all",
            is_active=True,
            sort_order=1,
        )
    
    def test_payment_method_creation(self):
        """Zahlungsmethode kann erstellt werden."""
        self.assertEqual(self.method.name, "Credit Card")
        self.assertEqual(self.method.code, "credit_card")
        self.assertEqual(self.method.provider, "stripe")
        self.assertEqual(self.method.customer_group, "all")
        self.assertTrue(self.method.is_active)
    
    def test_payment_method_code_unique(self):
        """Code muss eindeutig sein."""
        with self.assertRaises(Exception):
            PaymentMethod.objects.create(
                name="Another Card",
                code="credit_card",
                provider="stripe",
            )
    
    def test_payment_method_customer_group_choices(self):
        """customer_group Choices all/b2c/b2b werden unterstützt."""
        for group in ["all", "b2c", "b2b"]:
            method = PaymentMethod.objects.create(
                name=f"Method {group}",
                code=f"method_{group}",
                customer_group=group,
            )
            self.assertEqual(method.customer_group, group)
    
    def test_payment_method_str(self):
        """__str__ gibt sinnvollen String zurück."""
        self.assertEqual(str(self.method), "Credit Card (credit_card)")
    
    def test_payment_method_ordering(self):
        """Methoden werden nach sort_order und name sortiert."""
        method2 = PaymentMethod.objects.create(
            name="A Method",
            code="a_method",
            sort_order=0,
        )
        method3 = PaymentMethod.objects.create(
            name="Z Method",
            code="z_method",
            sort_order=0,
        )
        methods = list(PaymentMethod.objects.all())
        # sort_order 0 zuerst, dann name
        self.assertEqual(methods[0].code, "a_method")
    
    def test_payment_method_is_active_default(self):
        """is_active hat default True."""
        method = PaymentMethod.objects.create(
            name="Test",
            code="test_active",
        )
        self.assertTrue(method.is_active)
    
    def test_payment_method_sort_order_default(self):
        """sort_order hat default 0."""
        method = PaymentMethod.objects.create(
            name="Test",
            code="test_sort",
        )
        self.assertEqual(method.sort_order, 0)


class TestPaymentTransactionModel(TestCase):
    """Tests für PaymentTransaction Modell."""
    
    def setUp(self):
        self.method = PaymentMethod.objects.create(
            name="Bank Transfer",
            code="bank_transfer",
            provider="bank_transfer",
        )
        self.transaction = PaymentTransaction.objects.create(
            method=self.method,
            amount=Decimal("99.99"),
            currency="EUR",
            customer_group="b2c",
            provider="bank_transfer",
            status="pending",
        )
    
    def test_payment_transaction_creation(self):
        """Transaktion kann erstellt werden."""
        self.assertEqual(self.transaction.amount, Decimal("99.99"))
        self.assertEqual(self.transaction.currency, "EUR")
        self.assertEqual(self.transaction.customer_group, "b2c")
        self.assertEqual(self.transaction.status, "pending")
    
    def test_payment_transaction_amount_non_negative(self):
        """Amount darf nicht negativ sein (via CheckConstraint)."""
        with self.assertRaises(Exception):
            transaction = PaymentTransaction(
                method=self.method,
                amount=Decimal("-10.00"),
                currency="EUR",
                customer_group="b2c",
            )
            transaction.full_clean()
    
    def test_payment_transaction_status_default(self):
        """Status hat default 'pending'."""
        transaction = PaymentTransaction.objects.create(
            amount=Decimal("50.00"),
        )
        self.assertEqual(transaction.status, "pending")
    
    def test_payment_transaction_raw_response_default(self):
        """raw_response hat default dict."""
        transaction = PaymentTransaction.objects.create(
            amount=Decimal("50.00"),
        )
        self.assertEqual(transaction.raw_response, {})
    
    def test_payment_transaction_metadata_default(self):
        """metadata hat default dict."""
        transaction = PaymentTransaction.objects.create(
            amount=Decimal("50.00"),
        )
        self.assertEqual(transaction.metadata, {})
    
    def test_payment_transaction_str(self):
        """__str__ gibt sinnvollen String zurück."""
        result = str(self.transaction)
        self.assertIn("PaymentTransaction", result)
        self.assertIn("pending", result)
    
    def test_payment_transaction_ordering(self):
        """Transaktionen werden nach -created_at sortiert."""
        t1 = PaymentTransaction.objects.create(amount=Decimal("10.00"))
        t2 = PaymentTransaction.objects.create(amount=Decimal("20.00"))
        transactions = list(PaymentTransaction.objects.all())
        # Neueste zuerst
        self.assertEqual(transactions[0].id, t2.id)


class TestPaymentMethodSnapshotModel(TestCase):
    """Tests für PaymentMethodSnapshot Modell."""
    
    def setUp(self):
        self.method = PaymentMethod.objects.create(
            name="Invoice",
            code="invoice",
            provider="invoice",
        )
        self.snapshot = PaymentMethodSnapshot.objects.create(
            method=self.method,
            method_code="invoice",
            method_name="Invoice",
            provider="invoice",
            customer_group="b2b",
        )
    
    def test_payment_method_snapshot_creation(self):
        """Snapshot kann erstellt werden."""
        self.assertEqual(self.snapshot.method_code, "invoice")
        self.assertEqual(self.snapshot.method_name, "Invoice")
        self.assertEqual(self.snapshot.provider, "invoice")
        self.assertEqual(self.snapshot.customer_group, "b2b")
    
    def test_payment_method_snapshot_str(self):
        """__str__ gibt sinnvollen String zurück."""
        result = str(self.snapshot)
        self.assertIn("PaymentMethodSnapshot", result)
        self.assertIn("Invoice", result)
    
    def test_payment_method_snapshot_ordering(self):
        """Snapshots werden nach -created_at sortiert."""
        s1 = PaymentMethodSnapshot.objects.create(
            method_code="test1",
            method_name="Test 1",
            provider="manual",
        )
        s2 = PaymentMethodSnapshot.objects.create(
            method_code="test2",
            method_name="Test 2",
            provider="manual",
        )
        snapshots = list(PaymentMethodSnapshot.objects.all())
        # Neueste zuerst
        self.assertEqual(snapshots[0].id, s2.id)


class TestPaymentServices(TestCase):
    """Tests für Payment Services."""
    
    def setUp(self):
        self.method_all = PaymentMethod.objects.create(
            name="Credit Card",
            code="credit_card",
            provider="stripe",
            customer_group="all",
            is_active=True,
        )
        self.method_b2c = PaymentMethod.objects.create(
            name="PayPal",
            code="paypal",
            provider="paypal",
            customer_group="b2c",
            is_active=True,
        )
        self.method_b2b = PaymentMethod.objects.create(
            name="Bank Transfer",
            code="bank_transfer",
            provider="bank_transfer",
            customer_group="b2b",
            is_active=True,
        )
        self.method_inactive = PaymentMethod.objects.create(
            name="Inactive",
            code="inactive",
            provider="manual",
            is_active=False,
        )
    
    def test_get_available_payment_methods_b2c(self):
        """B2C erhält 'all' und 'b2c' Methoden."""
        methods = get_available_payment_methods(customer_group="b2c")
        codes = [m.code for m in methods]
        self.assertIn("credit_card", codes)
        self.assertIn("paypal", codes)
        self.assertNotIn("bank_transfer", codes)
        self.assertNotIn("inactive", codes)
    
    def test_get_available_payment_methods_b2b(self):
        """B2B erhält 'all' und 'b2b' Methoden."""
        methods = get_available_payment_methods(customer_group="b2b")
        codes = [m.code for m in methods]
        self.assertIn("credit_card", codes)
        self.assertIn("bank_transfer", codes)
        self.assertNotIn("paypal", codes)
        self.assertNotIn("inactive", codes)
    
    def test_get_available_payment_methods_ignores_inactive(self):
        """Inaktive Methoden werden ignoriert."""
        methods = get_available_payment_methods(customer_group="b2c")
        codes = [m.code for m in methods]
        self.assertNotIn("inactive", codes)
    
    def test_get_available_payment_methods_invalid_customer_group(self):
        """Ungültige Kundengruppe werft PaymentError."""
        with self.assertRaises(PaymentError):
            get_available_payment_methods(customer_group="invalid")
    
    def test_get_payment_method_found(self):
        """Methode wird gefunden und ist kompatibel."""
        method = get_payment_method(code="credit_card", customer_group="b2c")
        self.assertEqual(method.code, "credit_card")
    
    def test_get_payment_method_wrong_customer_group(self):
        """Falsche Kundengruppe wirft PaymentError."""
        with self.assertRaises(PaymentError):
            get_payment_method(code="paypal", customer_group="b2b")
    
    def test_get_payment_method_not_found(self):
        """Nicht existierende Methode wirft PaymentError."""
        with self.assertRaises(PaymentError):
            get_payment_method(code="nonexistent", customer_group="b2c")
    
    def test_get_payment_method_inactive(self):
        """Inaktive Methode wirft PaymentError."""
        with self.assertRaises(PaymentError):
            get_payment_method(code="inactive", customer_group="b2c")
    
    def test_build_payment_method_snapshot(self):
        """Snapshot wird mit erwarteten Feldern erstellt."""
        snapshot_dict = build_payment_method_snapshot(
            self.method_all, customer_group="b2c"
        )
        self.assertEqual(snapshot_dict["method_code"], "credit_card")
        self.assertEqual(snapshot_dict["method_name"], "Credit Card")
        self.assertEqual(snapshot_dict["provider"], "stripe")
        self.assertEqual(snapshot_dict["customer_group"], "b2c")
        self.assertIn("method_id", snapshot_dict)
    
    def test_create_payment_transaction_basic(self):
        """Transaktion wird ohne externe API erstellt."""
        transaction = create_payment_transaction(
            method=self.method_all,
            amount=Decimal("99.99"),
            currency="EUR",
            customer_group="b2c",
        )
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.amount, Decimal("99.99"))
        self.assertEqual(transaction.status, "pending")
        self.assertEqual(transaction.provider, "stripe")
    
    def test_create_payment_transaction_no_method(self):
        """Transaktion kann ohne Methode erstellt werden."""
        transaction = create_payment_transaction(
            amount=Decimal("50.00"),
            customer_group="b2c",
        )
        self.assertIsNotNone(transaction.id)
        self.assertIsNone(transaction.method)
        self.assertEqual(transaction.provider, "manual")
    
    def test_create_payment_transaction_negative_amount(self):
        """Negative Beträge werden abgelehnt."""
        with self.assertRaises(PaymentError):
            create_payment_transaction(
                amount=Decimal("-10.00"),
                customer_group="b2c",
            )
    
    def test_create_payment_transaction_missing_amount(self):
        """Fehlender Betrag wirft PaymentError."""
        with self.assertRaises(PaymentError):
            create_payment_transaction(customer_group="b2c")
    
    def test_mark_payment_paid(self):
        """Status wird zu 'paid' geändert und paid_at gesetzt."""
        transaction = create_payment_transaction(
            method=self.method_all,
            amount=Decimal("99.99"),
            customer_group="b2c",
        )
        updated = mark_payment_paid(transaction)
        self.assertEqual(updated.status, "paid")
        self.assertIsNotNone(updated.paid_at)
    
    def test_mark_payment_failed(self):
        """Status wird zu 'failed' geändert."""
        transaction = create_payment_transaction(
            method=self.method_all,
            amount=Decimal("99.99"),
            customer_group="b2c",
        )
        updated = mark_payment_failed(transaction)
        self.assertEqual(updated.status, "failed")
    
    def test_cancel_payment(self):
        """Status wird zu 'cancelled' geändert und cancelled_at gesetzt."""
        transaction = create_payment_transaction(
            method=self.method_all,
            amount=Decimal("99.99"),
            customer_group="b2c",
        )
        updated = cancel_payment(transaction)
        self.assertEqual(updated.status, "cancelled")
        self.assertIsNotNone(updated.cancelled_at)
    
    def test_refund_payment(self):
        """Status wird zu 'refunded' geändert und refunded_at gesetzt."""
        transaction = create_payment_transaction(
            method=self.method_all,
            amount=Decimal("99.99"),
            customer_group="b2c",
        )
        updated = refund_payment(transaction)
        self.assertEqual(updated.status, "refunded")
        self.assertIsNotNone(updated.refunded_at)


class TestPaymentAdmin(TestCase):
    """Tests für Payment Admin."""
    
    def test_payment_method_admin_registered(self):
        """PaymentMethodAdmin ist registriert."""
        from django.contrib.admin import site
        self.assertIn(PaymentMethod, site._registry)
    
    def test_payment_transaction_admin_registered(self):
        """PaymentTransactionAdmin ist registriert."""
        from django.contrib.admin import site
        self.assertIn(PaymentTransaction, site._registry)
    
    def test_payment_method_snapshot_admin_registered(self):
        """PaymentMethodSnapshotAdmin ist registriert."""
        from django.contrib.admin import site
        self.assertIn(PaymentMethodSnapshot, site._registry)
