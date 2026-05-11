import { useEffect, useState } from 'react';
import ErrorState from '../components/ErrorState.jsx';
import LoadingState from '../components/LoadingState.jsx';
import {
  fetchLegalDocuments,
  fetchPaymentMethods,
  fetchShippingMethods,
} from '../api/client.js';

function Info() {
  const [legal, setLegal] = useState([]);
  const [payments, setPayments] = useState([]);
  const [shipping, setShipping] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    Promise.all([
      fetchLegalDocuments('b2c'),
      fetchPaymentMethods('b2c'),
      fetchShippingMethods('b2c', 'DE'),
    ])
      .then(([legalData, paymentData, shippingData]) => {
        if (!active) return;
        setLegal(Array.isArray(legalData) ? legalData : []);
        setPayments(Array.isArray(paymentData) ? paymentData : []);
        setShipping(Array.isArray(shippingData) ? shippingData : []);
      })
      .catch((err) => {
        if (active) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="page-stack">
      <div className="section-heading">
        <span className="eyebrow">Info und Legal</span>
        <h1>Lokale Demo-Informationen</h1>
        <p>
          Diese Seite zeigt API-Metadaten fuer Rechtstexte, Versand und Zahlarten.
          Sie ersetzt keine echten Rechtstexte und ist nicht fuer Production.
        </p>
      </div>

      <div className="notice-panel">
        <strong>DEMO PLACEHOLDER / NOT FOR PRODUCTION</strong>
        <span>
          Die angezeigten Rechtstext-Metadaten sind lokale Demo-Daten. Vor einem
          Livegang muessen echte, gepruefte Inhalte hinterlegt werden.
        </span>
      </div>

      {loading ? <LoadingState label="Info-Daten werden geladen..." /> : null}
      {error ? <ErrorState message={error} /> : null}

      {!loading && !error ? (
        <div className="info-columns">
          <section className="detail-panel">
            <h2>Aktive Legal-Dokumente</h2>
            <div className="stack-list">
              {legal.map((document) => (
                <article key={`${document.document_type}-${document.version}`}>
                  <strong>{document.title}</strong>
                  <span>
                    {document.document_type} / Version {document.version} /{' '}
                    {document.target_group}
                  </span>
                </article>
              ))}
            </div>
          </section>

          <section className="detail-panel">
            <h2>Zahlarten Demo</h2>
            <div className="stack-list">
              {payments.map((payment) => (
                <article key={payment.code}>
                  <strong>{payment.name}</strong>
                  <span>{payment.provider} / {payment.customer_group}</span>
                </article>
              ))}
            </div>
          </section>

          <section className="detail-panel">
            <h2>Versand Demo</h2>
            <div className="stack-list">
              {shipping.map((method) => (
                <article key={method.code}>
                  <strong>{method.name}</strong>
                  <span>
                    {method.base_price} {method.currency}, {method.estimated_min_days}-
                    {method.estimated_max_days} Tage
                  </span>
                </article>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </section>
  );
}

export default Info;
