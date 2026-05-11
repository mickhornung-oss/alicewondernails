# Modulstatus

| Modul | Status | Tests | Freeze-Status | Notizen |
|---|---|---|---|---|
| core | tested | 3 tests (health, response format, no-db); 304 backend pytest gruen | frozen | technisches Basismodul fuer Health-Endpunkt; Freeze abgeschlossen in AB 16; keine Migrationen, keine Models, keine Fachlogik |
| accounts | frozen | gruen | frozen | stabiler Erststand, Aenderungen nur noch dokumentiert |
| customers | frozen | gruen | frozen | stabiler Erststand, Aenderungen nur noch dokumentiert |
| business | frozen | gruen | frozen | stabiler Erststand, Aenderungen nur noch dokumentiert |
| catalog | frozen | gruen | frozen | stabiler Erststand, Aenderungen nur noch dokumentiert |
| pricing | frozen | gruen | frozen | stabiler Erststand, Aenderungen nur noch dokumentiert |
| cart | frozen | gruen | frozen | stabiler Erststand, Aenderungen nur noch dokumentiert |
| orders | tested | gruen | frozen | stabiler Erststand, Aenderungen nur noch dokumentiert; AB 12 kontrollierte Erweiterung um Checkout-Snapshots und Versandkosten |
| legal | tested | gruen | frozen | LegalDocument/Version Versionierung; Review/Freeze abgeschlossen in 07.1 |
| consent | tested | gruen | frozen | ConsentCategory/Record Tracking; Review/Freeze abgeschlossen in 07.1 |
| auditlog | frozen | gruen | frozen | AuditLogEntry Infrastructure; Read-only Admin; Review/Freeze abgeschlossen in 08.1 |
| payments | frozen | gruen | frozen | PaymentMethod/Transaction/Snapshot Grundstruktur; Review/Freeze abgeschlossen in 10.1 |
| shipping | frozen | gruen | frozen | ShippingZone/Method/RateSnapshot; Review/Freeze abgeschlossen in 09.1 |
| checkout | frozen | gruen | frozen | CheckoutSession/Event Checkout-Sitzungen; Review/Freeze abgeschlossen in 11.1 |
| api | tested | 33 passed (304 total) | frozen | v1 read-only REST API; 7 endpoints; DRF integration; local/dev green; Review/Freeze abgeschlossen in 14.1 |
| content | planned | nein | offen | spaeter Content- und CMS-Funktionen |
