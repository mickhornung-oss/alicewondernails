import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import ErrorState from '../components/ErrorState.jsx';
import LoadingState from '../components/LoadingState.jsx';
import PriceBox from '../components/PriceBox.jsx';
import {
  fetchProductDetail,
  fetchProductPrices,
  fetchShippingMethods,
} from '../api/client.js';

function ProductDetail() {
  const { slug } = useParams();
  const [customerGroup, setCustomerGroup] = useState('b2c');
  const [product, setProduct] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [shipping, setShipping] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');

    async function loadProductDetail() {
      try {
        const productData = await fetchProductDetail(slug, customerGroup);
        const [priceData, shippingData] = await Promise.all([
          fetchProductPrices(slug, customerGroup),
          fetchShippingMethods(customerGroup, 'DE'),
        ]);

        if (!active) return;
        setProduct(productData);
        setPricing(priceData);
        setShipping(Array.isArray(shippingData) ? shippingData : []);

        return;
      } catch (err) {
        if (!active) return;
        setError(err.message);
        setProduct(null);
        setPricing(null);
        setShipping([]);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadProductDetail();

    return () => {
      active = false;
    };
  }, [slug, customerGroup]);

  return (
    <section className="page-stack">
      <div className="section-heading section-heading--split">
        <div>
          <span className="eyebrow">Produktdetail</span>
          <h1>{product?.name ?? 'Produkt'}</h1>
          <p>
            Preise und Versandinformationen sind Demo-Daten aus read-only
            Endpunkten. Es gibt keinen Warenkorb und keinen Kaufabschluss.
          </p>
        </div>
        <div className="segmented-control" aria-label="Kundengruppe">
          <button
            type="button"
            className={customerGroup === 'b2c' ? 'is-active' : ''}
            onClick={() => setCustomerGroup('b2c')}
          >
            B2C
          </button>
          <button
            type="button"
            className={customerGroup === 'b2b' ? 'is-active' : ''}
            onClick={() => setCustomerGroup('b2b')}
          >
            B2B
          </button>
        </div>
      </div>

      {loading ? <LoadingState label="Produktdaten werden geladen..." /> : null}
      {error ? (
        <ErrorState title="Produkt konnte nicht angezeigt werden" message={error}>
          <Link className="button button--secondary" to="/products">
            Zurueck zu Produkte
          </Link>
        </ErrorState>
      ) : null}

      {!loading && !error && product ? (
        <div className="detail-layout">
          <article className="detail-panel">
            <span className="eyebrow">{product.category?.name ?? 'Demo-Produkt'}</span>
            <h2>{product.name}</h2>
            <p>{product.description || product.short_description || 'Keine Beschreibung hinterlegt.'}</p>

            <h3>Varianten</h3>
            <div className="variant-list">
              {(product.variants ?? []).map((variant) => (
                <div className="variant-item" key={variant.id ?? variant.sku}>
                  <strong>{variant.name}</strong>
                  <span>{variant.sku}</span>
                  <small>
                    {[variant.color_name, variant.finish, variant.size_label]
                      .filter(Boolean)
                      .join(' / ') || 'Demo-Variante'}
                  </small>
                </div>
              ))}
            </div>
          </article>

          <aside className="detail-panel detail-panel--side">
            <h2>Demo-Preise</h2>
            <PriceBox prices={pricing?.prices ?? []} currency={pricing?.currency ?? 'EUR'} />

            <h3>Versandinfo Demo</h3>
            <div className="shipping-list">
              {shipping.map((method) => (
                <div className="shipping-item" key={method.code}>
                  <strong>{method.name}</strong>
                  <span>
                    {method.base_price} {method.currency} / {method.estimated_min_days}-
                    {method.estimated_max_days} Tage
                  </span>
                </div>
              ))}
            </div>
          </aside>
        </div>
      ) : null}
    </section>
  );
}

export default ProductDetail;
