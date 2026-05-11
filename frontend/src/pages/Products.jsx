import { useEffect, useState } from 'react';
import ErrorState from '../components/ErrorState.jsx';
import LoadingState from '../components/LoadingState.jsx';
import ProductCard from '../components/ProductCard.jsx';
import { fetchProducts } from '../api/client.js';

function Products() {
  const [customerGroup, setCustomerGroup] = useState('b2c');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');

    fetchProducts(customerGroup)
      .then((data) => {
        if (active) {
          setProducts(Array.isArray(data) ? data : []);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.message);
          setProducts([]);
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
  }, [customerGroup]);

  return (
    <section className="page-stack">
      <div className="section-heading section-heading--split">
        <div>
          <span className="eyebrow">Produktkatalog</span>
          <h1>Produkte</h1>
          <p>Demo-Produkte aus der API. Preise werden erst im Detail geladen.</p>
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

      {loading ? <LoadingState label="Produkte werden geladen..." /> : null}
      {error ? <ErrorState message={error} /> : null}

      {!loading && !error ? (
        <div className="product-grid">
          {products.map((product) => (
            <ProductCard key={product.slug} product={product} />
          ))}
        </div>
      ) : null}
    </section>
  );
}

export default Products;
